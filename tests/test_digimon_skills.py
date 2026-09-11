import json
import sys
import unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Scripts'))
from digimon_attachment_skills import common_skills
from digimon_skill_presentation import profile

def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))

class SkillTests(unittest.TestCase):
    def test_common_tms_are_consumable_and_teachable_by_all_forms(self):
        manifest=read(ROOT/'DataAsset/Digimon/phase2_manifest.json')
        common=common_skills(manifest)
        self.assertEqual(len(common),138)
        expected={'digi_'+s['id'] for s in common}
        for s in common:
            obj=read(ROOT/f"DumpAsset/Data/Item/digi_tm_{s['id']}.json")['Object']
            self.assertEqual(obj['MaxStack'],1)
            self.assertEqual(obj['UsageType'],6)
            self.assertTrue(obj['Released'])
            self.assertEqual(obj['GroundUseActions'][0]['Skill'],'digi_'+s['id'])
            self.assertEqual(obj['ItemStates'][0]['ID'],'digi_'+s['id'])
        for s in manifest['digimon']:
            form=read(ROOT/f"DumpAsset/Data/Monster/{s['id']}.json")['Object']['Forms'][0]
            self.assertEqual({row['Skill'] for row in form['TeachSkills']},expected)
        signatures={s['id'] for s in manifest['skills']} - {s['id'] for s in common}
        self.assertTrue(all(not (ROOT/f'DumpAsset/Data/Item/digi_tm_{s}.json').exists() for s in signatures))

    def test_attack_shapes_ranges_and_friendly_fire_match_descriptions(self):
        manifest=read(ROOT/'DataAsset/Digimon/phase2_manifest.json')
        classes={'melee':'AttackAction','dash':'DashAction','burst':'AreaAction','projectile':'ProjectileAction'}
        masks=set();templates=set()
        for s in manifest['skills']:
            p=profile(s)
            if p is None: continue
            template,shape,distance,mask=p
            obj=read(ROOT/f"DumpAsset/Data/Skill/digi_{s['id']}.json")['Object']
            action=obj['HitboxAction']
            self.assertIn(classes[shape]+',',action['$type'],s['id'])
            self.assertEqual(action['TargetAlignments'],mask)
            if shape!='melee': self.assertEqual(action['Range'],distance)
            if shape in ('dash','projectile'):
                self.assertTrue(action['StopAtHit'])
                self.assertTrue(action['StopAtWall'])
            masks.add(mask);templates.add(template)
        self.assertEqual(masks,{4,6})
        self.assertGreater(len(templates),20)
        self.assertNotIn('water_gun',templates)

    def test_nifty_chests_contain_complete_common_pool(self):
        expected={r['item'] for r in read(ROOT/'DataAsset/Digimon/attachment_skills.json')['skills']}
        found=[]
        def visit(x):
            if isinstance(x,dict):
                if x.get('BoxID')=='box_nifty':
                    pool=x['BaseSpawner']['Picker']['Spawner']['$values']
                    self.assertEqual({r['Spawn']['Value'] for r in pool},expected)
                    found.append(True)
                for v in x.values():visit(v)
            elif isinstance(x,list):
                for v in x:visit(v)
        for path in (ROOT/'DumpAsset/Data/Zone').glob('*.json'):visit(read(path))
        self.assertEqual(len(found),13)
