import csv
import json
import tempfile
import unittest
from pathlib import Path

from Scripts.digimon_dataset import DatasetError, FILES, build_manifest, main


TABLES = {
    "digimon": [
        {"Digimon": "Koromon", "Stage": "In-Training", "Type": "Free", "Attribute": "Neutral", "HP": "450"},
        {"Digimon": "Agumon", "Stage": "Rookie", "Type": "Vaccine", "Attribute": "Fire", "HP": "1030"},
        {"Digimon": "Greymon", "Stage": "Champion", "Type": "Vaccine", "Attribute": "Fire", "HP": "1230"},
    ],
    "requirements": [
        {"Digimon": "Agumon", "Level": "9"},
        {"Digimon": "Greymon", "Level": "16", "ATK": "55"},
    ],
    "digivolutions": [
        {"Digimon From": "Koromon", "Digimon To": "Agumon"},
        {"Digimon From": "Agumon", "Digimon To": "Greymon"},
    ],
    "skills_by_digimon": [
        {"Digimon": "Agumon", "Skill": "Pepper Breath", "Level": "1"},
        {"Digimon": "Greymon", "Skill": "Mega Flame", "Level": "1"},
    ],
    "skills": [
        {"Skill": "Pepper Breath", "SP Cost": "5", "Type": "Physical"},
        {"Skill": "Mega Flame", "SP Cost": "10", "Type": "Magic"},
    ],
}


def write_tables(root: Path, tables=TABLES):
    for key, rows in tables.items():
        fieldnames = list(dict.fromkeys(field for row in rows for field in row))
        with (root / FILES[key]).open("w", encoding="utf-8", newline="") as stream:
            writer = csv.DictWriter(stream, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(rows)


class DigimonDatasetTests(unittest.TestCase):
    def test_builds_bidirectional_graph_and_skill_links(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_tables(root)
            manifest = build_manifest(root)
            entries = {entry["id"]: entry for entry in manifest["digimon"]}

            self.assertEqual(entries["agumon"]["digivolves_from"], ["koromon"])
            self.assertEqual(entries["agumon"]["digivolves_to"], ["greymon"])
            self.assertEqual(entries["agumon"]["skills"][0]["skill"], "pepper_breath")
            self.assertEqual(entries["greymon"]["requirements"], [{"Level": "16", "ATK": "55"}])

    def test_rejects_unknown_species_reference(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            tables = {key: [dict(row) for row in rows] for key, rows in TABLES.items()}
            tables["digivolutions"][0]["Digimon To"] = "Missingmon"
            write_tables(root, tables)
            with self.assertRaisesRegex(DatasetError, "unknown Digimon"):
                build_manifest(root)

    def test_cli_writes_deterministic_json(self):
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            write_tables(root)
            output = root / "build" / "manifest.json"
            self.assertEqual(main(["--input", str(root), "--output", str(output)]), 0)
            manifest = json.loads(output.read_text(encoding="utf-8"))
            self.assertEqual(manifest["schema_version"], 2)
            self.assertEqual([entry["id"] for entry in manifest["digimon"]], ["agumon", "greymon", "koromon"])


if __name__ == "__main__":
    unittest.main()