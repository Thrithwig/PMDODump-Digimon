"""Build configured PMDO actions while preserving an approved Idle baseline."""
from __future__ import annotations

import copy
from concurrent.futures import ThreadPoolExecutor, as_completed
import hashlib
import json
import os
from pathlib import Path
import shutil
import time
from uuid import uuid4
import xml.etree.ElementTree as ET

import numpy as np
from PIL import Image

from .core import (DIRECTIONS, assemble_package, inspect_glb, load_config,
                   PersistentRenderer, sha256)

FILES = ("Idle-Anim.png", "Idle-Offsets.png", "Idle-Shadow.png", "AnimData.xml")
MOUTH_COLORS = ((147, 52, 76), (248, 112, 143))


def _idle_signature(directory: Path) -> dict[str, str]:
    """Hash only the approved Idle data, not unrelated action XML."""
    root = ET.parse(directory / "AnimData.xml")
    idle = next(node for node in root.findall("./Anims/Anim")
                if node.findtext("Name") == "Idle")
    idle = copy.deepcopy(idle)
    idle.tail = None
    return {
        **{name: sha256(directory / name) for name in FILES[:3]},
        "Idle.xml": hashlib.sha256(ET.tostring(idle)).hexdigest(),
    }


def _render_inputs(*, model_hash: str, renderer_hash: str, capture_hash: str,
                   core_hash: str, clip: str, seconds: float, azimuth: float,
                   render_size: int, frame_size: int, settings: dict,
                   direction: str | None = None,
                   dependencies_hash: str | None = None) -> dict:
    return {
        "schema": 2, "model_sha256": model_hash,
        "renderer_sha256": renderer_hash, "capture_sha256": capture_hash,
        "core_sha256": core_hash, "clip": clip,
        "time_seconds_hex": float(seconds).hex(),
        "azimuth_degrees_hex": float(azimuth).hex(),
        "render_size": int(render_size), "frame_size": int(frame_size),
        "settings": settings,
        "direction": direction,
        "dependencies_sha256": dependencies_hash,
    }


def _cache_record(path: Path) -> Path:
    return path.with_suffix(".render-input.json")


def _cache_matches(path: Path, expected: dict) -> bool:
    geometry = path.with_suffix(".geometry.json")
    record = _cache_record(path)
    if not path.exists() or not geometry.exists() or not record.exists():
        return False
    try:
        saved = json.loads(record.read_text(encoding="utf-8"))
        details = json.loads(geometry.read_text(encoding="utf-8"))
        return (
            saved.get("inputs") == expected
            and saved.get("image_sha256") == sha256(path)
            and saved.get("geometry_sha256") == sha256(geometry)
            and details.get("framing", {}).get("clip") == expected["clip"]
            and (not expected["settings"].get("offset_bones") or
                 set(details.get("bonePoints", {})) == set(expected["settings"]["offset_bones"]))
        )
    except (ValueError, OSError, KeyError):
        return False


def _render_code_hash(core_path: Path) -> str:
    """Hash renderer plumbing, excluding palette/assembly/XML conversion code."""
    source = core_path.read_bytes()
    start = source.index(b"class _RendererHandler")
    end = source.index(b"def _binary_alpha", start)
    return hashlib.sha256(source[start:end]).hexdigest()


