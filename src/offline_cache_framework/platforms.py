from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from pathlib import Path


class OSType(str, Enum):
    WINDOWS = "windows"
    MACOS = "macos"
    LINUX = "linux"


class CPUArch(str, Enum):
    X86 = "x86"        # 32-bit
    X64 = "x64"        # 64-bit
    ARM = "arm"
    ARM64 = "arm64"
    I386 = "i386"


@dataclass(frozen=True)
class Target:
    os: OSType
    arch: CPUArch
    distro: str | None = None  # e.g. ubuntu, debian, arch, fedora, rhel

    @property
    def cache_subdir(self) -> Path:
        """
        Map a target to a relative cache path, e.g.:
        linux/ubuntu/x64, linux/ubuntu/arm64, windows/x86, macos/apple_silicon, etc.
        """
        parts = [self.os.value]
        if self.os is OSType.LINUX and self.distro:
            parts.append(self.distro)
        parts.append(self.arch.value)
        return Path(*parts)


# Common targets we care about

WINDOWS_X86 = Target(OSType.WINDOWS, CPUArch.X86)
WINDOWS_X64 = Target(OSType.WINDOWS, CPUArch.X64)
WINDOWS_ARM64 = Target(OSType.WINDOWS, CPUArch.ARM64)

MACOS_INTEL = Target(OSType.MACOS, CPUArch.X64)
MACOS_APPLE_SILICON = Target(OSType.MACOS, CPUArch.ARM64)

LINUX_UBUNTU_X64 = Target(OSType.LINUX, CPUArch.X64, "ubuntu")
LINUX_UBUNTU_I386 = Target(OSType.LINUX, CPUArch.I386, "ubuntu")
LINUX_UBUNTU_ARMHF = Target(OSType.LINUX, CPUArch.ARM, "ubuntu")
LINUX_UBUNTU_ARM64 = Target(OSType.LINUX, CPUArch.ARM64, "ubuntu")

LINUX_DEBIAN_X64 = Target(OSType.LINUX, CPUArch.X64, "debian")
LINUX_DEBIAN_I386 = Target(OSType.LINUX, CPUArch.I386, "debian")

LINUX_FEDORA_X64 = Target(OSType.LINUX, CPUArch.X64, "fedora")
LINUX_RHEL_X64 = Target(OSType.LINUX, CPUArch.X64, "rhel")

LINUX_ARCH_X64 = Target(OSType.LINUX, CPUArch.X64, "arch")


ALL_DEFAULT_TARGETS: list[Target] = [
    WINDOWS_X86,
    WINDOWS_X64,
    WINDOWS_ARM64,
    MACOS_INTEL,
    MACOS_APPLE_SILICON,
    LINUX_UBUNTU_X64,
    LINUX_UBUNTU_I386,
    LINUX_UBUNTU_ARMHF,
    LINUX_UBUNTU_ARM64,
    LINUX_DEBIAN_X64,
    LINUX_DEBIAN_I386,
    LINUX_FEDORA_X64,
    LINUX_RHEL_X64,
    LINUX_ARCH_X64,
]

