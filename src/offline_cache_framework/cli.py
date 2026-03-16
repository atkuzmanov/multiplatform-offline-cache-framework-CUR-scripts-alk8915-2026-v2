from __future__ import annotations

import argparse
from pathlib import Path

import requests

from .alternatives import NoopAlternativeStrategy
from .downloader import download_candidates
from .manifests import load_manifests_dir
from .platforms import ALL_DEFAULT_TARGETS, Target
from .resolver import discover_downloads


def build_arg_parser() -> argparse.ArgumentParser:
    p = argparse.ArgumentParser(
        description=(
            "Multiplatform offline cache builder (v2).\n"
            "Given a manifests directory, discovers and downloads installers "
            "for multiple platforms into an offline cache tree."
        )
    )
    p.add_argument(
        "--manifests",
        type=Path,
        required=True,
        help="Path to the manifests directory (e.g. manifests/macos, manifests/ubuntu, ...).",
    )
    p.add_argument(
        "--cache-root",
        type=Path,
        required=True,
        help="Root directory where offline cache will be stored.",
    )
    p.add_argument(
        "--platform-target",
        type=str,
        default="all",
        help=(
            "Optional high-level platform target hint, e.g. 'macos', 'windows', 'ubuntu', 'arm'.\n"
            "This influences which default targets are assumed while scraping."
        ),
    )
    return p


def _select_targets(platform_target: str) -> list[Target]:
    platform_target = platform_target.lower().strip()
    if platform_target in ("all", ""):
        return list(ALL_DEFAULT_TARGETS)

    selected: list[Target] = []
    for t in ALL_DEFAULT_TARGETS:
        if platform_target in (t.os.value, t.distro or ""):
            selected.append(t)
        elif platform_target == "arm" and ("arm" in t.arch.value):
            selected.append(t)
    return selected or list(ALL_DEFAULT_TARGETS)


def main(argv: list[str] | None = None) -> int:
    parser = build_arg_parser()
    args = parser.parse_args(argv)

    manifests_dir: Path = args.manifests
    cache_root: Path = args.cache_root
    platform_target: str = args.platform_target

    software_entries = load_manifests_dir(manifests_dir)
    if not software_entries:
        print(f"No manifest entries found in {manifests_dir}")
        return 1

    targets = _select_targets(platform_target)
    session = requests.Session()
    alt_strategy = NoopAlternativeStrategy()

    for entry in software_entries:
        name = entry.name
        page_url = entry.download_page or entry.homepage
        if not page_url:
            print(f"[WARN] {name}: no homepage/download_page in manifest, skipping.")
            continue

        print(f"Processing {name} from {page_url}")

        # In this first version we simply try to discover all installer links
        # from the given page and classify them according to the selected targets.
        # More refined per-platform scraping can be added on top of this.
        try:
            candidates = discover_downloads(page_url, expected_targets=targets, session=session)
        except Exception as e:  # pragma: no cover - defensive, I/O heavy
            print(f"[ERROR] Failed to discover downloads for {name}: {e}")
            candidates = []

        if not candidates:
            # This is where alternative discovery would be triggered if a piece
            # of software is not available for a given platform. For now, the
            # strategy is a stub and returns nothing.
            print(f"[INFO] No installers found for {name}. Looking for alternatives (stub).")
            for target in targets:
                _ = alt_strategy.find_alternatives(name, target, limit=2)
            continue

        print(f"  Found {len(candidates)} candidate installer(s) for {name}. Downloading...")
        download_candidates(cache_root, candidates, default_target=None, session=session)

    print("Done.")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

