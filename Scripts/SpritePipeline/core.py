"""Core rendering, conversion, assembly, and validation helpers.

The module deliberately keeps the PMDO-facing part independent from the
proprietary DSTS data. The only input needed by the renderer is the exported
GLB path, while all output is deterministic from the checked-in config.
"""

from __future__ import annotations

import hashlib
import json
import math
import os
import queue
from pathlib import Path
import shutil
import signal
import subprocess
import tempfile
import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from typing import Any, Iterable
from urllib.parse import urlparse
import xml.etree.ElementTree as ET

from PIL import Image, ImageDraw
import numpy as np


DIRECTIONS = [
    "Down",
    "DownRight",
    "Right",
    "UpRight",
    "Up",
    "UpLeft",
    "Left",
    "DownLeft",
]

MARKER_COLORS = {
    "head": (0, 0, 0, 255),
    "left_hand": (255, 0, 0, 255),
    "center": (0, 255, 0, 255),
    "right_hand": (0, 0, 255, 255),
    "shadow": (255, 255, 255, 255),
}


def load_config(path: Path) -> dict[str, Any]:
    with path.open("r", encoding="utf-8") as handle:
        config = json.load(handle)
    names = [item["name"] for item in config["directions"]]
    if names != DIRECTIONS:
        raise ValueError(f"direction order must be {DIRECTIONS}, got {names}")
    if len(config["frame_times"]) != config["idle_frames"]:
        raise ValueError("frame_times must contain idle_frames entries")
    if config.get("placement", {}).get("mode") == "airborne" and "ground_contact_row" in config:
        raise ValueError("Airborne placement cannot also snap feet to ground")
    return config


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def read_glb_json(path: Path) -> dict[str, Any]:
    raw = path.read_bytes()
    if raw[:4] != b"glTF":
        raise ValueError(f"not a GLB file: {path}")
    json_length = int.from_bytes(raw[12:16], "little")
    if raw[16:20] != b"JSON":
        raise ValueError("GLB JSON chunk is missing")
    return json.loads(raw[20 : 20 + json_length].decode("utf-8"))


def inspect_glb(path: Path) -> dict[str, Any]:
    document = read_glb_json(path)
    return {
        "path": str(path),
        "sha256": sha256(path),
        "asset": document.get("asset"),
        "scene_count": len(document.get("scenes", [])),
        "node_names": [node.get("name") for node in document.get("nodes", []) if node.get("name")],
        "mesh_count": len(document.get("meshes", [])),
        "animation_names": [animation.get("name") for animation in document.get("animations", [])],
        "animation_count": len(document.get("animations", [])),
        "dsts_extras": document.get("extras", {}).get("dsts_schema"),
    }


def _find_chrome() -> Path:
    candidates = [
        Path(os.environ.get("PROGRAMFILES", "C:/Program Files")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("PROGRAMFILES(X86)", "C:/Program Files (x86)")) / "Google/Chrome/Application/chrome.exe",
        Path(os.environ.get("LOCALAPPDATA", "")) / "Google/Chrome/Application/chrome.exe",
    ]
    for candidate in candidates:
        if candidate.exists():
            return candidate
    found = shutil.which("chrome") or shutil.which("chrome.exe")
    if found:
        return Path(found)
    raise FileNotFoundError("Chrome was not found; install Chrome or set CHROME_PATH")


class _RendererHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args: Any, renderer_root: Path, model_path: Path, **kwargs: Any):
        self.model_path = model_path
        super().__init__(*args, directory=str(renderer_root), **kwargs)

    def do_GET(self) -> None:  # noqa: N802
        if urlparse(self.path).path == "/render-config.json":
            payload = json.dumps(getattr(self.server, "render_settings", {})).encode("utf-8")
            self.send_response(200)
            self.send_header("Content-Type", "application/json")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        if urlparse(self.path).path == "/model.glb":
            payload = self.model_path.read_bytes()
            self.send_response(200)
            self.send_header("Content-Type", "model/gltf-binary")
            self.send_header("Content-Length", str(len(payload)))
            self.end_headers()
            self.wfile.write(payload)
            return
        super().do_GET()

    def log_message(self, format: str, *args: Any) -> None:
        return

    def do_POST(self) -> None:
        if urlparse(self.path).path != "/geometry":
            self.send_error(404)
            return
        length = int(self.headers.get("Content-Length", "0"))
        # Large padded action cells retain a high-resolution source-feature
        # pass, so 128/192 px cells can legitimately exceed the original 16 MB
        # ceiling. Keep the local request bounded while admitting those native
        # captures when they are rendered one worker at a time.
        if not 0 < length < 64000000:
            self.send_error(413)
            return
        self.server.geometry = json.loads(self.rfile.read(length))
        self.send_response(204)
        self.end_headers()


def _start_server(renderer_root: Path, model_path: Path) -> tuple[ThreadingHTTPServer, int]:
    handler = lambda *args, **kwargs: _RendererHandler(  # noqa: E731
        *args, renderer_root=renderer_root, model_path=model_path, **kwargs
    )
    server = ThreadingHTTPServer(("127.0.0.1", 0), handler)
    return server, int(server.server_address[1])


