"""SPOT Linux namespace isolation policy."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from typing import List


class NamespaceType(str, Enum):
    """Linux namespace types supported by SPOT."""

    MOUNT = "mount"
    PID = "pid"
    NETWORK = "network"
    IPC = "ipc"
    UTS = "uts"
    USER = "user"
    CGROUP = "cgroup"


@dataclass
class NamespaceConfig:
    """Configuration for isolated Linux namespaces."""

    enabled: bool = True

    mount: bool = True
    pid: bool = True
    network: bool = True
    ipc: bool = True
    uts: bool = True
    user: bool = True
    cgroup: bool = False

    # SPOT should never automatically join an existing
    # privileged namespace.
    allow_namespace_join: bool = False

    def enabled_namespaces(self) -> List[NamespaceType]:
        """Return the enabled namespace types."""
        namespaces: List[NamespaceType] = []

        if not self.enabled:
            return namespaces

        mapping = {
            NamespaceType.MOUNT: self.mount,
            NamespaceType.PID: self.pid,
            NamespaceType.NETWORK: self.network,
            NamespaceType.IPC: self.ipc,
            NamespaceType.UTS: self.uts,
            NamespaceType.USER: self.user,
            NamespaceType.CGROUP: self.cgroup,
        }

        return [
            namespace
            for namespace, enabled in mapping.items()
            if enabled
        ]


class NamespaceManager:
    """Manage the desired namespace isolation state.

    This component describes the requested namespace boundary.
    Actual Linux namespace creation should occur in a restricted
    execution backend.
    """

    def __init__(
        self,
        config: NamespaceConfig | None = None,
    ) -> None:
        self.config = (
            config
            or NamespaceConfig()
        )

        self.prepared = False

    def validate(self) -> None:
        """Validate namespace configuration."""
        if not self.config.enabled:
            return

        if not self.config.enabled_namespaces():
            raise ValueError(
                "At least one namespace must be enabled."
            )

        if self.config.allow_namespace_join:
            raise ValueError(
                "Joining existing namespaces is disabled by default."
            )

    def prepare(self) -> None:
        """Prepare the namespace configuration."""
        self.validate()
        self.prepared = True

    def cleanup(self) -> None:
        """Release namespace state."""
        self.prepared = False

    def emergency_stop(self) -> None:
        """Immediately invalidate the namespace session."""
        self.prepared = False

    def has(
        self,
        namespace: NamespaceType,
    ) -> bool:
        """Return whether a namespace is enabled."""
        return namespace in (
            self.config.enabled_namespaces()
        )

    def summary(self) -> dict:
        """Return a namespace configuration summary."""
        return {
            "enabled": self.config.enabled,
            "namespaces": [
                namespace.value
                for namespace in self.config.enabled_namespaces()
            ],
            "prepared": self.prepared,
        }
