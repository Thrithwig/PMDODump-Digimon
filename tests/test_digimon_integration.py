"""Regression coverage for the supplied CSV shapes and the local pinned dataset."""
import copy
import csv
import hashlib
import json
from pathlib import Path
import tempfile
import unittest

from Scripts.digimon_dataset import DatasetError, build_manifest, main, select_roster
from test_digimon_dataset import TABLES, write_tables


ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / "DataAsset" / "Digimon"


class ImportRegressionTests(unittest.TestCase):
    def test_semicolon_stats_sentinel_and_numeric_learnset_sort(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tables = copy.deepcopy(TABLES)
            tables["digimon"][0].update({"HP lvl 1": "20", "HP lvl 50": "300", "HP lvl 99": "580"})
            tables["digivolutions"].append({"Digimon From": "Greymon", "Digimon To": "N/A"})
            tables["skills_by_digimon"] += [
                {"Digimon": "Agumon", "Skill": "Mega Flame", "Level": "10"},
                {"Digimon": "Agumon", "Skill": "Mega Flame", "Level": "2"},
            ]
            write_tables(root, tables)
            for path in root.glob("*.csv"):
                with path.open(newline="", encoding="utf-8") as stream:
                    rows = list(csv.reader(stream))
                with path.open("w", newline="", encoding="utf-8-sig") as stream:
                    csv.writer(stream, delimiter=";").writerows(rows + [[""] * len(rows[0])])
            manifest = build_manifest(root)
            entries = {x["id"]: x for x in manifest["digimon"]}
            self.assertEqual(entries["koromon"]["stats_by_level"]["99"]["hp"], "580")
            self.assertEqual(entries["greymon"]["digivolves_to"], [])
            self.assertEqual([s["level"] for s in entries["agumon"]["skills"]], ["1", "2", "10"])

    def test_distinct_variants_are_not_silently_assigned(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tables = copy.deepcopy(TABLES)
            tables["skills"].append({**tables["skills"][0], "SP Cost": "99"})
            write_tables(root, tables)
            manifest = build_manifest(root)
            skill = next(s for s in manifest["skills"] if s["id"] == "pepper_breath")
            self.assertEqual(len(skill["variants"]), 2)
            self.assertEqual({v["source"]["SP Cost"] for v in skill["variants"]}, {"5", "99"})
            agumon = next(x for x in manifest["digimon"] if x["id"] == "agumon")
            self.assertIsNone(agumon["skills"][0]["variant"])
            with self.assertRaisesRegex(DatasetError, "Unresolved skill variant"):
                select_roster(manifest, {"lines": [{"choice": "agumon", "species": ["agumon"]}]})

    def test_identical_duplicates_preserve_both_source_rows(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tables = copy.deepcopy(TABLES)
            tables["skills"].append(copy.deepcopy(tables["skills"][0]))
            write_tables(root, tables)
            skill = next(s for s in build_manifest(root)["skills"] if s["id"] == "pepper_breath")
            self.assertFalse(skill["requires_variant_resolution"])
            self.assertEqual(len(skill["variants"][0]["source_rows"]), 2)

    def test_bad_skill_fails_without_overwriting_output(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tables = copy.deepcopy(TABLES)
            tables["skills_by_digimon"][0]["Skill"] = "Unknown move"
            write_tables(root, tables)
            output = root / "existing.json"
            output.write_text("previous output")
            self.assertEqual(main(["--input", str(root), "--output", str(output)]), 1)
            self.assertEqual(output.read_text(), "previous output")

    def test_missing_and_malformed_tables_fail(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            with self.assertRaisesRegex(DatasetError, "Missing required table"):
                build_manifest(root)
            write_tables(root)
            (root / "Digimon.csv").write_text("Digimon;Stage\nExample;Rookie;extra\n")
            with self.assertRaisesRegex(DatasetError, "Malformed row"):
                build_manifest(root)


class PinnedDatasetTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.manifest = build_manifest(DATA / "Source")
        cls.roster = json.loads((DATA / "phase1_roster.json").read_text())

    def test_checked_in_outputs_match_regeneration_byte_for_byte(self):
        for manifest, path in [
            (self.manifest, ROOT / "DataAsset" / "Monster" / "digimon_manifest.json"),
            (select_roster(self.manifest, self.roster), DATA / "phase1_manifest.json"),
        ]:
            expected = (json.dumps(manifest, ensure_ascii=False, indent=2) + "\n").encode()
            self.assertEqual(path.read_bytes(), expected)

    def test_source_rows_hashes_and_correction(self):
        self.assertEqual(len(self.manifest["digimon"]), 341)
        self.assertEqual(len(self.manifest["skills"]), 494)
        self.assertEqual(sum(len(v["source_rows"]) for s in self.manifest["skills"] for v in s["variants"]), 505)
        self.assertEqual(len(self.manifest["issues"]), 10)
        self.assertEqual(self.manifest["corrections"][0]["original"], "Commet Hammer II")
        for name, metadata in self.manifest["source"]["files"].items():
            self.assertEqual(hashlib.sha256((DATA / "Source" / name).read_bytes()).hexdigest(), metadata["sha256"])
        for entry in self.manifest["digimon"]:
            self.assertEqual(set(entry["stats_by_level"]), {"1", "50", "99"})
            for stats in entry["stats_by_level"].values():
                self.assertEqual(set(stats), {"hp", "sp", "atk", "def", "int", "spd"})

    def test_roster_is_closed_and_reversible(self):
        slice_manifest = select_roster(self.manifest, self.roster)
        self.assertEqual({x["choice"] for x in self.roster["lines"]},
                         {"agumon", "gabumon", "biyomon", "tentomon", "palmon", "gomamon", "patamon", "gatomon"})
        entries = {x["id"]: x for x in slice_manifest["digimon"]}
        self.assertEqual(len(entries), 44)
        self.assertEqual(slice_manifest["issues"], [])
        for entry in entries.values():
            for target in entry["digivolves_to"]:
                self.assertIn(entry["id"], entries[target]["digivolves_from"])
        invalid = copy.deepcopy(self.roster)
        invalid["lines"][0]["species"] = ["agumon", "seraphimon"]
        with self.assertRaisesRegex(DatasetError, "edge absent"):
            select_roster(self.manifest, invalid)

    def test_image_coverage_checksums_and_png_signatures(self):
        selected = {x["id"] for x in select_roster(self.manifest, self.roster)["digimon"]}
        provenance = json.loads((DATA / "phase2_image_provenance.json").read_text())
        self.assertTrue(selected <= {x["species"] for x in provenance["images"]})
        for entry in provenance["images"]:
            data = (DATA / entry["path"]).read_bytes()
            self.assertTrue(data.startswith(b"\x89PNG\r\n\x1a\n"))
            self.assertEqual(hashlib.sha256(data).hexdigest(), entry["png_sha256"])


if __name__ == "__main__":
    unittest.main()
