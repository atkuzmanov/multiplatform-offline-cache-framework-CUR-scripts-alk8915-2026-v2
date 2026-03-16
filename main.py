"""
CLI entrypoint for the offline cache framework.

This file adjusts `sys.path` so that the `src` directory is importable when
you run `python3 main.py` from the project root.
"""

from __future__ import annotations

import sys
from pathlib import Path


def _bootstrap() -> int:
    project_root = Path(__file__).resolve().parent
    src_dir = project_root / "src"
    if str(src_dir) not in sys.path:
        sys.path.insert(0, str(src_dir))

    from offline_cache_framework.cli import main  # type: ignore[import-not-found]

    return main()


if __name__ == "__main__":
    raise SystemExit(_bootstrap())