def _action_context(repo_root: Path, config_path: Path | None,
                    actions_path: Path | None) -> tuple[dict, dict, Path, Path, Path, Path | None]:
    config_path = config_path or repo_root / "config/phase4/agumon.json"
    actions_path = actions_path or repo_root / "config/phase4/agumon-actions.json"
    config = load_config(config_path)
    data = json.loads(actions_path.read_text(encoding="utf-8"))
    species = config["species"]
    if data.get("species") != species:
        raise ValueError(f"Action manifest species {data.get('species')} does not match {species}")
    if actions_path.name != "agumon-actions.json":
        for key in ("model_path", "approved_idle", "palette_policy", "mouth_palette"):
            if key not in data:
                raise ValueError(f"{species}: action manifest needs explicit {key}")
    if data.get("palette_policy", "approved-idle") not in ("approved-idle", "quantized"):
        raise ValueError("palette_policy must be approved-idle or quantized")
    pmdo_id = config["pmdo_index"]
    if not isinstance(pmdo_id, int) or pmdo_id < 0:
        raise ValueError("pmdo_index must be a nonnegative integer")
    monster_index = json.loads((repo_root / "DumpAsset/Data/Monster/index.idx").read_text(
        encoding="utf-8-sig"))["Object"]
    if species not in monster_index:
        raise KeyError(f"{species}: absent from PMDO Monster index")
    indexed_slot = int(monster_index[species]["SortOrder"])
    if pmdo_id != indexed_slot:
        raise ValueError(
            f"{species}: pmdo_index {pmdo_id} does not match Monster index {indexed_slot}"
        )
    specs = data.get("actions")
    if not isinstance(specs, list) or not specs:
        raise ValueError("actions must be a nonempty list")
    names = [item.get("name") for item in specs]
    if len(names) != len(set(names)) or any(not isinstance(name, str) for name in names):
        raise ValueError("actions need unique names")
    for spec in specs:
        count = len(spec.get("durations", []))
        if not count or any(not isinstance(v, int) or v <= 0 for v in spec["durations"]):
            raise ValueError(f"{spec['name']}: durations must be positive ticks")
        if len(spec.get("turn_degrees", [0] * count)) != count:
            raise ValueError(f"{spec['name']}: turn_degrees length must match durations")
        if spec.get("ground_policy") not in ("per-frame", "fixed"):
            raise ValueError(f"{spec['name']}: ground_policy must be per-frame or fixed")
        if type(spec.get("vertical_offset_px", 0)) is not int:
            raise ValueError(f"{spec['name']}: vertical_offset_px must be an integer")
        penetration = spec.get("max_shadow_penetration_px")
        if penetration is not None and (type(penetration) is not int or penetration < 0):
            raise ValueError(f"{spec['name']}: max_shadow_penetration_px must be a nonnegative integer")
        if any(not 0 <= v < count for v in spec.get("events", {}).values()):
            raise ValueError(f"{spec['name']}: event frame outside action")
    registry = [node.findtext("Name") for node in ET.parse(
        repo_root / "DumpAsset/Base/GFXParams.xml").findall("./Actions/Action")]
    unknown = set(names) - set(registry)
    if unknown:
        raise ValueError(f"Unknown PMDO engine actions: {sorted(unknown)}")
    model = repo_root / data.get("model_path", f"work/phase4/source/{species}.glb")
    if not model.is_file():
        raise FileNotFoundError(f"Model for {species} not found: {model}")
    baseline = repo_root / data["approved_idle"] if data.get("approved_idle") else None
    if baseline is None or any(not (baseline / name).exists() for name in FILES):
        raise ValueError(f"{species}: approved_idle must point to a complete Idle baseline")
    baseline_names = {node.findtext("Name") for node in ET.parse(baseline / "AnimData.xml").findall("./Anims/Anim")}
    absent = set(names) - baseline_names
    if absent:
        raise ValueError(f"{species}: baseline XML lacks actions {sorted(absent)}")
    installed = repo_root / data["installed_idle"] if data.get("installed_idle") else None
    if installed is None and actions_path.name == "agumon-actions.json":
        installed = repo_root / "DumpAsset/Content/DigimonSprite/10018"
    return config, data, model, baseline, actions_path, installed


def _render_chunk(model: Path, renderer: Path, settings: dict, jobs: list[tuple]) -> int:
    with PersistentRenderer(model, renderer, settings) as worker:
        for path, azimuth, seconds, clip, expected in jobs:
            worker.render(path, azimuth_degrees=azimuth, time_seconds=seconds,
                          clip_name=clip, render_size=expected["render_size"],
                          frame_size=expected["frame_size"])
            geometry = path.with_suffix(".geometry.json")
            _cache_record(path).write_text(json.dumps({
                "inputs": expected, "image_sha256": sha256(path),
                "geometry_sha256": sha256(geometry),
            }, sort_keys=True), encoding="utf-8")
    return len(jobs)


