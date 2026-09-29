"""Focused GLB prefix checks for the bounded Phase 4 model exporter."""

import json
from pathlib import Path
import struct
import tempfile
import unittest

from Scripts import phase4_model_export_batch as exporter


def write_glb(path: Path, names: list[str]) -> None:
    document = {
        "asset": {"version": "2.0"},
        "scenes": [{}],
        "nodes": [{}],
        "meshes": [{}],
        "buffers": [{"byteLength": 0}],
        "animations": [{"name": name} for name in names],
    }
    payload = json.dumps(document).encode("utf-8")
    payload += b" " * (-len(payload) % 4)
    length = 12 + 8 + len(payload) + 8
    path.write_bytes(b"glTF" + struct.pack("<II", 2, length)
                     + struct.pack("<I4s", len(payload), b"JSON") + payload
                     + struct.pack("<I4s", 0, b"BIN\0"))


class ModelExportAliasTests(unittest.TestCase):
    def test_observed_alias_is_accepted_with_metadata(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "blackgatomon.glb"
            write_glb(path, ["chr092", "chr092_ba01", "chr092_br01"])
            details = exporter.validate_glb(path, "chr043")
            self.assertEqual(details["animation_prefix"], "chr092")
            self.assertTrue(details["animation_prefix_alias"])
            self.assertEqual(details["animations"], 3)

    def test_unapproved_or_mixed_prefix_is_rejected(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "model.glb"
            write_glb(path, ["chr999_ba01"])
            with self.assertRaisesRegex(ValueError, "no expected chr092"):
                exporter.validate_glb(path, "chr043")
            write_glb(path, ["chr092_ba01", "chr999_br01"])
            with self.assertRaisesRegex(ValueError, "unexpected animation prefix"):
                exporter.validate_glb(path, "chr043")

    def test_direct_source_remains_direct(self):
        with tempfile.TemporaryDirectory() as temporary:
            path = Path(temporary) / "model.glb"
            write_glb(path, ["chr001", "chr001_ba01"])
            details = exporter.validate_glb(path, "chr001")
            self.assertEqual(details["animation_prefix"], "chr001")
            self.assertFalse(details["animation_prefix_alias"])
            write_glb(path, ["chr999_ba01"])
            with self.assertRaisesRegex(ValueError, "no expected chr001"):
                exporter.validate_glb(path, "chr001")


if __name__ == "__main__":
    unittest.main()
