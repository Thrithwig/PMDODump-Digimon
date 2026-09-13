"""Build the scoped Phase 1 engine assets from source data and explicit adaptations."""
import argparse
import copy
import json
from pathlib import Path
import random
import re
import shutil
import subprocess
import xml.etree.ElementTree as ET
from digimon_skill_presentation import profile, apply as apply_presentation
from digimon_progression_tuning import STAGE_MULTIPLIERS, BASE_EXP_PER_MEMORY, growth_table, remove_apricorns

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'DataAsset/Digimon'
ASSETS = ROOT / 'DumpAsset'
ELEMENTS = {'Neutral':'normal','Fire':'fire','Water':'water','Plant':'grass','Electric':'electric',
            'Thunder':'electric','Earth':'ground','Wind':'flying','Light':'fairy','Dark':'dark'}


def read(path):
    return json.loads(path.read_text(encoding='utf-8-sig'))


def write(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8', newline='\n')


def lua(value):
    if value is None: return 'nil'
    if value is True: return 'true'
    if value is False: return 'false'
    if isinstance(value, str): return json.dumps(value, ensure_ascii=False)
    if isinstance(value, (int,float)): return str(value)
    if isinstance(value,list): return '{'+','.join(lua(x) for x in value)+'}'
    return '{'+','.join('['+lua(str(k))+']='+lua(v) for k,v in value.items())+'}'


def original(relative, raw=False):
    data=subprocess.run(['git','-c','safe.directory='+str(ASSETS).replace('\\','/'),'-C',str(ASSETS),'show','HEAD:'+relative],check=True,capture_output=True).stdout
    return data if raw else data.decode('utf-8-sig')


def priority(event, order=-1):
    return {'Key':{'str':[order]},'Value':event}


def native_skill(entry, index):
    source = entry['variants'][0]['source']
    support = source['Type']=='Support'
    skill_id = entry['id']
    mapping = {
        'acceleration_boost':'focus_energy','attack_charge':'swords_dance','attack_charge_field':'howl',
        'mental_charge':'calm_mind','mental_charge_field':'calm_mind','speed_charge':'agility',
        'speed_charge_field':'tailwind','guard_break':'leer','speed_break':'scary_face',
        'mirror_reflection':'magic_coat','status_barrier':'safeguard','safety_guard':'endure',
        'escape_dash':'teleport','heal':'heal_pulse','x_heal':'heal_pulse','final_heal':'heal_pulse',
        'aura':'life_dew','final_aura':'life_dew','revive':'heal_pulse','perfect_revival':'life_dew'
    }
    selected = profile(entry)
    template = mapping.get(skill_id, 'refresh') if support else selected[0]
    obj = copy.deepcopy(read(ASSETS / f'Data/Skill/{template}.json')['Object'])
    obj['Name']={'DefaultText':entry['name'],'LocalTexts':{}}
    obj['IndexNum']=12000+index
    obj['Released']=True
    obj['BaseCharges']=max(5,min(30,60//max(1,int(source['SP Cost']))))
    obj['Comment']='Cyber Sleuth source: '+source['Description']
    if support:
        description = 'Phase 1 adaptation: '+obj['Desc']['DefaultText']
        if skill_id in ('revive','perfect_revival'):
            obj['Data']['OnHits']=[priority({'$type':'PMDC.Dungeon.ReviveAllEvent, PMDC'})]
            obj['HitboxAction']['TargetAlignments']=1
            obj['Explosion']['TargetAlignments']=1
            description='Revives fallen teammates using the dungeon revival rules.'
        elif skill_id in ('heal','x_heal','final_heal','aura','final_aura'):
            numerator = {'heal':1,'aura':1,'x_heal':2,'final_heal':3,'final_aura':3}[skill_id]
            obj['Data']['OnHits']=[priority({'$type':'PMDC.Dungeon.RestoreHPEvent, PMDC',
                'Numerator':numerator,'Denominator':4,'AffectTarget':True})]
            description=f'Restores {numerator*25}% HP using the selected dungeon healing range.'
    else:
        data=obj['Data']
        for field in ('BeforeTryActions','BeforeActions','OnActions','BeforeExplosions','BeforeHits','OnHits','OnHitTiles','AfterActions','ElementEffects'):
            data[field]=[]
        power=int(source['Power'])
        data['Element']=ELEMENTS[source['Attribute']]
        data['Category']=1 if source['Type']=='Physical' else 2
        match=re.search(r'(\d+)% accuracy',source['Description'],re.I)
        data['HitRate']=-1 if 'always hits' in source['Description'].lower() else int(match.group(1)) if match else 100
        # Explicit vertical-slice combat conversion, separate from immutable source facts.
        mapped_power=max(1,(power+1)//2) if power else 60
        data['SkillStates']=[{'$type':'RogueEssence.Dungeon.BasePowerState, RogueEssence','Power':mapped_power}]
        damage={'$type':'PMDC.Dungeon.DamageFormulaEvent, PMDC'}
        if source['Type']=='Fixed':
            fixed=re.search(r'Fixed damage of (\d+)',source['Description'])
            if not fixed: raise ValueError('Missing fixed damage: '+skill_id)
            damage={'$type':'PMDC.Dungeon.SpecificDamageEvent, PMDC','Damage':max(1,int(fixed.group(1))//10)}
        data['OnHits']=[priority(damage)]
        targeting = apply_presentation(obj, selected)
        description=f"{source['Type']} {source['Attribute']} attack. " + (f"Power {mapped_power}." if source['Type']!='Fixed' else f"Deals {damage['Damage']} fixed damage.")
        description += ' ' + targeting
        description += ' Phase 1: source secondary effects are not applied.'
    obj['Desc']={'DefaultText':description,'LocalTexts':{}}
    return {'Version':'0.8.12.0','Object':obj}, {'skill':skill_id,'source_variant':entry['variants'][0]['id'],
        'template':template,'runtime_description':description,'source_description':source['Description']}


def main():
    parser=argparse.ArgumentParser();parser.add_argument('--phase2',action='store_true');args=parser.parse_args()
    phase='phase2' if args.phase2 else 'phase1'
    manifest=read(DATA/(phase+'_manifest.json')); gameplay=read(DATA/(phase+'_gameplay.json'))
    curves={x['id']:x for x in gameplay['species']}
    source={x['id']:x for x in manifest['digimon']}
    base_growth=read(ASSETS/'Data/GrowthGroup/medium_fast.json')
    stages=dict(STAGE_MULTIPLIERS)
    if args.phase2:
        STAGE_MULTIPLIERS.update({'Armor':1,'Ultra':0.5});stages=dict(STAGE_MULTIPLIERS)
    for stage in stages:
        growth=copy.deepcopy(base_growth)
        growth['Object']['Name']={'DefaultText':'Digimon '+stage,'LocalTexts':{}}
        growth['Object']['EXPTable']=growth_table(base_growth['Object']['EXPTable'],stage)
        write(ASSETS/('Data/GrowthGroup/digi_'+stage.lower().replace('-','_')+'.json'),growth)
    from digimon_starter_skills import generate as generate_starters, learnset as starter_learnset
    generate_starters(manifest)
    adaptations=[]
    for index,skill in enumerate(manifest['skills']):
        generated, adaptation=native_skill(skill,index)
        write(ASSETS/f"Data/Skill/digi_{skill['id']}.json",generated);adaptations.append(adaptation)
    prototype=read(ASSETS/'Data/Monster/bulbasaur.json')['Object']
    art=ASSETS/'Content/StaticCreature';art.mkdir(parents=True,exist_ok=True)
    runtime={'species':{},'transitions':gameplay['transitions'],'scope':['base_camp','base_camp_2'],
             'dungeon':'tropical_path','cast_seed':20260910}
    for entry in manifest['digimon']:
        species_id=entry['id']; obj=copy.deepcopy(prototype)
        number=10000+int(entry['source']['Number'])
        obj.update(Name={'DefaultText':entry['name'],'LocalTexts':{}},Title={'DefaultText':entry['stage']+' Digimon','LocalTexts':{}},
                   IndexNum=number,Released=True,Comment='Digimon Phase 1',EXPTable='digi_'+(('Mega' if species_id=='omnishoutmon' else 'Rookie') if entry['stage']=='None' else entry['stage']).lower().replace('-','_'),
                   SkillGroup1='undiscovered',SkillGroup2='undiscovered',JoinRate=-100000,PromoteFrom='',Promotions=[])
        form=obj['Forms'][0]; obj['Forms']=[form]
        form.update({'$type':'PMDC.Data.DigimonFormData, PMDC','GenderlessWeight':1,'MaleWeight':0,'FemaleWeight':0,
                     'Personalities':[0],'TeachSkills':[],'SharedSkills':[],'SecretSkills':[],
                     'FormName':{'DefaultText':entry['name'],'LocalTexts':{}},'Temporary':False,
                     'Element1':ELEMENTS[entry['attribute']],'Element2':'none',
                     'DigimonAttribute':entry['type'],
                     'Intrinsic1':'none','Intrinsic2':'none','Intrinsic3':'none',
                     'LevelSkills':[{'Level':int(s['level'] or 1),'Skill':'digi_'+s['skill']} for s in entry['skills']],
                     'LevelStats':[[row['stats'][key] for key in ('max_hp','attack','defense','magic_attack','magic_defense','speed')]
                                   for row in curves[species_id]['stats_by_level']],
                     'ExpYield':int(entry['source']['Memory'])*BASE_EXP_PER_MEMORY})
        form['LevelSkills'] = starter_learnset(entry, form['LevelSkills'])
        if not form['LevelSkills']: raise ValueError('No skills for '+species_id)
        write(ASSETS/f'Data/Monster/{species_id}.json',{'Version':'0.8.12.0','Object':obj})
        transparent_art=DATA/f'SpritePackages/Sources/{species_id}.png'
        shutil.copyfile(transparent_art if transparent_art.exists() else DATA/f'Images/{species_id}.png',art/f'{number}.png')
        runtime['species'][species_id]={'name':entry['name'],'stage':entry['stage'],
            'element':entry['attribute'],'attribute':entry['type'],
            'sp':[row['stats']['source_sp'] for row in curves[species_id]['stats_by_level']],
            'skills':form['LevelSkills']}
    if args.phase2:
        from digimon_passive_abilities import apply as apply_passives
        apply_passives()
        runtime['abi_maximum']=200
        scoped=read(DATA/'phase1_manifest.json')
    else: scoped=manifest
    runtime['npc_pool']=sorted(x['id'] for x in scoped['digimon'] if x['stage'] in ('Baby','In-Training','Rookie','Champion'))
    random.Random(runtime['cast_seed']).shuffle(runtime['npc_pool'])
    path=ASSETS/'Data/Script/origin/digimon/runtime_catalog.lua'
    path.write_text('-- Generated runtime catalog; source facts remain in DataAsset.\nreturn '+lua(runtime)+'\n',encoding='utf-8',newline='\n')
    write(DATA/(phase+'_skill_adaptations.json'),adaptations)
    if args.phase2:
        from digimon_terminal_catalog import render
        (ASSETS/'Data/Script/origin/digimon/catalog.lua').write_text(render(manifest,gameplay['policies']),encoding='utf-8')
        print(f'Generated {len(source)} monsters and {len(adaptations)} skills; scoped maps preserved')
        return
    # Only the explicitly scoped zone is changed. Keep item spawns and dialogue events.
    zone=json.loads(original('Data/Zone/tropical_path.json'))
    zone['Object']['ExpPercent']=100
    main_segment=zone['Object']['Segments'][0]
    pool=next(x for x in main_segment['ZoneSteps'] if 'TeamSpawnZoneStep' in x['$type'])
    template=pool['Spawns'][0]
    babies=sorted(x['id'] for x in manifest['digimon'] if x['stage'] in ('Baby','In-Training'))
    pool['Spawns']=[]
    for species_id in babies:
        spawn=copy.deepcopy(template);mob=spawn['Spawn']['Spawn']
        mob['BaseForm']={'Species':species_id,'Form':0,'Skin':'normal','Gender':0}
        mob['Level']={'Min':2,'Max':5};mob['Intrinsic']='none'
        mob['SpecifiedSkills']=['digi_'+source[species_id]['skills'][0]['skill']]
        mob['SpawnFeatures']=[{'$type':'PMDC.LevelGen.MobSpawnLuaTable, PMDC','LuaTable':'{ DigimonNatural = true }'}]
        spawn['Range']={'Min':0,'Max':4};spawn['Rate']=10;pool['Spawns'].append(spawn)
    # Convert the two tutorial NPC appearances while keeping their dialogue unchanged.
    npc_step=next(x for x in main_segment['ZoneSteps'] if 'SpreadStepZoneStep,' in x['$type'])
    for index, step in enumerate(npc_step['Spawns']['ToSpawn']):
        mob=step['Spawn']['Spawns'][0]['Spawns'][0]
        mob['BaseForm']={'Species':runtime['npc_pool'][index],'Form':0,'Skin':'normal','Gender':0}
        mob['Intrinsic']='none'
    # A guaranteed In-Training guardian completes the scoped final-floor encounter.
    final_floor=main_segment['Floors'][-1]
    boss=copy.deepcopy(pool['Spawns'][babies.index('koromon')]['Spawn']['Spawn'])
    boss['Level']={'Min':8,'Max':8}
    boss['SpawnFeatures'][0]['LuaTable']='{ DigimonNatural = true, DigimonBoss = true }'
    boss['SpawnFeatures'].append({'$type':'PMDC.LevelGen.MobSpawnBoost, PMDC','MaxHPBonus':20})
    placement=copy.deepcopy(next(x for x in final_floor['GenSteps'] if 'PlaceRandomMobsStep' in x['Value']['$type']))
    placement['Value']['Spawn']={'$type':'RogueEssence.LevelGen.PresetMultiTeamSpawner`1[[RogueEssence.LevelGen.MapGenContext, RogueEssence]], RogueEssence',
        'Spawns':[{'Explorer':False,'Spawns':[boss]}]}
    final_floor['GenSteps'].append(placement)
    stair_ids={'stairs_go_up':'digi_tropical_exit','stairs_secret_down':'digi_tropical_secret'}
    for old,new in stair_ids.items():
        tile=read(ASSETS/f'Data/Tile/{old}.json')
        tile['Object']['InteractWithTiles'].insert(0,{'Key':{'str':[-10]},'Value':{
            '$type':'RogueEssence.Dungeon.SingleCharScriptEvent, RogueEssence',
            'Script':'DigimonTropicalExit','ArgTable':'{}'}})
        write(ASSETS/f'Data/Tile/{new}.json',tile)
    def replace_stairs(value):
        if isinstance(value,dict):
            if value.get('ID') in stair_ids: value['ID']=stair_ids[value['ID']]
            for child in value.values(): replace_stairs(child)
        elif isinstance(value,list):
            for child in value: replace_stairs(child)
    replace_stairs(final_floor)
    # Keep Tropical Path's secret room: its stairs explicitly target segment 1.
    # Only unrelated mystery detours (segment 2) are excluded from this slice.
    main_segment['ZoneSteps']=[x for x in main_segment['ZoneSteps'] if 'SpreadStepRangeZoneStep' not in x['$type']]
    zone['Object']['Segments']=[main_segment, zone['Object']['Segments'][1]]
    write(ASSETS/'Data/Zone/tropical_path.json',remove_apricorns(zone))
    # User explicitly removed Apricorn loot/shop stock across the game.
    for zone_path in (ASSETS/'Data/Zone').glob('*.json'):
        raw=zone_path.read_bytes()
        text=raw.decode('utf-8-sig')
        if 'apricorn_' in text:
            cleaned=remove_apricorns(json.loads(text))
            output=json.dumps(cleaned,ensure_ascii=False,indent='')+'\n'
            if b'\r\n' in raw: output=output.replace('\n','\r\n')
            zone_path.write_bytes((b'\xef\xbb\xbf' if raw.startswith(b'\xef\xbb\xbf') else b'')+output.encode('utf-8'))
    shop_path=ASSETS/'Data/Script/origin/common_shop.lua'
    shop_text=shop_path.read_text(encoding='utf-8-sig')
    shop_path.write_text(''.join(line for line in shop_text.splitlines(keepends=True) if 'Index = "apricorn_' not in line),encoding='utf-8',newline='\n')
    xml=ET.fromstring(original('Data/StartParams.xml'))
    start=xml.find('StartChars');start.clear()
    for line in manifest['roster']['lines']:
        char=ET.SubElement(start,'StartChar')
        for key,value in {'Species':line['choice'],'Form':'0','Skin':'normal','Gender':'Genderless','Name':''}.items():
            ET.SubElement(char,key).text=value
    xml.find('MaxLevel').text='99'
    ET.indent(xml)
    (ASSETS/'Data/StartParams.xml').write_text(ET.tostring(xml,encoding='unicode')+'\n',encoding='utf-8',newline='\n')
    print(f"Generated {len(source)} monsters, {len(adaptations)} skills, {len(babies)} Tropical Path encounter species")


if __name__=='__main__':main()
