"""SPOT sandbox policy."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List


@dataclass
class SandboxConfig:
    """Configuration for sandboxed execution."""

    enabled: bool = True

    read_only_system: bool = True
    private_home: bool = True
    private_tmp: bool = True

    no_new_privileges: bool = True

    block_raw_sockets: bool = True
    block_ptrace: bool = True

    allow_device_access: bool = False
    allow_kernel_modules: bool = False

    allowed_capabilities: List[str] = field(
        default_factory=list
    )

    blocked_capabilities: List[str] = field(
        default_factory=lambda: [
            "CAP_SYS_ADMIN",
            "CAP_SYS_MODULE",
            "CAP_SYS_PTRACE",
            "CAP_NET_ADMIN",
            "CAP_NET_RAW",
        ]
    )


class SandboxManager:
    """Describe a least-privilege application sandbox."""

    def __init__(
        self,
        config: SandboxConfig | None = None,
    ) -> None:
        self.config = (
            config
            or SandboxConfig()
        )

        self.prepared = False
        self.stopped = False

    def validate(self) -> None:
        """Validate sandbox configuration."""
        if not self.config.enabled:
            return

        if (
            self.config.allow_device_access
            and self.config.no_new_privileges
        ):
            # Device access is allowed only as an explicit policy
            # choice; it is not granted automatically.
            pass

        for capability in self.config.allowed_capabilities:
            if capability in self.config.blocked_capabilities:
                raise ValueError(
                    "A capability cannot be both allowed and blocked: "
                    f"{capability}"
                )

    def prepare(self) -> None:
        """Prepare sandbox policy."""
        self.validate()

        self.prepared = True
        self.stopped = False

    def cleanup(self) -> None:
        """Clean up sandbox state."""
        self.prepared = False

    def emergency_stop(self) -> None:
        """Disable sandbox execution immediately."""
        self.prepared = False
        self.stopped = True

    def allows_capability(
        self,
        capability: str,
    ) -> bool:
        """Check whether a Linux capability is permitted."""
        if not self.config.enabled:
            return False

        if capability in self.config.blocked_capabilities:
            return False

        return (
            capability
            in self.config.allowed_capabilities
        )

    def summary(self) -> dict:
        """Return the effective sandbox policy."""
        return {
            "enabled": self.config.enabled,
            "read_only_system": (
                self.config.read_only_system
            ),
            "private_home": (
                self.config.private_home
            ),
            "private_tmp": (
                self.config.private_tmp
            ),
            "no_new_privileges": (
                self.config.no_new_privileges
            ),
            "allow_device_access": (
                self.config.allow_device_access
            ),
            "allow_kernel_modules": (
                self.config.allow_kernel_modules
            ),
            "prepared": self.prepared,
            "stopped": self.stopped,
        }