def _seconds(spec: dict, index: int, count: int) -> float:
    if "sample_phases" in spec:
        if len(spec["sample_phases"]) != count:
            raise ValueError(f"sample_phases must match frame count for {spec['name']}")
        return spec["seconds"] * spec["sample_phases"][index]
    if spec["name"] == "Walk":
        return spec["seconds"] * index / count
    cycle_count = int(spec.get("repeat_cycles", 1))
    phase_count = count // cycle_count
    phase_index = index % phase_count
    if spec["name"] == "Sleep":
        return spec["seconds"] * (0.35 + phase_index * 0.25)
    return spec["seconds"] * (0.03 + 0.92 * phase_index / max(1, phase_count - 1))


def _apply_idle_palette(path: Path, idle_path: Path,
                        mouth_colors: tuple = MOUTH_COLORS,
                        essential_colors: tuple = ((0,0,0),(255,255,255),(75,40,12))) -> None:
    with Image.open(idle_path) as idle:
        colors = sorted({pixel[:3] for pixel in idle.convert("RGBA").getdata() if pixel[3]})
    if (0, 0, 0) not in colors:
        raise ValueError("Approved Idle palette has no exact black")
    palette = np.array(colors, dtype=np.int16)
    with Image.open(path) as source:
        data = np.array(source.convert("RGBA"))
    opaque = data[:, :, 3] > 0
    mouth = np.zeros(opaque.shape, dtype=bool)
    for color in mouth_colors:
        mouth |= opaque & np.all(data[:, :, :3] == color, axis=2)
    body = opaque & ~mouth
    unique, inverse, frequencies = np.unique(data[body, :3], axis=0, return_inverse=True, return_counts=True)
    distances = ((unique[:, None, :].astype(np.int32) - palette[None, :, :].astype(np.int32)) ** 2).sum(axis=2)
    preliminary = np.argmin(distances, axis=1)
    usage = np.bincount(preliminary, weights=frequencies, minlength=len(palette))
    reserved = len([color for color in mouth_colors if np.any(opaque & np.all(data[:, :, :3] == color, axis=2))])
    limit = 64 - reserved
    essential = [i for i, color in enumerate(colors) if color in essential_colors]
    selected = list(dict.fromkeys(essential + list(np.argsort(-usage))))
    selected = selected[:limit]
    selected_palette = palette[selected]
    selected_distances = ((unique[:, None, :].astype(np.int32) - selected_palette[None, :, :].astype(np.int32)) ** 2).sum(axis=2)
    mapped = selected_palette[np.argmin(selected_distances, axis=1)][inverse].astype(np.uint8)
    black = np.all(data[body, :3] == 0, axis=1)
    mapped[black] = 0
    data[body, :3] = mapped
    data[~opaque, :3] = 0
    Image.fromarray(data, "RGBA").save(path)


def _write_xml(approved_xml: Path, output: Path, specs: list[dict], registry: Path,
               frame_size: int = 40) -> None:
    root = ET.parse(approved_xml).getroot()
    names = [node.findtext("Name") for node in ET.parse(registry).findall("./Actions/Action")]
    lookup = {node.findtext("Name"): node for node in root.findall("./Anims/Anim")}
    for spec in specs:
        name = spec["name"]
        if name not in lookup:
            raise ValueError(f"Approved XML lacks {name}")
        node = lookup[name]
        if node.findtext("Index") != str(names.index(name)):
            raise ValueError(f"GFXParams engine index mismatch for {name}")
        for child in list(node):
            if child.tag not in ("Name", "Index"):
                node.remove(child)
        for key, value in (("FrameWidth", frame_size), ("FrameHeight", frame_size)):
            ET.SubElement(node, key).text = str(value)
        for key in ("RushFrame", "HitFrame", "ReturnFrame"):
            if key in spec.get("events", {}):
                ET.SubElement(node, key).text = str(spec["events"][key])
        durations = ET.SubElement(node, "Durations")
        for value in spec["durations"]:
            ET.SubElement(durations, "Duration").text = str(value)
    ET.indent(root, space="  ")
    ET.ElementTree(root).write(output, encoding="utf-8", xml_declaration=True)


