"""SPOT Qubes OS integration manager."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .disposable import DisposableManager
from .networking import QubesNetworkManager
from .persona_qubes import PersonaQubeManager
from .qubes_rpc import QubesRPC
from .templates import QubeTemplateManager


@dataclass
class QubesSession:
    """State for a SPOT-managed Qubes session."""

    session_id: str
    persona_id: str | None = None
    qube_name: str | None = None

    active: bool = False

    metadata: Dict[str, str] = field(
        default_factory=dict
    )


class QubesManager:
    """Coordinate SPOT's Qubes OS integration."""

    def __init__(
        self,
        rpc: QubesRPC | None = None,
        templates: QubeTemplateManager | None = None,
        disposables: DisposableManager | None = None,
        networking: QubesNetworkManager | None = None,
        personas: PersonaQubeManager | None = None,
    ) -> None:
        self.rpc = rpc or QubesRPC()
        self.templates = (
            templates
            or QubeTemplateManager()
        )
        self.disposables = (
            disposables
            or DisposableManager()
        )
        self.networking = (
            networking
            or QubesNetworkManager()
        )
        self.personas = (
            personas
            or PersonaQubeManager()
        )

        self.sessions: Dict[
            str,
            QubesSession,
        ] = {}

    def create_session(
        self,
        session_id: str,
        persona_id: str | None = None,
        qube_name: str | None = None,
    ) -> QubesSession:
        """Create a Qubes integration session."""
        if session_id in self.sessions:
            raise ValueError(
                f"Qubes session already exists: {session_id}"
            )

        session = QubesSession(
            session_id=session_id,
            persona_id=persona_id,
            qube_name=qube_name,
        )

        self.sessions[session_id] = session
        return session

    def get(
        self,
        session_id: str,
    ) -> QubesSession | None:
        """Return a Qubes session."""
        return self.sessions.get(session_id)

    def require(
        self,
        session_id: str,
    ) -> QubesSession:
        """Return a Qubes session or raise an error."""
        session = self.get(session_id)

        if session is None:
            raise KeyError(
                f"Unknown Qubes session: {session_id}"
            )

        return session

    def start(
        self,
        session_id: str,
    ) -> QubesSession:
        """Mark a Qubes session active."""
        session = self.require(session_id)

        if session.active:
            return session

        session.active = True
        return session

    def stop(
        self,
        session_id: str,
    ) -> QubesSession:
        """Stop a Qubes session."""
        session = self.require(session_id)

        session.active = False
        return session

    def active(self) -> List[QubesSession]:
        """Return active Qubes sessions."""
        return [
            session
            for session in self.sessions.values()
            if session.active
        ]

    def stop_all(self) -> None:
        """Stop all SPOT Qubes sessions."""
        for session in self.sessions.values():
            session.active = False

        self.disposables.stop_all()

    def emergency_stop(self) -> None:
        """Emergency-stop Qubes-managed activity."""
        self.stop_all()
        self.networking.emergency_stop()

    def remove(
        self,
        session_id: str,
    ) -> None:
        """Remove an inactive Qubes session."""
        session = self.require(session_id)

        if session.active:
            raise RuntimeError(
                "Cannot remove an active Qubes session."
            )

        del self.sessions[session_id]
