"""Regression checks for requested EXP pacing and Apricorn-only loot removal."""
import json
from pathlib import Path
import random
import unittest
from Scripts.digimon_progression_tuning import award, growth_table, STAGE_MULTIPLIERS, remove_apricorns
ROOT=Path(__file__).resolve().parents[1]
ASSETS=ROOT/'DumpAsset'


def simulate(start,stage,seed):
    growth=json.loads((ASSETS/f"Data/GrowthGroup/digi_{stage.lower().replace('-','_')}.json").read_text(encoding='utf-8'))['Object']['EXPTable']
    rng=random.Random(seed);level=start;xp=0
    # Four regular floors, four ordinary defeats per floor, then the guardian.
    # The fifth floor is the existing secret reward room.
    for i in range(17):
        memory=3 if i==16 or rng.randrange(12)>=4 else 2
        enemy=8 if i==16 else rng.randrange(2,5)
        xp+=award(memory*24,enemy,level)
        while level<99 and xp>=growth[level]-growth[level-1]:
            xp-=growth[level]-growth[level-1];level+=1
    return level,xp


class ProgressionTuningTests(unittest.TestCase):
    def test_formula_and_overlevel_penalty(self):
        self.assertEqual(award(72,8,8),122)
        self.assertEqual(award(72,8,13),122)
        self.assertEqual(award(72,8,14),61)
        self.assertEqual(award(72,8,15),30)
        self.assertEqual(award(72,8,23),0)

    def test_stage_growth_tables_and_installed_species(self):
        base=json.loads((ASSETS/'Data/GrowthGroup/medium_fast.json').read_text(encoding='utf-8-sig'))['Object']['EXPTable']
        for stage in STAGE_MULTIPLIERS:
            path=ASSETS/f"Data/GrowthGroup/digi_{stage.lower().replace('-','_')}.json"
            self.assertEqual(json.loads(path.read_text(encoding='utf-8-sig'))['Object']['EXPTable'],growth_table(base,stage))
        manifest=json.loads((ROOT/'DataAsset/Digimon/phase1_manifest.json').read_text(encoding='utf-8-sig'))
        for mon in manifest['digimon']:
            native=json.loads((ASSETS/f"Data/Monster/{mon['id']}.json").read_text(encoding='utf-8-sig'))['Object']
            self.assertEqual(native['EXPTable'],'digi_'+mon['stage'].lower().replace('-','_'))
            self.assertEqual(native['Forms'][0]['ExpYield'],int(mon['source']['Memory'])*24)

    def test_all_341_digimon_share_one_experience_scale(self):
        expected=json.loads((ASSETS/'Data/GrowthGroup/digi_rookie.json').read_text(encoding='utf-8-sig'))['Object']['EXPTable']
        count=0
        for path in (ASSETS/'Data/Monster').glob('*.json'):
            mon=json.loads(path.read_text(encoding='utf-8-sig'))['Object']
            if 'DigimonFormData' not in mon['Forms'][0].get('$type',''): continue
            count+=1
            curve=json.loads((ASSETS/f"Data/GrowthGroup/{mon['EXPTable']}.json").read_text(encoding='utf-8-sig'))['Object']['EXPTable']
            self.assertEqual(curve,expected,path.stem)
        self.assertEqual(count,341)

    def test_intro_pacing_and_high_level_farming(self):
        levels=[simulate(5,'Rookie',seed)[0] for seed in range(200)]
        self.assertGreaterEqual(sum(levels)/len(levels),8.8)
        self.assertLessEqual(sum(levels)/len(levels),9.8)
        for stage in STAGE_MULTIPLIERS:
            self.assertEqual(simulate(20,stage,42)[0],20)
            self.assertEqual(simulate(30,stage,42),(30,0))

    def test_no_apricorns_remain_in_dungeon_tables_or_shop_stock(self):
        for path in (ASSETS/'Data/Zone').glob('*.json'):
            self.assertNotIn('apricorn_',path.read_text(encoding='utf-8-sig'),str(path))
        self.assertNotIn('apricorn_', (ASSETS/'Data/Script/origin/common_shop.lua').read_text(encoding='utf-8'))

    def test_apricorn_filter_preserves_unrelated_entries_and_rooms(self):
        source={'Floors':[{'Rooms':[1,2], 'Items':[{'Spawn':{'ID':'apricorn_blue'},'Rate':5},
                {'Spawn':{'ID':'berry_oran'},'Rate':10}],
                'ToSpawn':[{'ToSpawn':{'ID':'box','HiddenValue':'apricorn_big'}}]}]}
        result=remove_apricorns(source)
        self.assertEqual(result,{'Floors':[{'Rooms':[1,2],'Items':[{'Spawn':{'ID':'berry_oran'},'Rate':10}],'ToSpawn':[]}]})
        self.assertEqual(remove_apricorns(result),result)


if __name__=='__main__': unittest.main()
