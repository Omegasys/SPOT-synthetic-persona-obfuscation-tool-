"""SPOT filesystem isolation."""

from __future__ import annotations

from dataclasses import dataclass, field
from pathlib import Path
from typing import List


@dataclass
class FilesystemPolicy:
    """Policy controlling filesystem access."""

    allow_read_paths: List[str] = field(
        default_factory=list
    )

    allow_write_paths: List[str] = field(
        default_factory=list
    )

    deny_paths: List[str] = field(
        default_factory=lambda: [
            "/etc/shadow",
            "/etc/gshadow",
            "/root",
            "/home",
        ]
    )

    allow_temporary_directory: bool = True

    private_home: bool = True
    read_only_system: bool = True


class FilesystemIsolation:
    """Describe and enforce SPOT filesystem boundaries.

    This class intentionally performs only bounded filesystem
    preparation. System-wide mount manipulation belongs in a
    privileged integration layer.
    """

    def __init__(
        self,
        root: str | Path | None = None,
        policy: FilesystemPolicy | None = None,
    ) -> None:
        self.root = (
            Path(root).expanduser()
            if root is not None
            else None
        )

        self.policy = (
            policy
            or FilesystemPolicy()
        )

        self.prepared = False

    def prepare(self) -> None:
        """Prepare the isolated filesystem directory."""
        if self.root is not None:
            self.root.mkdir(
                parents=True,
                exist_ok=True,
            )

        self.prepared = True

    def cleanup(self) -> None:
        """Mark the filesystem isolation as inactive.

        Deleting filesystem contents is deliberately not automatic.
        Cleanup policies should be handled by an explicit storage
        component so that accidental data loss is avoided.
        """
        self.prepared = False

    def can_read(
        self,
        path: str | Path,
    ) -> bool:
        """Check whether a path may be read."""
        return self._allowed(
            path,
            self.policy.allow_read_paths,
        )

    def can_write(
        self,
        path: str | Path,
    ) -> bool:
        """Check whether a path may be written."""
        if self.policy.read_only_system:
            path_obj = Path(path).expanduser()

            if str(path_obj).startswith("/etc"):
                return False

        return self._allowed(
            path,
            self.policy.allow_write_paths,
        )

    def resolve(
        self,
        path: str | Path,
    ) -> Path:
        """Resolve a path inside the configured root."""
        path_obj = Path(path).expanduser()

        if self.root is None:
            return path_obj.resolve()

        if path_obj.is_absolute():
            relative = Path(
                str(path_obj).lstrip("/")
            )
        else:
            relative = path_obj

        resolved = (
            self.root / relative
        ).resolve()

        root_resolved = self.root.resolve()

        if (
            resolved != root_resolved
            and root_resolved not in resolved.parents
        ):
            raise PermissionError(
                "Filesystem path escapes isolation root."
            )

        return resolved

    def _allowed(
        self,
        path: str | Path,
        allowed_paths: List[str],
    ) -> bool:
        """Check a path against allow and deny rules."""
        path_obj = Path(path).expanduser()

        if self._matches(
            path_obj,
            self.policy.deny_paths,
        ):
            return False

        if not allowed_paths:
            return False

        return self._matches(
            path_obj,
            allowed_paths,
        )

    @staticmethod
    def _matches(
        path: Path,
        rules: List[str],
    ) -> bool:
        """Return whether a path falls under a policy rule."""
        try:
            resolved = path.resolve()
        except OSError:
            resolved = path.absolute()

        for rule in rules:
            rule_path = Path(rule).expanduser()

            try:
                rule_resolved = rule_path.resolve()
            except OSError:
                rule_resolved = rule_path.absolute()

            if (
                resolved == rule_resolved
                or rule_resolved in resolved.parents
            ):
                return True

        return False
