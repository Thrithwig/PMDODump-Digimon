"""Prove compact renderer face coverage is pixel-equivalent to legacy masks."""

import json
import sys
import tempfile
import unittest
from pathlib import Path

import numpy as np
from PIL import Image


ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Scripts"))
from SpritePipeline.core import _outline_frame  # noqa: E402


class FaceCoverageCompactionTests(unittest.TestCase):
    def test_compact_coverage_matches_high_resolution_mask(self):
        size, high_size = 4, 8
        image = Image.new("RGBA", (size, size), (180, 140, 90, 255))
        raw = np.zeros((high_size, high_size, 4), dtype=np.uint8)
        # WebGL rows are bottom-up. Multiple source samples in a PMDO pixel
        # exercise the mouth threshold, while channel 1 exercises the nose.
        raw[4, 2, 0] = raw[4, 3, 0] = 255
        raw[5, 4, 1] = 255
        legacy = {
            "size": size,
            "normals": [0] * (size * size * 4),
            "depth": [0] * (size * size * 4),
            "featureSize": high_size,
            "faceFeatures": raw.reshape(-1).tolist(),
            "eyes": [],
        }
        coverage = np.zeros((size, size, 2), dtype=np.int64)
        for y in range(high_size):
            for x in range(high_size):
                target_y = (high_size - 1 - y) * size // high_size
                target_x = x * size // high_size
                coverage[target_y, target_x] += raw[y, x, :2]
        compact = {
            "size": size,
            "normals": legacy["normals"],
            "depth": legacy["depth"],
            "faceCoverage": coverage.reshape(-1).tolist(),
            "eyes": [],
        }
        with tempfile.TemporaryDirectory() as temp:
            legacy_path = Path(temp) / "legacy.geometry.json"
            compact_path = Path(temp) / "compact.geometry.json"
            legacy_path.write_text(json.dumps(legacy), encoding="utf-8")
            compact_path.write_text(json.dumps(compact), encoding="utf-8")
            legacy_result = _outline_frame(image, legacy_path, {})
            compact_result = _outline_frame(image, compact_path, {})
        self.assertEqual(list(legacy_result.getdata()), list(compact_result.getdata()))


if __name__ == "__main__":
    unittest.main()
