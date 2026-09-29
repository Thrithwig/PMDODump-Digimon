"""Command-line entry point for the Phase 4 sprite pipeline."""

from pathlib import Path
import sys


scripts_dir = Path(__file__).resolve().parent
if str(scripts_dir) not in sys.path:
    sys.path.insert(0, str(scripts_dir))

from SpritePipeline.cli import main  # noqa: E402


if __name__ == "__main__":
    raise SystemExit(main())
