#!/usr/bin/env python3
"""Normalize the five Digimon Cyber Sleuth CSV tables into one manifest.

The source tables are downloaded manually from the Kaggle dataset documented in
``docs/DIGIMON_CONVERSION_PLAN.md``.  This script deliberately performs no network
access and does not redistribute the source data.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from pathlib import Path


DATASET_URL = (
    "https://www.kaggle.com/datasets/lianebrisebois/"
    "digimon-cyber-sleuth-dataset"
)
FILES = {
    "digimon": "Digimon.csv",
    "requirements": "Digivolution Requirements.csv",
    "digivolutions": "Digivolutions.csv",
    "skills_by_digimon": "Skills by Digimon.csv",
    "skills": "Skills.csv",
}


class DatasetError(ValueError):
    """Raised when the input tables are absent or internally inconsistent."""


def _key(value: str) -> str:
    return re.sub(r"[^a-z0-9]", "", value.casefold())


def _id(value: str) -> str:
    result = re.sub(r"[^a-z0-9]+", "_", value.casefold()).strip("_")
    if not result:
        raise DatasetError(f"Cannot create a stable ID from {value!r}")
    return result


def _read(path: Path) -> list[dict[str, str]]:
    if not path.is_file():
        raise DatasetError(f"Missing required table: {path.name}")
    with path.open(encoding="utf-8-sig", newline="") as stream:
        header = stream.readline()
        stream.seek(0)
        reader = csv.DictReader(stream, delimiter=";" if ";" in header else ",")
        if not reader.fieldnames:
            raise DatasetError(f"Table has no header: {path.name}")
        rows = []
        for row_number, row in enumerate(reader, 2):
            if None in row or any(value is None for value in row.values()):
                raise DatasetError(f"Malformed row {row_number} in {path.name}")
            clean = {(name or "").strip(): (value or "").strip() for name, value in row.items()}
            if any(clean.values()):
                clean["_source_row"] = str(row_number)
                rows.append(clean)
        if not rows:
            raise DatasetError(f"Table has no records: {path.name}")
        return rows


def _value(row: dict[str, str], aliases: tuple[str, ...], table: str) -> str:
    columns = {_key(name): value for name, value in row.items() if not name.startswith("_")}
    for alias in aliases:
        if _key(alias) in columns:
            return columns[_key(alias)]
    raise DatasetError(
        f"{table} row {row.get('_source_row', '?')} needs one of columns "
        + ", ".join(aliases)
    )


def _optional(row: dict[str, str], *aliases: str) -> str:
    columns = {_key(name): value for name, value in row.items() if not name.startswith("_")}
    return next((columns[_key(alias)] for alias in aliases if _key(alias) in columns), "")


def _public_row(row: dict[str, str], excluded: set[str] | None = None) -> dict[str, str]:
    excluded = {_key(value) for value in (excluded or set())}
    return {
        name: value
        for name, value in row.items()
        if not name.startswith("_") and _key(name) not in excluded and value != ""
    }


def build_manifest(input_dir: Path) -> dict:
    tables = {name: _read(input_dir / filename) for name, filename in FILES.items()}
    digimon: dict[str, dict] = {}
    names: dict[str, str] = {}

    for row in tables["digimon"]:
        name = _value(row, ("Digimon", "Name"), FILES["digimon"])
        species_id = _id(name)
        if species_id in digimon or _key(name) in names:
            raise DatasetError(f"Duplicate Digimon ID {species_id!r}")
        names[_key(name)] = species_id
        stats = {
            stat.lower(): _optional(row, stat)
            for stat in ("HP", "SP", "ATK", "DEF", "INT", "SPD")
            if _optional(row, stat)
        }
        digimon[species_id] = {
            "id": species_id,
            "name": name,
            "stage": _optional(row, "Stage"),
            "type": _optional(row, "Type"),
            "attribute": _optional(row, "Attribute"),
            "memory": _optional(row, "Memory"),
            "equip_slots": _optional(row, "Equip Slots", "EquipSlots"),
            "stats": stats,
            "stats_by_level": {
                str(level): {stat.lower(): _optional(row, f"{stat} lvl {level}")
                             for stat in ("HP", "SP", "ATK", "DEF", "INT", "SPD")
                             if _optional(row, f"{stat} lvl {level}")}
                for level in (1, 50, 99)
                if _optional(row, f"HP lvl {level}")
            },
            "skills": [],
            "digivolves_from": [],
            "digivolves_to": [],
            "requirements": [],
            "source": _public_row(row),
        }

    def species(value: str, table: str, row: dict[str, str]) -> str:
        result = names.get(_key(value))
        if result is None:
            raise DatasetError(
                f"{table} row {row.get('_source_row', '?')} references unknown Digimon {value!r}"
            )
        return result

    # A name identifies a skill group, not necessarily a unique definition.
    # Keep conflicting definitions explicit; consumers must resolve a variant.
    skills: dict[str, dict] = {}
    skill_names: dict[str, str] = {}
    issues = []
    corrections = []
    for row in tables["skills"]:
        name = _value(row, ("Skill", "Skill Name", "Name"), FILES["skills"])
        skill_id = _id(name)
        if _key(name) in skill_names and skill_names[_key(name)] != skill_id:
            raise DatasetError(f"Ambiguous normalized skill name {name!r}")
        skill_names[_key(name)] = skill_id
        source = _public_row(row)
        digest = hashlib.sha256(json.dumps(source, sort_keys=True).encode()).hexdigest()
        group = skills.setdefault(skill_id, {"id": skill_id, "name": name, "variants": []})
        variant = next((v for v in group["variants"] if v["source"] == source), None)
        if variant is None:
            variant = {"id": skill_id + "__" + digest, "source": source, "source_rows": []}
            group["variants"].append(variant)
        variant["source_rows"].append(int(row["_source_row"]))
    for skill in skills.values():
        skill["variants"].sort(key=lambda v: v["id"])
        skill["requires_variant_resolution"] = len(skill["variants"]) > 1
        if skill["requires_variant_resolution"]:
            issues.append({"kind": "ambiguous_skill", "skill": skill["id"],
                           "variants": [v["id"] for v in skill["variants"]]})

    for row in tables["skills_by_digimon"]:
        owner_name = _value(row, ("Digimon", "Digimon Name"), FILES["skills_by_digimon"])
        skill_name = _value(row, ("Skill", "Skill Name"), FILES["skills_by_digimon"])
        owner_id = species(owner_name, FILES["skills_by_digimon"], row)
        # Explicit dataset spelling correction; source rows remain intact.
        resolved_name = "Comet Hammer II" if skill_name == "Commet Hammer II" else skill_name
        if resolved_name != skill_name:
            corrections.append({"table": FILES["skills_by_digimon"],
                                "row": int(row["_source_row"]),
                                "original": skill_name, "resolved": resolved_name,
                                "reason": "Learnset typo; matching definition exists in Skills.csv"})
        skill_id = skill_names.get(_key(resolved_name))
        if skill_id is None:
            raise DatasetError(
                f"{FILES['skills_by_digimon']} row {row['_source_row']} references "
                f"unknown skill {skill_name!r}"
            )
        digimon[owner_id]["skills"].append(
            {"skill": skill_id, "level": _optional(row, "Level", "Level Learned"),
             "variant": skills[skill_id]["variants"][0]["id"]
                        if not skills[skill_id]["requires_variant_resolution"] else None,
             "source": _public_row(row)}
        )

    for row in tables["requirements"]:
        target_name = _value(
            row, ("Digimon", "Digimon To", "To Digimon", "Digivolution"), FILES["requirements"]
        )
        target_id = species(target_name, FILES["requirements"], row)
        digimon[target_id]["requirements"].append(
            _public_row(row, {"Digimon", "Digimon To", "To Digimon", "Digivolution"})
        )

    for row in tables["digivolutions"]:
        source_name = _value(
            row,
            ("Digimon From", "From Digimon", "Digivolves From", "From", "Source"),
            FILES["digivolutions"],
        )
        target_name = _value(
            row,
            ("Digimon To", "To Digimon", "Digivolves To", "To", "Target"),
            FILES["digivolutions"],
        )
        source_id = species(source_name, FILES["digivolutions"], row)
        if target_name == "N/A":
            continue
        target_id = species(target_name, FILES["digivolutions"], row)
        if source_id == target_id:
            raise DatasetError(f"Self-referencing digivolution at row {row['_source_row']}")
        digimon[source_id]["digivolves_to"].append(target_id)
        digimon[target_id]["digivolves_from"].append(source_id)

    for entry in digimon.values():
        entry["skills"].sort(key=lambda item: (int(item["level"] or 0), item["skill"]))
        entry["digivolves_from"] = sorted(set(entry["digivolves_from"]))
        entry["digivolves_to"] = sorted(set(entry["digivolves_to"]))

    return {
        "schema_version": 2,
        "source": {"dataset": "Digimon Cyber Sleuth Dataset", "url": DATASET_URL,
                   "download_date": None, "version": None,
                   "files": {filename: {"sha256": hashlib.sha256((input_dir / filename).read_bytes()).hexdigest(),
                                         "records": len(tables[key])}
                             for key, filename in FILES.items()}},
        "corrections": corrections,
        "issues": issues,
        "digimon": [digimon[key] for key in sorted(digimon)],
        "skills": [skills[key] for key in sorted(skills)],
    }


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--input", type=Path, required=True, help="directory containing all five CSVs")
    parser.add_argument("--output", type=Path, required=True, help="normalized JSON manifest")
    parser.add_argument("--roster", type=Path, help="optional curated line selection JSON")
    args = parser.parse_args(argv)
    try:
        manifest = build_manifest(args.input)
        if args.roster:
            manifest = select_roster(manifest, json.loads(args.roster.read_text(encoding="utf-8")))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n"
        )
    except (ValueError, OSError, csv.Error) as exc:
        print(f"error: {exc}", file=sys.stderr)
        return 1
    print(
        f"Wrote {len(manifest['digimon'])} Digimon and {len(manifest['skills'])} skills "
        f"to {args.output}"
    )
    return 0


def select_roster(manifest: dict, roster: dict) -> dict:
    """Derive a closed slice using only selected source edges, without inventing facts."""
    import copy

    entries = {entry["id"]: entry for entry in manifest["digimon"]}
    selected = set()
    edges = set()
    choices = set()
    if not roster.get("lines"):
        raise DatasetError("Roster must contain lines")
    for line in roster["lines"]:
        path = line["species"]
        choice = line["choice"]
        if choice in choices or choice not in path or len(set(path)) != len(path):
            raise DatasetError(f"Invalid or duplicate roster line: {choice}")
        choices.add(choice)
        for species_id in path:
            if species_id not in entries:
                raise DatasetError(f"Unknown roster species: {species_id}")
        for source, target in zip(path, path[1:]):
            if target not in entries[source]["digivolves_to"]:
                raise DatasetError(f"Roster edge absent from source: {source} -> {target}")
            edges.add((source, target))
        selected.update(path)
    result = copy.deepcopy(manifest)
    result["roster"] = copy.deepcopy(roster)
    result["digimon"] = [x for x in result["digimon"] if x["id"] in selected]
    skill_ids = set()
    for entry in result["digimon"]:
        entry["digivolves_to"] = sorted(b for a, b in edges if a == entry["id"])
        entry["digivolves_from"] = sorted(a for a, b in edges if b == entry["id"])
        for skill in entry["skills"]:
            if skill["variant"] is None:
                raise DatasetError(f"Unresolved skill variant for {entry['id']}: {skill['skill']}")
            skill_ids.add(skill["skill"])
    result["skills"] = [s for s in result["skills"] if s["id"] in skill_ids]
    result["issues"] = [i for i in result["issues"] if i.get("skill") in skill_ids]
    return result


if __name__ == "__main__":
    raise SystemExit(main())