def render_frame(
    model_path: Path,
    renderer_root: Path,
    output_path: Path,
    *,
    azimuth_degrees: float,
    time_seconds: float,
    clip_name: str,
    render_size: int,
    frame_size: int = 40,
    render_settings: dict[str, Any] | None = None,
) -> None:
    """Render exactly one GLB frame with the local Three.js renderer."""

    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    node = shutil.which("node")
    if not node:
        raise FileNotFoundError("Node.js is required for the readiness-aware renderer")
    server, port = _start_server(renderer_root, model_path)
    server.render_settings = render_settings or {}
    server_thread = __import__("threading").Thread(target=server.serve_forever, daemon=True)
    server_thread.start()
    chrome = Path(os.environ.get("CHROME_PATH", _find_chrome()))
    with tempfile.TemporaryDirectory(prefix="pmdo-chrome-") as profile:
        url = (
            f"http://127.0.0.1:{port}/render.html?model=/model.glb"
            f"&azimuth={azimuth_degrees}&time={time_seconds}&clip={clip_name}&size={render_size}&pixels={frame_size}"
        )
        command = [node, str(renderer_root / "capture.mjs"), str(chrome), url,
                   str(output_path), str(render_size), profile]
        try:
            result = subprocess.run(command, capture_output=True, text=True, timeout=55)
        finally:
            server.shutdown()
            server.server_close()
        if result.returncode != 0 or not output_path.exists():
            details = (result.stderr or result.stdout).strip()
            raise RuntimeError(f"Chrome render failed ({result.returncode}): {details[-2000:]}")
    geometry = getattr(server, "geometry", None)
    if geometry is None:
        raise RuntimeError("Renderer did not return the geometry contour pass: " + result.stderr[-3000:])
    if "error" in geometry:
        raise RuntimeError(f"Renderer failed: {geometry['error']}")
    output_path.with_suffix(".geometry.json").write_text(json.dumps(geometry), encoding="utf-8")


class PersistentRenderer:
    """A private browser and model load shared by sequential requests in one worker."""

    def __init__(self, model_path: Path, renderer_root: Path, settings: dict[str, Any]):
        self.model_path, self.renderer_root, self.settings = model_path, renderer_root, settings

    def __enter__(self) -> "PersistentRenderer":
        node = shutil.which("node")
        if not node:
            raise FileNotFoundError("Node.js is required for the batch renderer")
        try:
            self.server, port = _start_server(self.renderer_root, self.model_path)
            self.server.render_settings = self.settings
            self.thread = threading.Thread(target=self.server.serve_forever, daemon=True)
            self.thread.start()
            # Chrome can retain an Extension State log handle for a brief moment
            # after its owned process exits on Windows.  A late temp-profile
            # cleanup failure must not turn an otherwise complete render into a
            # failed package; the directory remains disposable OS-temp data.
            self.profile = tempfile.TemporaryDirectory(
                prefix="pmdo-batch-", ignore_cleanup_errors=True)
            chrome = Path(os.environ.get("CHROME_PATH", _find_chrome()))
            url = f"http://127.0.0.1:{port}/render.html?batch=1"
            self.process = subprocess.Popen(
                [node, str(self.renderer_root / "batch.mjs"), str(chrome), url, self.profile.name],
                stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.DEVNULL,
                text=True, bufsize=1,
                **({"creationflags": subprocess.CREATE_NEW_PROCESS_GROUP} if os.name == "nt"
                   else {"start_new_session": True}),
            )
            self.responses = queue.Queue()
            self.reader = threading.Thread(target=self._read_responses, daemon=True)
            self.reader.start()
            response = self._response(45)
            if response.get("ready") is not True:
                raise RuntimeError(f"Batch renderer startup failed: {response}")
            self.chrome_pid = response.get("chromePid")
        except Exception:
            self.__exit__(None, None, None)
            raise
        return self

    def _read_responses(self) -> None:
        for line in self.process.stdout:
            self.responses.put(line)
        self.responses.put(None)

    def _response(self, timeout: float) -> dict:
        try:
            line = self.responses.get(timeout=timeout)
        except queue.Empty as error:
            raise TimeoutError(f"Batch renderer did not respond within {timeout}s") from error
        if line is None:
            raise RuntimeError("Batch renderer exited before responding")
        return json.loads(line)

    def render(self, output_path: Path, *, azimuth_degrees: float,
               time_seconds: float, clip_name: str, render_size: int,
               frame_size: int) -> None:
        output_path = output_path.resolve()
        output_path.parent.mkdir(parents=True, exist_ok=True)
        self.server.geometry = None
        request = {"output": str(output_path), "azimuth": azimuth_degrees,
                   "time": time_seconds, "clip": clip_name,
                   "size": render_size, "pixels": frame_size}
        try:
            self.process.stdin.write(json.dumps(request) + "\n")
            self.process.stdin.flush()
            response = self._response(55)
            geometry = self.server.geometry
            if response != {"ok": True} or not isinstance(geometry, dict) or "error" in geometry:
                raise RuntimeError(f"Batch render failed: {response}; geometry: {str(geometry)[:500]}")
            output_path.with_suffix(".geometry.json").write_text(json.dumps(geometry), encoding="utf-8")
        except Exception:
            output_path.unlink(missing_ok=True)
            output_path.with_suffix(".geometry.json").unlink(missing_ok=True)
            self.__exit__(None, None, None)
            raise

    def __exit__(self, exc_type: object, exc: object, tb: object) -> None:
        process = getattr(self, "process", None)
        if process:
            try:
                if process.poll() is None:
                    process.stdin.write('{"stop":true}\n')
                    process.stdin.flush()
                    process.wait(timeout=5)
            except (OSError, subprocess.TimeoutExpired):
                if process.poll() is None:
                    if os.name == "nt":
                        try:
                            subprocess.run(["taskkill", "/PID", str(process.pid), "/T", "/F"],
                                           capture_output=True, timeout=10)
                        except (OSError, subprocess.TimeoutExpired):
                            pass
                        chrome_pid = getattr(self, "chrome_pid", None)
                        if chrome_pid and process.poll() is None:
                            try:
                                subprocess.run(["taskkill", "/PID", str(chrome_pid), "/T", "/F"],
                                               capture_output=True, timeout=10)
                            except (OSError, subprocess.TimeoutExpired):
                                pass
                    else:
                        os.killpg(process.pid, signal.SIGKILL)
                    if process.poll() is None:
                        process.kill()
                    process.wait(timeout=5)
            for stream in (process.stdin, process.stdout):
                if stream:
                    stream.close()
            self.process = None
        server = getattr(self, "server", None)
        if server:
            server.shutdown()
            server.server_close()
            thread = getattr(self, "thread", None)
            if thread:
                thread.join(timeout=3)
            self.server = None
        profile = getattr(self, "profile", None)
        if profile:
            profile.cleanup()
            self.profile = None


