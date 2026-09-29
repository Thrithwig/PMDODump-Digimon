import json
import sys
import tempfile
import unittest
import xml.etree.ElementTree as ET
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Scripts"))
from SpritePipeline.actions import (_cache_matches, _cache_record, _render_inputs,
                                    _seconds, _write_xml)
from SpritePipeline.core import sha256


class AgumonActionsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.specs = json.loads((ROOT / "config/phase4/agumon-actions.json").read_text())["actions"]

    def test_requested_actions_have_distinct_native_or_documented_motion(self):
        self.assertEqual([s["reference_index"] for s in self.specs],
                         [0, 1, 2, 5, 6, 8, 9, 10, 11, 12])
        self.assertEqual(len({s["name"] for s in self.specs}), 10)
        self.assertTrue(all(s["clip"].startswith("chr050_") for s in self.specs))
        self.assertTrue(all(len(s["durations"]) >= 2 for s in self.specs))
        for spec in self.specs:
            for index in spec.get("events", {}).values():
                self.assertTrue(0 <= index < len(spec["durations"]), spec["name"])

    def test_double_has_two_complete_native_strike_cycles(self):
        spec = next(s for s in self.specs if s["name"] == "Double")
        count = len(spec["durations"])
        self.assertEqual(count, 16)
        self.assertEqual([_seconds(spec, i, count) for i in range(8)],
                         [_seconds(spec, i, count) for i in range(8, 16)])

    def test_walk_samples_loop_at_equal_quarter_phases(self):
        spec = next(s for s in self.specs if s["name"] == "Walk")
        self.assertEqual([_seconds(spec, i, 4) for i in range(4)],
                         [spec["seconds"] * i / 4 for i in range(4)])

    def test_hurt_samples_inspected_impact_and_recoil(self):
        spec = next(s for s in self.specs if s["name"] == "Hurt")
        self.assertEqual([_seconds(spec, i, 2) for i in range(2)], [0.35, 0.65])
        self.assertEqual(spec["ground_policy"], "per-frame")

    def test_render_cache_requires_exact_sampling_and_verified_files(self):
        with tempfile.TemporaryDirectory() as temp:
            frame = Path(temp) / "frame_00.png"
            geometry = frame.with_suffix(".geometry.json")
            frame.write_bytes(b"known-render")
            geometry.write_text(json.dumps({
                "framing": {"clip": "chr050_ba02"},
                "bonePoints": {name: [0, 0] for name in
                               ("head", "center", "left_hand", "right_hand")},
            }), encoding="utf-8")
            base = dict(model_hash="model", renderer_hash="renderer",
                        capture_hash="capture", core_hash="core",
                        clip="chr050_ba02", seconds=0.35, azimuth=45.0,
                        render_size=512, frame_size=40,
                        settings={"eye_mode": "approved"})
            expected = _render_inputs(**base)
            self.assertFalse(_cache_matches(frame, expected),
                             "Legacy renders without attestations are unverified")
            _cache_record(frame).write_text(json.dumps({
                "inputs": expected, "image_sha256": sha256(frame),
                "geometry_sha256": sha256(geometry),
            }), encoding="utf-8")
            self.assertTrue(_cache_matches(frame, expected))
            for changed in ({"seconds": 0.65}, {"azimuth": 90.0},
                            {"model_hash": "changed-model"},
                            {"settings": {"eye_mode": "changed"}}):
                self.assertFalse(_cache_matches(frame, _render_inputs(**(base | changed))),
                                 changed)
            frame.write_bytes(b"tampered-render")
            self.assertFalse(_cache_matches(frame, expected))

    def test_category_numbers_do_not_override_engine_registry(self):
        cfg = json.loads((ROOT / "config/phase4/agumon-actions.json").read_text())
        self.assertEqual(cfg["approved_idle_category_index"], 7)
        self.assertEqual(cfg["approved_idle_engine_index"], 1)
        self.assertEqual(cfg["charmander_shoot_xml_index"], 3)

    def test_provenance_pins_current_config_and_reference(self):
        from SpritePipeline.core import sha256
        config_path = ROOT / "config/phase4/agumon-actions.json"
        cfg = json.loads(config_path.read_text(encoding="utf-8"))
        report = json.loads((ROOT / "work/phase4/agumon-actions/provenance.json").read_text(encoding="utf-8"))
        self.assertEqual(report["actions_config_sha256"], sha256(config_path))
        self.assertEqual(report["reference_commit"], cfg["reference_commit"])
        self.assertEqual(report["reference_animdata_sha256"], cfg["reference_animdata_sha256"])
        self.assertEqual(report["actions"], cfg["actions"])

    def test_xml_keeps_engine_indices_and_approved_idle_element(self):
        approved = ROOT / "work/phase4/face-corrected/output/agumon/AnimData.xml"
        registry = ROOT / "DumpAsset/Base/GFXParams.xml"
        with tempfile.TemporaryDirectory() as temp:
            candidate = Path(temp) / "AnimData.xml"
            _write_xml(approved, candidate, self.specs, registry)
            before = ET.parse(approved)
            after = ET.parse(candidate)
            lookup = {n.findtext("Name"): n for n in after.findall("./Anims/Anim")}
            idle = next(n for n in before.findall("./Anims/Anim") if n.findtext("Name") == "Idle")
            self.assertEqual(ET.tostring(lookup["Idle"]), ET.tostring(idle))
            engine_names = [n.findtext("Name") for n in ET.parse(registry).findall("./Actions/Action")]
            for spec in self.specs:
                node = lookup[spec["name"]]
                self.assertEqual(int(node.findtext("Index")), engine_names.index(spec["name"]))
                self.assertIsNone(node.find("CopyOf"))
                self.assertEqual([int(n.text) for n in node.findall("./Durations/Duration")],
                                 spec["durations"])


if __name__ == "__main__":
    unittest.main()
