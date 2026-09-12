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

# Enemy stage follows each spawn's own level, aligned with the source digivolution
# requirements (Rookie->Champion median level 14, Champion->Ultimate 28, Ultimate->Mega 55)
# so wild Digimon are never a full stage ahead of what the player can reach.
# Each tier lists (first level, lower stage, upper stage, upper share at tier start,
# upper share at tier end); the upper share rises linearly across the tier.
STAGE_TIERS = (
    (1, "Baby", "In-Training", 0.5, 0.5),
    (8, "In-Training", "Rookie", 0.6, 0.6),
    (14, "Rookie", "Champion", 0.2, 0.5),
    (28, "Champion", "Ultimate", 0.2, 0.5),
    (55, "Ultimate", "Mega", 0.2, 0.5),
)
EXCLUDED_SUFFIXES = ("_nx",)
# Hand-authored encounters that keep their species regardless of tier.
RETIER_EXEMPT_ZONES = ("tropical_path",)
RETIER_EXEMPT_SPECIES = {"guildmaster_island": ("monzaemon",)}


def stage_weights(level: int) -> dict[str, float]:
    """Stage probabilities for one enemy level."""
    tiers = list(STAGE_TIERS)
    for index, (start, lower, upper, share_start, share_end) in enumerate(tiers):
        end = tiers[index + 1][0] - 1 if index + 1 < len(tiers) else start + 20
        if level <= end or index + 1 == len(tiers):
            span = max(1, end - start)
            share = share_start + (share_end - share_start) * min(1.0, max(0, level - start) / span)
            return {lower: 1 - share, upper: share}
    raise AssertionError("unreachable")


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


def stage_pool(species: list[dict], level: int) -> list[dict]:
    """Every species eligible at this enemy level, in stable order."""
    stages = stage_weights(level)
    return [row for row in species if row["stage"] in stages and not row["id"].endswith(EXCLUDED_SUFFIXES)]


def stable_fraction(value: str) -> float:
    return int.from_bytes(hashlib.sha256(value.encode("utf-8")).digest()[8:16], "big") / 2 ** 64


def pick_species(species: list[dict], level: int, key: str) -> dict:
    """Deterministic weighted choice: stage by tier share, then a species within that stage."""
    weights = stage_weights(level)
    roll = stable_fraction(key + ":stage")
    chosen_stage = None
    for stage, weight in weights.items():
        if roll < weight or chosen_stage is None:
            chosen_stage = stage
            if roll < weight:
                break
        roll -= weight
    candidates = [row for row in stage_pool(species, level) if row["stage"] == chosen_stage]
    if not candidates:
        candidates = stage_pool(species, level)
    return candidates[stable_index(key + ":species", len(candidates))]


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


def exempt(node, zone_id: str, species_id: str) -> bool:
    if zone_id in RETIER_EXEMPT_ZONES or species_id in RETIER_EXEMPT_SPECIES.get(zone_id, ()):
        return True
    return "DigimonBoss" in str(node.get("LuaTable", ""))


def convert(node, *, zone_id: str, start_level: int, pool: list[dict], path: str = "") -> int:
    """Assign a tier-appropriate Digimon to every spawn.

    Pokemon spawns are always converted. Existing Digimon spawns are re-picked from the
    tier for their own level (a deterministic function of zone, path and level, so the
    result is stable across reruns) unless the encounter is hand-authored. ``pool`` holds
    every species record; the stage is selected per spawn, not per zone.
    """
    changed = 0
    if isinstance(node, dict):
        base = node.get("BaseForm")
        if isinstance(base, dict) and isinstance(base.get("Species"), str):
            old = base["Species"]
            level = encounter_level(node.get("Level"), start_level)
            if not exempt(node, zone_id, old):
                chosen = pick_species(pool, level, f"{zone_id}:{path}:{level}")
                base.update({"Species": chosen["id"], "Form": 0, "Skin": "normal", "Gender": -1})
                if "SpecifiedSkills" in node:
                    node["SpecifiedSkills"] = known_skills(chosen["id"], level)
                if "Intrinsic" in node:
                    # digimon_passive_abilities.py assigns the species passive afterwards.
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
        count = convert(data, zone_id=path.stem, start_level=level, pool=species)
        path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
        summary.append({"id": path.stem, "level": level, "digimon_encounter_records": count})
    out = ROOT / "DataAsset" / "Digimon" / "early_zone_manifest.json"
    out.write_text(json.dumps({"schema_version": 1, "zones": summary}, indent=2) + "\n", encoding="utf-8")
    print(f"Prepared {len(summary)} level 5-15 zones with {sum(x['digimon_encounter_records'] for x in summary)} Digimon encounter records.")


if __name__ == "__main__":
    main()
