"""Full-roster contract. Original CSV normalization and Phase 1 remain immutable."""
import copy
import json
from pathlib import Path
from digimon_balance import build_catalog, compile_conditions

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'DataAsset/Digimon'

def write(name, value):
    (DATA/name).write_text(json.dumps(value, ensure_ascii=False, indent=2)+'\n', encoding='utf-8')

def main():
    original=json.loads((ROOT/'DataAsset/Monster/digimon_manifest.json').read_text())
    manifest=copy.deepcopy(original)
    manifest['roster']=json.loads((DATA/'phase1_manifest.json').read_text())['roster']
    overlay=json.loads((DATA/'phase1_overlay.json').read_text())
    overlay['progression']['training']['maximum']=200
    # Variant assignments are explicit adaptations: dataset names do not disambiguate
    # their learners. Keep every source variant and record each selected assignment.
    assignments=[]; skills=[]
    for skill in manifest['skills']:
        if len(skill['variants'])==1:
            skills.append(skill); continue
        for species in manifest['digimon']:
            for learned in species['skills']:
                if learned['skill']!=skill['id']: continue
                variants=skill['variants']; sid=species['id']; key=skill['id']
                nx=sid.endswith('_nx')
                if key=='celestial_blade':
                    chosen=next(v for v in variants if v['source']['Attribute']==('Electric' if sid=='ravemon' else 'Light'))
                elif key=='supreme_cannon':
                    chosen=next(v for v in variants if (v['source']['Power']=='0')==(sid=='omnimon_zwart'))
                elif key=='transcendent_sword':
                    chosen=next(v for v in variants if (v['source']['Power']=='130')==(sid=='omnimon_zwart'))
                elif key in ('blade_of_the_dragon_king','lightning_joust','shield_of_the_just','soul_digitalization'):
                    chosen=sorted(variants,key=lambda v:int(v['source']['Power']))[0 if nx else -1]
                elif key in ('fist_of_athena','spiral_masquerade'):
                    chosen=sorted(variants,key=lambda v:len(v['source']['Description']))[0 if nx else -1]
                else: chosen=variants[0] # synonymous Black Aura Blast rows
                new_id=key+'__'+sid
                skills.append({'id':new_id,'name':skill['name'],'variants':[chosen]})
                learned['skill']=new_id
                assignments.append({'species':sid,'skill':key,'runtime_skill':new_id,'variant':chosen['id'],
                    'policy':'Explicit learner adaptation; source CSV lacks variant-to-learner association.'})
    manifest['skills']=skills; manifest['issues']=[]
    entries={x['id']:x for x in manifest['digimon']}
    gates={}; removed=[]; modes=set()
    for entry in manifest['digimon']:
        req=entry['requirements'][0]; extra=req.get('Extra Condition','')
        if extra.startswith('Item: '):
            name=extra[6:]; item={'Human Spirit of Flame':'evo_fire_stone','Human Spirit of Light':'evo_thunder_stone','Beast Spirit of Flame':'evo_dusk_stone','Beast Spirit of Light':'evo_dawn_stone','Digi-Egg of Courage':'evo_sun_stone','Digi-Egg of Miracles':'evo_shiny_stone','Digi-Egg of Destiny':'evo_moon_stone'}[name]
            gates[entry['id']]=[{'kind':'item','item':item,'name':name,'minimum':1}]
        elif extra.startswith('Digimon: '):
            gates[entry['id']]=[{'kind':'party','species':p,'minimum':int(req['Level'])} for p in entry['digivolves_from']]
        elif extra=='Mode Change': modes.add(entry['id'])
        elif extra.startswith('Cleared '): removed.append({'species':entry['id'],'condition':extra})
        elif extra not in ('','Starter digimon','Cannot digivolve','Mode Change'):
            raise ValueError('Unrecognized condition: '+extra)
        req.pop('Extra Condition',None)
    # Compile each form's curve through the unchanged, strict Phase 1 compiler.
    # Edge reachability is checked separately including earned training bonuses.
    disconnected=copy.deepcopy(manifest)
    for e in disconnected['digimon']: e['digivolves_to']=[];e['digivolves_from']=[]
    gameplay=build_catalog(disconnected,overlay)
    transitions={}
    for e in manifest['digimon']:
        for target in e['digivolves_to']:
            requirements=compile_conditions(entries[target],overlay)+gates.get(target,[])
            for a,b,d,req in ((e['id'],target,'digivolve',requirements),(target,e['id'],'dedigivolve',[])):
                if target in modes: d='mode_change'
                identity=a+'__to__'+b
                edge={'id':identity,'from':a,'to':b,'direction':d,'requirements':copy.deepcopy(req),
                      **copy.deepcopy(overlay['progression']['transitions'])}
                edge['preserve_level']=False
                edge['reset_level']=1
                # Explicit source forward direction wins over an inferred reverse.
                if identity not in transitions or d=='digivolve': transitions[identity]=edge
    gameplay['transitions']=sorted(transitions.values(),key=lambda e:e['id'])
    gameplay['status']='runtime_enabled';gameplay['source_forward_edges']=sum(len(e['digivolves_to']) for e in manifest['digimon'])
    write('phase2_manifest.json',manifest);write('phase2_gameplay.json',gameplay)
    write('phase2_decisions.json',{'removed_story_gates':removed,'skill_assignments':assignments,
        'restoration_only':[e['id'] for e in manifest['digimon'] if e['id'].endswith('_nx')],
        'item_gates':gates,'fusion_policy':'Both listed partners must be in the active party at the source required level. Partner remains in the party; no duplication or item substitute.',
        'growth_policy':{'Armor':'Champion (1x)','Ultra':'Mega (0.5x)','None':'Rookie for Shoutmon; Mega for OmniShoutmon'}})
    print(len(manifest['digimon']), 'species;',len(transitions),'directed transitions')

if __name__=='__main__': main()
