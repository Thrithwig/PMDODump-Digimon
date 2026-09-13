"""Full source-graph, acquisition-gate, artwork and item migration regressions."""
import hashlib
import json
from pathlib import Path
import unittest

ROOT=Path(__file__).resolve().parents[1]
DATA=ROOT/'DataAsset/Digimon'
def read(path): return json.loads(path.read_text(encoding='utf-8-sig'))

class FullRosterTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.source=read(ROOT/'DataAsset/Monster/digimon_manifest.json')
        cls.gameplay=read(DATA/'phase2_gameplay.json')
        cls.species={x['id']:x for x in cls.gameplay['species']}
        cls.edges={(x['from'],x['to']):x for x in cls.gameplay['transitions']}

    def test_source_graph_complete_and_only_nx_isolated(self):
        self.assertEqual(len(self.species),341)
        self.assertEqual(len(self.edges),len(self.gameplay['transitions']))
        for entry in self.source['digimon']:
            for target in entry['digivolves_to']:
                self.assertIn((entry['id'],target),self.edges)
                self.assertIn((target,entry['id']),self.edges)
        reached={x['species'] for x in self.gameplay['starters']}
        while True:
            expanded=reached|{b for a,b in self.edges if a in reached}
            if expanded==reached: break
            reached=expanded
        self.assertEqual(set(self.species)-reached,{e['id'] for e in self.source['digimon'] if e['id'].endswith('_nx')})
        self.assertEqual(len(reached),336)

    def test_all_numeric_requirements_reachable_with_earned_training(self):
        for (source,_),edge in self.edges.items():
            for req in edge['requirements']:
                if req['kind']=='stat': maximum=self.species[source]['stats_by_level'][-1]['stats'][req['stat']]+256
                elif req['kind']=='level': maximum=99
                elif req['kind']=='bond': maximum=100
                elif req['kind']=='training': maximum=200
                else: continue
                self.assertLessEqual(req['minimum'],maximum,edge['id'])

    def test_story_gates_removed_and_items_and_partners_retained(self):
        for entry in self.source['digimon']:
            extra=entry['requirements'][0].get('Extra Condition','')
            for parent in entry['digivolves_from']:
                reqs=self.edges[(parent,entry['id'])]['requirements']
                self.assertNotIn('story',{r['kind'] for r in reqs})
                if extra.startswith('Item: '):
                    items=[r for r in reqs if r['kind']=='item']
                    self.assertEqual(len(items),1)
                    native=read(ROOT/('DumpAsset/Data/Item/'+items[0]['item']+'.json'))['Object']
                    self.assertEqual(native['Name']['DefaultText'],extra[6:])
                if extra.startswith('Digimon: '):
                    self.assertEqual({r['species'] for r in reqs if r['kind']=='party'},set(entry['digivolves_from']))
                if extra=='Mode Change':
                    self.assertFalse(self.edges[(parent,entry['id'])]['preserve_level'])
                    self.assertFalse(self.edges[(entry['id'],parent)]['preserve_level'])

    def test_art_is_complete_verified_and_installed(self):
        from PIL import Image
        art=read(DATA/'phase2_image_provenance.json')['images']
        self.assertEqual({x['species'] for x in art},set(self.species))
        for record in art:
            path=DATA/record['path']
            self.assertEqual(hashlib.sha256(path.read_bytes()).hexdigest(),record['png_sha256'])
            with Image.open(path) as image:
                self.assertEqual(image.size,(record['width'],record['height']))
                self.assertEqual(image.convert('RGBA').getchannel('A').getextrema()[0]<255,record['transparent'])
            monster=read(ROOT/('DumpAsset/Data/Monster/'+record['species']+'.json'))['Object']
            installed=ROOT/f"DumpAsset/Content/StaticCreature/{monster['IndexNum']}.png"
            transparent=DATA/f"SpritePackages/Sources/{record['species']}.png"
            if transparent.exists():
                provenance=read(DATA/f"SpritePackages/Records/{record['species']}.json")
                self.assertEqual(hashlib.sha256(transparent.read_bytes()).hexdigest(),provenance['png_sha256'])
                path=transparent
            self.assertEqual(installed.read_bytes(),path.read_bytes())

    def test_every_item_accounted_for_without_changing_ids(self):
        mapped=read(DATA/'item_mapping.json');unmatched=read(DATA/'unmatched_items.json')
        ids=[r['item_id'] for r in mapped+unmatched]
        self.assertEqual(len(ids),len(set(ids)))
        generated={r['item'] for r in read(DATA/'attachment_skills.json')['skills']}
        self.assertEqual(set(ids)|generated,{p.stem for p in (ROOT/'DumpAsset/Data/Item').glob('*.json') if not p.stem.startswith(('digi_brave_point_','digixcl_'))})
        for row in mapped:
            native=read(ROOT/('DumpAsset/Data/Item/'+row['item_id']+'.json'))['Object']
            self.assertEqual(native['Name']['DefaultText'],row['cyber_sleuth_item'])
            self.assertEqual(native['Desc']['DefaultText'],row['runtime_description'])
            self.assertTrue(row['adaptation'])
        for row in unmatched: self.assertTrue(row['reason'])

    def test_element_guards_and_manual_revival_have_real_effect_changes(self):
        item=read(ROOT/'DumpAsset/Data/Item/held_flame_plate.json')['Object']
        effect=item['BeforeBeingHits'][0]['Value']
        self.assertEqual((effect['Numerator'],effect['Denominator']),(4,5))
        revive=read(ROOT/'DumpAsset/Data/Item/seed_reviver.json')['Object']
        self.assertEqual(revive['OnDeaths'],[])
        self.assertIn('ReviveAllEvent',revive['UseEvent']['OnHits'][0]['Value']['$type'])

if __name__=='__main__':unittest.main()
