"""Config-driven, attested initial Idle candidates; legacy core.build is unchanged."""
from concurrent.futures import ThreadPoolExecutor, as_completed
import copy
import json
import math
import os
from pathlib import Path
import shutil
import time
from uuid import uuid4
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw

from .actions import _cache_matches, _render_chunk, _render_code_hash, _render_inputs
from .core import (DIRECTIONS, MARKER_COLORS, assemble_package, load_config,
                   read_glb_json, sha256, validate_package)


def _save(path, value):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(value, indent=2)+"\n", encoding="utf-8")


def idle_context(repo_root, config_path, model_path=None):
    config = load_config(config_path)
    if not isinstance(config.get("species"), str) or not config["species"]:
        raise ValueError("Idle config needs a species")
    if type(config.get("pmdo_index")) is not int or config["pmdo_index"] < 0:
        raise ValueError("Idle config needs a nonnegative PMDO index")
    if model_path is None and not config.get("model_path"):
        raise ValueError("Specify model_path in config or --model")
    model = (repo_root / (model_path or config["model_path"])).resolve()
    doc = read_glb_json(model)
    clip = next((c for c in doc.get("animations", []) if c.get("name") == config.get("idle_clip")), None)
    if clip is None:
        raise ValueError("Configured native Idle clip is missing")
    duration = max(doc["accessors"][s["input"]]["max"][0] for s in clip["samplers"])
    times = config["frame_times"]
    if len(times) < 2 or any(not math.isfinite(t) or not 0 <= t < duration for t in times):
        raise ValueError("Idle needs >=2 finite samples before the native loop endpoint")
    if times != sorted(set(times)):
        raise ValueError("Idle sample times must be strictly increasing")
    ticks = config.get("idle_duration_ticks", 8)
    if type(ticks) is not int or ticks <= 0:
        raise ValueError("idle_duration_ticks must be a positive integer")
    neutral = config.get("neutral_frame", 0)
    if type(neutral) is not int or not 0 <= neutral < len(times):
        raise ValueError("neutral_frame must be an Idle frame index")
    for key in ("frame_size", "render_size", "palette_size"):
        if type(config.get(key)) is not int or config[key] <= 0:
            raise ValueError(f"{key} must be a positive integer")
    if not 1 <= config.get("minimum_edge_margin", 2) < config["frame_size"]//2:
        raise ValueError("Invalid minimum_edge_margin")
    if config.get("idle_ground_policy", "per-frame") not in ("per-frame", "fixed"):
        raise ValueError("idle_ground_policy must be per-frame or fixed")
    renderer = config.get("renderer", {})
    if not (renderer.get("fixed_framing") or renderer.get("framing")):
        raise ValueError("Initial Idle requires fixed_framing or a fixed union framing sample set")
    if renderer.get("eye_mode") not in ("source", "forward-pupil"):
        raise ValueError("Specify inspected eye_mode explicitly")
    anchors = renderer.get("offset_bones", {})
    if set(anchors) != {"head", "center", "left_hand", "right_hand"} or config["offsets"]["source"] != "projected-native-bones-v1":
        raise ValueError("Initial Idle requires four explicit projected anatomical anchors")
    node_names = {n.get("name") for n in doc["nodes"]}
    for anchor in anchors.values():
        name = anchor if isinstance(anchor, str) else anchor.get("bone")
        if name not in node_names:
            raise ValueError(f"Missing anatomical anchor bone {name}")
        if not isinstance(anchor, str):
            point = anchor.get("local_point")
            if not isinstance(point, list) or len(point) != 3 or not all(math.isfinite(v) for v in point):
                raise ValueError("Body anchors require a finite local_point[3]")
    return config, model, duration


