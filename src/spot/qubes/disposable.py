"""SPOT Qubes disposable management."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class DisposableConfig:
    """Policy for disposable Qubes."""

    enabled: bool = True

    max_active: int = 3

    destroy_on_stop: bool = True
    persistent_storage: bool = False

    allow_personal_data: bool = False
    allow_credentials: bool = False


@dataclass
class DisposableQube:
    """Metadata for a disposable Qube."""

    name: str
    persona_id: str | None = None

    active: bool = False

    metadata: Dict[str, str] = field(
        default_factory=dict
    )


class DisposableManager:
    """Manage disposable Qube metadata and lifecycle."""

    def __init__(
        self,
        config: DisposableConfig | None = None,
    ) -> None:
        self.config = (
            config
            or DisposableConfig()
        )

        self.disposables: Dict[
            str,
            DisposableQube,
        ] = {}

    def create(
        self,
        name: str,
        persona_id: str | None = None,
    ) -> DisposableQube:
        """Create disposable-Qube metadata."""
        if not self.config.enabled:
            raise RuntimeError(
                "Disposable Qubes are disabled."
            )

        if name in self.disposables:
            raise ValueError(
                f"Disposable already exists: {name}"
            )

        if len(self.active()) >= self.config.max_active:
            raise RuntimeError(
                "Maximum active disposable Qubes reached."
            )

        qube = DisposableQube(
            name=name,
            persona_id=persona_id,
        )

        self.disposables[name] = qube
        return qube

    def start(
        self,
        name: str,
    ) -> DisposableQube:
        """Start a disposable Qube."""
        qube = self.require(name)

        if len(self.active()) >= self.config.max_active:
            raise RuntimeError(
                "Maximum active disposable Qubes reached."
            )

        qube.active = True
        return qube

    def stop(
        self,
        name: str,
    ) -> DisposableQube:
        """Stop a disposable Qube."""
        qube = self.require(name)

        qube.active = False

        return qube

    def require(
        self,
        name: str,
    ) -> DisposableQube:
        """Return a disposable or raise an error."""
        qube = self.disposables.get(name)

        if qube is None:
            raise KeyError(
                f"Unknown disposable Qube: {name}"
            )

        return qube

    def active(self) -> List[DisposableQube]:
        """Return active disposable Qubes."""
        return [
            qube
            for qube in self.disposables.values()
            if qube.active
        ]

    def stop_all(self) -> None:
        """Stop all disposable Qubes."""
        for qube in self.disposables.values():
            qube.active = False

    def clear_stopped(self) -> None:
        """Remove stopped disposable Qubes."""
        self.disposables = {
            name: qube
            for name, qube in self.disposables.items()
            if qube.active
        }
