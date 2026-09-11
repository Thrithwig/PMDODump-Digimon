"""Apply the user's unmatched-item decisions while preserving existing matches."""
import copy
import json
import re
import subprocess
from pathlib import Path
from digimon_runtime_assets import ROOT, ASSETS, DATA, lua, write

def event(name, **values):return {'Key':{'str':[0]},'Value':{'$type':name,**values}}
def script(name, **args):return event('RogueEssence.Dungeon.BattleScriptEvent, RogueEssence',Script=name,ArgTable=lua(args))
def native(path,value):path.write_text('\ufeff'+json.dumps(value,ensure_ascii=False,indent='')+'\n',encoding='utf-8',newline='\n')
def baseline_items():
    paths=sorted((ASSETS/'Data/Item').glob('*.json'))
    paths=[p for p in paths if not p.stem.startswith(('digi_brave_point_','digi_tm_'))]
    process=subprocess.run(['git','-C',str(ASSETS),'cat-file','--batch'],input=''.join('HEAD:Data/Item/'+p.name+'\n' for p in paths).encode(),capture_output=True,check=True)
    data=process.stdout;offset=0;result={}
    for path in paths:
        end=data.index(b'\n',offset);size=int(data[offset:end].split()[-1]);offset=end+1
        result[path.stem]=json.loads(data[offset:offset+size].decode('utf-8-sig'));offset+=size+1
    return result

def filter_drops(value,banned):
    if isinstance(value,list):return [clean for child in value if (clean:=filter_drops(child,banned)) is not None]
    if not isinstance(value,dict):return value
    # Typed item entries and weighted item-string lists. Do not match tile ID "empty".
    if any(isinstance(value.get(k),str) and value[k] in banned for k in ('Item','HiddenValue','Value')):return None
    if value.get('ID') in banned and (value.get('ID')!='empty' or 'Amount' in value or 'Cursed' in value):return None
    clean={}
    for k,child in value.items():
        converted=filter_drops(child,banned)
        if child is not None and converted is None and k in ('Spawn','ToSpawn','Item1'):return None
        clean[k]=converted
    if 'Key' in clean and 'Value' in clean and clean['Value'] is None:return None
    if isinstance(clean.get('Spawns'),dict):
        clean['Spawns']={k:v for k,v in clean['Spawns'].items() if k not in banned and not (isinstance(v,dict) and v.get('Spawns')==[])}
    return clean

