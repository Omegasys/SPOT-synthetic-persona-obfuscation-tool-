"""SPOT Qubes RPC policy layer."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class RPCPolicy:
    """Default-deny policy for Qubes RPC operations."""

    enabled: bool = True

    allowed_services: List[str] = field(
        default_factory=list
    )

    denied_services: List[str] = field(
        default_factory=lambda: [
            "admin.vm.Start",
            "admin.vm.Kill",
            "admin.vm.Remove",
            "admin.vm.volume.Import",
            "admin.vm.device.Attach",
        ]
    )

    allow_dom0_operations: bool = False


@dataclass
class RPCRequest:
    """A declarative Qubes RPC request."""

    service: str
    source: str | None = None
    target: str | None = None
    arguments: Dict[str, str] = field(
        default_factory=dict
    )


class QubesRPC:
    """Validate Qubes RPC requests.

    Actual RPC transmission is intentionally delegated to a
    future restricted backend. This class does not directly
    manipulate dom0.
    """

    def __init__(
        self,
        policy: RPCPolicy | None = None,
    ) -> None:
        self.policy = (
            policy
            or RPCPolicy()
        )

        self.history: List[RPCRequest] = []

    def validate(
        self,
        request: RPCRequest,
    ) -> None:
        """Validate a Qubes RPC request."""
        if not self.policy.enabled:
            raise PermissionError(
                "Qubes RPC integration is disabled."
            )

        if not request.service:
            raise ValueError(
                "RPC service cannot be empty."
            )

        if (
            request.service
            in self.policy.denied_services
        ):
            raise PermissionError(
                f"Qubes RPC service is denied: "
                f"{request.service}"
            )

        if self.policy.allowed_services:
            if (
                request.service
                not in self.policy.allowed_services
            ):
                raise PermissionError(
                    f"Qubes RPC service is not allowlisted: "
                    f"{request.service}"
                )

        if (
            not self.policy.allow_dom0_operations
            and request.target == "dom0"
        ):
            raise PermissionError(
                "Direct dom0 operations are disabled."
            )

    def prepare(
        self,
        service: str,
        source: str | None = None,
        target: str | None = None,
        arguments: Dict[str, str] | None = None,
    ) -> RPCRequest:
        """Prepare a policy-checked RPC request."""
        request = RPCRequest(
            service=service,
            source=source,
            target=target,
            arguments=dict(arguments or {}),
        )

        self.validate(request)

        self.history.append(request)

        return request

    def clear_history(self) -> None:
        """Clear RPC request history."""
        self.history.clear()

    def allowed(
        self,
        service: str,
        target: str | None = None,
    ) -> bool:
        """Check whether an RPC request would be allowed."""
        try:
            self.validate(
                RPCRequest(
                    service=service,
                    target=target,
                )
            )
        except (PermissionError, ValueError):
            return False

        return True
