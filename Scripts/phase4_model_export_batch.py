"""Bounded, resumable DSTS model exports for the Phase 4 roster.

Uses the same ``dsts_extractor export`` invocation as idle_stage_batch.py.
Only this helper's model-exports directory is written. Existing outputs are
validated and skipped; conflicting or damaged outputs are never replaced.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import os
from pathlib import Path
import re
import shutil
import struct
import subprocess
import sys
import tempfile


ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "DataAsset/Monster/digimon_manifest.json"
COVERAGE = Path(r"C:\Users\arlet\Documents\Codex\2026-09-23\b\outputs\digimon-size-census\conversion-model-coverage.json")
DATA_ROOT = ROOT / "work/phase4/dsts-data"
OUTPUT = ROOT / "work/phase4/model-exports"
PYTHON = ROOT / "venv/Scripts/python.exe"
MATCHES = {"direct", "name_alias", "normal_variant_fallback", "missing_model"}
MISSING_MODELS = {
    "alphamon_nx", "arcadiamon_champion", "arcadiamon_in_tr",
    "arcadiamon_mega", "arcadiamon_rookie", "arcadiamon_ultimate",
    "arcadiamon_ultra", "crusadermon_nx", "gallantmon_nx", "hudiemon",
    "leopardmon_nx", "omnimon_nx", "sistermon_b_awake",
    "sistermon_blanc", "sistermon_c_awake", "sistermon_ciel",
}
NORMAL_FALLBACKS = {
    "agumon_blk": "chr050", "blackwargreymon": "chr027",
    "gabumon_blk": "chr151", "garurumon_blk": "chr012",
    "greymon_blue": "chr326", "metalgarurumon_blk": "chr135",
    "metalgreymon_blue": "chr302", "weregarurumon_blk": "chr140",
}
# Audited from fresh dsts_extractor GLBs on 2026-09-28. These geometry source IDs
# embed animation names with a different chr prefix. This is an exact allowlist,
# not permission to accept an arbitrary prefix found in a GLB.
ANIMATION_PREFIX_ALIASES = {
    "chr043": "chr092",  # blackgatomon
    "chr753": "chr455",  # blackkingnumemon
    "chr177": "chr010",  # bluemeramon
    "chr150": "chr126",  # chaosgallantmon
    "chr054": "chr326",  # geogreymon
    "chr729": "chr070",  # geremon
    "chr402": "chr301",  # gigadramon
    "chr760": "chr341",  # guardromon_gold
    "chr730": "chr093",  # icedevimon
    "chr754": "chr425",  # kuzuhamon
    "chr750": "chr701",  # lopmon
    "chr434": "chr132",  # metalseadramon
    "chr756": "chr595",  # meteormon
    "chr759": "chr370",  # mudfrigimon
    "chr757": "chr088",  # omnimon_zwart
    "chr409": "chr072",  # panjyamon
    "chr069": "chr113",  # platinumnumemon
    "chr752": "chr313",  # platinumsukamon
    "chr751": "chr722",  # rapidmon_armor
    "chr347": "chr132",  # seadramon
    "chr755": "chr377",  # socerimon
    "chr728": "chr009",  # solarmon
}
SLUG = re.compile(r"[a-z0-9]+(?:_[a-z0-9]+)*\Z")
CHR = re.compile(r"chr\d{3,}\Z")


def load_json(path: Path) -> dict:
    return json.loads(path.read_text(encoding="utf-8-sig"))


def roster_and_coverage(coverage_path: Path) -> tuple[list[str], dict]:
    roster = [item["id"] for item in load_json(MANIFEST)["digimon"]]
    entries = load_json(coverage_path)["conversion_assignments"]
    assignments = {item["id"]: item for item in entries}
    if len(roster) != len(set(roster)) or len(entries) != len(assignments):
        raise ValueError("duplicate species in manifest or conversion coverage")
    if set(roster) != set(assignments):
        raise ValueError("manifest and conversion coverage species differ")
    for species, assignment in assignments.items():
        match = assignment.get("model_match")
        chr_id = assignment.get("source_chr_id")
        if not SLUG.fullmatch(species) or match not in MATCHES:
            raise ValueError(f"invalid species or model match: {species}")
        if match == "missing_model":
            if chr_id:
                raise ValueError(f"excluded species has a source: {species}")
        elif not isinstance(chr_id, str) or not CHR.fullmatch(chr_id):
            raise ValueError(f"missing or invalid chr ID for {species}: {chr_id}")
    actual_missing = {item["id"] for item in entries if item["model_match"] == "missing_model"}
    actual_fallbacks = {item["id"]: item["source_chr_id"] for item in entries
                        if item["model_match"] == "normal_variant_fallback"}
    if actual_missing != MISSING_MODELS:
        raise ValueError("coverage differs from the 16 approved missing-model exclusions")
    if actual_fallbacks != NORMAL_FALLBACKS:
        raise ValueError("coverage differs from the eight approved normal-model fallbacks")
    return roster, assignments


def validate_glb(path: Path, chr_id: str) -> dict:
    raw = path.read_bytes()
    if len(raw) < 28 or raw[:4] != b"glTF":
        raise ValueError("missing GLB header")
    version, declared_length = struct.unpack_from("<II", raw, 4)
    if version != 2 or declared_length != len(raw):
        raise ValueError("invalid GLB version or declared length")
    offset = 12
    chunks = []
    while offset < len(raw):
        if len(raw) - offset < 8:
            raise ValueError("truncated GLB chunk header")
        length, kind = struct.unpack_from("<I4s", raw, offset)
        offset += 8
        if length % 4 or offset + length > len(raw):
            raise ValueError("misaligned or truncated GLB chunk")
        chunks.append((kind, raw[offset:offset + length]))
        offset += length
    if not chunks or chunks[0][0] != b"JSON":
        raise ValueError("GLB JSON chunk missing")
    if len(chunks) < 2 or chunks[1][0] != b"BIN\0":
        raise ValueError("GLB binary chunk missing")
    doc = json.loads(chunks[0][1].decode("utf-8"))
    if doc.get("asset", {}).get("version") != "2.0":
        raise ValueError("not a glTF 2.0 asset")
    if not doc.get("scenes") or not doc.get("nodes") or not doc.get("meshes"):
        raise ValueError("GLB lacks scene, nodes, or meshes")
    buffers = doc.get("buffers", [])
    if len(buffers) != 1 or buffers[0].get("byteLength", 0) > len(chunks[1][1]):
        raise ValueError("GLB binary buffer is missing or incomplete")
    clips = [a.get("name", "") for a in doc.get("animations", [])]
    prefix = ANIMATION_PREFIX_ALIASES.get(chr_id, chr_id)
    if not clips or not any(isinstance(name, str) and name.startswith(prefix + "_")
                            for name in clips):
        raise ValueError(f"GLB has no expected {prefix} animation for {chr_id}")
    if prefix != chr_id and not all(isinstance(name, str) and
                                    (name == prefix or name.startswith(prefix + "_"))
                                    for name in clips):
        raise ValueError(f"GLB has unexpected animation prefix for {chr_id}; expected {prefix}")
    return {
        "sha256": hashlib.sha256(raw).hexdigest(),
        "bytes": len(raw),
        "meshes": len(doc["meshes"]),
        "animations": len(clips),
        "animation_prefix": prefix,
        "animation_prefix_alias": prefix != chr_id,
    }


def existing_model_index() -> dict[str, list[Path]]:
    """Find models already exported by earlier Phase 4 work."""
    index: dict[str, list[Path]] = {}
    phase4 = ROOT / "work/phase4"
    # Earlier jobs stored models in source/ or directly in their candidate or
    # preflight directories. Avoid walking large render-cache trees.
    paths = list((phase4 / "source").glob("*.glb"))
    paths.extend(phase4.glob("*-production/*/*.glb"))
    paths.extend(phase4.glob("*-production/*/*/*.glb"))
    for path in paths:
        index.setdefault(path.stem.replace("_", "-"), []).append(path)
    return index


def export_one(species: str, chr_id: str, timeout: int) -> dict:
    destination = OUTPUT / f"{species.replace('_', '-')}.glb"
    if destination.exists():
        try:
            details = validate_glb(destination, chr_id)
        except (OSError, ValueError, json.JSONDecodeError) as error:
            raise ValueError(f"existing output is invalid; refusing overwrite: {destination}: {error}") from error
        return {"species": species, "source_chr_id": chr_id, "status": "existing", **details}
    if not (DATA_ROOT / f"{chr_id}.geom").is_file() or not (DATA_ROOT / f"{chr_id}.nlst").is_file():
        raise FileNotFoundError(f"unpacked geometry or name list missing for {chr_id}")
    if not PYTHON.is_file():
        raise FileNotFoundError(f"lab extractor Python missing: {PYTHON}")
    OUTPUT.mkdir(parents=True, exist_ok=True)
    with tempfile.TemporaryDirectory(prefix=f".{species}-", dir=OUTPUT) as temporary:
        staged = Path(temporary) / destination.name
        command = [str(PYTHON), "-m", "dsts_extractor", "export", chr_id,
                   "--data-root", str(DATA_ROOT), "--out-dir", temporary,
                   "--name", destination.stem]
        environment = os.environ.copy()
        environment["PYTHONIOENCODING"] = "utf-8"
        result = subprocess.run(command, cwd=ROOT, env=environment, text=True,
                                capture_output=True, timeout=timeout, check=False)
        if result.returncode:
            raise RuntimeError(f"extractor exit {result.returncode}: {result.stderr[-1500:]}")
        if not staged.is_file():
            raise RuntimeError(f"extractor did not produce {staged.name}")
        details = validate_glb(staged, chr_id)
        # Exclusive creation prevents replacing an existing output even if
        # another batch process wrote it while this model was rendering.
        with staged.open("rb") as source, destination.open("xb") as target:
            shutil.copyfileobj(source, target, 1024 * 1024)
        try:
            validate_glb(destination, chr_id)
        except Exception:
            # Keep the published file for inspection; a later run refuses it.
            raise
    return {"species": species, "source_chr_id": chr_id,
            "status": "exported", **details}


def run(args: argparse.Namespace) -> int:
    roster, assignments = roster_and_coverage(args.coverage)
    prior_models = existing_model_index()
    requested = set(args.species or [])
    unknown = requested - set(roster)
    if unknown:
        raise ValueError(f"unknown species: {', '.join(sorted(unknown))}")
    selected = [name for name in roster if not requested or name in requested]
    excluded = [name for name in selected if assignments[name]["model_match"] == "missing_model"]
    pending = []
    existing = 0
    existing_elsewhere = 0
    conflicts = []
    for species in selected:
        assignment = assignments[species]
        if assignment["model_match"] == "missing_model":
            continue
        destination = OUTPUT / f"{species.replace('_', '-')}.glb"
        if destination.exists():
            try:
                validate_glb(destination, assignment["source_chr_id"])
                existing += 1
            except (OSError, ValueError, json.JSONDecodeError) as error:
                conflicts.append(f"{species}: {error}")
        else:
            earlier = prior_models.get(species.replace("_", "-"), [])
            if earlier:
                valid = False
                for path in earlier:
                    try:
                        validate_glb(path, assignment["source_chr_id"])
                        valid = True
                        break
                    except (OSError, ValueError, json.JSONDecodeError):
                        continue
                if valid:
                    existing_elsewhere += 1
                    continue
            pending.append(species)
    if conflicts:
        raise ValueError("invalid existing exports; refusing overwrite:\n" + "\n".join(conflicts))
    queue = pending[:args.limit]
    print(json.dumps({"selected": len(selected), "excluded": excluded,
                      "existing": existing, "existing_elsewhere": existing_elsewhere,
                      "pending": len(pending),
                      "queued": [{"species": name,
                                  "source_chr_id": assignments[name]["source_chr_id"],
                                  "animation_prefix": ANIMATION_PREFIX_ALIASES.get(
                                      assignments[name]["source_chr_id"],
                                      assignments[name]["source_chr_id"]),
                                  "model_match": assignments[name]["model_match"]}
                                 for name in queue], "dry_run": args.dry_run}, indent=2), flush=True)
    if args.dry_run:
        return 0
    failures = 0
    for species in queue:
        try:
            outcome = export_one(species, assignments[species]["source_chr_id"], args.timeout)
        except (OSError, ValueError, RuntimeError, subprocess.TimeoutExpired) as error:
            failures += 1
            outcome = {"species": species, "status": "failed", "error": str(error)}
        print(json.dumps(outcome), flush=True)
    return 1 if failures else 0


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--species", action="append", help="manifest species ID; repeatable")
    parser.add_argument("--limit", type=int, default=5, help="maximum new exports per run (default: 5)")
    parser.add_argument("--dry-run", action="store_true", help="show queue without writing")
    parser.add_argument("--coverage", type=Path, default=COVERAGE,
                        help="conversion-model-coverage.json from the Phase 4 census")
    parser.add_argument("--timeout", type=int, default=300, help="seconds allowed per export")
    args = parser.parse_args()
    if args.limit < 1 or args.timeout < 1:
        parser.error("--limit and --timeout must be positive")
    try:
        return run(args)
    except (OSError, ValueError, KeyError, json.JSONDecodeError) as error:
        parser.exit(2, f"error: {error}\n")


if __name__ == "__main__":
    sys.exit(main())
