from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
import shutil
from typing import Any, Mapping, Optional

from spot.plugins.interface import PluginMetadata, SPOTPlugin


class QubesPluginStatus(str, Enum):
    """Possible Qubes plugin states."""

    DISABLED = "disabled"
    CONFIGURED = "configured"
    AVAILABLE = "available"
    UNAVAILABLE = "unavailable"
    BLOCKED = "blocked"
    ERROR = "error"


class QubeType(str, Enum):
    """Supported Qube types for SPOT personas."""

    APPVM = "appvm"
    DISPOSABLE = "disposable"


class QubesNetworkMode(str, Enum):
    """Supported SPOT Qubes networking modes."""

    OFFLINE = "offline"
    WHONIX = "whonix"


@dataclass
class QubeAssignment:
    """Mapping between a SPOT persona and a Qube."""

    persona_id: str
    qube_name: str
    qube_type: QubeType = QubeType.APPVM

    network_mode: QubesNetworkMode = QubesNetworkMode.WHONIX
    network_qube: str = "sys-whonix"

    enabled: bool = True
    destroy_after_stop: bool = False

    metadata: dict[str, Any] = field(default_factory=dict)

    def validate(self) -> None:
        if not self.persona_id.strip():
            raise ValueError("persona_id cannot be empty.")

        if not self.qube_name.strip():
            raise ValueError("qube_name cannot be empty.")

        if not self.network_qube.strip():
            raise ValueError("network_qube cannot be empty.")

        if self.qube_type == QubeType.DISPOSABLE:
            if not self.destroy_after_stop:
                raise ValueError(
                    "Disposable Qubes must be destroyed after use."
                )

        if self.qube_type == QubeType.APPVM:
            if self.destroy_after_stop:
                raise ValueError(
                    "Persistent AppVM assignments cannot use "
                    "destroy_after_stop."
                )

        if self.network_mode == QubesNetworkMode.OFFLINE:
            if self.network_qube:
                # Offline assignments do not use a network qube.
                self.network_qube = ""

        elif self.network_mode == QubesNetworkMode.WHONIX:
            if not self.network_qube.strip():
                raise ValueError(
                    "Whonix assignments require a network Qube."
                )


@dataclass
class QubesRPCPolicy:
    """Default-deny policy for SPOT Qubes RPC services."""

    allowed_services: set[str] = field(default_factory=set)

    denied_services: set[str] = field(
        default_factory=lambda: {
            "admin.vm.Create",
            "admin.vm.Remove",
            "admin.vm.Start",
            "admin.vm.Shutdown",
            "admin.vm.property.Set",
            "admin.vm.device.Attach",
            "admin.vm.device.Detach",
            "admin.vm.volume.Import",
            "admin.vm.volume.ImportWithSize",
        }
    )

    allow_dom0: bool = False
    allow_arbitrary_commands: bool = False
    allow_shell: bool = False

    def validate_service(self, service: str) -> None:
        if not service or not service.strip():
            raise ValueError("RPC service cannot be empty.")

        if service in self.denied_services:
            raise PermissionError(
                f"RPC service explicitly denied: {service}"
            )

        if service not in self.allowed_services:
            raise PermissionError(
                f"RPC service not explicitly allowed: {service}"
            )

    def allows(self, service: str) -> bool:
        """Return whether a service is explicitly permitted."""

        try:
            self.validate_service(service)
        except (ValueError, PermissionError):
            return False

        return True


@dataclass
class QubesRPCRequest:
    """Validated request for a narrow Qubes RPC operation."""

    service: str
    operation: str
    persona_id: Optional[str] = None
    qube_name: Optional[str] = None

    def validate(
        self,
        policy: QubesRPCPolicy,
    ) -> None:
        policy.validate_service(self.service)

        if not self.operation.strip():
            raise ValueError("RPC operation cannot be empty.")

        if self.operation in {
            "exec",
            "shell",
            "arbitrary-command",
        }:
            raise PermissionError(
                "Arbitrary command execution is not permitted."
            )

        if self.qube_name and not self.qube_name.strip():
            raise ValueError(
                "qube_name cannot be empty when provided."
            )

        if self.persona_id and not self.persona_id.strip():
            raise ValueError(
                "persona_id cannot be empty when provided."
            )


