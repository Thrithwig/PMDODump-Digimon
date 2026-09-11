#!/usr/bin/env python3
"""Compile the selected Digimon source manifest plus explicit PMDO balance rules.

This is a validated gameplay-data contract, not a runtime implementation. Never
rewrites the normalized source manifest or translates unrecognized conditions.
"""
from __future__ import annotations

import argparse
import copy
from fractions import Fraction
import hashlib
import json
from pathlib import Path
import re
import sys


class BalanceError(ValueError):
    """Input cannot be faithfully compiled into the supported Phase 1 contract."""


SOURCE_STATS = {"hp", "sp", "atk", "def", "int", "spd"}
OUTPUT_STATS = {"max_hp", "attack", "defense", "magic_attack", "magic_defense", "speed", "source_sp"}


def integer(value, label, minimum=0, maximum=None):
    if isinstance(value, bool) or not re.fullmatch(r"[0-9]+", str(value)):
        raise BalanceError(f"{label}: expected an integer, got {value!r}")
    result = int(value)
    if result < minimum or (maximum is not None and result > maximum):
        raise BalanceError(f"{label}: outside allowed range")
    return result


def canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, separators=(",", ":")).encode("utf-8")


def require_keys(value, keys, label):
    if not isinstance(value, dict) or set(value) != set(keys):
        raise BalanceError(f"{label}: expected keys {sorted(keys)}")


def validate_overlay(overlay):
    require_keys(overlay, {"schema_version", "balance_version", "status", "level", "stats",
                           "requirement_stats", "progression", "scan"}, "overlay")
    if overlay["schema_version"] != 1 or not isinstance(overlay["balance_version"], str) or not overlay["balance_version"]:
        raise BalanceError("Unsupported overlay schema or missing balance version")
    require_keys(overlay["level"], {"start", "maximum"}, "level")
    maximum = integer(overlay["level"]["maximum"], "maximum level", 1, 99)
    integer(overlay["level"]["start"], "start level", 1, maximum)
    require_keys(overlay["stats"], OUTPUT_STATS, "stats")
    for stat, rule in overlay["stats"].items():
        require_keys(rule, {"source", "numerator", "denominator", "offset"}, stat)
        if rule["source"] not in SOURCE_STATS:
            raise BalanceError(f"Unknown source stat for {stat}")
        for field in ("numerator", "denominator"):
            integer(rule[field], f"{stat}.{field}", 1)
        integer(rule["offset"], f"{stat}.offset")
    require_keys(overlay["requirement_stats"], {s.upper() for s in SOURCE_STATS}, "requirement_stats")
    for source, stat in overlay["requirement_stats"].items():
        if stat not in OUTPUT_STATS or overlay["stats"][stat]["source"] != source.lower():
            raise BalanceError(f"Requirement {source} must map to a stat derived from the same source")
    progression = overlay["progression"]
    require_keys(progression, {"bond", "training", "transitions"}, "progression")
    for name, gain_field in (("bond", "per_eligible_defeat"), ("training", "per_new_highest_level")):
        rule = progression[name]
        require_keys(rule, {"initial", "maximum", gain_field}, name)
        cap = integer(rule["maximum"], f"{name}.maximum", 1, 200 if name == "training" else 100)
        integer(rule["initial"], f"{name}.initial", 0, cap)
        integer(rule[gain_field], f"{name}.{gain_field}", 1)
    if progression["transitions"] != {"hub_only": True, "preserve_level": True, "costs": [], "dedigivolution": {"reset_level": 1, "levels_per_stat_bonus": 10, "levels_per_abi": 5, "maximum_stat_bonus": 256}}:
        raise BalanceError("Phase 1 transitions require the explicit hub and dedigivolution training policy")
    scan = overlay["scan"]
    require_keys(scan, {"points_per_defeat", "unlock_threshold", "points_per_species_per_floor",
                        "overflow_bits_per_point", "restoration_level", "restoration_requires_digicode",
                        "direct_recruitment", "excluded_sources", "restoration_levels_per_threshold", "restoration_maximum_level"}, "scan")
    for field in ("points_per_defeat", "unlock_threshold", "points_per_species_per_floor"):
        integer(scan[field], f"scan.{field}", 1)
    integer(scan["overflow_bits_per_point"], "scan.overflow_bits_per_point", 0, 0)
    integer(scan["restoration_levels_per_threshold"], "scan.restoration_levels_per_threshold", 1)
    integer(scan["restoration_maximum_level"], "scan.restoration_maximum_level", 1, maximum)
    integer(scan["restoration_level"], "scan.restoration_level", 1, maximum)
    if scan["restoration_level"] != overlay["level"]["start"]:
        raise BalanceError("Restoration and starting level must match the progression reachability model")
    if scan["direct_recruitment"] is not False or scan["restoration_requires_digicode"] is not True:
        raise BalanceError("Recruitment must require DigiCode restoration")
    excluded = ["summon", "illusion", "friendly", "neutral", "pvp_ghost", "scripted_defeat"]
    if sorted(scan["excluded_sources"]) != sorted(excluded):
        raise BalanceError("Scan source exclusions must be explicit and complete")


