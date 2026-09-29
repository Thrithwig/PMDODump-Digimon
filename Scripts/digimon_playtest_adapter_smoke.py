"""Lab-only smoke test for the local PMDC file adapter.

The script writes atomic JSON requests into one disposable session. PMDC owns
all rendering and gameplay input; this script does not inject OS input or call
Lua/gameplay functions. It is deliberately limited to Test Camp's normal
South Exit traversal.
"""

from __future__ import annotations

import argparse
import json
import os
from pathlib import Path
import subprocess
import sys
import time
from typing import Any


LAB_ROOT = Path(__file__).resolve().parents[1]
PROFILE_ROOT = LAB_ROOT / "work" / "playtest-profiles"
RESULT_ROOT = LAB_ROOT / "work" / "visual-checks"
PUBLISHED_ROOT = LAB_ROOT / "PMDC" / "publish" / "win-x64" / "PMDC"
EXE = PUBLISHED_ROOT / "PMDC.exe"


def under(path: Path, root: Path) -> bool:
    try:
        path.resolve().relative_to(root.resolve())
        return True
    except ValueError:
        return False


def atomic_json(path: Path, data: dict[str, Any]) -> None:
    temp = path.with_name(path.name + f".{time.time_ns()}.tmp")
    temp.write_text(json.dumps(data, indent=2) + "\n", encoding="utf-8")
    os.replace(temp, path)


def wait_json(path: Path, timeout: float, process: subprocess.Popen[str]) -> dict[str, Any]:
    deadline = time.monotonic() + timeout
    while time.monotonic() < deadline:
        if path.is_file():
            return json.loads(path.read_text(encoding="utf-8"))
        if process.poll() is not None:
            raise RuntimeError(f"PMDC exited with {process.returncode} before response {path.name}.")
        time.sleep(0.05)
    raise TimeoutError(f"Timed out waiting for {path.name}.")


def submit(control: Path, session_id: str, request_id: str, command: str, arguments: dict[str, Any], process: subprocess.Popen[str], timeout: int = 20) -> dict[str, Any]:
    request = {
        "schema_version": 1,
        "session_id": session_id,
        "request_id": request_id,
        "command": command,
        "arguments": arguments,
        "wall_timeout_seconds": timeout,
    }
    atomic_json(control / "requests" / f"{request_id}.json", request)
    response = wait_json(control / "responses" / f"{request_id}.json", timeout + 10, process)
    if response.get("status") != "completed":
        raise RuntimeError(f"{request_id} returned {response.get('status')}: {response.get('error')}")
    return response


def hidden_startup() -> tuple[Any, int]:
    if os.name != "nt":
        return None, 0
    startup = subprocess.STARTUPINFO()
    startup.dwFlags |= subprocess.STARTF_USESHOWWINDOW
    startup.wShowWindow = subprocess.SW_HIDE
    return startup, subprocess.CREATE_NO_WINDOW


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", required=True, type=Path, help="New result directory beneath work/visual-checks.")
    parser.add_argument("--timeout-seconds", type=int, default=45, help="Whole smoke deadline (10-60 seconds).")
    args = parser.parse_args()
    output = args.output.resolve()
    if not under(output, RESULT_ROOT) or output == RESULT_ROOT.resolve():
        parser.error("--output must be a child of work/visual-checks.")
    if output.exists() and any(output.iterdir()):
        parser.error("--output must be new or empty.")
    if not 10 <= args.timeout_seconds <= 60:
        parser.error("--timeout-seconds must be between 10 and 60.")
    if not EXE.is_file():
        parser.error(f"Published lab executable missing: {EXE}")

    output.mkdir(parents=True, exist_ok=True)
    session = (PROFILE_ROOT / f"adapter-smoke-{int(time.time())}").resolve()
    session.mkdir(parents=True, exist_ok=False)
    control = session / "playtest-control"
    # PathMod concatenates the asset root with relative directory names, so the
    # command-line value must retain a trailing separator.
    asset_root = str(PUBLISHED_ROOT) + os.sep
    command = [str(EXE), "-dev", "-asset", asset_root, "-appdata", str(PROFILE_ROOT), "-playtest", str(session), "-playtest-adapter-smoke"]
    startupinfo, creationflags = hidden_startup()
    process = subprocess.Popen(command, cwd=LAB_ROOT, startupinfo=startupinfo, creationflags=creationflags, text=True)
    started = time.monotonic()
    try:
        info = wait_json(control / "session.json", 20, process)
        session_id = info["session_id"]
        at_test_camp = submit(control, session_id, "wait-test-camp", "wait_for", {"predicate": "map_id_equals", "map_id": "test_camp"}, process, 25)
        capture = submit(control, session_id, "capture-test-camp", "capture", {"mode": "viewport", "file_name": "adapter-smoke.png"}, process, 20)
        input_response = submit(control, session_id, "input-south-exit", "input", {"direction": "Down", "buttons": [], "press_frames": 30, "release_frames": 1}, process, 15)
        at_base_camp = submit(control, session_id, "wait-base-camp", "wait_for", {"predicate": "map_id_equals", "map_id": "base_camp"}, process, 20)
        process.wait(timeout=max(1, args.timeout_seconds - (time.monotonic() - started)))
        if process.returncode != 0:
            raise RuntimeError(f"PMDC returned {process.returncode} after Base Camp arrival.")
        artifact = session / "artifacts" / "adapter" / "capture-test-camp" / "adapter-smoke.png"
        if not artifact.is_file() or artifact.stat().st_size == 0:
            raise RuntimeError("Adapter capture artifact is missing or empty.")
        result = {
            "schema_version": 1,
            "status": "passed",
            "visual_review": "unreviewed",
            "elapsed_seconds": round(time.monotonic() - started, 3),
            "session": str(session.relative_to(LAB_ROOT)),
            "artifact": str(artifact.relative_to(LAB_ROOT)),
            "responses": {
                "wait_test_camp": at_test_camp,
                "capture": capture,
                "input": input_response,
                "wait_base_camp": at_base_camp,
            },
        }
        atomic_json(output / "result.json", result)
        print(f"PASSED (visual review unreviewed): {output / 'result.json'}")
        return 0
    except (OSError, RuntimeError, TimeoutError, KeyError, json.JSONDecodeError) as ex:
        atomic_json(output / "result.json", {
            "schema_version": 1,
            "status": "failed",
            "visual_review": "unreviewed",
            "session": str(session.relative_to(LAB_ROOT)),
            "error": str(ex),
        })
        print(f"FAILED: {ex}", file=sys.stderr)
        return 1
    finally:
        if process.poll() is None:
            process.terminate()
            try:
                process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                process.kill()
                process.wait(timeout=5)


if __name__ == "__main__":
    raise SystemExit(main())
