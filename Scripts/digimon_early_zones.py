#!/usr/bin/env python3
"""Populate and release every dungeon whose configured entry level is 5-15."""

from __future__ import annotations

import hashlib
import json
import subprocess
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
ZONE_DIR = ROOT / "DumpAsset" / "Data" / "Zone"
MONSTER_DIR = ROOT / "DumpAsset" / "Data" / "Monster"

ALLOWED_STAGES = {
    5: ("Baby", "In-Training", "Rookie"),
    10: ("In-Training", "Rookie", "Champion"),
    15: ("Rookie", "Champion"),
}
EXCLUDED_SUFFIXES = ("_nx",)


def load(path: Path):
    return json.loads(path.read_text(encoding="utf-8-sig"))


def baseline_zone(zone_id: str):
    raw = subprocess.check_output(
        ["git", "-C", str(ROOT / "DumpAsset"), "show", f"HEAD:Data/Zone/{zone_id}.json"]
    )
    return json.loads(raw.decode("utf-8-sig"))


def restore_placement_ranges(current, baseline) -> None:
    """Restore placement geometry accidentally emptied when unavailable loot was removed."""
    if isinstance(current, dict) and isinstance(baseline, dict):
        for placement in ('ItemPlacements', 'TilePlacements', 'MobPlacements'):
            if placement in current and placement in baseline:
                nodes = current[placement].get('nodes', [])
                originals = baseline[placement].get('nodes', [])
                if not nodes:
                    current[placement] = baseline[placement]
                else:
                    for row in nodes:
                        if row.get('Item') is None:
                            match = next((r for r in originals if r['Range'] == row['Range']), None)
                            if match is not None:
                                row['Item'] = match['Item']
        for key in current.keys() & baseline.keys():
            restore_placement_ranges(current[key], baseline[key])
    elif isinstance(current, list) and isinstance(baseline, list):
        for left, right in zip(current, baseline):
            restore_placement_ranges(left, right)


def stable_index(value: str, size: int) -> int:
    return int.from_bytes(hashlib.sha256(value.encode("utf-8")).digest()[:8], "big") % size


def stage_pool(species: list[dict], start_level: int) -> list[dict]:
    stages = (ALLOWED_STAGES[5 if start_level <= 5 else 10 if start_level <= 10 else 15]
              if start_level <= 15 else ('Champion', 'Ultimate') if start_level < 35 else ('Ultimate', 'Mega'))
    return [row for row in species if row["stage"] in stages and not row["id"].endswith(EXCLUDED_SUFFIXES)]


def encounter_level(value, fallback: int) -> int:
    if isinstance(value, int):
        return value
    if isinstance(value, dict):
        for key in ("Min", "Max"):
            if isinstance(value.get(key), int):
                return value[key]
    return fallback


def known_skills(species_id: str, level: int) -> list[str]:
    monster = load(MONSTER_DIR / f"{species_id}.json")["Object"]
    skills = [row["Skill"] for row in monster["Forms"][0]["LevelSkills"] if row["Level"] <= level]
    return skills[-4:] or [monster["Forms"][0]["LevelSkills"][0]["Skill"]]


def convert(node, *, zone_id: str, start_level: int, pool: list[dict], path: str = "") -> int:
    changed = 0
    if isinstance(node, dict):
        base = node.get("BaseForm")
        if isinstance(base, dict) and isinstance(base.get("Species"), str):
            old = base["Species"]
            is_digimon = (MONSTER_DIR / f"{old}.json").exists() and load(MONSTER_DIR / f"{old}.json")["Object"].get("Comment") == "Digimon Phase 1"
            if not is_digimon:
                chosen = pool[stable_index(f"{zone_id}:{path}:{old}", len(pool))]
                base.update({"Species": chosen["id"], "Form": 0, "Skin": "normal", "Gender": -1})
                level = encounter_level(node.get("Level"), start_level)
                if "SpecifiedSkills" in node:
                    node["SpecifiedSkills"] = known_skills(chosen["id"], level)
                if "Intrinsic" in node:
                    node["Intrinsic"] = "none"
            changed += 1
        for key, value in node.items():
            changed += convert(value, zone_id=zone_id, start_level=start_level, pool=pool, path=f"{path}/{key}")
    elif isinstance(node, list):
        for index, value in enumerate(node):
            changed += convert(value, zone_id=zone_id, start_level=start_level, pool=pool, path=f"{path}/{index}")
    return changed


def main() -> None:
    gameplay = load(ROOT / "DataAsset" / "Digimon" / "phase2_gameplay.json")
    species = gameplay["species"]
    summary = []
    for path in sorted(ZONE_DIR.glob("*.json")):
        data = load(path)
        obj = data.get("Object", {})
        level = obj.get("Level")
        if not isinstance(level, int) or not 5 <= level <= 15:
            continue
        obj["Released"] = True
        restore_placement_ranges(data, baseline_zone(path.stem))
        count = convert(data, zone_id=path.stem, start_level=level, pool=stage_pool(species, level))
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        summary.append({"id": path.stem, "level": level, "digimon_encounter_records": count})
    out = ROOT / "DataAsset" / "Digimon" / "early_zone_manifest.json"
    out.write_text(json.dumps({"schema_version": 1, "zones": summary}, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(summary)} level 5-15 zones with {sum(x['digimon_encounter_records'] for x in summary)} Digimon encounter records.")


if __name__ == "__main__":
    main()
