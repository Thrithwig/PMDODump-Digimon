"""Apply explicit Cyber Sleuth item equivalents; inventory every unmatched item.

Runtime IDs stay stable so existing drops, shops and saves reference the same item.
Unsupported effects remain untouched and are listed, never silently relabeled.
"""
import copy
import csv
import json
from pathlib import Path
from digimon_runtime_assets import original, write

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'DataAsset/Digimon'
ITEMS=ROOT/'DumpAsset/Data/Item'
MAPPING={
 'seed_reviver':('Full Revival Spray','revival'),
 'held_power_band':('ATK Attach E','attachment'),
 'held_defense_scarf':('DEF Attach E','attachment'),
 'held_special_band':('INT Attach E','attachment'),
 'held_zinc_band':('INT Attach E','attachment'),
 'held_scope_lens':('CRT Attach C','attachment'),
 'held_wide_lens':('HIT Attach C','attachment'),
 'berry_oran':('HP Capsule A','heal'),
 'berry_leppa':('SP Capsule A','pp'),
 'berry_lum':('Multi-Recovery','cure'),
 'medicine_potion':('HP Spray C','heal'),
 'medicine_max_potion':('HP Spray A','heal'),
 'medicine_elixir':('SP Spray B','pp'),
 'medicine_max_elixir':('SP Spray A','pp'),
 'medicine_full_heal':('Multi-Recovery DX','cure'),
 'medicine_x_attack':('ATK Boost','buff'),
 'medicine_x_defense':('DEF Boost','buff'),
 'medicine_x_sp_atk':('INT Boost','buff'),
 'medicine_x_speed':('SPD Boost','buff'),
 'medicine_x_accuracy':('HIT Boost','buff'),
 'medicine_dire_hit':('CRT Boost','buff'),
 'orb_all_dodge':('AGL Boost','buff'),
 'orb_escape':('Export','escape'),
 'boost_hp_up':('Vigor Mushroom','training'),
 'boost_protein':('Power Pine','training'),
 'boost_iron':('Aegis Apple','training'),
 'boost_calcium':('Clever Carrot','training'),
 'boost_zinc':('Clever Carrot','training'),
 'boost_carbos':('Boost Banana','training'),
 'held_flame_plate':('Flare Guard DX','guard'),
 'held_splash_plate':('Aqua Guard DX','guard'),
 'held_meadow_plate':('Plant Guard DX','guard'),
 'held_zap_plate':('Electric Guard DX','guard'),
 'held_earth_plate':('Sand Guard DX','guard'),
 'held_sky_plate':('Wind Guard DX','guard'),
 'held_pixie_plate':('Shine Guard DX','guard'),
 'held_dread_plate':('Dark Guard DX','guard'),
 'held_blank_plate':('Noise Guard DX','guard'),
 'loot_pearl':('Pearl','treasure'),
 'loot_nugget':('Topaz','treasure'),
 'loot_star_piece':('Ruby','treasure'),
 'loot_comet_shard':('Diamond','treasure'),
 'evo_fire_stone':('Human Spirit of Flame','unlock'),
 'evo_thunder_stone':('Human Spirit of Light','unlock'),
 'evo_dusk_stone':('Beast Spirit of Flame','unlock'),
 'evo_dawn_stone':('Beast Spirit of Light','unlock'),
 'evo_sun_stone':('Digi-Egg of Courage','unlock'),
 'evo_shiny_stone':('Digi-Egg of Miracles','unlock'),
 'evo_moon_stone':('Digi-Egg of Destiny','unlock'),
}

