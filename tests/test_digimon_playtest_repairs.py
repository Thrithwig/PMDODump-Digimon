import sys
import unittest
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Scripts'))
from digimon_runtime_assets import ASSETS, DATA, native_skill, read
from digimon_move_balance import values

class PlaytestRepairTests(unittest.TestCase):
    def test_single_global_mission_spawner(self):
        steps = read(ASSETS / 'Data/Universal.json')['Object']['ZoneSteps']
        self.assertEqual(sum(s.get('Script') == 'SpawnMissionNpcFromSV' for s in steps), 1)
        for path in (ASSETS / 'Data/Zone').glob('*.json'):
            for segment in read(path)['Object']['Segments']:
                self.assertFalse(any(s.get('Script') == 'SpawnMissionNpcFromSV'
                                     for s in segment.get('ZoneSteps', [])), path.stem)

    def test_installed_attacks_and_generator_respect_starter_baseline(self):
        for index, entry in enumerate(read(DATA / 'phase2_manifest.json')['skills']):
            if entry['variants'][0]['source']['Type'] == 'Support':
                continue
            generated, _ = native_skill(entry, index)
            installed = read(ASSETS / 'Data/Skill' / ('digi_' + entry['id'] + '.json'))
            for record in (installed, generated):
                obj = record['Object']
                power = next(s['Power'] for s in obj['Data']['SkillStates'] if 'BasePowerState' in s['$type'])
                self.assertGreaterEqual(power, 20, entry['id'])
                tier = values(entry)['tier']
                self.assertTrue(20 + 20 * tier <= power <= 39 + 20 * tier, entry['id'])
                self.assertTrue(20 + 10 * tier <= obj['BaseCharges'] <= 29 + 10 * tier, entry['id'])
                self.assertIn(obj['Data']['HitRate'], (-1, 100), entry['id'])
                for event in obj['Data']['OnHits']:
                    if 'SpecificDamageEvent' in event['Value'].get('$type', ''):
                        self.assertGreaterEqual(event['Value']['Damage'], 20, entry['id'])

    def test_stage_exclusive_attacks_strictly_improve_damage_and_pp(self):
        groups = {tier: [] for tier in range(4)}
        for entry in read(DATA / 'phase2_manifest.json')['skills']:
            balance = values(entry)
            if balance['power'] is not None and not balance['shared_exception']:
                obj = read(ASSETS / 'Data/Skill' / ('digi_' + entry['id'] + '.json'))['Object']
                power = next(s['Power'] for s in obj['Data']['SkillStates'] if 'BasePowerState' in s['$type'])
                groups[balance['tier']].append((power, obj['BaseCharges']))
        for tier in range(1, 4):
            for field in (0, 1):
                self.assertGreater(min(s[field] for s in groups[tier]), max(s[field] for s in groups[tier - 1]))
