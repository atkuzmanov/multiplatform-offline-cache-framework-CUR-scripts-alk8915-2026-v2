from __future__ import annotations

from pathlib import Path
from typing import Iterable

import requests
from tqdm import tqdm

from .platforms import Target
from .resolver import CandidateDownload


def _safe_filename_from_url(url: str) -> str:
    name = url.split("/")[-1] or "download"
    # Extremely simple sanitisation
    return name.replace("?", "_").replace("&", "_").replace("#", "_")


def download_candidates(
    cache_root: Path,
    candidates: Iterable[CandidateDownload],
    default_target: Target | None = None,
    session: requests.Session | None = None,
) -> None:
    """
    Download all candidate URLs into the cache root.

    If a candidate has a `target_hint`, its cache path is:
        cache_root / target_hint.cache_subdir / <filename>
    otherwise, if `default_target` is provided, that is used.
    """
    cache_root.mkdir(parents=True, exist_ok=True)
    sess = session or requests.Session()

    for cand in tqdm(list(candidates), desc="Downloading installers"):
        target = cand.target_hint or default_target
        if target is None:
            # Put into a generic bucket if we really can't classify it.
            target_dir = cache_root / "unknown"
        else:
            target_dir = cache_root / target.cache_subdir
        target_dir.mkdir(parents=True, exist_ok=True)

        filename = _safe_filename_from_url(cand.url)
        dest = target_dir / filename

        if dest.exists():
            # Already cached
            continue

        with sess.get(cand.url, stream=True, timeout=120) as r:
            r.raise_for_status()
            with dest.open("wb") as f:
                for chunk in r.iter_content(chunk_size=1024 * 256):
                    if not chunk:
                        continue
                    f.write(chunk)