def run():
    reference={}
    for line in (DATA/'Source/Cyber Sleuth items.txt').read_text(encoding='utf-8-sig').splitlines():
        cells=line.split('\t')
        if len(cells)==3 and cells[0]!='Item Name': reference[cells[0]]=cells[2]
    rows=[]; unmatched=[]
    for path in sorted(ITEMS.glob('*.json')):
        sid=path.stem
        baseline=original('Data/Item/'+path.name,raw=True) if sid in MAPPING else path.read_bytes()
        value=json.loads(baseline.decode('utf-8-sig'))
        obj=value['Object'];name=obj['Name']['DefaultText'];desc=obj['Desc']['DefaultText']
        if sid not in MAPPING:
            prefix=sid.split('_')[0]
            reason={
                'xcl':'Species-exclusive Pokemon equipment; no corresponding Digimon-specific item in the reference.',
                'tm':'Move-teaching disc; Cyber Sleuth reference has no skill-disc consumable equivalent.',
                'apricorn':'Recruitment item removed from loot and shops; acquisition uses scan restoration.',
                'food':'Belly/hunger mechanic has no equivalent in the Cyber Sleuth item reference.',
                'gummi':'Random type-favored growth and belly effects do not match a specific training food.',
                'evo':'Pokemon evolution or held effect has no matching remaining Cyber Sleuth unlock.',
                'wand':'Projectile dungeon effect has no matching Cyber Sleuth consumable.',
                'ammo':'Thrown ammunition has no matching Cyber Sleuth item.',
                'box':'Dungeon container mechanic has no matching Cyber Sleuth item.'
            }.get(prefix,'No equivalent with the same effect in the supplied Cyber Sleuth item reference.')
            candidates={'seed_joy':'Brave Point E','seed_golden':'Brave Point A','seed_reviver':'Revival Capsule DX',
                'held_power_band':'ATK Attach','held_special_band':'INT Attach','held_defense_scarf':'DEF Attach',
                'held_zinc_band':'INT Attach','held_scope_lens':'CRT Attach','held_wide_lens':'HIT Attach'}
            if sid in candidates: reason='Related item exists, but native '+('automatic revival' if sid=='seed_reviver' else 'level or percentage/stage modification')+' differs from its fixed-value/manual Cyber Sleuth effect; conversion deferred.'
            unmatched.append({'item_id':sid,'original_name':name,'released':obj['Released'],'category':prefix,
                              'candidate':candidates.get(sid,''),'reason':reason,'original_description':desc})
            continue
        target,kind=MAPPING[sid]
        if kind!='unlock' or not target.endswith(('Flame','Light')): assert target in reference,target
        runtime=desc.replace('Pokémon','Digimon').replace('Pokemon','Digimon')
        notes='Dungeon adaptation: existing effect amounts and targeting retained.'
        if kind=='unlock':
            obj['OnActions']=[]
            runtime='Unlocks compatible digivolutions at the Base Camp terminal while in the bag or equipped. Not consumed.'
            notes='Reuses an existing evolution-item drop ID; removes its Pokemon held attack modifier.'
        elif kind=='revival':
            obj['OnDeaths']=[]
            obj['ItemStates']=[]
            obj['UseEvent']['OnHits']=[{'Key':{'str':[0]},'Value':{'$type':'PMDC.Dungeon.ReviveAllEvent, PMDC'}}]
            runtime='Manually revives all fallen teammates with full HP. Does not activate automatically on defeat.'
            notes='Uses native party revival; replaces the automatic Reviver Seed effect.'
        elif kind=='attachment':
            notes='Closest stat-equipment role; native percentage or critical-stage effect retained instead of source fixed stat points.'
        elif kind=='guard':
            for event in obj['BeforeBeingHits']:
                v=event['Value']
                if 'MultiplyElementEvent' in v['$type']:v['Numerator']=4;v['Denominator']=5
            runtime=reference[target]
            notes='Source 20% reduction applied to the corresponding dungeon element.'
        elif kind=='treasure':
            runtime='Valuable data that can be sold for Bits.';notes='Sale-only equivalent; existing price retained.'
        elif kind=='cure':
            runtime='Cures dungeon status problems.'+(' Affects teammates within 5 tiles.' if sid.startswith('medicine') else '')
            notes='Cures engine bad statuses; source additional 100 HP healing is not applied.'
        elif kind=='pp':
            runtime=('Fully restores move PP.' if target.endswith('A') else 'Restores 10 PP to each move.')+(' Affects nearby teammates.' if sid.startswith('medicine') else '')
            notes='Move PP is the dungeon analogue of SP; source SP is used only for evolution requirements.'
        elif kind=='training':
            stat={'boost_hp_up':'maximum HP','boost_protein':'Attack','boost_iron':'Defense','boost_calcium':'Special Attack','boost_zinc':'Special Defense','boost_carbos':'Speed'}[sid]
            runtime='Permanently increases '+stat+' by 4, up to the engine training cap.'
            notes='Training food usable in dungeons before the farm minigame; INT is split across Special Attack and Special Defense.'
        if kind in ('heal','pp','cure','training'):
            obj['UseEvent']['OnHits']=[e for e in obj['UseEvent']['OnHits'] if 'RestoreBellyEvent' not in e['Value']['$type']]
            obj['ItemStates']=[x for x in obj['ItemStates'] if 'BerryState' not in x['$type']]
        obj['Name']={'DefaultText':target,'LocalTexts':{}}
        obj['Desc']={'DefaultText':runtime,'LocalTexts':{}}
        obj['Comment']='Cyber Sleuth equivalent. '+notes
        # Preserve upstream JSON formatting so the diff shows the actual conversion.
        text=json.dumps(value,ensure_ascii=False,indent='')+'\n'
        if b'\r\n' in baseline: text=text.replace('\n','\r\n')
        path.write_bytes((b'\xef\xbb\xbf' if baseline.startswith(b'\xef\xbb\xbf') else b'')+text.encode('utf-8'))
        rows.append({'item_id':sid,'original_name':name,'cyber_sleuth_item':target,'source_description':reference.get(target,'Evolution requirement CSV'),
                     'runtime_description':runtime,'adaptation':notes})
    write(DATA/'item_mapping.json',rows)
    # Machine-readable pipeline result, also used by the user-facing CSV exporter.
    write(DATA/'unmatched_items.json',unmatched)
    with (DATA/'unmatched_items.csv').open('w',encoding='utf-8-sig',newline='') as stream:
        writer=csv.DictWriter(stream,fieldnames=list(unmatched[0]));writer.writeheader();writer.writerows(unmatched)
    print(f'{len(rows)} item equivalents; {len(unmatched)} unmatched items; {len(rows)+len(unmatched)} total.')

if __name__=='__main__':run()
