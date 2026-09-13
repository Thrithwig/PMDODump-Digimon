"""Family-exclusive items: coverage, eligibility data, drops and swap recipes."""
import collections
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Scripts'))
from digimon_runtime_assets import family_assignments, read  # noqa: E402
from digimon_family_items import item_id, validate  # noqa: E402


def families():
    rows = read(ROOT / 'DataAsset/Digimon/digimon_family_types.json')['family_types']
    assignments, removed, _ = family_assignments(rows)
    out = collections.defaultdict(list)
    for species_id, types in assignments.items():
        for t in types:
            if t not in removed:
                out[t].append(species_id)
    return dict(out)


class FamilyItemTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.design = json.loads((ROOT / 'DataAsset/Digimon/family_items.json').read_text(encoding='utf-8'))
        cls.families = families()
        cls.items = {}
        for row in cls.design['families']:
            for index, item in enumerate(row['items'], 1):
                cls.items[item_id(row['family'], index)] = (row['family'], item)
        source = (ROOT / 'DataGenerator/Data/AutoItemInfo.cs').read_text(encoding='utf-8')
        enum = source[source.index('public enum ExclusiveItemEffect'):]
        cls.effects = set(re.findall(r'^\s*([A-Za-z]+),', enum[:enum.index('}')], re.M))

    def test_design_covers_every_family_with_all_three_tiers(self):
        self.assertEqual(validate(self.design, self.families, self.effects), [])
        self.assertEqual({row['family'] for row in self.design['families']}, set(self.families))

    def test_generated_items_carry_family_membership_and_rarity(self):
        for iid, (family, item) in self.items.items():
            path = ROOT / 'DumpAsset/Data/Item' / f'{iid}.json'
            self.assertTrue(path.exists(), iid)
            obj = read(path)['Object']
            self.assertTrue(obj['Released'], iid)
            self.assertEqual(obj['Name']['DefaultText'], item['name'])
            self.assertEqual(obj['Rarity'], item['tier'], iid)
            self.assertIn(f'A rare treasure for {family} Digimon.', obj['Desc']['DefaultText'])
            self.assertNotIn('Pok', obj['Desc']['DefaultText'], iid)
            states = obj['ItemStates']
            family_state = next(s for s in states if 'FamilyState' in s['$type'])
            self.assertEqual(sorted(family_state['Members']), sorted(self.families[family]), iid)
            self.assertTrue(any('ExclusiveState' in s['$type'] for s in states), iid)
            events = {k: v for k, v in obj.items() if isinstance(v, (list, dict)) and v and k not in ('ItemStates', 'Name', 'Desc', 'UseEvent')}
            self.assertTrue(events, f'{iid} has no effect events')

    def test_swap_recipes_exchange_lower_tiers_of_the_same_family(self):
        text = (ROOT / 'DumpAsset/Data/Script/origin/digimon/family_trades.lua').read_text(encoding='utf-8')
        trades = {m.group(1): re.findall(r'"([^"]+)"', m.group(2))
                  for m in re.finditer(r'Item="([^"]+)",\s*ReqItem=\{([^}]*)\}', text)}
        tops = {iid for iid, (_, item) in self.items.items() if item['tier'] == 3}
        self.assertEqual(set(trades), tops)
        for top, inputs in trades.items():
            family = self.items[top][0]
            self.assertEqual({self.items[i][0] for i in inputs}, {family}, top)
            self.assertEqual(sorted(self.items[i][1]['tier'] for i in inputs), [1, 2], top)
            for i in inputs:
                self.assertTrue((ROOT / 'DumpAsset/Data/Item' / f'{i}.json').exists(), i)
        catalog = (ROOT / 'DumpAsset/Data/Script/origin/ground/base_camp_2/init.lua').read_text(encoding='utf-8-sig')
        self.assertIn("origin.digimon.family_trades", catalog)

    def test_items_are_indexed_for_treasure_boxes(self):
        rarity_map = read(ROOT / 'DumpAsset/Data/Misc/Rarity.json')['Object']['RarityMap']
        for row in self.design['families']:
            family = row['family']
            expected = {(item['tier'], item_id(family, i)) for i, item in enumerate(row['items'], 1)}
            for species in self.families[family]:
                table = rarity_map.get(species, {})
                have = {(int(tier), iid) for tier, ids in table.items() for iid in ids if iid.startswith('digixcl_')}
                self.assertTrue(expected <= have, (family, species, expected - have))
        self.assertEqual(set(rarity_map), set(self.items_species()))

    def items_species(self):
        return {s for members in self.families.values() for s in members}

if __name__ == '__main__':
    unittest.main()
