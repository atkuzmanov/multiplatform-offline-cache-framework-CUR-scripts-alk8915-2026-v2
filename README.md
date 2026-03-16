Multiplatform Offline Cache Framework – CUR Scripts – alk8915 – 2026 – v2
========================================================================

This project is a **multiplatform offline cache builder**. It is designed to
take **manifests of desired software** and **pre-download installers**
for many OS / architecture combinations into a structured offline cache.

### Goals

- **Input**: A *manifests folder* (e.g. `manifests/macos`, `manifests/ubuntu`,
  `manifests/windows`, `manifests/arm`), each containing one or more manifest
  files describing software to acquire.
- **Output**: A **cache directory** tree containing downloaded artifacts for:
  - Linux (Ubuntu/Debian, Arch, Fedora/RHEL) – x86_64, i386, ARM variants
  - macOS (Intel, Apple Silicon)
  - Windows (x86, x64, ARM64)
- **Behaviour**:
  - For each software entry, discover and download **all available installers**
    for the supported platforms (e.g. `.deb`, `.rpm`, `.tar.gz`, `.pkg`,
    `.dmg`, `.exe`, `.msi`, `.zip`).
  - If a software is **not available for a given platform**, download
    **top 2 alternatives** for that platform instead (extensible hook; initial
    implementation uses a pluggable strategy and leaves room for smarter
    search later).

### High-level design

- **Language**: Python 3 (single-file CLI plus small package).
- **Core components**:
  - `platforms` – declares OS / architecture targets and cache layout.
  - `manifests` – simple YAML/JSON manifests per platform.
  - `resolver` – given a software entry, resolves candidate download URLs
    (per platform) from vendor pages using simple heuristics.
  - `downloader` – downloads installers into the correct cache subfolders.
  - `alternatives` – strategy interface for finding alternatives when a
    requested software is unavailable on a target platform.
  - `cli` – entrypoint script you run on any OS.

This v2 project is **new and self-contained** and does **not** modify any of
your existing v1 projects.