def _binary_alpha(image: Image.Image, cutoff: int) -> Image.Image:
    image = image.convert("RGBA")
    pixels = []
    for red, green, blue, alpha in image.getdata():
        if alpha < cutoff:
            pixels.append((0, 0, 0, 0))
        else:
            pixels.append((red, green, blue, 255))
    result = Image.new("RGBA", image.size)
    result.putdata(pixels)
    return result


def _resize_frame(path: Path, size: int, cutoff: int) -> Image.Image:
    with Image.open(path) as source:
        image = source.convert("RGBA").resize((size, size), Image.Resampling.LANCZOS)
    return _binary_alpha(image, cutoff)


def _outline_frame(image: Image.Image, geometry_path: Path, settings: dict[str, Any],
                   geometry: dict[str, Any] | None = None) -> Image.Image:
    """One-pixel contour from the silhouette and visible surface discontinuities."""
    if geometry is None:
        geometry = json.loads(geometry_path.read_text(encoding="utf-8"))
    size = image.width
    if geometry["size"] != size:
        raise ValueError("Geometry pass resolution does not match the PMDO frame")
    # WebGL readback is bottom-up; the PNG image is top-down.
    normals = np.array(geometry["normals"], dtype=np.float32).reshape(size, size, 4)[::-1]
    depth = np.array(geometry["depth"], dtype=np.float32).reshape(size, size, 4)[::-1, :, 0] / 255.0
    vectors = normals[:, :, :3] / 127.5 - 1.0
    vectors /= np.maximum(np.linalg.norm(vectors, axis=2, keepdims=True), 1e-6)
    rgba = np.array(image).copy()
    opaque = rgba[:, :, 3] > 0
    valid = (normals[:, :, 3] > 127) & opaque
    contour = np.zeros((size, size), dtype=bool)
    outer = np.zeros((size, size), dtype=bool)
    for dy, dx in ((0, 1), (0, -1), (1, 0), (-1, 0)):
        for y in range(1, size - 1):
            for x in range(1, size - 1):
                ny, nx = y + dy, x + dx
                if not opaque[y, x] and opaque[ny, nx]:
                    outer[y, x] = True
                if not (valid[y, x] and valid[ny, nx]):
                    continue
                delta = depth[y, x] - depth[ny, nx]
                # Draw on the foreground side only, avoiding double-width seams.
                if delta > settings.get("depth_threshold", 0.045):
                    contour[y, x] = True
                elif (dy, dx) in ((0, 1), (1, 0)) and delta >= 0:
                    if float(np.dot(vectors[y, x], vectors[ny, nx])) < settings.get("normal_dot_threshold", 0.45):
                        contour[y, x] = True
    if "headMask" in geometry:
        head = np.array(geometry["headMask"], dtype=np.uint8).reshape(size, size, 4)[::-1, :, 0] > 20
        contour &= ~head
    rgba[outer | contour] = (0, 0, 0, 255)
    # Recover the actual texture's thin mouth seam and nostrils; never use
    # the curved snout's normal changes as facial ink.
    if "faceCoverage" in geometry:
        coverage = (np.array(geometry["faceCoverage"], dtype=float)
                    .reshape(size, size, 2) / 255.0)
    elif "faceFeatures" in geometry:
        high_size = geometry["featureSize"]
        features = np.array(geometry["faceFeatures"], dtype=np.uint8).reshape(high_size, high_size, 4)[::-1]
        coverage = np.zeros((size, size, 2), dtype=float)
        # Non-Agumon source-only materials can have an entirely empty mouth/
        # nose diagnostic. Zero coverage is exact; skip the expensive empty loop.
        for y in range(high_size if features[:, :, :2].any() else 0):
            for x in range(high_size):
                coverage[y*size//high_size, x*size//high_size] += features[y, x, :2] / 255.0
    else:
        coverage = None
    if coverage is not None:
        mouth_points = []
        for x in range(size):
            y = int(np.argmax(coverage[:, x, 0]))
            if coverage[y, x, 0] >= 1.5 and opaque[y, x]:
                mouth_points.append((x, y))
        mouth_image = Image.new("L", (size, size))
        pen = ImageDraw.Draw(mouth_image)
        for index, point in enumerate(mouth_points):
            pen.point(point, fill=255)
            if index:
                pen.line([mouth_points[index-1], point], fill=255, width=1)
        rgba[(np.array(mouth_image) > 0) & opaque] = (75, 40, 12, 255)
        nose = (coverage[:, :, 1] >= 0.4) & opaque
        # One dark nostril pixel per local maximum, not a filled black nose.
        for y, x in zip(*np.where(nose)):
            patch = coverage[max(0,y-1):y+2, max(0,x-1):x+2, 1]
            if coverage[y,x,1] >= patch.max():
                rgba[y,x] = (50, 28, 10, 255)
    # Project an anterior point on each eye so the gaze follows the snout.
    # Only covered eye pixels may receive white or black, preventing the
    # former sclera highlight from painting over the brow or muzzle.
    for eye in geometry.get("eyes", []):
        if eye.get("sourceOnly") and not settings.get("closed_eyes"):
            # Opt-in, source-bounded contrast for pale faces (Tokomon). Recolor
            # only the native dark eye pixels; never fabricate a ring or pupil.
            if "source_eye_dark_rgb" in settings:
                coverage = np.array(eye["coverage"]).reshape(size, size)
                dark = (coverage >= max(3, coverage.max() * 0.45)) & opaque
                dark &= (rgba[:, :, :3].max(axis=2) < 180)
                dark &= (rgba[:, :, :3].sum(axis=2) > 0)
                rgba[dark, :3] = settings["source_eye_dark_rgb"]
            continue
        if "coverage" not in eye:
            raise ValueError("Eye geometry must be rerendered for forward-facing pupils")
        eye_coverage = np.array(eye["coverage"]).reshape(size, size)
        candidates = (eye_coverage >= max(3, eye_coverage.max()*0.2)) & opaque
        ys, xs = np.where(candidates)
        if len(xs):
            if settings.get("closed_eyes"):
                rgba[candidates] = (*settings.get("closed_eye_fill", (255, 174, 20)), 255)
                eyelid_y = (int(np.argmax(candidates.sum(axis=1)))
                            if settings.get("closed_eye_row") == "widest" else int(np.median(ys)))
                for x in range(int(xs.min()), int(xs.max()) + 1):
                    if candidates[eyelid_y, x]:
                        rgba[eyelid_y, x] = (*settings.get("closed_eye_ink", (75, 40, 12)), 255)
                continue
            rgba[candidates] = (255, 255, 255, 255)
            px, py = eye["pupil"]
            choice = int(np.argmin((xs+0.5-px*size)**2 + (ys+0.5-py*size)**2))
            rgba[ys[choice], xs[choice]] = (0, 0, 0, 255)
    return Image.fromarray(rgba)


def _template_point(config: dict[str, Any], name: str, size: int) -> tuple[int, int]:
    x, y = config["offsets"][name]
    return (min(size - 1, max(0, round(x * (size - 1)))), min(size - 1, max(0, round(y * (size - 1)))))


def _paint_marker(sheet: Image.Image, x: int, y: int, color: tuple[int, int, int, int]) -> None:
    if 0 <= x < sheet.width and 0 <= y < sheet.height:
        sheet.putpixel((x, y), color)


def _fixed_palette_rgb(rgb: Image.Image, alpha: Image.Image, colors: list) -> Image.Image:
    """Map source RGB directly to one explicit palette, independent of atlas mix."""
    if (not isinstance(colors, list) or not 1 <= len(colors) <= 64
            or any(not isinstance(c, (list, tuple)) or len(c) != 3
                   or any(type(v) is not int or not 0 <= v <= 255 for v in c)
                   for c in colors)
            or len({tuple(c) for c in colors}) != len(colors)):
        raise ValueError("fixed_palette_colors must contain 1-64 unique RGB byte triples")
    data = np.array(rgb.convert("RGB"))
    opaque = np.array(alpha) > 0
    unique, inverse = np.unique(data[opaque], axis=0, return_inverse=True)
    palette = np.array(colors, dtype=np.int32)
    distances = ((unique[:, None, :].astype(np.int32) - palette[None, :, :]) ** 2).sum(axis=2)
    data[opaque] = palette[np.argmin(distances, axis=1)][inverse].astype(np.uint8)
    data[~opaque] = 0
    return Image.fromarray(data)


def assemble_package(
    config: dict[str, Any],
    frames_root: Path,
    output_dir: Path,
    *,
    gfx_params: Path | None = None,
    action_name: str = "Idle",
    emit_animdata: bool = True,
    ground_policy: str = "per-frame",
) -> dict[str, Any]:
    """Create PMDO sheets, markers, and AnimData.xml from rendered frames."""

    frame_size = int(config["frame_size"])
    frame_count = int(config["idle_frames"])
    cutoff = int(config["alpha_cutoff"])
    sheet_size = (frame_size * frame_count, frame_size * len(DIRECTIONS))
    rendered: list[Image.Image] = []
    vertical_shifts: list[int] = []
    frame_geometry: list[dict[str, Any]] = []
    for direction in DIRECTIONS:
        for frame_number in range(frame_count):
            path = frames_root / direction / f"frame_{frame_number:02d}.png"
            if not path.exists():
                raise FileNotFoundError(path)
            frame = _resize_frame(path, frame_size, cutoff)
            geometry_path = path.with_suffix(".geometry.json")
            geometry = (json.loads(geometry_path.read_text(encoding="utf-8"))
                        if geometry_path.exists() else {})
            # Dense normal/depth and source-feature buffers are consumed while
            # outlining this frame. Projected offsets only need the bone map,
            # so retaining full geometry across an action wastes gigabytes on
            # padded 128/192 px cells.
            frame_geometry.append({"bonePoints": geometry.get("bonePoints", {})})
            if config.get("outline", {}).get("enabled"):
                frame = _outline_frame(frame, geometry_path, config["outline"], geometry)
            shift = 0
            if "ground_contact_row" in config and ground_policy == "per-frame":
                bounds = frame.getchannel("A").getbbox()
                if bounds is None:
                    raise ValueError(f"Empty frame: {path}")
                shift = int(config["ground_contact_row"]) - (bounds[3] - 1)
                if bounds[1] + shift < 1 or bounds[3] + shift >= frame_size:
                    raise ValueError(f"Ground placement clips sprite: {path}")
                grounded = Image.new("RGBA", frame.size)
                grounded.paste(frame, (0, shift))
                frame = grounded
            vertical_shifts.append(shift)
            rendered.append(frame)

    if "ground_contact_row" in config and ground_policy == "fixed":
        for row in range(len(DIRECTIONS)):
            first = rendered[row * frame_count].getchannel("A").getbbox()
            if first is None:
                raise ValueError(f"Empty first frame in {action_name} {DIRECTIONS[row]}")
            shift = int(config["ground_contact_row"]) - (first[3] - 1)
            for column in range(frame_count):
                index = row * frame_count + column
                frame = rendered[index]
                bounds = frame.getchannel("A").getbbox()
                if bounds is None or bounds[1] + shift < 1 or bounds[3] + shift >= frame_size:
                    raise ValueError(f"Fixed ground placement clips {action_name} {DIRECTIONS[row]} frame {column}")
                placed = Image.new("RGBA", frame.size)
                placed.paste(frame, (0, shift))
                rendered[index] = placed
                vertical_shifts[index] = shift

    placement = config.get("placement", {})
    if placement.get("mode") == "airborne":
        # One fixed transform for the whole loop and all directions. Preserve
        # source bob/wing motion; never normalize each flying frame's bottom.
        bounds_by_frame = [frame.getchannel("A").getbbox() for frame in rendered]
        for index, bounds in enumerate(bounds_by_frame):
            if bounds is None:
                row, column = divmod(index, frame_count)
                raise ValueError(f"Empty frame in {action_name} {DIRECTIONS[row]} frame {column}")
        lowest = max(bounds[3] - 1 for bounds in bounds_by_frame)
        shift = int(placement.get("fixed_vertical_shift",
                    int(placement["shadow_row"]) - int(placement["minimum_gap"]) - lowest))
        for index, frame in enumerate(rendered):
            bounds = bounds_by_frame[index]
            if bounds[1] + shift < 1 or bounds[3] + shift >= frame_size:
                raise ValueError("Airborne placement clips the sprite; increase frame margin")
            shifted = Image.new("RGBA", frame.size)
            shifted.paste(frame, (0, shift))
            rendered[index] = shifted
            vertical_shifts[index] = shift

    # Optional action-level translation is applied after the normal ground
    # policy so it preserves the source animation rather than re-grounding it.
    # A penetration limit may add the smallest extra upward correction needed
    # by an individual frame. Offset markers receive the same correction below;
    # the shadow marker intentionally remains at the configured ground row.
    action_offset = int(config.get("action_vertical_offset_px", 0))
    max_penetration = config.get("max_shadow_penetration_px")
    if max_penetration is not None and "ground_contact_row" not in config:
        raise ValueError("max_shadow_penetration_px requires ground_contact_row")
    if action_offset or max_penetration is not None:
        ground_row = int(config["ground_contact_row"]) if max_penetration is not None else None
        for index, frame in enumerate(rendered):
            bounds = frame.getchannel("A").getbbox()
            if bounds is None:
                raise ValueError(f"Empty assembled frame in {action_name}")
            correction = action_offset
            if max_penetration is not None:
                excess = bounds[3] - 1 + correction - (ground_row + int(max_penetration))
                correction -= max(0, excess)
            if correction:
                if bounds[1] + correction < 1 or bounds[3] + correction >= frame_size:
                    raise ValueError(f"Action vertical offset clips {action_name} frame {index}")
                shifted = Image.new("RGBA", frame.size)
                shifted.paste(frame, (0, correction))
                rendered[index] = shifted
                vertical_shifts[index] += correction

    rgb_atlas = Image.new("RGB", sheet_size, (0, 0, 0))
    alpha_atlas = Image.new("L", sheet_size, 0)
    for index, image in enumerate(rendered):
        x = (index % frame_count) * frame_size
        y = (index // frame_count) * frame_size
        rgb_atlas.paste(image.convert("RGB"), (x, y))
        alpha_atlas.paste(image.getchannel("A"), (x, y))
    # Reserve exact black for one-pixel outlines instead of blending it into orange.
    outline_enabled = config.get("outline", {}).get("enabled", False)
    if "fixed_palette_colors" in config:
        colors = config["fixed_palette_colors"]
        quantized = _fixed_palette_rgb(rgb_atlas, alpha_atlas, colors)
        if outline_enabled and [0, 0, 0] not in [list(c) for c in colors]:
            raise ValueError("fixed_palette_colors must reserve exact black for outlines")
        if config.get("mouth_palette"):
            raise ValueError("fixed_palette_colors cannot be combined with legacy mouth_palette painting")
    else:
        quantized = rgb_atlas.quantize(colors=int(config["palette_size"]) - int(outline_enabled), method=Image.Quantize.MEDIANCUT).convert("RGB")
    anim = Image.merge("RGBA", (*quantized.split(), alpha_atlas))
    if outline_enabled:
        pixels = np.array(anim)
        source_pixels = np.array(rgb_atlas)
        black = np.all(source_pixels == 0, axis=2) & (np.array(alpha_atlas) > 0)
        pixels[black, :3] = 0
        if "source_eye_dark_rgb" in config.get("outline", {}):
            eye_rgb = np.asarray(config["outline"]["source_eye_dark_rgb"])
            eye_pixels = np.all(source_pixels == eye_rgb, axis=2) & (np.array(alpha_atlas) > 0)
            pixels[eye_pixels, :3] = eye_rgb
        anim = Image.fromarray(pixels)
    if config.get("mouth_palette"):
        pixels = np.array(anim)
        source_pixels = np.array(rgb_atlas)
        opaque = np.array(alpha_atlas) > 0
        red, green, blue = (source_pixels[:, :, i].astype(np.int16) for i in range(3))
        # Native tongue/interior is sparse at 40px and otherwise disappears
        # during whole-sheet quantization. These pixels are sampled from the
        # model render, then assigned two stable action-only mouth colors.
        mouth = opaque & (red > 120) & (red - green > 45) & (blue > 50) & (blue * 4 > green * 3)
        dark = mouth & ((red < 225) | (green < 100))
        pixels[mouth, :3] = (248, 112, 143)
        pixels[dark, :3] = (147, 52, 76)
        anim = Image.fromarray(pixels)
    anim.putdata([(r, g, b, a) if a else (0, 0, 0, 0) for r, g, b, a in anim.getdata()])

    offsets = Image.new("RGBA", sheet_size, (0, 0, 0, 0))
    shadow = Image.new("RGBA", sheet_size, (0, 0, 0, 0))
    for row in range(len(DIRECTIONS)):
        for column in range(frame_count):
            origin_x = column * frame_size
            origin_y = row * frame_size
            occupied = set()
            for marker_name in ("head", "left_hand", "center", "right_hand"):
                if config["offsets"]["source"] == "projected-native-bones-v1":
                    point = frame_geometry[row * frame_count + column]["bonePoints"][marker_name]
                    marker_x, marker_y = (int(v * frame_size) for v in point)
                else:
                    marker_x, marker_y = _template_point(config, marker_name, frame_size)
                marker_y += vertical_shifts[row * frame_count + column]
                # Screen-projected bones can coincide in profile. Preserve
                # every required marker with the nearest unused pixel <=2px.
                candidates = sorted(((marker_x+dx, marker_y+dy) for dx in range(-2,3) for dy in range(-2,3)),
                                    key=lambda p:(p[0]-marker_x)**2+(p[1]-marker_y)**2)
                point = next((p for p in candidates if p not in occupied and 0 <= p[0] < frame_size and 0 <= p[1] < frame_size), None)
                if point is None:
                    raise ValueError(
                        f"Invalid projected marker {marker_name} in {action_name} "
                        f"{DIRECTIONS[row]} frame {column}: {(marker_x, marker_y)}"
                    )
                marker_x, marker_y = point
                occupied.add(point)
                _paint_marker(offsets, origin_x + marker_x, origin_y + marker_y, MARKER_COLORS[marker_name])
            shadow_x, shadow_y = _template_point(config, "shadow", frame_size)
            if "ground_contact_row" in config:
                shadow_x = frame_size // 2
                shadow_y = int(config["ground_contact_row"])
            elif placement.get("mode") == "airborne":
                shadow_x, shadow_y = frame_size // 2, int(placement["shadow_row"])
            _paint_marker(shadow, origin_x + shadow_x, origin_y + shadow_y, MARKER_COLORS["shadow"])

    output_dir.mkdir(parents=True, exist_ok=True)
    anim_path = output_dir / f"{action_name}-Anim.png"
    offsets_path = output_dir / f"{action_name}-Offsets.png"
    shadow_path = output_dir / f"{action_name}-Shadow.png"
    anim.save(anim_path)
    offsets.save(offsets_path)
    shadow.save(shadow_path)
    if emit_animdata:
        write_animdata(config, output_dir / "AnimData.xml", gfx_params=gfx_params)
    return {
        "output_dir": str(output_dir),
        "frame_size": frame_size,
        "frame_count": frame_count,
        "direction_order": DIRECTIONS,
        "palette_size": int(config["palette_size"]),
        "offset_source": config["offsets"]["source"],
        "files": [anim_path.name, offsets_path.name, shadow_path.name] + (["AnimData.xml"] if emit_animdata else []),
    }


def _text(parent: ET.Element, tag: str, value: str | int) -> ET.Element:
    child = ET.SubElement(parent, tag)
    child.text = str(value)
    return child


def write_animdata(config: dict[str, Any], path: Path, *, gfx_params: Path | None) -> None:
    names = ["None", "Idle", "Walk", "Sleep", "Hurt", "Attack", "Charge", "Shoot", "Strike", "Chop", "Cut", "Beam", "Swing", "Thrust", "Punch", "Projectile", "Throw", "Eat", "Dance", "Bite", "Claw", "Tail", "Special", "Start", "End", "ChargeAttack", "ChargeShot", "ChargeBeam", "ChargeClaw", "ChargeTail", "ChargeBite", "ChargePunch", "ChargeSwing", "ChargeThrust", "ChargeProjectile", "ChargeThrow", "ChargeEat", "ChargeDance", "ChargeSpecial"]
    if gfx_params and gfx_params.exists():
        try:
            root = ET.parse(gfx_params).getroot()
            names = [node.text.strip() for node in root.findall("./Actions/Action/Name") if node.text and node.text.strip()]
        except ET.ParseError:
            pass
    if "Idle" not in names:
        names.insert(1, "Idle")
    root = ET.Element("AnimData")
    _text(root, "ShadowSize", 0)
    anims = ET.SubElement(root, "Anims")
    frame_count = int(config["idle_frames"])
    duration_ticks = int(config.get("idle_duration_ticks", 8))
    for index, name in enumerate(names):
        anim = ET.SubElement(anims, "Anim")
        _text(anim, "Name", name)
        _text(anim, "Index", index)
        if name == "Idle":
            _text(anim, "FrameWidth", config["frame_size"])
            _text(anim, "FrameHeight", config["frame_size"])
            _text(anim, "RushFrame", 0)
            _text(anim, "HitFrame", 0)
            _text(anim, "ReturnFrame", 0)
            durations = ET.SubElement(anim, "Durations")
            for _ in range(frame_count):
                _text(durations, "Duration", duration_ticks)
        else:
            _text(anim, "CopyOf", "Idle")
    ET.indent(root, space="  ")
    path.parent.mkdir(parents=True, exist_ok=True)
    ET.ElementTree(root).write(path, encoding="utf-8", xml_declaration=True)


def _frame_colors(image: Image.Image, box: tuple[int, int, int, int]) -> set[tuple[int, int, int, int]]:
    return set(image.crop(box).getdata())


def validate_package(package_dir: Path, config: dict[str, Any]) -> dict[str, Any]:
    failures: list[str] = []
    frame_size = int(config["frame_size"])
    frame_count = int(config["idle_frames"])
    expected_size = (frame_size * frame_count, frame_size * len(DIRECTIONS))
    paths = {name: package_dir / name for name in ("Idle-Anim.png", "Idle-Offsets.png", "Idle-Shadow.png", "AnimData.xml")}
    images: dict[str, Image.Image] = {}
    for name in ("Idle-Anim.png", "Idle-Offsets.png", "Idle-Shadow.png"):
        if not paths[name].exists():
            failures.append(f"missing {name}")
            continue
        image = Image.open(paths[name]).convert("RGBA")
        images[name] = image
        if image.size != expected_size:
            failures.append(f"{name} has size {image.size}, expected {expected_size}")
    if paths["AnimData.xml"].exists():
        try:
            root = ET.parse(paths["AnimData.xml"]).getroot()
            idle = next((node for node in root.findall("./Anims/Anim") if node.findtext("Name") == "Idle"), None)
            if idle is None:
                failures.append("AnimData.xml has no Idle animation")
            else:
                if idle.findtext("FrameWidth") != str(frame_size) or idle.findtext("FrameHeight") != str(frame_size):
                    failures.append("Idle frame dimensions do not match config")
                durations = idle.findall("./Durations/Duration")
                if len(durations) != frame_count:
                    failures.append(f"Idle has {len(durations)} durations, expected {frame_count}")
        except ET.ParseError as exc:
            failures.append(f"invalid AnimData.xml: {exc}")
    else:
        failures.append("missing AnimData.xml")

    if "Idle-Offsets.png" in images:
        image = images["Idle-Offsets.png"]
        for row in range(len(DIRECTIONS)):
            for column in range(frame_count):
                left = column * frame_size
                top = row * frame_size
                colors = _frame_colors(image, (left, top, left + frame_size, top + frame_size))
                for marker_name in ("head", "left_hand", "center", "right_hand"):
                    if MARKER_COLORS[marker_name] not in colors:
                        failures.append(f"offset marker {marker_name} missing in {DIRECTIONS[row]} frame {column}")
    if "Idle-Shadow.png" in images:
        image = images["Idle-Shadow.png"]
        for row in range(len(DIRECTIONS)):
            for column in range(frame_count):
                left = column * frame_size
                top = row * frame_size
                if MARKER_COLORS["shadow"] not in _frame_colors(image, (left, top, left + frame_size, top + frame_size)):
                    failures.append(f"shadow marker missing in {DIRECTIONS[row]} frame {column}")

    palette_count = None
    if "Idle-Anim.png" in images:
        image = images["Idle-Anim.png"]
        opaque_colors = {pixel[:3] for pixel in image.getdata() if pixel[3]}
        palette_count = len(opaque_colors)
        if palette_count > int(config["palette_size"]):
            failures.append(f"Idle-Anim.png uses {palette_count} opaque colors, max {config['palette_size']}")
        alpha_values = {pixel[3] for pixel in image.getdata()}
        if not alpha_values.issubset({0, 255}):
            failures.append(f"Idle-Anim.png alpha is not binary: {sorted(alpha_values)}")
        for row, direction in enumerate(DIRECTIONS):
            for column in range(frame_count):
                alpha = image.getchannel("A").crop((
                    column * frame_size, row * frame_size,
                    (column + 1) * frame_size, (row + 1) * frame_size,
                ))
                if alpha.getextrema() != (0, 255):
                    failures.append(f"{direction} frame {column} must contain transparent background and opaque sprite pixels")
                corners = [(0, 0), (frame_size - 1, 0), (0, frame_size - 1), (frame_size - 1, frame_size - 1)]
                if any(alpha.getpixel(point) != 0 for point in corners):
                    failures.append(f"{direction} frame {column} has an opaque background corner")
                placement = config.get("placement", {})
                if placement.get("mode") == "airborne":
                    bounds = alpha.getbbox()
                    shadow_row = int(placement["shadow_row"])
                    if bounds is None or shadow_row - (bounds[3]-1) < int(placement["minimum_gap"]):
                        failures.append(f"{direction} frame {column} has insufficient flight clearance")
                    shadow = images.get("Idle-Shadow.png")
                    if shadow is not None and shadow.getpixel((column*frame_size+frame_size//2,row*frame_size+shadow_row)) != MARKER_COLORS["shadow"]:
                        failures.append(f"{direction} frame {column} flying shadow is not fixed at root ground")
                if "ground_contact_row" in config:
                    bounds = alpha.getbbox()
                    contact_row = int(config["ground_contact_row"])
                    if bounds is None or bounds[3] - 1 != contact_row:
                        failures.append(f"{direction} frame {column} does not touch the configured ground row")
                    shadow = images.get("Idle-Shadow.png")
                    if shadow is not None and shadow.getpixel((
                        column * frame_size + frame_size // 2, row * frame_size + contact_row
                    )) != MARKER_COLORS["shadow"]:
                        failures.append(f"{direction} frame {column} shadow is detached from ground contact")
    return {
        "ok": not failures,
        "failures": failures,
        "package_dir": str(package_dir),
        "expected_size": expected_size,
        "palette_count": palette_count,
    }


def build(config_path: Path, model_path: Path, output_root: Path, repo_root: Path) -> dict[str, Any]:
    config = load_config(config_path)
    renderer_root = Path(__file__).resolve().parent / "renderer"
    intermediate = output_root / "intermediate" / config["species"] / "idle"
    package_dir = output_root / "output" / config["species"]
    # Existing files alone cannot establish cache validity: camera, renderer,
    # model or configuration changes must invalidate all intermediate renders.
    render_signature = hashlib.sha256(json.dumps({
        "config": config,
        "model": sha256(model_path),
        "renderer": sha256(renderer_root / "render.html"),
        "capture": sha256(renderer_root / "capture.mjs"),
        "pipeline": sha256(Path(__file__)),
    }, sort_keys=True).encode("utf-8")).hexdigest()
    signature_path = intermediate / "render-signature.txt"
    cache_valid = signature_path.exists() and signature_path.read_text(encoding="utf-8") == render_signature
    for direction in config["directions"]:
        for frame_number, time_seconds in enumerate(config["frame_times"]):
            output_path = intermediate / direction["name"] / f"frame_{frame_number:02d}.png"
            if cache_valid and output_path.exists() and output_path.stat().st_size > 0 and output_path.with_suffix(".geometry.json").exists():
                continue
            render_frame(
                model_path,
                renderer_root,
                output_path,
                azimuth_degrees=float(direction["azimuth_degrees"]),
                time_seconds=float(time_seconds),
                clip_name=config["idle_clip"],
                render_size=int(config["render_size"]),
                frame_size=int(config["frame_size"]),
                render_settings=config.get("renderer", {}),
            )
    signature_path.write_text(render_signature, encoding="utf-8")
    result = assemble_package(
        config,
        intermediate,
        package_dir,
        gfx_params=repo_root / "DumpAsset" / "Base" / "GFXParams.xml",
    )
    validation = validate_package(package_dir, config)
    result["validation"] = validation
    result["glb"] = inspect_glb(model_path)
    result["config"] = str(config_path)
    result["provenance"] = {
        "pipeline_version": "0.1.0",
        "model_sha256": sha256(model_path),
        "model_path": str(model_path),
        "dsts_extractor": "0.9.0",
        "clip": config["idle_clip"],
        "render_size": config["render_size"],
        "frame_size": config["frame_size"],
        "frames_per_direction": config["idle_frames"],
        "directions": DIRECTIONS,
        "offset_source": config["offsets"]["source"],
        "outline": config.get("outline"),
        "ground_contact_row": config.get("ground_contact_row"),
        "placement": config.get("placement"),
        "renderer_settings": config.get("renderer", {}),
        "pupils": config.get("renderer", {}).get("eye_mode", "forward-pupil"),
    }
    output_root.mkdir(parents=True, exist_ok=True)
    (output_root / "phase4-build-report.json").write_text(json.dumps(result, indent=2), encoding="utf-8")
    return result
