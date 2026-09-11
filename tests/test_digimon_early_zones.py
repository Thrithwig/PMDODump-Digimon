import json
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]


class EarlyZoneTests(unittest.TestCase):
    def test_level_5_through_15_zones_are_released_and_populated(self):
        manifest = json.loads((ROOT / "DataAsset/Digimon/early_zone_manifest.json").read_text(encoding="utf-8"))
        self.assertEqual(14, len(manifest["zones"]))
        self.assertGreaterEqual(sum(row["digimon_encounter_records"] for row in manifest["zones"]), 2089)
        for row in manifest["zones"]:
            zone = json.loads((ROOT / "DumpAsset/Data/Zone" / f"{row['id']}.json").read_text(encoding="utf-8"))["Object"]
            self.assertTrue(zone["Released"], row["id"])
            self.assertTrue(5 <= zone["Level"] <= 15, row["id"])

    def test_camp_routes_match_progression(self):
        import re
        expected = {
            'base_camp': {'guildmaster_trail', 'tropical_path', 'faultline_ridge'},
            'forest_camp': {'faded_trail','bramble_woods','trickster_woods','overgrown_wilds','moonlit_courtyard','ambush_forest','tiny_tunnel','sickly_hollow','secret_garden'},
            'cliff_camp': {'fertile_valley','flyaway_cliffs','wayward_wetlands','geode_crevice'},
            'canyon_camp': {'copper_quarry','depleted_basin','forsaken_desert','relic_tower','sleeping_caldera'},
            'rest_stop': {'thunderstruck_pass','veiled_ridge','snowbound_path','treacherous_mountain','cave_of_whispers'},
            'final_stop': {'champions_road'},
        }
        for camp, ids in expected.items():
            text = (ROOT / f'DumpAsset/Data/Script/origin/ground/{camp}/init.lua').read_text(encoding='utf-8-sig')
            routes = set()
            for table in re.findall(r'dungeons\s*=\s*\{([^}]+)\}', text):
                routes.update(re.findall(r"'([^']+)'", table))
            self.assertEqual(routes, ids, camp)

    def test_repaired_enemy_tables_cover_every_floor(self):
        for name in ['cave_of_whispers','eon_island','labyrinth_of_the_lost','prism_isles','the_neverending_tale']:
            zone = json.loads((ROOT / f'DumpAsset/Data/Zone/{name}.json').read_text(encoding='utf-8-sig'))['Object']
            segment = zone['Segments'][0]
            enemies = next(s for s in segment['ZoneSteps'] if 'TeamSpawnZoneStep' in s['$type'])
            loot = next(s for s in segment['ZoneSteps'] if 'ItemSpawnZoneStep' in s['$type'])
            for floor in range(len(segment['Floors'])):
                self.assertTrue(any(r['Range']['Min'] <= floor < r['Range']['Max'] and r['Rate'] > 0 for r in enemies['Spawns']), (name, floor))
                self.assertTrue(any(any(r['Range']['Min'] <= floor < r['Range']['Max'] and r['Rate'] > 0 for r in cat['Spawns']) for cat in loot['Spawns'].values()), (name, floor))

    def test_released_zones_have_valid_steps_and_item_references(self):
        from Scripts.digimon_progression_tuning import remove_apricorns
        def walk(node):
            if isinstance(node, dict):
                yield node
                for value in node.values(): yield from walk(value)
            elif isinstance(node, list):
                for value in node: yield from walk(value)
        items = {p.stem: json.loads(p.read_text(encoding='utf-8-sig'))['Object'] for p in (ROOT/'DumpAsset/Data/Item').glob('*.json')}
        for path in (ROOT/'DumpAsset/Data/Zone').glob('*.json'):
            zone = json.loads(path.read_text(encoding='utf-8-sig'))['Object']
            if not zone.get('Released'): continue
            for node in walk(zone):
                for row in node.get('GenSteps', []):
                    self.assertIsNotNone(row['Value'], path.stem)
                if 'Cursed' in node and node.get('ID'):
                    self.assertIn(node['ID'], items, path.stem)
                    self.assertTrue(items[node['ID']]['Released'], (path.stem, node['ID']))
                    self.assertFalse(node['ID'].startswith('apricorn_'))
        step = {'Key': {'str': [6, 2]}, 'Value': {'Spawn': {'ID': 'apricorn_plain'}}}
        self.assertEqual(remove_apricorns([step]), [])
        from Scripts.digimon_unmatched_items import filter_drops
        placement = {'SuccessPercent': 100, 'Spawn': None, 'Filters': []}
        self.assertEqual(remove_apricorns(placement), placement)
        self.assertEqual(filter_drops(placement, {'apricorn_plain'}), placement)


if __name__ == "__main__":
    unittest.main()
