"""CLI for the Phase 4 Agumon 3D-to-PMDO pipeline."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

from .core import (
    assemble_package,
    build,
    inspect_glb,
    load_config,
    render_frame,
    validate_package,
)
from .actions import build_actions, validate_actions
from .previews import make_previews
from .efficiency import audition, benchmark
from .idle import build_idle, idle_context, validate_idle


def _config_arg(value: str) -> Path:
    path = Path(value).resolve()
    if not path.exists():
        raise argparse.ArgumentTypeError(f"config does not exist: {path}")
    return path


def parser() -> argparse.ArgumentParser:
    root = argparse.ArgumentParser(description=__doc__)
    sub = root.add_subparsers(dest="command", required=True)

    inspect = sub.add_parser("inspect", help="inspect a DSTS-exported GLB")
    inspect.add_argument("glb", type=Path)

    render = sub.add_parser("render", help="render one GLB frame through the local browser renderer")
    render.add_argument("glb", type=Path)
    render.add_argument("output", type=Path)
    render.add_argument("--azimuth", type=float, default=0)
    render.add_argument("--time", type=float, default=0)
    render.add_argument("--clip", default="chr050_bn01")
    render.add_argument("--size", type=int, default=256)
    render.add_argument("--config", type=_config_arg)

    assemble = sub.add_parser("assemble", help="assemble rendered frames into a PMDO package")
    assemble.add_argument("config", type=_config_arg)
    assemble.add_argument("frames_root", type=Path)
    assemble.add_argument("output_dir", type=Path)
    assemble.add_argument("--gfx-params", type=Path)

    validate = sub.add_parser("validate", help="validate PMDO files and markers")
    validate.add_argument("config", type=_config_arg)
    validate.add_argument("package_dir", type=Path)

    full = sub.add_parser("build", help="render, assemble, validate, and write provenance")
    full.add_argument("config", type=_config_arg)
    full.add_argument("glb", type=Path)
    full.add_argument("output_root", type=Path)
    full.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    initial = sub.add_parser("build-idle", help="build an immutable initial Idle using exact per-frame cache")
    initial.add_argument("config", type=_config_arg)
    initial.add_argument("output_root", type=Path)
    initial.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    initial.add_argument("--model", type=Path, help="override config model_path")
    initial.add_argument("--cache-root", type=Path)
    initial.add_argument("--workers", type=int, default=2)
    initial.add_argument("--assemble-only", action="store_true")
    initial_check = sub.add_parser("validate-idle", help="validate initial Idle and explicit placeholders")
    initial_check.add_argument("config", type=_config_arg)
    initial_check.add_argument("package_dir", type=Path)
    initial_check.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    actions = sub.add_parser("build-actions", help="build Agumon's additional PMDO actions")
    actions.add_argument("output_root", type=Path)
    actions.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    actions.add_argument("--only", action="append", help="diagnostic partial package with only named actions")
    actions.add_argument("--assemble-only", action="store_true", help="reassemble cached model renders without launching Chrome")
    actions.add_argument("--config", type=_config_arg, help="species render config (defaults to Agumon)")
    actions.add_argument("--actions-config", type=_config_arg, help="species actions manifest (defaults to Agumon)")
    actions.add_argument("--cache-root", type=Path, help="reuse verified render frames across candidate revisions")
    actions.add_argument("--workers", type=int, default=2)
    check_actions = sub.add_parser("validate-actions", help="validate Agumon's additional PMDO actions")
    check_actions.add_argument("output_root", type=Path)
    check_actions.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    check_actions.add_argument("--config", type=_config_arg)
    check_actions.add_argument("--actions-config", type=_config_arg)
    previews = sub.add_parser("previews", help="make transparent review previews for completed actions")
    previews.add_argument("output_root", type=Path)
    previews.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[2])
    previews.add_argument("--config", type=_config_arg)
    previews.add_argument("--actions-config", type=_config_arg)
    for name in ("benchmark", "audition"):
        command = sub.add_parser(name, help=f"run a bounded {name} manifest")
        command.add_argument("config", type=_config_arg)
        command.add_argument("manifest", type=_config_arg)
        command.add_argument("glb", type=Path)
        command.add_argument("output_root", type=Path)
        if name == "benchmark":
            command.add_argument("--baseline-renderer", type=Path)
    return root


def main(argv: list[str] | None = None) -> int:
    args = parser().parse_args(argv)
    if args.command == "inspect":
        result = inspect_glb(args.glb)
    elif args.command == "render":
        config = load_config(args.config) if args.config else {}
        render_frame(
            args.glb,
            Path(__file__).resolve().parent / "renderer",
            args.output,
            azimuth_degrees=args.azimuth,
            time_seconds=args.time,
            clip_name=config.get("idle_clip", args.clip),
            render_size=config.get("render_size", args.size),
            frame_size=config.get("frame_size", 40),
            render_settings=config.get("renderer", {}),
        )
        result = {"ok": True, "output": str(args.output)}
    elif args.command == "assemble":
        config = load_config(args.config)
        result = assemble_package(config, args.frames_root, args.output_dir, gfx_params=args.gfx_params)
    elif args.command == "validate":
        config = load_config(args.config)
        result = validate_package(args.package_dir, config)
    elif args.command == "build-idle":
        result = build_idle(args.repo_root,args.config,args.output_root,model_path=args.model,
                            cache_root=args.cache_root,workers=args.workers,assemble_only=args.assemble_only)
    elif args.command == "validate-idle":
        result = validate_idle(args.repo_root,load_config(args.config),args.package_dir)
    elif args.command == "build-actions":
        result = build_actions(args.repo_root, args.output_root, set(args.only) if args.only else None,
                               assemble_only=args.assemble_only, config_path=args.config,
                               actions_path=args.actions_config, workers=args.workers,
                               cache_root=args.cache_root)
    elif args.command == "validate-actions":
        result = validate_actions(args.repo_root, args.output_root,
                                  config_path=args.config, actions_path=args.actions_config)
    elif args.command == "previews":
        result = {"actions": make_previews(args.repo_root, args.output_root,
                                            config_path=args.config, actions_path=args.actions_config)}
    elif args.command in ("benchmark", "audition"):
        config = load_config(args.config)
        if config["species"] != json.loads(args.manifest.read_text(encoding="utf-8")).get("species"):
            raise ValueError("manifest species does not match renderer config")
        runner = benchmark if args.command == "benchmark" else audition
        extra = {"baseline_renderer": args.baseline_renderer} if args.command == "benchmark" else {}
        result = runner(args.manifest, args.glb, Path(__file__).resolve().parent / "renderer",
                        args.output_root, config.get("renderer", {}),
                        config["render_size"], config["frame_size"], **extra)
    else:
        result = build(args.config, args.glb, args.output_root, args.repo_root)
    print(json.dumps(result, indent=2))
    return 0 if result.get("validation", result).get("ok", True) else 1
