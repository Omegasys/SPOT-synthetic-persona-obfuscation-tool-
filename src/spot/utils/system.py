"""Operating-system utilities for SPOT."""

from __future__ import annotations

import os
import platform
import shutil
import subprocess
from dataclasses import dataclass
from typing import Optional, Sequence


@dataclass(frozen=True)
class SystemInfo:
    """Basic information about the host operating system."""

    operating_system: str
    kernel: str
    architecture: str
    hostname: str
    python_version: str
    cpu_count: int


@dataclass(frozen=True)
class CommandResult:
    """Result of a safely executed external command."""

    returncode: int
    stdout: str
    stderr: str


def system_info() -> SystemInfo:
    """Return basic host-system information."""
    return SystemInfo(
        operating_system=platform.system(),
        kernel=platform.release(),
        architecture=platform.machine(),
        hostname=platform.node(),
        python_version=platform.python_version(),
        cpu_count=os.cpu_count() or 1,
    )


def is_linux() -> bool:
    """Return whether SPOT is running on Linux."""
    return platform.system().lower() == "linux"


def is_qubes() -> bool:
    """Return whether the current environment appears to be Qubes OS."""
    if not is_linux():
        return False

    indicators = (
        "/usr/bin/qvm-run-vm",
        "/usr/bin/qrexec-client-vm",
        "/etc/qubes-release",
    )

    return any(os.path.exists(path) for path in indicators)


def command_exists(command: str) -> bool:
    """Return whether an executable is available on PATH."""
    return shutil.which(command) is not None


def execute(
    command: Sequence[str],
    timeout: float = 30.0,
    cwd: Optional[str] = None,
    environment: Optional[dict[str, str]] = None,
) -> CommandResult:
    """Execute a narrowly specified external command.

    Shell execution is intentionally disabled. Callers should provide
    an explicit argument sequence rather than a shell command string.
    """
    if not command:
        raise ValueError("Command cannot be empty.")

    if any(not isinstance(item, str) for item in command):
        raise TypeError("Command arguments must be strings.")

    process = subprocess.run(
        list(command),
        capture_output=True,
        text=True,
        timeout=timeout,
        cwd=cwd,
        env=environment,
        shell=False,
        check=False,
    )

    return CommandResult(
        returncode=process.returncode,
        stdout=process.stdout,
        stderr=process.stderr,
    )


def get_uid() -> int:
    """Return the current Unix user ID."""
    return os.getuid()


def get_gid() -> int:
    """Return the current Unix group ID."""
    return os.getgid()


def is_root() -> bool:
    """Return whether the current process has UID 0."""
    return get_uid() == 0


def cpu_count() -> int:
    """Return the available CPU count."""
    return os.cpu_count() or 1


def available_command(
    command: str,
) -> Optional[str]:
    """Return the executable path if available."""
    return shutil.which(command)


def environment_flag(
    name: str,
    default: bool = False,
) -> bool:
    """Read a simple boolean environment variable."""
    value = os.environ.get(name)

    if value is None:
        return default

    return value.strip().lower() in {
        "1",
        "true",
        "yes",
        "on",
        "enabled",
    }