def build_actions(repo_root: Path, output_root: Path, only: set[str] | None = None,
                  assemble_only: bool = False, config_path: Path | None = None,
                  actions_path: Path | None = None, workers: int = 2,
                  cache_root: Path | None = None) -> dict:
    repo_root, output_root = repo_root.resolve(), output_root.resolve()
    protected = (repo_root / "work/phase4/agumon-actions").resolve()
    if output_root.is_relative_to(protected):
        raise ValueError("Reviewed Agumon package is immutable; use a new output root")
    config, action_data, model, approved, actions_path, installed = _action_context(
        repo_root, config_path, actions_path)
    package = output_root / "package" / str(config["pmdo_index"])
    if package.exists():
        raise FileExistsError(f"Candidate already exists: {package}; choose a new output root")
    cache_root = (cache_root or output_root / "intermediate").resolve()
    if cache_root.is_relative_to(protected):
        raise ValueError("Reviewed Agumon cache is read-only; use a new cache root")
    if actions_path.name == "agumon-actions.json" and config["species"] == "agumon":
        config["offsets"]["source"] = "projected-native-bones-v1"
        config.setdefault("renderer", {})["offset_bones"] = {
            "head": "J_head", "center": "J_center",
            "left_hand": "J_hand_l", "right_hand": "J_hand_r"}
    if set(config.get("renderer", {}).get("offset_bones", {})) != {"head", "center", "left_hand", "right_hand"}:
        raise ValueError("Production actions require four configured anatomical offset bones")
    all_specs = action_data["actions"]
    unknown = (only or set()) - {spec["name"] for spec in all_specs}
    if unknown:
        raise ValueError(f"Unknown actions: {sorted(unknown)}")
    specs = [spec for spec in all_specs if only is None or spec["name"] in only]
    if not specs:
        raise ValueError("No actions selected")
    source_hashes = {name: sha256(approved / name) for name in FILES}
    installed_hashes = {name: sha256(installed / name) for name in FILES} if installed else None
    if installed is not None and _idle_signature(approved) != _idle_signature(installed):
        raise ValueError("Installed Idle differs from approved baseline")
    clips = set(inspect_glb(model)["animation_names"])
    renderer = repo_root / "Scripts/SpritePipeline/renderer"
    hashes = {"model": sha256(model), "renderer": sha256(renderer / "render.html"),
              "capture": sha256(renderer / "batch.mjs"),
              "dependencies": sha256(renderer / "pnpm-lock.yaml"),
              "core": _render_code_hash(repo_root / "Scripts/SpritePipeline/core.py")}
    plans, pending = [], []
    for spec in specs:
        name, clip = spec["name"], spec["clip"]
        if clip not in clips:
            raise ValueError(f"Missing native clip {clip} for {name}")
        times = [_seconds(spec, i, len(spec["durations"])) for i in range(len(spec["durations"]))]
        if min(times) < 0 or max(times) > spec["seconds"]:
            raise ValueError(f"Samples exceed declared clip duration: {name}")
        frames = cache_root / name
        plans.append((spec, times, frames))
        for direction in config["directions"]:
            for i, seconds in enumerate(times):
                path = frames / direction["name"] / f"frame_{i:02d}.png"
                azimuth = (direction["azimuth_degrees"] + spec.get("turn_degrees", [0]*len(times))[i]) % 360
                expected = _render_inputs(
                    model_hash=hashes["model"], renderer_hash=hashes["renderer"],
                    capture_hash=hashes["capture"], core_hash=hashes["core"],
                    clip=clip, seconds=seconds, azimuth=azimuth,
                    render_size=config["render_size"], frame_size=config["frame_size"],
                    settings=config["renderer"], direction=direction["name"],
                    dependencies_hash=hashes["dependencies"])
                if not _cache_matches(path, expected):
                    pending.append((path, azimuth, seconds, clip, expected))
    total = sum(len(times)*len(DIRECTIONS) for _, times, _ in plans)
    summary = {"status": "pending", "species": config["species"], "pmdo_index": config["pmdo_index"],
               "actions": [spec["name"] for spec in specs], "frames": total,
               "cache_hits": total-len(pending), "cache_misses": len(pending),
               "browser_starts": 0, "completed_frames": total-len(pending)}
    output_root.mkdir(parents=True, exist_ok=True)
    def save_summary() -> None:
        (output_root / "summary.json").write_text(json.dumps(summary, indent=2), encoding="utf-8")
    save_summary()
    if assemble_only and pending:
        raise ValueError(f"{len(pending)} frames lack exact verified cache; first: {pending[0][0]}")
    if not 1 <= workers <= 3:
        raise ValueError("workers must be between 1 and 3")
    started = time.perf_counter()
    try:
        if pending:
            chunks = [[] for _ in range(min(workers, len(pending)))]
            for i, item in enumerate(pending):
                chunks[i % len(chunks)].append(item)
            summary["browser_starts"] = len(chunks)
            with ThreadPoolExecutor(max_workers=len(chunks)) as pool:
                futures = [pool.submit(_render_chunk, model, renderer, config["renderer"], chunk)
                           for chunk in chunks]
                for future in as_completed(futures):
                    future.result()
        summary["completed_frames"] = total
        stage_root = output_root / f".stage-{uuid4().hex}"
        stage_root.mkdir()
        try:
            staged = stage_root / str(config["pmdo_index"])
            staged.mkdir()
            for name in FILES[:3]:
                shutil.copy2(approved / name, staged / name)
            for spec, times, frames in plans:
                action_config = copy.deepcopy(config)
                action_config["idle_frames"] = len(times)
                action_config["frame_times"] = times
                action_config["mouth_palette"] = action_data.get("mouth_palette", config["species"] == "agumon")
                action_config["action_vertical_offset_px"] = spec.get("vertical_offset_px", 0)
                if "max_shadow_penetration_px" in spec:
                    action_config["max_shadow_penetration_px"] = spec["max_shadow_penetration_px"]
                if spec.get("closed_eyes"):
                    action_config["outline"]["closed_eyes"] = True
                assemble_package(action_config, frames, staged, action_name=spec["name"],
                                 emit_animdata=False, ground_policy=spec["ground_policy"])
                if action_data.get("palette_policy", "approved-idle") == "approved-idle":
                    mouth = tuple(tuple(color) for color in action_data.get(
                        "mouth_colors", MOUTH_COLORS if config["species"] == "agumon" else []))
                    essential = ((0,0,0),(255,255,255),(75,40,12)) if config["species"] == "agumon" else ((0,0,0),(255,255,255))
                    _apply_idle_palette(staged / f"{spec['name']}-Anim.png",
                                        approved / "Idle-Anim.png", mouth, essential)
            _write_xml(approved / "AnimData.xml", staged / "AnimData.xml", specs,
                       repo_root / "DumpAsset/Base/GFXParams.xml", config["frame_size"])
            if any(sha256(staged / name) != source_hashes[name] for name in FILES[:3]):
                raise ValueError("Approved Idle changed in candidate")
            if installed and any(sha256(installed / name) != installed_hashes[name] for name in FILES):
                raise ValueError("Installed Idle changed during build")
            package.parent.mkdir(parents=True, exist_ok=True)
            os.replace(staged, package)
        finally:
            if stage_root.resolve().is_relative_to(output_root):
                shutil.rmtree(stage_root)
        summary.update(status="complete-unreviewed", package=str(package),
                       elapsed_seconds=time.perf_counter()-started)
        save_summary()
        provenance = {**summary, "approved_idle_hashes": source_hashes,
                      "installed_idle_hashes": installed_hashes,
                      "model_sha256": hashes["model"], "actions_config_sha256": sha256(actions_path),
                      "reference": action_data.get("reference"),
                      "reference_commit": action_data.get("reference_commit"),
                      "reference_animdata_sha256": action_data.get("reference_animdata_sha256"),
                      "actions_detail": specs}
        (output_root / "provenance.json").write_text(json.dumps(provenance, indent=2), encoding="utf-8")
        return summary
    except Exception as error:
        summary.update(status="failed-resumable", error=str(error),
                       elapsed_seconds=time.perf_counter()-started)
        if pending:
            summary["browser_starts_planned"] = summary["browser_starts"]
            summary["browser_starts"] = None
        summary["completed_frames"] = total - sum(
            not _cache_matches(path, expected) for path, _, _, _, expected in pending)
        save_summary()
        raise