def validate_idle(repo_root, config, package):
    # Fixed ground policy preserves source vertical motion, unlike legacy
    # validation's strict per-frame ground snap. Shadow remains ground-fixed.
    check_config = copy.deepcopy(config)
    if config.get("idle_ground_policy") == "fixed":
        check_config.pop("ground_contact_row", None)
    result = validate_package(package, check_config)
    failures = result["failures"]
    size, count = config["frame_size"], config["idle_frames"]
    margin = config.get("minimum_edge_margin", 2)
    registry = [n.text for n in ET.parse(repo_root/"DumpAsset/Base/GFXParams.xml").findall("./Actions/Action/Name")]
    nodes = {n.findtext("Name"): n for n in ET.parse(package/"AnimData.xml").findall("./Anims/Anim")}
    for index, name in enumerate(registry):
        node = nodes.get(name)
        if node is None or node.findtext("Index") != str(index):
            failures.append(f"Invalid engine registry entry {name}")
        elif name != "Idle" and node.findtext("CopyOf") != "Idle":
            failures.append(f"Initial-only placeholder {name} must explicitly copy Idle")
    if [int(n.text) for n in nodes["Idle"].findall("./Durations/Duration")] != [config.get("idle_duration_ticks", 8)]*count:
        failures.append("Idle durations differ from config")
    frames, motion = [], []
    sheets = {k: Image.open(package/f"Idle-{k}.png").convert("RGBA") for k in ("Anim", "Offsets", "Shadow")}
    for row, direction in enumerate(DIRECTIONS):
        seen = set()
        for col in range(count):
            box = (col*size,row*size,(col+1)*size,(row+1)*size)
            frame = sheets["Anim"].crop(box); bounds = frame.getbbox()
            if not bounds:
                failures.append(f"{direction}/{col}: empty frame"); continue
            edge = min(bounds[0],bounds[1],size-bounds[2],size-bounds[3])
            if edge < margin: failures.append(f"{direction}/{col}: margin {edge} < {margin}")
            for kind, colors in (("Offsets", [MARKER_COLORS[k] for k in ("head","left_hand","center","right_hand")]), ("Shadow", [MARKER_COLORS["shadow"]])):
                pixels = list(sheets[kind].crop(box).getdata())
                if any(pixels.count(color) != 1 for color in colors): failures.append(f"{direction}/{col}: invalid {kind} marker multiplicity")
            if "ground_contact_row" in config:
                if sheets["Shadow"].getpixel((col*size+size//2,row*size+config["ground_contact_row"])) != MARKER_COLORS["shadow"]:
                    failures.append(f"{direction}/{col}: ground shadow moved")
            frames.append(dict(direction=direction,frame=col,bounds=bounds,height=bounds[3]-bounds[1],margin=edge))
            seen.add(frame.tobytes())
        motion.append(len(seen))
    if min(motion) < 2: failures.append(f"Idle motion collapsed in some directions: {motion}")
    target = config.get("approved_neutral_height")
    neutral = config.get("neutral_frame", 0)
    if target is not None and frames[neutral]["height"] != target:
        failures.append(f"Neutral Down height {frames[neutral]['height']} != approved {target}")
    result.update(ok=not failures,frame_checks=frames,unique_frames_by_direction=motion,
                  status="structural-only-pending-visual-review",placeholder_actions=len(registry)-1)
    return result


def idle_previews(config, package, output):
    size, count = config["frame_size"], config["idle_frames"]
    atlas = Image.open(package/"Idle-Anim.png").convert("RGBA")
    scale = 3
    sheet = Image.new("RGBA",(100+atlas.width*scale,30+atlas.height*scale),"#aeb3b1")
    sheet.alpha_composite(atlas.resize((atlas.width*scale,atlas.height*scale),Image.Resampling.NEAREST),(100,30))
    pen = ImageDraw.Draw(sheet)
    pen.text((5,7),f"{config.get('display_name',config['species'])} Idle | native scale unchanged | {size}px canvas",fill="black")
    for row,name in enumerate(DIRECTIONS): pen.text((5,40+row*size*scale),name,fill="black")
    sheet.convert("RGB").save(output/"contact-sheet.png")
    atlas.save(output/"native-sheet.png")
    offsets = Image.open(package/"Idle-Offsets.png").convert("RGBA")
    shadow = Image.open(package/"Idle-Shadow.png").convert("RGBA")
    marked = Image.alpha_composite(Image.alpha_composite(atlas,offsets),shadow)
    marked.resize((atlas.width*scale,atlas.height*scale),Image.Resampling.NEAREST).save(output/"offset-sheet.png")
    frames=[]
    for col in range(count):
        image=Image.new("RGBA",(4*size*2,2*size*2),"#aeb3b1")
        for row in range(8):
            frame=atlas.crop((col*size,row*size,(col+1)*size,(row+1)*size)).resize((size*2,size*2),Image.Resampling.NEAREST)
            image.alpha_composite(frame,((row%4)*size*2,(row//4)*size*2))
        frames.append(image.convert("RGB"))
    frames[0].save(output/"idle-playback.gif",save_all=True,append_images=frames[1:],
                   duration=round(config.get("idle_duration_ticks",8)*1000/60),loop=0)


def build_idle(repo_root, config_path, output_root, model_path=None, cache_root=None,
               workers=2, assemble_only=False):
    repo_root, output_root = Path(repo_root).resolve(), Path(output_root).resolve()
    config, model, duration = idle_context(repo_root, config_path, model_path)
    package = output_root/"package"/str(config["pmdo_index"])
    if (output_root/"package").exists() or (output_root/"output").exists():
        raise FileExistsError(f"Immutable candidate exists under: {output_root}")
    if output_root == repo_root/"work" or not output_root.is_relative_to(repo_root/"work"):
        raise ValueError("Initial candidate output must be inside lab work/")
    cache = (cache_root or output_root/"intermediate").resolve()
    if not cache.is_relative_to(repo_root/"work"):
        raise ValueError("Initial candidate cache must be inside lab work/")
    if not 1 <= workers <= 3: raise ValueError("workers must be 1..3")
    renderer = Path(__file__).resolve().parent/"renderer"
    signature = dict(model_hash=sha256(model),renderer_hash=sha256(renderer/"render.html"),
        capture_hash=sha256(renderer/"batch.mjs"),dependencies_hash=sha256(renderer/"pnpm-lock.yaml"),
        core_hash=_render_code_hash(Path(__file__).resolve().parent/"core.py"))
    jobs=[]
    for direction in config["directions"]:
        for col,seconds in enumerate(config["frame_times"]):
            expected=_render_inputs(**signature,clip=config["idle_clip"],seconds=seconds,
              azimuth=direction["azimuth_degrees"],render_size=config["render_size"],frame_size=config["frame_size"],
              settings=config["renderer"],direction=direction["name"])
            path=cache/direction["name"]/f"frame_{col:02d}.png"
            jobs.append((path,direction["azimuth_degrees"],seconds,config["idle_clip"],expected))
    pending=[job for job in jobs if not _cache_matches(job[0],job[4])]
    summary=dict(status="pending",species=config["species"],frames=len(jobs),cache_hits=len(jobs)-len(pending),
                 cache_misses=len(pending),browser_starts=0,completed_frames=len(jobs)-len(pending))
    output_root.mkdir(parents=True,exist_ok=True)
    started=time.perf_counter()
    stage=output_root/f".stage-{uuid4().hex}"
    try:
        _save(output_root/"summary.json",summary)
        if assemble_only and pending: raise ValueError(f"{len(pending)} frames lack exact cache")
        if pending:
            chunks=[pending[i::min(workers,len(pending))] for i in range(min(workers,len(pending)))]
            summary["browser_starts"]=len(chunks)
            with ThreadPoolExecutor(max_workers=len(chunks)) as pool:
                for future in as_completed([pool.submit(_render_chunk,model,renderer,config["renderer"],chunk) for chunk in chunks]): future.result()
        summary["completed_frames"]=len(jobs)
        staged=stage/str(config["pmdo_index"])
        assemble_package(config,cache,staged,gfx_params=repo_root/"DumpAsset/Base/GFXParams.xml",
                         ground_policy=config.get("idle_ground_policy","per-frame"))
        validation=validate_idle(repo_root,config,staged)
        _save(output_root/"validation.json",validation)
        if not validation["ok"]: raise ValueError("Idle structural validation failed; see validation.json")
        package.parent.mkdir(parents=True,exist_ok=True)
        os.replace(staged,package)
        validation["package_dir"]=str(package)
        _save(output_root/"validation.json",validation)
        idle_previews(config,package,output_root)
        summary.update(status="pending-parent-visual-review",package=str(package),elapsed_seconds=time.perf_counter()-started)
        _save(output_root/"provenance.json",dict(config=config,config_sha256=sha256(config_path),model_path=str(model),
              render_signature=signature,native_clip_duration=duration,
              package_hashes={p.name:sha256(p) for p in package.iterdir()},
              limitations=["Initial Idle only; all other XML actions explicitly CopyOf Idle placeholders.",
                           "Structural and native import are not independent visual or live-game approval."]))
        _save(output_root/"summary.json",summary)
        return {**summary,"validation":{"ok":True}}
    except Exception as error:
        summary.update(status="failed-resumable",error=str(error),elapsed_seconds=time.perf_counter()-started,
                       completed_frames=sum(_cache_matches(job[0],job[4]) for job in jobs))
        _save(output_root/"summary.json",summary)
        raise
    finally:
        if stage.exists() and stage.resolve().is_relative_to(output_root): shutil.rmtree(stage)