class QubesPlugin(SPOTPlugin):
    """
    Controlled Qubes OS integration plugin.

    This class provides policy and state integration. It does not
    execute arbitrary dom0 commands or unrestricted Qubes operations.
    """

    metadata = PluginMetadata(
        id="platform-qubes",
        name="Qubes Platform Plugin",
        version="0.1.0",
        description=(
            "Provides controlled Qubes OS integration for SPOT."
        ),
    )

    def __init__(
        self,
        enabled: bool = True,
        require_whonix: bool = True,
        fail_closed: bool = True,
        allow_direct_network: bool = False,
        assignments: Optional[
            Mapping[str, QubeAssignment]
        ] = None,
        rpc_policy: Optional[QubesRPCPolicy] = None,
    ) -> None:
        self.enabled = enabled
        self.require_whonix = require_whonix
        self.fail_closed = fail_closed
        self.allow_direct_network = allow_direct_network

        self.assignments: dict[str, QubeAssignment] = dict(
            assignments or {}
        )

        self.rpc_policy = rpc_policy or QubesRPCPolicy()

        self._initialized = False
        self._running = False
        self._blocked = False

        self.context: Any = None

    def initialize(self, context: Any) -> bool:
        """Initialize the Qubes plugin."""

        if self.fail_closed and self.allow_direct_network:
            return False

        try:
            for assignment in self.assignments.values():
                assignment.validate()
        except ValueError:
            return False

        self.context = context
        self._initialized = True

        return True

    def start(self) -> bool:
        """Start the Qubes integration."""

        if not self._initialized:
            return False

        if not self.enabled:
            return False

        if self._blocked:
            return False

        self._running = True

        return True

    def stop(self) -> bool:
        """Stop the Qubes integration."""

        self._running = False

        return True

    def health_check(self) -> bool:
        """Return whether the plugin is operational."""

        return (
            self._initialized
            and self._running
            and self.enabled
            and not self._blocked
        )

    @property
    def status(self) -> QubesPluginStatus:
        """Return the current plugin state."""

        if self._blocked:
            return QubesPluginStatus.BLOCKED

        if not self.enabled:
            return QubesPluginStatus.DISABLED

        if not self._initialized:
            return QubesPluginStatus.UNAVAILABLE

        if self._running:
            return QubesPluginStatus.AVAILABLE

        return QubesPluginStatus.CONFIGURED

    def detect_qubes(self) -> bool:
        """
        Detect whether Qubes command tooling is available.

        This is only an environment check. It does not execute any
        Qubes management command.
        """

        return shutil.which("qvm-check") is not None

    def add_assignment(
        self,
        assignment: QubeAssignment,
    ) -> None:
        """Add a validated persona-to-Qube assignment."""

        assignment.validate()

        if assignment.persona_id in self.assignments:
            raise ValueError(
                f"Persona already assigned: "
                f"{assignment.persona_id}"
            )

        self.assignments[assignment.persona_id] = assignment

    def remove_assignment(
        self,
        persona_id: str,
    ) -> QubeAssignment:
        """Remove and return a persona assignment."""

        if persona_id not in self.assignments:
            raise KeyError(persona_id)

        return self.assignments.pop(persona_id)

    def assignment_for(
        self,
        persona_id: str,
    ) -> QubeAssignment:
        """Return a persona's Qube assignment."""

        try:
            return self.assignments[persona_id]
        except KeyError as exc:
            raise KeyError(
                f"No Qube assignment for persona: {persona_id}"
            ) from exc

    def validate_assignment(
        self,
        persona_id: str,
    ) -> bool:
        """Validate an existing persona assignment."""

        assignment = self.assignment_for(persona_id)

        assignment.validate()

        if (
            self.require_whonix
            and assignment.network_mode
            != QubesNetworkMode.WHONIX
        ):
            return False

        if (
            not self.allow_direct_network
            and assignment.network_mode
            == QubesNetworkMode.OFFLINE
        ):
            # Offline is acceptable as a non-networked mode.
            return True

        return True

    def network_allowed(
        self,
        persona_id: str,
    ) -> bool:
        """Return whether a persona may use its assigned network."""

        if not self.health_check():
            return False

        assignment = self.assignment_for(persona_id)

        if not assignment.enabled:
            return False

        if assignment.network_mode == QubesNetworkMode.OFFLINE:
            return False

        if (
            self.require_whonix
            and assignment.network_mode
            != QubesNetworkMode.WHONIX
        ):
            return False

        if (
            not self.allow_direct_network
            and assignment.network_mode
            != QubesNetworkMode.WHONIX
        ):
            return False

        return True

    def prepare_rpc(
        self,
        request: QubesRPCRequest,
    ) -> QubesRPCRequest:
        """
        Validate an RPC request without transmitting it.
        """

        request.validate(self.rpc_policy)

        if request.persona_id:
            assignment = self.assignment_for(
                request.persona_id
            )

            if request.qube_name:
                if request.qube_name != assignment.qube_name:
                    raise PermissionError(
                        "RPC request targets a Qube different "
                        "from the persona assignment."
                    )

        return request

    def emergency_stop(self) -> bool:
        """
        Block new Qubes-backed activity.

        Actual Qube shutdown is delegated to the platform backend.
        """

        self._blocked = True
        self._running = False

        return True

    def reset_emergency_stop(self) -> bool:
        """Clear the local emergency-stop state."""

        if not self._initialized:
            return False

        self._blocked = False

        return True

    def summary(self) -> dict[str, Any]:
        """Return a non-sensitive plugin summary."""

        return {
            "enabled": self.enabled,
            "initialized": self._initialized,
            "running": self._running,
            "blocked": self._blocked,
            "status": self.status.value,
            "qubes_detected": self.detect_qubes(),
            "require_whonix": self.require_whonix,
            "fail_closed": self.fail_closed,
            "allow_direct_network": self.allow_direct_network,
            "assignment_count": len(self.assignments),
            "rpc_allowed_services": sorted(
                self.rpc_policy.allowed_services
            ),
            "rpc_dom0_allowed": self.rpc_policy.allow_dom0,
            "rpc_arbitrary_commands": (
                self.rpc_policy.allow_arbitrary_commands
            ),
        }


PLUGIN = QubesPlugin()
