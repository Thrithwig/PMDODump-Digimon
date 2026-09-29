"""Bounded renderer auditions and single-frame/persistent parity measurement."""
from __future__ import annotations

import json
from pathlib import Path
import time

from PIL import Image, ImageDraw

from .core import PersistentRenderer, inspect_glb, render_frame, sha256
from .actions import _cache_matches, _cache_record, _render_code_hash, _render_inputs


def _read_jobs(path: Path, model: Path, *, max_jobs: int = 16) -> list[dict]:
    data = json.loads(path.read_text(encoding="utf-8"))
    jobs = data.get("jobs")
    if not isinstance(jobs, list) or not 1 <= len(jobs) <= max_jobs:
        raise ValueError(f"jobs must contain 1..{max_jobs} requests")
    clips = set(inspect_glb(model)["animation_names"])
    for i, job in enumerate(jobs):
        if job.get("clip") not in clips:
            raise ValueError(f"jobs[{i}]: unknown native clip {job.get('clip')}")
        if not isinstance(job.get("azimuth"), (int, float)) or not isinstance(job.get("time"), (int, float)):
            raise ValueError(f"jobs[{i}]: azimuth and time must be numbers")
        if not 0 <= job["time"] < 1000:
            raise ValueError(f"jobs[{i}]: invalid sample time")
    return jobs


def _same_frame(left: Path, right: Path) -> dict:
    with Image.open(left) as image:
        a = image.convert("RGBA")
    with Image.open(right) as image:
        b = image.convert("RGBA")
    pixels_equal = a.size == b.size and a.tobytes() == b.tobytes()
    geometry_a = json.loads(left.with_suffix(".geometry.json").read_text(encoding="utf-8"))
    geometry_b = json.loads(right.with_suffix(".geometry.json").read_text(encoding="utf-8"))
    geometry_equal = geometry_a == geometry_b
    return {"pixels_equal": pixels_equal, "geometry_equal": geometry_equal,
            "old_png_sha256": sha256(left), "new_png_sha256": sha256(right),
            "old_geometry_sha256": sha256(left.with_suffix(".geometry.json")),
            "new_geometry_sha256": sha256(right.with_suffix(".geometry.json"))}


def benchmark(manifest: Path, model: Path, renderer: Path, output: Path,
              settings: dict, size: int, pixels: int,
              baseline_renderer: Path | None = None) -> dict:
    jobs = _read_jobs(manifest, model)
    output.mkdir(parents=True, exist_ok=True)
    old_start = time.perf_counter()
    for i, job in enumerate(jobs):
        render_frame(model, baseline_renderer or renderer, output / "old" / f"{i:02d}.png",
                     azimuth_degrees=job["azimuth"], time_seconds=job["time"],
                     clip_name=job["clip"], render_size=size, frame_size=pixels,
                     render_settings=settings)
    old_elapsed = time.perf_counter() - old_start
    new_start = time.perf_counter()
    with PersistentRenderer(model, renderer, settings) as worker:
        cold = time.perf_counter() - new_start
        for i, job in enumerate(jobs):
            worker.render(output / "new" / f"{i:02d}.png",
                          azimuth_degrees=job["azimuth"], time_seconds=job["time"],
                          clip_name=job["clip"], render_size=size, frame_size=pixels)
    new_elapsed = time.perf_counter() - new_start
    comparison = [_same_frame(output / "old" / f"{i:02d}.png", output / "new" / f"{i:02d}.png")
                  for i in range(len(jobs))]
    report = {"jobs": len(jobs), "old_seconds": old_elapsed,
              "new_seconds": new_elapsed, "new_startup_seconds": cold,
              "new_warm_seconds": new_elapsed-cold,
              "old_browser_starts": len(jobs), "new_browser_starts": 1,
              "old_model_loads": len(jobs), "new_model_loads": 1,
              "cache_hits": 0, "cache_misses": len(jobs)*2,
              "ratio_old_over_new": old_elapsed/new_elapsed,
              "parity": all(item["pixels_equal"] and item["geometry_equal"] for item in comparison),
              "comparison": comparison, "manifest": str(manifest), "model_sha256": sha256(model),
              "baseline_renderer": str(baseline_renderer or renderer),
              "baseline_renderer_sha256": sha256((baseline_renderer or renderer) / "render.html")}
    report["ok"] = report["parity"]
    (output / "benchmark.json").write_text(json.dumps(report, indent=2), encoding="utf-8")
    return report


def audition(manifest: Path, model: Path, renderer: Path, output: Path,
             settings: dict, size: int, pixels: int) -> dict:
    jobs = _read_jobs(manifest, model)
    output.mkdir(parents=True, exist_ok=True)
    hashes = {"model": sha256(model), "renderer": sha256(renderer / "render.html"),
              "capture": sha256(renderer / "batch.mjs"),
              "dependencies": sha256(renderer / "pnpm-lock.yaml"),
              "core": _render_code_hash(Path(__file__).with_name("core.py"))}
    hits = 0
    missing = []
    for i, job in enumerate(jobs):
        frame = output / "frames" / f"{i:02d}.png"
        inputs = _render_inputs(model_hash=hashes["model"], renderer_hash=hashes["renderer"],
                                capture_hash=hashes["capture"], core_hash=hashes["core"],
                                clip=job["clip"], seconds=job["time"], azimuth=job["azimuth"],
                                render_size=size, frame_size=pixels, settings=settings,
                                dependencies_hash=hashes["dependencies"])
        if _cache_matches(frame, inputs):
            hits += 1
        else:
            missing.append((frame, job, inputs))
    if missing:
        with PersistentRenderer(model, renderer, settings) as worker:
            for frame, job, inputs in missing:
                worker.render(frame, azimuth_degrees=job["azimuth"], time_seconds=job["time"],
                              clip_name=job["clip"], render_size=size, frame_size=pixels)
                _cache_record(frame).write_text(json.dumps({"inputs":inputs,"image_sha256":sha256(frame),
                    "geometry_sha256":sha256(frame.with_suffix(".geometry.json"))}), encoding="utf-8")
    width = min(4, len(jobs))
    sheet = Image.new("RGBA", (width*size, ((len(jobs)+width-1)//width)*(size+24)), "#252525")
    draw = ImageDraw.Draw(sheet)
    for i, job in enumerate(jobs):
        with Image.open(output / "frames" / f"{i:02d}.png") as frame:
            sheet.alpha_composite(frame.convert("RGBA"), ((i%width)*size, (i//width)*(size+24)))
        draw.text(((i%width)*size+4,(i//width)*(size+24)+size+3),
                  f"{i}: {job['clip']} t={job['time']} az={job['azimuth']}", fill="white")
    sheet.save(output / "contact-sheet.png")
    report = {"ok":True,"jobs":len(jobs),"cache_hits":hits,"cache_misses":len(missing),
              "browser_starts":int(bool(missing)), "model_loads":int(bool(missing)),
              "model_sha256":hashes["model"],"contact_sheet":str(output / "contact-sheet.png"),
              "status":"unreviewed", "jobs_metadata":jobs}
    (output / "audition.json").write_text(json.dumps(report,indent=2),encoding="utf-8")
    return report
