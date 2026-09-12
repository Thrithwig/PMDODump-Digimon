import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Scripts'))
from digimon_starter_skills import assignment, learnset, skill_id, STAGES, eligible
from digimon_runtime_assets import read, lua, ELEMENTS

class StarterTests(unittest.TestCase):
    def test_every_low_stage_has_reliable_first_elemental_attack(self):
        manifest=read(ROOT/'DataAsset/Digimon/phase2_manifest.json')
        catalog=(ROOT/'DumpAsset/Data/Script/origin/digimon/runtime_catalog.lua').read_text(encoding='utf-8-sig')
        count=0
        for entry in manifest['digimon']:
            if not eligible(entry): continue
            count+=1
            element, category=assignment(entry)
            expected=skill_id(element,category)
            form=read(ROOT/f"DumpAsset/Data/Monster/{entry['id']}.json")['Object']['Forms'][0]
            rows=form['LevelSkills']
            self.assertEqual(rows[0],{'Level':1,'Skill':expected},entry['id'])
            self.assertEqual(rows[1:],[{'Level':int(s['level'] or 1),'Skill':'digi_'+s['skill']} for s in entry['skills']])
            self.assertIn(lua(rows),catalog)
            obj=read(ROOT/f'DumpAsset/Data/Skill/{expected}.json')['Object']
            self.assertEqual(obj['BaseCharges'],20)
            self.assertEqual(obj['Data']['Element'],ELEMENTS[element])
            self.assertEqual(obj['Data']['Category'],1 if category=='Physical' else 2)
            self.assertEqual(obj['Data']['SkillStates'][0]['Power'],20)
            self.assertEqual(obj['Data']['HitRate'],100)
            # Native RollLatestSkills scans backwards and keeps the four latest.
            for level in range(1,10):
                selected=[]
                for row in reversed(rows):
                    if row['Level']<=level and row['Skill'] not in selected and len(selected)<4:
                        selected.insert(0,row['Skill'])
                self.assertIn(expected,selected,(entry['id'],level))
            self.assertEqual(learnset(entry,rows),rows)
        self.assertGreaterEqual(count,67)

    def test_tie_uses_special_and_stronger_attack_uses_physical(self):
        e={'attribute':'Fire','stats_by_level':{'1':{'atk':'20','int':'20'}}}
        self.assertEqual(assignment(e),('Fire','Magic'))
        e['stats_by_level']['1']['atk']='21'
        self.assertEqual(assignment(e),('Fire','Physical'))

    def test_runtime_regeneration_applies_starters_before_passives(self):
        from unittest.mock import patch
        import digimon_runtime_assets as runtime
        import digimon_starter_skills as starters
        generated={}
        def record(path, obj):
            generated[str(path)] = obj
        def passives():
            # The passive overlay must run after every form has been generated.
            monsters=[v for k,v in generated.items() if '/Monster/' in k.replace(chr(92),'/')]
            self.assertEqual(len(monsters),341)
        with patch.object(sys,'argv',['digimon_runtime_assets.py','--phase2']), \
             patch.object(runtime,'write',side_effect=record), \
             patch.object(starters,'write',side_effect=record), \
             patch.object(runtime.shutil,'copyfile'), \
             patch.object(Path,'write_text'), \
             patch('digimon_passive_abilities.apply',side_effect=passives) as apply_passives:
            runtime.main()
        apply_passives.assert_called_once()
        manifest=read(ROOT/'DataAsset/Digimon/phase2_manifest.json')
        for entry in manifest['digimon']:
            if not eligible(entry): continue
            obj=generated[str(ROOT/f"DumpAsset/Data/Monster/{entry['id']}.json")]
            self.assertEqual(obj['Object']['Forms'][0]['LevelSkills'][0],
                             {'Level':1,'Skill':skill_id(*assignment(entry))})