def scaled(value, rule):
    """Positive rational scaling, round half up, then clamp to a minimum of one."""
    result = Fraction(value) * rule["numerator"] / rule["denominator"] + rule["offset"]
    return max(1, (2 * result.numerator + result.denominator) // (2 * result.denominator))


def source_at_level(anchors, stat, level):
    if not 1 <= level <= 99:
        raise BalanceError("Source interpolation supports levels 1 through 99")
    low, high = (1, 50) if level <= 50 else (50, 99)
    left, right = anchors[str(low)][stat], anchors[str(high)][stat]
    return Fraction(left) + Fraction((right - left) * (level - low), high - low)


def compile_conditions(entry, overlay):
    if len(entry["requirements"]) != 1:
        raise BalanceError(f"{entry['id']}: expected exactly one source requirement row")
    conditions = []
    for key, value in entry["requirements"][0].items():
        if key == "Number":
            continue
        if key == "Extra Condition":
            if value == "Starter digimon" and not entry["digivolves_from"]:
                continue
            raise BalanceError(f"{entry['id']}: unsupported source condition {value!r}")
        if key == "CAM":
            if not re.fullmatch(r"\d+%", value):
                raise BalanceError(f"{entry['id']}: invalid CAM percentage")
            minimum = integer(value[:-1], "CAM", maximum=100)
            kind, stat = "bond", None
        elif key == "ABI":
            minimum = integer(value, "ABI", maximum=overlay["progression"]["training"]["maximum"])
            kind, stat = "training", None
        elif key == "Level":
            minimum = integer(value, "Level", maximum=overlay["level"]["maximum"])
            kind, stat = "level", None
        elif key in overlay["requirement_stats"]:
            stat = overlay["requirement_stats"][key]
            minimum = scaled(integer(value, key), overlay["stats"][stat])
            kind = "stat"
        else:
            raise BalanceError(f"{entry['id']}: unsupported requirement column {key!r}")
        if minimum:
            condition = {"kind": kind, "minimum": minimum, "source_field": key, "source_value": value}
            if stat:
                condition["stat"] = stat
            conditions.append(condition)
    return sorted(conditions, key=lambda c: (c["kind"], c.get("stat", "")))


def preview(conditions, level, stats, bond, training):
    """Pure requirement evaluation for validation/preview; never changes game state."""
    rows = []
    for condition in conditions:
        kind = condition["kind"]
        actual = stats[condition["stat"]] if kind == "stat" else {
            "level": level, "bond": bond, "training": training}[kind]
        label = condition.get("stat", kind).replace("_", " ").capitalize()
        rows.append({**condition, "current": actual, "met": actual >= condition["minimum"],
                     "text": f"{label}: {actual}/{condition['minimum']}"})
    return {"eligible": all(row["met"] for row in rows), "requirements": rows}


def build_catalog(manifest, overlay):
    validate_overlay(overlay)
    if manifest.get("schema_version") != 2 or manifest.get("issues"):
        raise BalanceError("A resolved schema-2 roster manifest is required")
    entries = {x["id"]: x for x in manifest["digimon"]}
    if not entries or len(entries) != len(manifest["digimon"]):
        raise BalanceError("Empty roster or duplicate species IDs")
    choices = [line["choice"] for line in manifest["roster"]["lines"]]
    if len(set(choices)) != len(choices) or any(choice not in entries for choice in choices):
        raise BalanceError("Invalid roster choices")
    max_level = overlay["level"]["maximum"]
    start_level = overlay["level"]["start"]
    species = {}
    for species_id, entry in sorted(entries.items()):
        anchors = entry["stats_by_level"]
        require_keys(anchors, {"1", "50", "99"}, f"{species_id} stat anchors")
        parsed = {}
        for level, values in anchors.items():
            require_keys(values, SOURCE_STATS, f"{species_id} stats at {level}")
            parsed[level] = {stat: integer(value, f"{species_id}.{stat}", 1) for stat, value in values.items()}
        for stat in SOURCE_STATS:
            if not parsed["1"][stat] <= parsed["50"][stat] <= parsed["99"][stat]:
                raise BalanceError(f"{species_id}.{stat}: decreasing source anchors")
        curves = [{"level": level, "stats": {
            stat: scaled(source_at_level(parsed, rule["source"], level), rule)
            for stat, rule in overlay["stats"].items()}}
            for level in range(1, max_level + 1)]
        species[species_id] = {"id": species_id, "name": entry["name"], "stage": entry["stage"],
                               "source_manifest_id": species_id, "stats_by_level": curves,
                               "scan": copy.deepcopy(overlay["scan"])}
    # Validate all rows, including roots; do not quietly drop unsupported conditions.
    conditions = {key: compile_conditions(entry, overlay) for key, entry in entries.items()}
    transitions = []
    reachability = []
    training = overlay["progression"]["training"]
    bond = overlay["progression"]["bond"]
    for source_id, entry in sorted(entries.items()):
        if len(set(entry["digivolves_to"])) != len(entry["digivolves_to"]):
            raise BalanceError(f"Duplicate outgoing edge for {source_id}")
        for parent in entry["digivolves_from"]:
            if parent not in entries or source_id not in entries[parent]["digivolves_to"]:
                raise BalanceError(f"Broken reverse edge: {parent} -> {source_id}")
        for target_id in sorted(entry["digivolves_to"]):
            if target_id == source_id or target_id not in entries or source_id not in entries[target_id]["digivolves_from"]:
                raise BalanceError(f"Broken forward edge: {source_id} -> {target_id}")
            required = conditions[target_id]
            earliest = None
            for row in species[source_id]["stats_by_level"]:
                level = row["level"]
                if level < start_level:
                    continue
                available_training = min(training["maximum"], training["initial"] +
                                         (level - start_level) * training["per_new_highest_level"])
                if preview(required, level, row["stats"], bond["maximum"], available_training)["eligible"]:
                    earliest = level
                    break
            if earliest is None:
                raise BalanceError(f"Unreachable selected transition: {source_id} -> {target_id}")
            needed_bond = max([c["minimum"] for c in required if c["kind"] == "bond"] + [0])
            gap = max(0, needed_bond - bond["initial"])
            reachability.append({"from": source_id, "to": target_id, "earliest_level_with_sufficient_bond": earliest,
                                 "eligible_defeats_for_bond_from_initial":
                                 (gap + bond["per_eligible_defeat"] - 1) // bond["per_eligible_defeat"]})
            for a, b, direction, reqs in ((source_id, target_id, "digivolve", required),
                                          (target_id, source_id, "dedigivolve", [])):
                transitions.append({"id": f"{a}__to__{b}", "from": a, "to": b, "direction": direction,
                                    "requirements": copy.deepcopy(reqs),
                                    **copy.deepcopy(overlay["progression"]["transitions"])})
                transitions[-1]["preserve_level"] = direction == "digivolve"
    ids = [edge["id"] for edge in transitions]
    if len(ids) != len(set(ids)):
        raise BalanceError("Selected source graph has conflicting forward/reverse transitions")
    return {"schema_version": 1, "status": "data_contract_not_runtime_enabled",
            "balance_version": overlay["balance_version"],
            "inputs": {"manifest_sha256": hashlib.sha256(canonical(manifest)).hexdigest(),
                       "overlay_sha256": hashlib.sha256(canonical(overlay)).hexdigest()},
            "policies": copy.deepcopy(overlay),
            "starters": [{"species": choice, "level": start_level,
                          "stage": entries[choice]["stage"],
                          "stats": species[choice]["stats_by_level"][start_level - 1]["stats"]}
                         for choice in choices],
            "species": list(species.values()),
            "transitions": sorted(transitions, key=lambda edge: edge["id"]),
            "reachability": reachability}


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--overlay", required=True, type=Path)
    parser.add_argument("--output", required=True, type=Path)
    args = parser.parse_args(argv)
    try:
        if args.output.resolve() in {args.manifest.resolve(), args.overlay.resolve()}:
            raise BalanceError("Output must not overwrite source inputs")
        result = build_catalog(json.loads(args.manifest.read_text(encoding="utf-8")),
                               json.loads(args.overlay.read_text(encoding="utf-8")))
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(json.dumps(result, ensure_ascii=False, indent=2) + "\n", encoding="utf-8", newline="\n")
    except (ValueError, KeyError, TypeError, OSError) as error:
        print(f"error: {error}", file=sys.stderr)
        return 1
    print(f"Wrote {len(result['species'])} forms and {len(result['transitions'])} transitions to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
