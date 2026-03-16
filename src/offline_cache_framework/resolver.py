from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable
from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from .platforms import Target, OSType


DOWNLOAD_EXTENSIONS = (
    ".deb",
    ".rpm",
    ".tar.gz",
    ".tar.xz",
    ".pkg",
    ".dmg",
    ".exe",
    ".msi",
    ".zip",
)


@dataclass
class CandidateDownload:
    url: str
    target_hint: Target | None = None


def _guess_target_from_href(href: str, base_target: Target | None) -> Target | None:
    """
    Best-effort mapping from a link's href text to a more specific target.
    The manifests and cache structure are responsible for the final target.
    """
    if base_target is None:
        return None

    href_lower = href.lower()

    # Heuristics – these can be expanded as needed per vendor.
    if base_target.os is OSType.WINDOWS:
        # Example substrings: x86, x64, arm64
        from .platforms import CPUArch

        if "arm64" in href_lower or "aarch64" in href_lower:
            return Target(base_target.os, CPUArch.ARM64)
        if "x86_64" in href_lower or "x64" in href_lower or "64" in href_lower:
            return Target(base_target.os, CPUArch.X64)
        if "x86" in href_lower or "32" in href_lower or "i386" in href_lower:
            return Target(base_target.os, CPUArch.X86)

    if base_target.os is OSType.MACOS:
        from .platforms import CPUArch

        if "arm64" in href_lower or "aarch64" in href_lower or "apple-silicon" in href_lower:
            return Target(base_target.os, CPUArch.ARM64)
        if "intel" in href_lower or "x86_64" in href_lower or "x64" in href_lower:
            return Target(base_target.os, CPUArch.X64)

    if base_target.os is OSType.LINUX:
        from .platforms import CPUArch

        distro = base_target.distro
        # Very rough distro hints
        if "ubuntu" in href_lower:
            distro = "ubuntu"
        elif "debian" in href_lower:
            distro = "debian"
        elif "fedora" in href_lower:
            distro = "fedora"
        elif "rhel" in href_lower:
            distro = "rhel"
        elif "arch" in href_lower:
            distro = "arch"

        if "arm64" in href_lower or "aarch64" in href_lower:
            arch = CPUArch.ARM64
        elif "arm" in href_lower:
            arch = CPUArch.ARM
        elif "i386" in href_lower or "i686" in href_lower:
            arch = CPUArch.I386
        elif "x86_64" in href_lower or "x64" in href_lower:
            arch = CPUArch.X64
        else:
            arch = base_target.arch

        return Target(base_target.os, arch, distro)

    return base_target


def discover_downloads(
    page_url: str,
    expected_targets: Iterable[Target] | None = None,
    session: requests.Session | None = None,
) -> list[CandidateDownload]:
    """
    Fetch a vendor download page and extract candidate installer links.

    This is deliberately generic: it looks for anchor tags whose `href`
    ends with known installer extensions and associates them with a best-effort
    target hint so that the caller can route them into the right cache folder.
    """
    sess = session or requests.Session()
    resp = sess.get(page_url, timeout=30)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")

    page_host = urlparse(page_url).netloc

    candidates: list[CandidateDownload] = []

    for a in soup.find_all("a", href=True):
        href: str = a["href"]
        if not href:
            continue
        full_url = urljoin(page_url, href)

        url_lower = full_url.lower()

        # First: direct links that already have a known installer extension.
        if not url_lower.endswith(DOWNLOAD_EXTENSIONS):
            # Second chance: some sites (like GitKraken) use intermediate
            # "pretty" URLs such as `/download/windows64` which then redirect
            # to the actual `.msi`/`.dmg`/`.deb` file. For URLs on the same
            # host that look like download endpoints, follow the redirect
            # with a HEAD request and inspect the final URL.
            parsed = urlparse(full_url)
            if parsed.netloc == page_host and "download" in parsed.path:
                try:
                    head_resp = sess.head(full_url, allow_redirects=True, timeout=30)
                    final_url = str(head_resp.url)
                    if not str(final_url).lower().endswith(DOWNLOAD_EXTENSIONS):
                        continue
                    full_url = final_url
                    url_lower = full_url.lower()
                except Exception:
                    # If anything goes wrong, just skip this link.
                    continue
            else:
                continue

        base_target = None
        if expected_targets:
            # If we know the context (e.g. "we're scraping a Linux page"),
            # use the first target as a base for guessing; more complex logic
            # can be added later.
            base_target = next(iter(expected_targets), None)

        target_hint = _guess_target_from_href(full_url, base_target)
        candidates.append(CandidateDownload(url=full_url, target_hint=target_hint))

    return candidates