def validate_actions(repo_root: Path, output_root: Path,
                     config_path: Path | None = None,
                     actions_path: Path | None = None) -> dict:
    repo_root, output_root = repo_root.resolve(), output_root.resolve()
    config, data, _, approved, _, installed = _action_context(repo_root, config_path, actions_path)
    package = output_root / "package" / str(config["pmdo_index"])
    specs = data["actions"]
    summary_path = output_root / "summary.json"
    if summary_path.exists():
        selected = set(json.loads(summary_path.read_text(encoding="utf-8"))["actions"])
        specs = [spec for spec in specs if spec["name"] in selected]
    size = config["frame_size"]
    edge_margin = int(config.get("minimum_edge_margin", 1))
    if not 1 <= edge_margin < size // 2:
        raise ValueError("minimum_edge_margin must be positive and less than half the canvas")
    placement = config.get("placement", {})
    ground_row = config.get("ground_contact_row", placement.get("shadow_row"))
    mouth_colors = {tuple(c) for c in data.get("mouth_colors", MOUTH_COLORS if config["species"] == "agumon" else [])}
    open_mouth = set(data.get("open_mouth_actions", ("Attack", "Shoot", "Double", "Hop")
                              if config["species"] == "agumon" else ()))
    names = [node.findtext("Name") for node in ET.parse(repo_root / "DumpAsset/Base/GFXParams.xml").findall("./Actions/Action")]
    xml = ET.parse(package / "AnimData.xml")
    baseline = ET.parse(approved / "AnimData.xml")
    nodes = {n.findtext("Name"): n for n in xml.findall("./Anims/Anim")}
    failures = []
    for name in FILES[:3]:
        if sha256(package / name) != sha256(approved / name):
            failures.append(f"approved {name} changed in candidate")
    if installed:
        for name in FILES[:3]:
            if sha256(installed / name) != sha256(approved / name):
                failures.append(f"installed {name} differs from approved baseline")
        if _idle_signature(installed)["Idle.xml"] != _idle_signature(approved)["Idle.xml"]:
            failures.append("installed Idle XML element differs from approved baseline")
    baseline_idle = next(n for n in baseline.findall("./Anims/Anim") if n.findtext("Name") == "Idle")
    if ET.tostring(nodes["Idle"]) != ET.tostring(baseline_idle):
        failures.append("approved Idle XML element changed")
    with Image.open(approved / "Idle-Anim.png") as idle:
        palette = {p[:3] for p in idle.convert("RGBA").getdata() if p[3]}
        # Action canvases may add padding while the approved Idle stays intact.
        idle_size = int(baseline_idle.findtext("FrameWidth"))
        idle_height = int(baseline_idle.findtext("FrameHeight"))
        idle_count = idle.width // idle_size
        idle_frames = [idle.convert("RGBA").crop((i*idle_size, row*idle_height, (i+1)*idle_size, (row+1)*idle_height)).tobytes()
                       for row in range(8) for i in range(idle_count)]
    shared_colors = set(palette)
    results = {}
    for spec in specs:
        name = spec["name"]
        node = nodes.get(name)
        count = len(spec["durations"])
        issues = []
        if node is None:
            issues.append("missing XML action")
        else:
            if node.findtext("Index") != str(names.index(name)):
                issues.append("engine index mismatch")
            if node.find("CopyOf") is not None:
                issues.append("action still copies another animation")
            if [int(n.text) for n in node.findall("./Durations/Duration")] != spec["durations"]:
                issues.append("durations mismatch")
            if node.findtext("FrameWidth") != str(size) or node.findtext("FrameHeight") != str(size):
                issues.append("frame dimensions mismatch")
            for event in ("RushFrame","HitFrame","ReturnFrame"):
                value = node.findtext(event)
                expected = spec.get("events", {}).get(event)
                if (int(value) if value is not None else None) != expected:
                    issues.append(f"{event} mismatch")
                if value is not None and not 0 <= int(value) < count:
                    issues.append(f"{event} out of bounds")
        images = {}
        for kind in ("Anim","Offsets","Shadow"):
            path = package / f"{name}-{kind}.png"
            if not path.exists():
                issues.append(f"missing {kind} sheet")
                continue
            images[kind] = Image.open(path).convert("RGBA")
            if images[kind].size != (count*size, 8*size):
                issues.append(f"{kind} sheet dimensions mismatch")
        if len(images) == 3 and all(image.size == (count*size,8*size) for image in images.values()):
            seen_motion = []
            gaps = []
            for row in range(8):
                pixels = []
                for col in range(count):
                    box = (col*size,row*size,(col+1)*size,(row+1)*size)
                    frame = images["Anim"].crop(box)
                    alpha = frame.getchannel("A")
                    alphas = set(alpha.getdata())
                    if alphas != {0,255}:
                        issues.append(f"{DIRECTIONS[row]} frame {col}: alpha is not binary/transparent")
                    if any(alpha.crop(edge).getbbox() for edge in [(0,0,size,edge_margin),(0,size-edge_margin,size,size),(0,0,edge_margin,size),(size-edge_margin,0,size,size)]):
                        issues.append(f"{DIRECTIONS[row]} frame {col}: violates {edge_margin}px sheet edge margin")
                    if data.get("palette_policy", "approved-idle") == "approved-idle" and not {p[:3] for p in frame.getdata() if p[3]}.issubset(palette | mouth_colors):
                        issues.append(f"{DIRECTIONS[row]} frame {col}: undocumented action color")
                    if frame.tobytes() in idle_frames:
                        issues.append(f"{DIRECTIONS[row]} frame {col}: exact Idle clone")
                    offset = images["Offsets"].crop(box)
                    marker_counts = {color: list(offset.getdata()).count(color) for color in
                                     [(0,0,0,255),(255,0,0,255),(0,255,0,255),(0,0,255,255)]}
                    if any(value != 1 for value in marker_counts.values()):
                        issues.append(f"{DIRECTIONS[row]} frame {col}: offset marker count")
                    shadow = images["Shadow"].crop(box)
                    if list(shadow.getdata()).count((255,255,255,255)) != 1 or (config["species"] == "agumon" and shadow.getpixel((20,32)) != (255,255,255,255)):
                        issues.append(f"{DIRECTIONS[row]} frame {col}: shadow marker")
                    bounds = alpha.getbbox()
                    if bounds:
                        gap = (ground_row if ground_row is not None else size-1) - (bounds[3]-1)
                        gaps.append(gap)
                        expected_gap = -int(spec.get("vertical_offset_px", 0))
                        if ("ground_contact_row" in config and spec["ground_policy"] == "per-frame"
                                and gap != expected_gap):
                            issues.append(
                                f"{DIRECTIONS[row]} frame {col}: ground gap {gap}, expected {expected_gap}")
                        max_penetration = spec.get("max_shadow_penetration_px")
                        if max_penetration is not None and gap < -int(max_penetration):
                            issues.append(
                                f"{DIRECTIONS[row]} frame {col}: shadow penetration {-gap} exceeds {max_penetration}")
                        if placement.get("mode") == "airborne":
                            if gap < placement["minimum_gap"]:
                                issues.append(f"{DIRECTIONS[row]} frame {col}: airborne gap {gap}")
                            if shadow.getpixel((size//2,ground_row)) != (255,255,255,255):
                                issues.append(f"{DIRECTIONS[row]} frame {col}: airborne shadow moved")
                    pixels.append(frame.tobytes())
                seen_motion.append(len(set(pixels)))
            opaque_colors = {p[:3] for p in images["Anim"].getdata() if p[3]}
            shared_colors.update(opaque_colors)
            if len(opaque_colors) > config.get("palette_size", 64):
                issues.append(f"{len(opaque_colors)} opaque colors exceed {config.get('palette_size',64)}")
            if name in open_mouth and not (opaque_colors & mouth_colors):
                issues.append("native open-mouth color missing")
            if min(seen_motion) < 2:
                issues.append(f"no visible motion in some directions: {seen_motion}")
            if name == "Hop" and config["species"] == "agumon":
                if max(gaps) < 2:
                    issues.append(f"no airborne arc: {gaps}")
                if gaps[0] != 0:
                    issues.append("Hop does not begin on ground")
            results[name] = {"ok":not issues,"failures":issues,"unique_frames_by_direction":seen_motion,
                             "ground_gaps":gaps if name == "Hop" else None,
                             "opaque_palette_count":len(opaque_colors),
                             "native_mouth_colors_present":[list(c) for c in mouth_colors if c in opaque_colors]}
        else:
            results[name] = {"ok":False,"failures":issues}
        failures.extend(f"{name}: {issue}" for issue in issues)
    report = {"ok":not failures,"failures":failures,"actions":results,"package":str(package),
              "shared_palette_union_count":len(shared_colors),
              "status":"structural-only-unreviewed"}
    (output_root / "validation.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report
