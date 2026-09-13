"""Family-exclusive items: coverage, eligibility data, drops and swap recipes."""
import collections
import copy
import json
import re
import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Scripts'))
from digimon_runtime_assets import family_assignments, read  # noqa: E402
from digimon_family_items import (SECRET_ROOM_ZONES, encounter_species, item_id,
                                 restore_secret_room_boxes, secret_room_boxes, validate)  # noqa: E402


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
            self.assertTrue(obj['BagEffect'], iid)
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

    def test_secret_rooms_restore_family_treasure_boxes(self):
        rarity_map = read(ROOT / 'DumpAsset/Data/Misc/Rarity.json')['Object']['RarityMap']
        for zone_id in SECRET_ROOM_ZONES:
            zone = read(ROOT / 'DumpAsset/Data/Zone' / f'{zone_id}.json')
            boxes = secret_room_boxes(zone)
            self.assertEqual([(box['Spawn']['BoxID'], box['Rate']) for box in boxes],
                             [('box_light', 3), ('box_heavy', 1)], zone_id)
            for box, rarity in zip(boxes, (1, 2)):
                spawner = box['Spawn']['BaseSpawner']
                self.assertIn('SpeciesItemListSpawner', spawner['$type'])
                self.assertEqual(spawner['Rarity'], {'Min': rarity, 'Max': rarity + 1})
                self.assertEqual(spawner['Species'], sorted(encounter_species(zone['Object'])))
                self.assertTrue(spawner['Species'], zone_id)
                # This is the native spawner's complete pool, independent of an
                # empty fixed room's respawn table. Neither tier may fall back.
                for species in spawner['Species']:
                    ids = rarity_map[species][str(rarity)]
                    self.assertTrue(ids, (zone_id, species, rarity))
                    for iid in ids:
                        obj = read(ROOT / 'DumpAsset/Data/Item' / f'{iid}.json')['Object']
                        self.assertTrue(obj['Released'], iid)
                        self.assertTrue(iid.startswith('digixcl_'), iid)
                        self.assertEqual(obj['Rarity'], rarity, iid)

    def test_secret_room_repair_is_idempotent_and_preserves_dungeon(self):
        rarity_map = read(ROOT / 'DumpAsset/Data/Misc/Rarity.json')['Object']['RarityMap']
        for zone_id in SECRET_ROOM_ZONES:
            zone = read(ROOT / 'DumpAsset/Data/Zone' / f'{zone_id}.json')
            expected = copy.deepcopy(zone)
            self.assertFalse(restore_secret_room_boxes(zone, rarity_map), zone_id)
            # Reproduce the broken prior pair: IDs alone must not skip repair.
            for choice in secret_room_boxes(zone):
                spawner = choice['Spawn']['BaseSpawner']
                spawner['$type'] = spawner['$type'].replace('SpeciesItemListSpawner', 'SpeciesItemContextSpawner')
                spawner.pop('Species')
                choice['Rate'] = 99
            self.assertTrue(restore_secret_room_boxes(zone, rarity_map), zone_id)
            self.assertEqual(zone, expected, zone_id)
            self.assertFalse(restore_secret_room_boxes(zone, rarity_map), zone_id)

    def test_secret_room_missing_family_pool_fails_without_mutation(self):
        zone = read(ROOT / 'DumpAsset/Data/Zone/ambush_forest.json')
        before = copy.deepcopy(zone)
        with self.assertRaisesRegex(ValueError, 'missing Digimon family treasure pool'):
            restore_secret_room_boxes(zone, {})
        self.assertEqual(zone, before)

    def items_species(self):
        return {s for members in self.families.values() for s in members}

if __name__ == '__main__':
    unittest.main()
