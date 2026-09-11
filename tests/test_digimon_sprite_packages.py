import json
import sys
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

from PIL import Image, ImageOps

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'Scripts'))
import digimon_sprite_packages as sprites


class SpritePackageTests(unittest.TestCase):
    def test_name_matching_preserves_model_and_form(self):
        self.assertIsNotNone(sprites.score('Kudamon_2006_Model_DSR.png', 'Kudamon 2006'))
        self.assertIsNotNone(sprites.score('Lucemon_falldown_new_century.png', 'Lucemon: Falldown Mode'))
        self.assertIsNone(sprites.score('Agumon_black_new_century.png', 'Agumon'))
        self.assertIsNone(sprites.score('Agumon_RE_Collectors_Card.png', 'Agumon'))

    def test_opaque_images_are_rejected(self):
        self.assertFalse(sprites.transparent(Image.new('RGBA', (100, 100), 'white')))
        self.assertFalse(sprites.transparent(Image.new('RGBA', (100, 100))))

    def test_initial_roster_has_every_package(self):
        roster = json.loads((sprites.DATA / 'phase1_roster.json').read_text())
        for line in roster['lines']:
            for sid in line['species']:
                self.assertTrue((sprites.OUTPUT / 'Packages' / sid / 'AnimData.xml').exists(), sid)

    def test_every_package_has_exact_directional_rows(self):
        for path in sorted((sprites.OUTPUT / 'Packages').iterdir()):
            if not path.is_dir():
                continue
            with self.subTest(species=path.name):
                root = ET.parse(path / 'AnimData.xml')
                idle = next(anim for anim in root.findall('./Anims/Anim') if anim.findtext('Name') == 'Idle')
                size = int(idle.findtext('FrameWidth'))
                self.assertEqual(size, int(idle.findtext('FrameHeight')))
                self.assertEqual(len(idle.findall('./Durations/Duration')), 1)
                with Image.open(path / 'Idle-Anim.png') as sheet:
                    self.assertEqual(sheet.size, (size, size*8))
                    normal = sheet.crop((0, 0, size, size))
                    for row in range(8):
                        expected = ImageOps.mirror(normal) if row in (5, 6, 7) else normal
                        self.assertEqual(sheet.crop((0, row*size, size, (row+1)*size)).tobytes(), expected.tobytes())
                for kind in ['Offsets', 'Shadow']:
                    with Image.open(path / ('Idle-' + kind + '.png')) as markers:
                        self.assertEqual(markers.size, (size, size*8))
                        for row in range(8):
                            self.assertEqual(markers.getpixel((size//2, row*size+size//2)), (255, 255, 255, 255))
                with Image.open(sprites.OUTPUT / 'Sources' / (path.name + '.png')) as source:
                    self.assertTrue(sprites.transparent(source.convert('RGBA')))


if __name__ == '__main__':
    unittest.main()
