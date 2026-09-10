"""SPOT Qubes networking policy."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


class QubesNetworkMode:
    """Supported SPOT Qubes network modes."""

    OFFLINE = "offline"
    DIRECT = "direct"
    WHONIX = "whonix"


@dataclass
class QubesNetworkPolicy:
    """Network policy for a SPOT Qube."""

    mode: str = QubesNetworkMode.WHONIX

    fail_closed: bool = True

    allow_direct_network: bool = False

    netvm: str | None = "sys-whonix"

    allowed_netvms: List[str] = field(
        default_factory=lambda: [
            "sys-whonix",
        ]
    )


@dataclass
class QubeNetworkAssignment:
    """Network assignment for a specific Qube."""

    qube_name: str
    netvm: str | None
    mode: str

    active: bool = False


class QubesNetworkManager:
    """Manage declarative Qubes network assignments."""

    def __init__(
        self,
        policy: QubesNetworkPolicy | None = None,
    ) -> None:
        self.policy = (
            policy
            or QubesNetworkPolicy()
        )

        self.assignments: Dict[
            str,
            QubeNetworkAssignment,
        ] = {}

        self.stopped = False

    def validate(self) -> None:
        """Validate the network policy."""
        allowed_modes = {
            QubesNetworkMode.OFFLINE,
            QubesNetworkMode.DIRECT,
            QubesNetworkMode.WHONIX,
        }

        if self.policy.mode not in allowed_modes:
            raise ValueError(
                f"Unsupported Qubes network mode: "
                f"{self.policy.mode}"
            )

        if (
            self.policy.mode
            == QubesNetworkMode.DIRECT
            and not self.policy.allow_direct_network
        ):
            raise PermissionError(
                "Direct Qubes networking is disabled."
            )

        if (
            self.policy.mode
            == QubesNetworkMode.WHONIX
            and not self.policy.netvm
        ):
            raise ValueError(
                "Whonix mode requires a netvm."
            )

        if (
            self.policy.netvm
            and self.policy.allowed_netvms
            and self.policy.netvm
            not in self.policy.allowed_netvms
        ):
            raise PermissionError(
                "Configured netvm is not allowlisted."
            )

    def assign(
        self,
        qube_name: str,
        netvm: str | None = None,
    ) -> QubeNetworkAssignment:
        """Prepare a network assignment."""
        self.validate()

        selected_netvm = (
            netvm
            if netvm is not None
            else self.policy.netvm
        )

        if selected_netvm:
            if (
                self.policy.allowed_netvms
                and selected_netvm
                not in self.policy.allowed_netvms
            ):
                raise PermissionError(
                    "Requested netvm is not allowlisted."
                )

        if (
            self.policy.mode
            == QubesNetworkMode.OFFLINE
        ):
            selected_netvm = None

        assignment = QubeNetworkAssignment(
            qube_name=qube_name,
            netvm=selected_netvm,
            mode=self.policy.mode,
        )

        self.assignments[qube_name] = assignment

        return assignment

    def start(
        self,
        qube_name: str,
    ) -> QubeNetworkAssignment:
        """Mark a network assignment active."""
        assignment = self.assignments.get(qube_name)

        if assignment is None:
            raise KeyError(
                f"No network assignment for Qube: {qube_name}"
            )

        if self.stopped:
            raise RuntimeError(
                "Qubes networking is emergency-stopped."
            )

        assignment.active = True
        return assignment

    def stop(
        self,
        qube_name: str,
    ) -> None:
        """Stop networking for a Qube."""
        assignment = self.assignments.get(qube_name)

        if assignment is not None:
            assignment.active = False

    def emergency_stop(self) -> None:
        """Disable all managed Qubes networking."""
        self.stopped = True

        for assignment in self.assignments.values():
            assignment.active = False

    def reset(self) -> None:
        """Reset the emergency-stop state."""
        self.stopped = False

    def active(self) -> List[QubeNetworkAssignment]:
        """Return active network assignments."""
        return [
            assignment
            for assignment in self.assignments.values()
            if assignment.active
        ]
