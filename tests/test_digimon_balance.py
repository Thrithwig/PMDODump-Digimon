import copy
from fractions import Fraction
import json
from pathlib import Path
import tempfile
import unittest

from Scripts.digimon_balance import BalanceError, build_catalog, main, preview, scaled, source_at_level


DATA = Path(__file__).resolve().parents[1] / "DataAsset" / "Digimon"


class BalanceTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = json.loads((DATA / "phase1_manifest.json").read_text())
        cls.overlay = json.loads((DATA / "phase1_overlay.json").read_text())
        cls.catalog = build_catalog(cls.manifest, cls.overlay)

    def test_source_is_unchanged_and_catalog_reproduces_exactly(self):
        manifest = copy.deepcopy(self.manifest)
        overlay = copy.deepcopy(self.overlay)
        actual = build_catalog(manifest, overlay)
        self.assertEqual(manifest, self.manifest)
        self.assertEqual(overlay, self.overlay)
        expected_bytes = (json.dumps(actual, ensure_ascii=False, indent=2) + "\n").encode()
        self.assertEqual((DATA / "phase1_gameplay.json").read_bytes(), expected_bytes)

    def test_interpolation_and_rounding_at_boundaries(self):
        anchors = {"1": {"hp": 100}, "50": {"hp": 590}, "99": {"hp": 1570}}
        self.assertEqual(source_at_level(anchors, "hp", 1), 100)
        self.assertEqual(source_at_level(anchors, "hp", 25), 340)
        self.assertEqual(source_at_level(anchors, "hp", 50), 590)
        self.assertEqual(source_at_level(anchors, "hp", 51), 610)
        self.assertEqual(source_at_level(anchors, "hp", 99), 1570)
        self.assertEqual(scaled(105, {"numerator": 1, "denominator": 10, "offset": 20}), 31)
        self.assertEqual(scaled(Fraction(1049, 10), {"numerator": 1, "denominator": 10, "offset": 20}), 30)
        with self.assertRaises(BalanceError):
            source_at_level(anchors, "hp", 100)

    def test_all_forms_have_monotone_positive_stats_and_exact_anchors(self):
        source = {entry["id"]: entry for entry in self.manifest["digimon"]}
        self.assertEqual(len(self.catalog["species"]), 44)
        for entry in self.catalog["species"]:
            self.assertEqual(len(entry["stats_by_level"]), 99)
            previous = {stat: 0 for stat in self.overlay["stats"]}
            for row in entry["stats_by_level"]:
                for stat, value in row["stats"].items():
                    self.assertGreaterEqual(value, max(1, previous[stat]))
                    previous[stat] = value
            for level in (1, 50, 99):
                for stat, rule in self.overlay["stats"].items():
                    value = int(source[entry["id"]]["stats_by_level"][str(level)][rule["source"]])
                    self.assertEqual(entry["stats_by_level"][level - 1]["stats"][stat], scaled(value, rule))

    def test_forward_conditions_retain_source_and_reverse_is_free(self):
        edges = {(edge["from"], edge["to"]): edge for edge in self.catalog["transitions"]}
        self.assertEqual(len(edges), 80)
        greymon = edges["agumon", "greymon"]
        self.assertIn({"kind": "bond", "minimum": 50, "source_field": "CAM", "source_value": "50%"}, greymon["requirements"])
        self.assertIn({"kind": "stat", "minimum": 33, "source_field": "ATK", "source_value": "55", "stat": "attack"}, greymon["requirements"])
        for edge in edges.values():
            self.assertTrue(edge["hub_only"])
            self.assertEqual(edge["preserve_level"], edge["direction"] == "digivolve")
            self.assertEqual(edge["costs"], [])
            if edge["direction"] == "digivolve":
                reverse = edges[edge["to"], edge["from"]]
                self.assertEqual(reverse["direction"], "dedigivolve")
                self.assertEqual(reverse["requirements"], [])

    def test_preview_exact_threshold_and_no_mutation(self):
        requirements = [{"kind": "level", "minimum": 16},
                        {"kind": "stat", "stat": "attack", "minimum": 33},
                        {"kind": "bond", "minimum": 50},
                        {"kind": "training", "minimum": 5}]
        original = copy.deepcopy(requirements)
        self.assertTrue(preview(requirements, 16, {"attack": 33}, 50, 5)["eligible"])
        for level, attack, bond, training in ((15, 33, 50, 5), (16, 32, 50, 5), (16, 33, 49, 5), (16, 33, 50, 4)):
            result = preview(requirements, level, {"attack": attack}, bond, training)
            self.assertFalse(result["eligible"])
            self.assertEqual(sum(not row["met"] for row in result["requirements"]), 1)
        self.assertEqual(requirements, original)

    def test_selected_lines_can_complete_in_sequence(self):
        species = {x["id"]: x for x in self.catalog["species"]}
        edges = {(x["from"], x["to"]): x for x in self.catalog["transitions"]}
        # This proves numeric reachability with enough eligible encounters, not
        # dungeon access or XP availability. Level is preserved at every step.
        for line in self.manifest["roster"]["lines"]:
            level = 5
            path = line["species"]
            for source, target in zip(path, path[1:]):
                while level <= 99:
                    state = species[source]["stats_by_level"][level - 1]["stats"]
                    if preview(edges[source, target]["requirements"], level, state, 100, level - 5)["eligible"]:
                        break
                    level += 1
                self.assertLessEqual(level, 99, f"Unreachable {source} -> {target}")
            for target, source in zip(reversed(path), list(reversed(path))[1:]):
                self.assertTrue(preview(edges[target, source]["requirements"], level, {}, 0, 0)["eligible"])

    def test_unreachable_and_unknown_requirements_fail(self):
        for extra, message in (({"HP": "999999"}, "Unreachable"),
                               ({"Extra Condition": "A special item"}, "unsupported source condition"),
                               ({"StoryFlag": "1"}, "unsupported requirement column"),
                               ({"CAM": "many"}, "invalid CAM")):
            manifest = copy.deepcopy(self.manifest)
            next(x for x in manifest["digimon"] if x["id"] == "greymon")["requirements"][0].update(extra)
            with self.assertRaisesRegex(BalanceError, message):
                build_catalog(manifest, self.overlay)

    def test_bad_graph_and_stat_data_fail(self):
        manifest = copy.deepcopy(self.manifest)
        manifest["digimon"][0]["digivolves_to"].append("missingmon")
        with self.assertRaisesRegex(BalanceError, "Broken forward edge"):
            build_catalog(manifest, self.overlay)
        manifest = copy.deepcopy(self.manifest)
        manifest["digimon"][0]["stats_by_level"]["50"]["hp"] = "0"
        with self.assertRaises(BalanceError):
            build_catalog(manifest, self.overlay)

    def test_invalid_policies_fail_closed(self):
        invalid = []
        overlay = copy.deepcopy(self.overlay)
        overlay["stats"]["attack"]["denominator"] = 0
        invalid.append(overlay)
        overlay = copy.deepcopy(self.overlay)
        overlay["scan"]["direct_recruitment"] = True
        invalid.append(overlay)
        overlay = copy.deepcopy(self.overlay)
        overlay["progression"]["training"]["maximum"] = 1
        invalid.append(overlay)
        overlay = copy.deepcopy(self.overlay)
        overlay["requirement_stats"]["ATK"] = "defense"
        invalid.append(overlay)
        overlay = copy.deepcopy(self.overlay)
        overlay["scan"]["restoration_level"] = 99
        invalid.append(overlay)
        for overlay in invalid:
            with self.subTest(overlay=overlay), self.assertRaises(BalanceError):
                build_catalog(self.manifest, overlay)

    def test_starters_preserve_selected_identity_and_stage(self):
        starters = {x["species"]: x for x in self.catalog["starters"]}
        self.assertEqual(len(starters), 8)
        self.assertEqual(starters["gatomon"]["stage"], "Champion")
        self.assertTrue(all(x["level"] == 5 for x in starters.values()))
        self.assertTrue(all(x["stage"] == "Rookie" for key, x in starters.items() if key != "gatomon"))

    def test_cli_never_overwrites_inputs_or_output_on_validation_error(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            source, overlay, output = root / "manifest.json", root / "overlay.json", root / "output.json"
            source.write_text(json.dumps(self.manifest))
            overlay.write_text(json.dumps(self.overlay))
            before = source.read_bytes()
            args = ["--manifest", str(source), "--overlay", str(overlay), "--output"]
            self.assertEqual(main(args + [str(source)]), 1)
            self.assertEqual(source.read_bytes(), before)
            output.write_text("keep me")
            overlay.write_text("{}")
            self.assertEqual(main(args + [str(output)]), 1)
            self.assertEqual(output.read_text(), "keep me")


if __name__ == "__main__":
    unittest.main()
