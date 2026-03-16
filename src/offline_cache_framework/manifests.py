from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path
from typing import Any

import yaml


@dataclass
class SoftwareEntry:
    name: str
    # Optional vendor or download page URL to start discovery from
    homepage: str | None = None
    download_page: str | None = None


def load_manifest_file(path: Path) -> list[SoftwareEntry]:
    """
    Load a single YAML manifest file that looks like:

    items:
      - name: GitKraken
        homepage: https://www.gitkraken.com/
        download_page: https://www.gitkraken.com/download
      - name: SomeOtherTool
        homepage: https://example.com/
    """
    with path.open("r", encoding="utf-8") as f:
        data: dict[str, Any] = yaml.safe_load(f) or {}

    items = data.get("items", []) or []
    result: list[SoftwareEntry] = []
    for raw in items:
        if not isinstance(raw, dict):
            continue
        name = str(raw.get("name") or "").strip()
        if not name:
            continue
        result.append(
            SoftwareEntry(
                name=name,
                homepage=raw.get("homepage"),
                download_page=raw.get("download_page"),
            )
        )
    return result


def load_manifests_dir(directory: Path) -> list[SoftwareEntry]:
    """
    Load all YAML/JSON manifests from a directory.
    For now we support only YAML (`*.yml` / `*.yaml`) for simplicity.
    """
    entries: list[SoftwareEntry] = []
    if not directory.exists():
        return entries

    for path in sorted(directory.glob("*.yml")) + sorted(directory.glob("*.yaml")):
        entries.extend(load_manifest_file(path))
    return entries

