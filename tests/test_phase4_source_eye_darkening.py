"""Guard the user-approved Motimon/Tokomon dark-red eye exception."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Scripts"))
from SpritePipeline.core import _outline_frame  # noqa: E402


class SourceEyeDarkeningTests(unittest.TestCase):
    def test_only_source_covered_native_dark_pixels_change(self):
        size = 8
        image = Image.new("RGBA", (size, size), (210, 175, 130, 255))
        image.putpixel((3, 3), (100, 80, 65, 255))
        image.putpixel((4, 3), (240, 240, 240, 255))
        image.putpixel((5, 3), (100, 80, 65, 255))
        coverage = [0] * (size * size)
        coverage[3 * size + 3] = 255
        coverage[3 * size + 4] = 255
        geometry = {
            "size": size,
            "normals": [0] * (size * size * 4),
            "depth": [0] * (size * size * 4),
            "eyes": [{"sourceOnly": True, "coverage": coverage}],
        }
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "frame.geometry.json"
            path.write_text(json.dumps(geometry), encoding="utf-8")
            result = _outline_frame(image, path, {"source_eye_dark_rgb": [96, 28, 40]})
        self.assertEqual(result.getpixel((3, 3)), (96, 28, 40, 255))
        self.assertEqual(result.getpixel((4, 3)), (240, 240, 240, 255))
        self.assertEqual(result.getpixel((5, 3)), (100, 80, 65, 255))


if __name__ == "__main__":
    unittest.main()
