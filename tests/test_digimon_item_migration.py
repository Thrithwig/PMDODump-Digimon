import json
from pathlib import Path
import unittest
from Scripts.digimon_progression_tuning import remove_apricorns

ROOT=Path(__file__).resolve().parents[1]
def read(path):return json.loads(path.read_text(encoding='utf-8-sig'))
class ItemMigrationTests(unittest.TestCase):
    def test_removed_items_and_previous_matches(self):
        report=read(ROOT/'DataAsset/Digimon/item_implementation.json')
        protected=set(report['protected_matches'])
        self.assertFalse(protected & set(report['unavailable']))
        for sid in report['unavailable']:
            self.assertFalse(read(ROOT/f'DumpAsset/Data/Item/{sid}.json')['Object']['Released'],sid)
        self.assertTrue(read(ROOT/'DumpAsset/Data/Item/seed_reviver.json')['Object']['Released'])
        self.assertTrue(read(ROOT/'DumpAsset/Data/Item/medicine_potion.json')['Object']['Released'])

    def test_brave_point_amounts_and_chip_coverage(self):
        for grade,amount in {'e':2500,'d':5000,'c':10000,'b':20000,'a':40000}.items():
            obj=read(ROOT/f'DumpAsset/Data/Item/digi_brave_point_{grade}.json')['Object']
            self.assertEqual(obj['UseEvent']['OnHits'][0]['Value']['Script'],'DigimonBravePoint')
            self.assertIn(str(amount),obj['UseEvent']['OnHits'][0]['Value']['ArgTable'])
        names={read(p)['Object']['Name']['DefaultText'] for p in (ROOT/'DumpAsset/Data/Item').glob('ammo*.json') if read(p)['Object']['Released']}
        for stat in ('HP','SP','ATK','DEF','INT','SPD'):self.assertIn(stat+' Restraint Chip C',names)

    def test_food_boxes_and_gummi_categories(self):
        self.assertEqual(read(ROOT/'DumpAsset/Data/Item/food_apple.json')['Object']['Name']['DefaultText'],'Cookie')
        self.assertEqual(read(ROOT/'DumpAsset/Data/Item/food_banana.json')['Object']['Name']['DefaultText'],'Pie')
        box=read(ROOT/'DumpAsset/Data/Item/box_dainty.json')['Object']
        self.assertTrue(box['Released']);self.assertEqual(box['Name']['DefaultText'],'Dainty Box')
        for path in (ROOT/'DumpAsset/Data/Item').glob('gummi*.json'):
            obj=read(path)['Object']
            if obj['Released']:
                effects=obj['UseEvent']['OnHits']
                self.assertEqual(effects[0]['Value']['Script'],'DigimonTrainingFood')
                self.assertNotIn('TargetElement',json.dumps(effects))

    def test_no_removed_item_entries_in_zone_loot(self):
        banned=set(read(ROOT/'DataAsset/Digimon/item_implementation.json')['unavailable'])
        def check(value):
            if isinstance(value,list):
                for child in value:check(child)
            elif isinstance(value,dict):
                for key in ('Item','HiddenValue','Value'):
                    if isinstance(value.get(key),str):self.assertNotIn(value[key],banned)
                if isinstance(value.get('ID'),str) and value['ID']!='empty':self.assertNotIn(value['ID'],banned)
                for child in value.values():check(child)
        for path in (ROOT/'DumpAsset/Data/Zone').glob('*.json'):check(read(path))

if __name__=='__main__':unittest.main()
