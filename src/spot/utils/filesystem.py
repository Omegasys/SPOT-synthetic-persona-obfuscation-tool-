"""Filesystem utilities for SPOT."""

from __future__ import annotations

import os
import tempfile
from pathlib import Path
from typing import Iterable, Optional


def ensure_directory(path: Path, mode: int = 0o700) -> Path:
    """Create a directory if necessary."""
    path = Path(path)
    path.mkdir(parents=True, exist_ok=True)

    try:
        path.chmod(mode)
    except OSError:
        pass

    return path


def ensure_parent(path: Path, mode: int = 0o700) -> Path:
    """Create the parent directory for a file."""
    path = Path(path)
    ensure_directory(path.parent, mode=mode)
    return path


def path_exists(path: Path) -> bool:
    """Return whether a path exists."""
    return Path(path).exists()


def is_file(path: Path) -> bool:
    """Return whether a path is a regular file."""
    return Path(path).is_file()


def is_directory(path: Path) -> bool:
    """Return whether a path is a directory."""
    return Path(path).is_dir()


def resolve_path(path: Path) -> Path:
    """Resolve a path without requiring it to exist."""
    return Path(path).expanduser().resolve(strict=False)


def is_within(
    path: Path,
    directory: Path,
) -> bool:
    """Return whether path is contained within directory."""
    path = resolve_path(path)
    directory = resolve_path(directory)

    try:
        path.relative_to(directory)
        return True
    except ValueError:
        return False


def safe_join(
    directory: Path,
    *parts: str,
) -> Path:
    """Join path components while preventing directory escape."""
    directory = resolve_path(directory)
    candidate = resolve_path(directory.joinpath(*parts))

    if not is_within(candidate, directory):
        raise ValueError(
            "Path escapes the permitted directory."
        )

    return candidate


def remove_file(path: Path) -> bool:
    """Remove a regular file if it exists."""
    path = Path(path)

    if not path.exists():
        return False

    if not path.is_file():
        raise ValueError(
            f"Refusing to remove non-file path: {path}"
        )

    path.unlink()
    return True


def list_files(
    directory: Path,
    pattern: str = "*",
) -> list[Path]:
    """List regular files matching a pattern."""
    directory = Path(directory)

    if not directory.is_dir():
        return []

    return [
        item
        for item in directory.glob(pattern)
        if item.is_file()
    ]


def secure_temp_directory(
    prefix: str = "spot-",
    parent: Optional[Path] = None,
) -> Path:
    """Create a private temporary directory."""
    directory = tempfile.mkdtemp(
        prefix=prefix,
        dir=str(parent) if parent else None,
    )

    path = Path(directory)

    try:
        path.chmod(0o700)
    except OSError:
        pass

    return path


def atomic_write(
    path: Path,
    data: bytes,
    mode: int = 0o600,
) -> None:
    """Atomically write bytes to a file."""
    path = Path(path)
    ensure_parent(path)

    fd, temporary = tempfile.mkstemp(
        prefix=f".{path.name}.",
        dir=str(path.parent),
    )

    temporary_path = Path(temporary)

    try:
        os.fchmod(fd, mode)

        with os.fdopen(fd, "wb") as handle:
            handle.write(data)
            handle.flush()
            os.fsync(handle.fileno())

        os.replace(temporary_path, path)

    except Exception:
        try:
            temporary_path.unlink(missing_ok=True)
        except OSError:
            pass
        raise


def read_text(
    path: Path,
    encoding: str = "utf-8",
) -> str:
    """Read UTF-8 text from a file."""
    return Path(path).read_text(encoding=encoding)


def write_text(
    path: Path,
    content: str,
    encoding: str = "utf-8",
    mode: int = 0o600,
) -> None:
    """Atomically write text to a file."""
    atomic_write(
        Path(path),
        content.encode(encoding),
        mode=mode,
    )


def remove_empty_directories(
    directories: Iterable[Path],
) -> int:
    """Remove empty directories.

    Returns the number of directories removed.
    """
    removed = 0

    for directory in directories:
        directory = Path(directory)

        if not directory.is_dir():
            continue

        try:
            directory.rmdir()
            removed += 1
        except OSError:
            pass

    return removed
