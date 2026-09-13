"""Validate playable passives against immutable species data and actual native events."""
import json
from pathlib import Path
import sys
import unittest
ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'Scripts'))
from digimon_passive_abilities import intrinsic
from digimon_runtime_assets import ELEMENTS

def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
def serialize(obj):return json.dumps(obj,sort_keys=True)

class PassiveCatalogTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.rows=read(ROOT/'DataAsset/Digimon/passive_abilities.json')['abilities']
        cls.source={e['id']:e for e in read(ROOT/'DataAsset/Monster/digimon_manifest.json')['digimon']}
        cls.families={e['id']:e for e in read(ROOT/'DataAsset/Digimon/digimon_families.json')['families']}

    def test_complete_unique_native_effects_and_unchanged_attributes(self):
        self.assertEqual(len(self.rows),341)
        self.assertEqual({r['species'] for r in self.rows},set(self.source))
        self.assertEqual(set(self.families),set(self.source))
        self.assertEqual(len({r['ability_id'] for r in self.rows}),341)
        signatures=set()
        for row in self.rows:
            for field in ('type','attribute','stage'):
                self.assertEqual(row[field],self.source[row['species']][field],(row['species'],field))
            actual=read(ROOT/f"DumpAsset/Data/Intrinsic/{row['ability_id']}.json")
            self.assertEqual(actual,intrinsic(row))
            obj=actual['Object']
            signature={k:v for k,v in obj.items() if isinstance(v,list) or k=='ProximityEvent'}
            signatures.add(serialize(signature))
            monster=read(ROOT/f"DumpAsset/Data/Monster/{row['species']}.json")['Object']
            for form in monster['Forms']:
                self.assertEqual(form['Intrinsic1'],row['ability_id'])
                self.assertEqual((form['Intrinsic2'],form['Intrinsic3']),('none','none'))
                self.assertEqual(form['Element1'],ELEMENTS[row['attribute']])
                self.assertEqual(form['DigimonAttribute'],row['type'])
                self.assertEqual(form['DigimonFamily'],self.families[row['species']]['family'])
            self.assertNotIn('Own ',row['description'])
        self.assertEqual(len(signatures),341,'Different names must not hide duplicate native effects')

    def test_anchor_modifiers_can_affect_every_listed_move(self):
        for row in self.rows:
            anchor=row['effects'][0]
            self.assertEqual((anchor['scope'],anchor['hook']),('self','OnActions'))
            event=anchor['event'];self.assertIn('SpecificSkillNeededEvent',event['$type'])
            self.assertTrue(event['AcceptedMoves'])
            learnset=read(ROOT/f"DumpAsset/Data/Monster/{row['species']}.json")['Object']['Forms'][0]['LevelSkills']
            for sid in event['AcceptedMoves']:
                self.assertIn(sid,{s['Skill'] for s in learnset})
                skill=read(ROOT/f'DumpAsset/Data/Skill/{sid}.json')['Object']
                self.assertTrue(skill['Released'])
                self.assertIn(skill['Name']['DefaultText'],row['description'])
                leaf=event['BaseEvent']
                self.assertGreater(leaf['Numerator'],leaf['Denominator'])
                if 'MultiplyDamageEvent' in leaf['$type']:
                    self.assertIn('DamageFormulaEvent',serialize(skill['Data']['OnHits']),(row['species'],sid))
                elif 'MultiplyAccuracyEvent' in leaf['$type']:
                    self.assertGreater(skill['Data']['HitRate'],0,(row['species'],sid))
                else:self.fail(leaf['$type'])

    def test_pp_restore_rewards_require_enemy_defeat_and_direct_damage(self):
        found=0
        for row in self.rows:
            for effect in row['effects']:
                if effect['hook']!='AfterHittings':continue
                found+=1
                target=effect['event']
                self.assertIn('TargetNeededEvent',target['$type'])
                self.assertEqual(target['Target'],4)
                dead=target['BaseEvents'][0]
                self.assertIn('TargetDeadNeededEvent',dead['$type'])
                hit=dead['BaseEvents'][0]
                self.assertIn('OnHitEvent',hit['$type'])
                self.assertTrue(hit['RequireDamage'])
                self.assertEqual(hit['Chance'],100)
                restore=hit['BaseEvents'][0]
                self.assertIn('BattlelessEvent',restore['$type'])
                self.assertFalse(restore['AffectTarget'])
                self.assertIn('DeepBreathEvent',restore['BaseEvent']['$type'])
                self.assertTrue(restore['BaseEvent']['RestoreAll'])
        self.assertEqual(found,6)
