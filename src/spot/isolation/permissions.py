"""SPOT isolation permissions."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, Iterable, Set


class Permission(str, Enum):
    """Capabilities that may be granted to an isolated session."""

    FILESYSTEM_READ = "filesystem.read"
    FILESYSTEM_WRITE = "filesystem.write"

    NETWORK = "network"
    DNS = "network.dns"

    BROWSER = "browser"
    PROCESS = "process"

    IPC = "ipc"

    CONTAINER = "container"

    DEVICE = "device"
    CREDENTIALS = "credentials"
    PERSONAL_DATA = "personal_data"

    QUBES_RPC = "qubes.rpc"


@dataclass
class PermissionPolicy:
    """Default-deny permission policy."""

    default_allow: bool = False

    granted: Set[Permission] = field(
        default_factory=set
    )

    denied: Set[Permission] = field(
        default_factory=lambda: {
            Permission.CREDENTIALS,
            Permission.PERSONAL_DATA,
            Permission.QUBES_RPC,
            Permission.DEVICE,
        }
    )


class PermissionManager:
    """Control capabilities available to isolated SPOT sessions."""

    def __init__(
        self,
        policy: PermissionPolicy | None = None,
    ) -> None:
        self.policy = (
            policy
            or PermissionPolicy()
        )

        self.overrides: Dict[
            str,
            Set[Permission],
        ] = {}

    def grant(
        self,
        permission: Permission,
        session_id: str | None = None,
    ) -> None:
        """Grant a permission unless explicitly forbidden."""
        if permission in self.policy.denied:
            raise PermissionError(
                f"Permission is permanently denied: "
                f"{permission.value}"
            )

        if session_id is None:
            self.policy.granted.add(permission)
            return

        self.overrides.setdefault(
            session_id,
            set(),
        ).add(permission)

    def revoke(
        self,
        permission: Permission,
        session_id: str | None = None,
    ) -> None:
        """Revoke a permission."""
        if session_id is None:
            self.policy.granted.discard(permission)
            return

        permissions = self.overrides.get(
            session_id
        )

        if permissions is not None:
            permissions.discard(permission)

    def deny(
        self,
        permission: Permission,
    ) -> None:
        """Permanently deny a permission."""
        self.policy.denied.add(permission)
        self.policy.granted.discard(permission)

        for permissions in self.overrides.values():
            permissions.discard(permission)

    def allows(
        self,
        permission: Permission,
        session_id: str | None = None,
    ) -> bool:
        """Return whether a permission is allowed."""
        if permission in self.policy.denied:
            return False

        if session_id is not None:
            session_permissions = self.overrides.get(
                session_id,
                set(),
            )

            if permission in session_permissions:
                return True

        if permission in self.policy.granted:
            return True

        return self.policy.default_allow

    def require(
        self,
        permission: Permission,
        session_id: str | None = None,
    ) -> None:
        """Raise an error if a permission is unavailable."""
        if not self.allows(
            permission,
            session_id,
        ):
            raise PermissionError(
                f"Permission denied: {permission.value}"
            )

    def grant_many(
        self,
        permissions: Iterable[Permission],
        session_id: str | None = None,
    ) -> None:
        """Grant several permissions."""
        for permission in permissions:
            self.grant(
                permission,
                session_id=session_id,
            )

    def clear_session(
        self,
        session_id: str,
    ) -> None:
        """Remove all session-specific permissions."""
        self.overrides.pop(
            session_id,
            None,
        )

    def summary(
        self,
        session_id: str | None = None,
    ) -> dict:
        """Return a permission summary."""
        granted = set(
            self.policy.granted
        )

        if session_id is not None:
            granted.update(
                self.overrides.get(
                    session_id,
                    set(),
                )
            )

        return {
            "default_allow": self.policy.default_allow,
            "granted": sorted(
                permission.value
                for permission in granted
            ),
            "denied": sorted(
                permission.value
                for permission in self.policy.denied
            ),
        }