def main():
    originals=baseline_items()
    protected={x['item_id'] for x in json.loads((DATA/'item_mapping.json').read_text())}
    before={i:(ASSETS/f'Data/Item/{i}.json').read_bytes() for i in protected}
    banned=set();report=[]
    food_names={'apple':'Cookie','apple_big':'Large Cookie','apple_huge':'Jumbo Cookie','apple_perfect':'Perfect Cookie',
        'apple_golden':'Golden Cookie','banana':'Pie','banana_big':'Large Pie','banana_golden':'Golden Pie','grimy':'Corrupted Snack','chestnut':'Data Nut'}
    foods=[('Vigor Mushroom','MaxHPBonus'),('Mental Melon','sp'),('Power Pine','AtkBonus'),('Aegis Apple','DefBonus'),
           ('Clever Carrot','MAtkBonus'),('Boost Banana','SpeedBonus'),('Digimeat','bond'),('Exciting Meat','bond'),('Best Meat','bond'),('Miracle Meat','abi')]
    ammo={'ammo_cacnea_spike':'ATK','ammo_corsola_twig':'INT','ammo_iron_thorn':'DEF','ammo_silver_spike':'SPD',
          'ammo_stick':'HP','ammo_geo_pebble':'SP','ammo_gravelerock':'DEF','ammo_golden_thorn':'ATK','ammo_rare_fossil':'SPD'}
    food_index=0
    for sid,base in originals.items():
        if sid in protected:continue
        obj=copy.deepcopy(base['Object']);old=obj['Name']['DefaultText'];prefix=sid.split('_')[0]
        action='retained';detail='Existing mechanics retained.'
        if not obj['Released'] or prefix in ('apricorn','evo','herb','medicine','wand','xcl','tm') or sid=='empty' or (prefix=='seed' and sid!='seed_blast'):
            banned.add(sid);obj['Released']=False;action='disabled'
            detail='Removed from availability; definition retained for existing references.'
            if prefix in ('xcl','tm'):detail='Removed from stores and drop tables pending replacement design.'
        elif prefix=='food':
            obj['Name']={'DefaultText':food_names[sid[5:]],'LocalTexts':{}};action='renamed'
        elif prefix=='orb':
            obj['Name']={'DefaultText':old.replace('Orb','Command'),'LocalTexts':{}};action='renamed'
        elif sid=='seed_blast':obj['Name']={'DefaultText':'Dynamite','LocalTexts':{}};action='renamed'
        elif prefix=='gummi':
            name,stat=foods[food_index%len(foods)];food_index+=1
            obj['Name']={'DefaultText':name,'LocalTexts':{}}
            obj['UseEvent']['OnHits']=[script('DigimonTrainingFood',stat=stat)]
            obj['Desc']={'DefaultText':'Training food. Adds a training point or 5 CAM/ABI, fills 5 Belly, and grants your personality bonus. View your personality at the Tree of Life.','LocalTexts':{}}
            action='converted';detail='No elemental dependence. Personality adds 5% of its favored stat; Builder/Searcher add one to all stats.'
        elif prefix=='ammo':
            stat=ammo[sid];keep={k:obj[k] for k in ('Price','Released')}
            obj=copy.deepcopy(originals['ammo_cacnea_spike']['Object']);obj.update(keep)
            obj['Name']={'DefaultText':stat+' Restraint Chip C','LocalTexts':{}}
            statuses={'ATK':'mod_attack','DEF':'mod_defense','INT':'mod_special_attack','SPD':'mod_speed'}
            if stat in statuses:
                obj['UseEvent']['OnHits'][1]=event('PMDC.Dungeon.StatusStackBattleEvent, PMDC',Stack=-2,StatusID=statuses[stat],AffectTarget=True,SelfInflicted=False,SilentCheck=True,Anonymous=False,TriggerMsg={'Key':None},Anims=[])
                effect='lowers '+stat+' by two stages'
            else:
                obj['UseEvent']['OnHits'][1]=script('DigimonRestraint',stat=stat);effect='removes up to 8 trained '+stat+' points'
            obj['Desc']={'DefaultText':'A thrown chip that deals damage and '+effect+'.','LocalTexts':{}}
            action='converted';detail='Cacnea Spike projectile and damage design; '+effect+'.'
        elif prefix=='held':
            # Unmatched legacy gear becomes a real source equipment effect, not a
            # Pokemon-specific passive with a misleading new label.
            keep={k:obj[k] for k in ('Price','Sprite','Released')}
            obj=copy.deepcopy(originals['held_flame_plate']['Object']);obj.update(keep)
            element=next((e for key,e in {'fire':'fire','charcoal':'fire','water':'water','icicle':'water','ice':'water','grass':'grass','seed':'grass','electric':'electric','magnet':'electric','ground':'ground','sand':'ground','flying':'flying','beak':'flying','fairy':'fairy','pink':'fairy','dark':'dark','glasses':'dark'}.items() if key in sid),None)
            if element:
                name={'fire':'Flare','water':'Aqua','grass':'Plant','electric':'Electric','ground':'Sand','flying':'Wind','fairy':'Shine','dark':'Dark'}[element]+' Guard'
                obj['BeforeBeingHits']=[event('PMDC.Dungeon.MultiplyElementEvent, PMDC',MultElement=element,Numerator=9,Denominator=10,Anims=[],Msg=False)]
                desc='Reduces '+element+' damage by 10%.'
            else:
                name='Master Guard';desc='Reduces incoming damage by 5%.'
                obj['BeforeBeingHits']=[event('PMDC.Dungeon.MultiplyDamageEvent, PMDC',Numerator=19,Denominator=20)]
            obj['Name']={'DefaultText':name,'LocalTexts':{}};obj['Desc']={'DefaultText':desc,'LocalTexts':{}}
            action='converted';detail='Replaced old passive with Cyber Sleuth guard equipment; price and item ID retained.'
        if action=='renamed':
            obj['Desc']={'DefaultText':obj['Desc']['DefaultText'].replace(old,obj['Name']['DefaultText']).replace('Pokémon','Digimon').replace('berry','snack').replace('orb','command'),'LocalTexts':{}}
        if action!='retained':native(ASSETS/f'Data/Item/{sid}.json',{'Version':base['Version'],'Object':obj})
        report.append({'item_id':sid,'original_name':old,'name':obj['Name']['DefaultText'],'action':action,'detail':detail})
    for grade,amount in {'e':2500,'d':5000,'c':10000,'b':20000,'a':40000}.items():
        sid='digi_brave_point_'+grade;obj=copy.deepcopy(originals['seed_joy']['Object'])
        obj['Name']={'DefaultText':'Brave Point '+grade.upper(),'LocalTexts':{}}
        obj['Desc']={'DefaultText':'Grants '+str(amount)+' EXP.','LocalTexts':{}}
        obj['Released']=True;obj['ItemStates']=[]
        obj['UseEvent']['OnHits']=[script('DigimonBravePoint',amount=amount)]
        native(ASSETS/f'Data/Item/{sid}.json',{'Version':'0.8.12.0','Object':obj})
        report.append({'item_id':sid,'name':obj['Name']['DefaultText'],'action':'added','detail':str(amount)+' fixed EXP'})
    for path in (ASSETS/'Data/Zone').glob('*.json'):
        raw=path.read_bytes();data=json.loads(raw.decode('utf-8-sig'));clean=filter_drops(data,banned)
        if clean!=data:native(path,clean)
    shop=ASSETS/'Data/Script/origin/common_shop.lua';text=shop.read_text(encoding='utf-8-sig')
    text=''.join(line for line in text.splitlines(keepends=True) if not any(id in banned for id in re.findall(r'Index\s*=\s*"([^"]+)"',line)))
    if 'Index = "digi_brave_point_e"' not in text:
        text=text.replace('COMMON.ESSENTIALS = {','COMMON.ESSENTIALS = {\n  { Index = "digi_brave_point_e", Amount = 0, Price = 2500},\n  { Index = "digi_brave_point_d", Amount = 0, Price = 5000},\n  { Index = "digi_brave_point_c", Amount = 0, Price = 10000},\n  { Index = "digi_brave_point_b", Amount = 0, Price = 20000},\n  { Index = "digi_brave_point_a", Amount = 0, Price = 40000},')
    shop.write_text(text,encoding='utf-8',newline='\n')
    write(DATA/'item_implementation.json',{'items':report,'unavailable':sorted(banned),'protected_matches':sorted(protected)})
    assert all((ASSETS/f'Data/Item/{i}.json').read_bytes()==raw for i,raw in before.items())
    print('Processed',len(report),'items;',len(banned),'unavailable; existing',len(protected),'matches unchanged.')

if __name__=='__main__':main()
