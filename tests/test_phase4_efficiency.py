import json
import io
from contextlib import redirect_stdout
import queue
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch, MagicMock

from PIL import Image

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "Scripts"))
from SpritePipeline.actions import (_action_context, _cache_record, _render_chunk,
                                    _render_code_hash, _render_inputs, _write_xml, build_actions)
from SpritePipeline.core import PersistentRenderer
from SpritePipeline.previews import make_previews
from SpritePipeline.cli import main


class EfficiencyTests(unittest.TestCase):
    def test_stalled_response_has_deadline(self):
        worker = PersistentRenderer(Path("model"), Path("renderer"), {})
        worker.responses = queue.Queue()
        with self.assertRaises(TimeoutError):
            worker._response(0.01)

    def test_startup_failure_cleans_server_and_profile(self):
        server = MagicMock()
        server.serve_forever.return_value = None
        worker = PersistentRenderer(Path("model"), Path("renderer"), {})
        with patch("SpritePipeline.core.shutil.which", return_value="node"), \
             patch("SpritePipeline.core._start_server", return_value=(server, 123)), \
             patch("SpritePipeline.core._find_chrome", side_effect=FileNotFoundError("missing chrome")):
            with self.assertRaises(FileNotFoundError):
                worker.__enter__()
        server.shutdown.assert_called_once()
        server.server_close.assert_called_once()
        self.assertIsNone(worker.profile)

    def test_renderer_reported_startup_error_cleans_process(self):
        server = MagicMock()
        process = MagicMock()
        process.stdout = io.StringIO('{"fatal":"model failed"}\n')
        process.stdin = io.StringIO()
        process.poll.return_value = 1
        worker = PersistentRenderer(Path("model"), Path("renderer"), {})
        with patch("SpritePipeline.core.shutil.which", return_value="node"), \
             patch("SpritePipeline.core._start_server", return_value=(server, 123)), \
             patch("SpritePipeline.core._find_chrome", return_value=Path("chrome")), \
             patch("SpritePipeline.core.subprocess.Popen", return_value=process):
            with self.assertRaisesRegex(RuntimeError, "model failed"):
                worker.__enter__()
        server.server_close.assert_called_once()
        self.assertTrue(process.stdout.closed)
        self.assertIsNone(worker.profile)

    def test_failed_chunk_keeps_only_verified_completed_frame(self):
        with tempfile.TemporaryDirectory() as temp:
            first = Path(temp) / "first.png"
            second = Path(temp) / "second.png"
            class FailingWorker:
                def __enter__(self): return self
                def __exit__(self, *args): return None
                def render(self, path, **kwargs):
                    if path == second:
                        raise RuntimeError("simulated render failure")
                    path.write_bytes(b"image")
                    path.with_suffix(".geometry.json").write_text("{}")
            expected = {"render_size": 256, "frame_size": 40, "settings": {}}
            jobs = [(p, 0, 0, "clip", expected) for p in (first, second)]
            with patch("SpritePipeline.actions.PersistentRenderer", return_value=FailingWorker()):
                with self.assertRaisesRegex(RuntimeError, "simulated"):
                    _render_chunk(Path("model"), Path("renderer"), {}, jobs)
            self.assertTrue(_cache_record(first).exists())
            self.assertFalse(_cache_record(second).exists())

    def test_tentomon_identity_and_48px_xml_preview(self):
        with tempfile.TemporaryDirectory() as temp:
            temp = Path(temp)
            actions = temp / "actions.json"
            actions.write_text(json.dumps({"species":"tentomon",
                "approved_idle":"work/phase4/tentomon/output/tentomon",
                "model_path":"work/phase4/source/tentomon.glb",
                "palette_policy":"quantized", "mouth_palette":False,
                "actions":[{"name":"Hurt","clip":"chr303_bd01","seconds":1,
                            "durations":[2,8],"ground_policy":"fixed","events":{"HitFrame":1}}]}))
            config, _, model, baseline, _, installed = _action_context(
                ROOT, ROOT / "config/phase4/tentomon.json", actions)
            self.assertEqual((config["pmdo_index"], config["frame_size"]), (10040, 48))
            self.assertIsNone(installed)
            self.assertEqual(model.name, "tentomon.glb")
            package = temp / "package" / "10040"
            package.mkdir(parents=True)
            spec = json.loads(actions.read_text())["actions"][0]
            _write_xml(baseline / "AnimData.xml", package / "AnimData.xml", [spec],
                       ROOT / "DumpAsset/Base/GFXParams.xml", 48)
            xml = (package / "AnimData.xml").read_text()
            self.assertIn("<FrameWidth>48</FrameWidth>", xml)
            self.assertIn("<HitFrame>1</HitFrame>", xml)
            for kind in ("Anim", "Offsets", "Shadow"):
                Image.new("RGBA", (96, 384), (0,0,0,0)).save(package / f"Hurt-{kind}.png")
            self.assertEqual(make_previews(ROOT, temp, ROOT / "config/phase4/tentomon.json", actions), ["Hurt"])
            with Image.open(temp / "previews/Hurt-contact.png") as image:
                self.assertEqual(image.size, (384, 1536))
            html = (temp / "previews/index.html").read_text()
            self.assertIn("package/10040", html)
            self.assertIn("Tentomon", html)

    def test_accepted_candidate_is_immutable(self):
        with self.assertRaisesRegex(ValueError, "immutable"):
            build_actions(ROOT, ROOT / "work/phase4/agumon-actions", only={"Hurt"})
        with self.assertRaisesRegex(ValueError, "immutable"):
            build_actions(ROOT, ROOT / "work/phase4/agumon-actions/nested", only={"Hurt"})

    def test_unknown_action_rejected_before_output(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "bad"
            with self.assertRaisesRegex(ValueError, "Unknown actions"):
                build_actions(ROOT, output, only={"Imaginary"})
            self.assertFalse(output.exists())

    def test_failed_build_is_resumable_and_unpublished(self):
        with tempfile.TemporaryDirectory() as temp:
            output = Path(temp) / "failed"
            with patch("SpritePipeline.actions._render_chunk", side_effect=RuntimeError("worker broke")):
                with self.assertRaisesRegex(RuntimeError, "worker broke"):
                    build_actions(ROOT, output, only={"Hurt"}, workers=1)
            summary = json.loads((output / "summary.json").read_text())
            self.assertEqual(summary["status"], "failed-resumable")
            self.assertEqual(summary["completed_frames"], 0)
            self.assertFalse((output / "package").exists())

    def test_render_code_hash_ignores_conversion_suffix(self):
        source = (ROOT / "Scripts/SpritePipeline/core.py").read_bytes()
        with tempfile.TemporaryDirectory() as temp:
            path = Path(temp) / "core.py"
            path.write_bytes(source)
            before = _render_code_hash(path)
            path.write_bytes(source + b"\n# downstream conversion note\n")
            self.assertEqual(before, _render_code_hash(path))

    def test_render_identity_tracks_direction_and_dependencies(self):
        base = dict(model_hash="model", renderer_hash="html", capture_hash="batch",
                    core_hash="render-code", clip="clip", seconds=0.25, azimuth=90,
                    render_size=256, frame_size=48, settings={"eye_mode":"source"},
                    direction="Right", dependencies_hash="three-lock")
        original = _render_inputs(**base)
        for change in ({"direction":"Left"}, {"dependencies_hash":"new-three-lock"},
                       {"settings":{"eye_mode":"forward-pupil"}}, {"frame_size":40}):
            self.assertNotEqual(original, _render_inputs(**(base | change)))

    def test_benchmark_pixel_mismatch_exits_nonzero(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            manifest = root / "jobs.json"
            manifest.write_text(json.dumps({"species":"agumon", "jobs":[
                {"clip":"chr050_bn01","time":0,"azimuth":0}]}))
            model = root / "model.glb"
            model.write_bytes(b"test-model")
            output = root / "benchmark"
            def write_frame(path, color):
                path.parent.mkdir(parents=True, exist_ok=True)
                Image.new("RGBA", (1, 1), color).save(path)
                path.with_suffix(".geometry.json").write_text("{}")
            def old_render(model, renderer, path, **kwargs):
                write_frame(path, "red")
            new_color = "blue"
            class NewRenderer:
                def __enter__(self): return self
                def __exit__(self, *args): return None
                def render(self, path, **kwargs): write_frame(path, new_color)
            args = ["benchmark", str(ROOT / "config/phase4/agumon.json"),
                    str(manifest), str(model), str(output)]
            with patch("SpritePipeline.efficiency._read_jobs", return_value=[
                    {"clip":"chr050_bn01","time":0,"azimuth":0}]), \
                 patch("SpritePipeline.efficiency.render_frame", side_effect=old_render), \
                 patch("SpritePipeline.efficiency.PersistentRenderer", return_value=NewRenderer()), \
                 redirect_stdout(io.StringIO()):
                self.assertEqual(main(args), 1)
                new_color = "red"
                self.assertEqual(main(args[:-1] + [str(root / "matching")]), 0)
            report = json.loads((output / "benchmark.json").read_text())
            self.assertFalse(report["parity"])
            self.assertFalse(report["ok"])
            matching = json.loads((root / "matching/benchmark.json").read_text())
            self.assertTrue(matching["parity"])
            self.assertTrue(matching["ok"])


if __name__ == "__main__":
    unittest.main()
