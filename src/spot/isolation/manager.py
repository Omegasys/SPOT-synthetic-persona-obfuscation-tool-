"""SPOT isolation manager."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List

from .containers import ContainerConfig, ContainerManager
from .filesystem import FilesystemIsolation
from .namespaces import NamespaceConfig, NamespaceManager
from .permissions import PermissionPolicy, PermissionManager
from .processes import ProcessIsolation
from .sandbox import SandboxConfig, SandboxManager


@dataclass
class IsolationSession:
    """State for an isolated SPOT session."""

    session_id: str
    persona_id: str

    filesystem: FilesystemIsolation
    processes: ProcessIsolation
    namespaces: NamespaceManager
    sandbox: SandboxManager
    containers: ContainerManager
    permissions: PermissionManager

    active: bool = False
    metadata: Dict[str, str] = field(default_factory=dict)

    def start(self) -> None:
        """Start the isolation session."""
        if self.active:
            return

        self.filesystem.prepare()
        self.namespaces.prepare()
        self.sandbox.prepare()

        self.active = True

    def stop(self) -> None:
        """Stop the isolation session."""
        if not self.active:
            return

        self.sandbox.cleanup()
        self.namespaces.cleanup()
        self.filesystem.cleanup()

        self.active = False

    def emergency_stop(self) -> None:
        """Immediately disable the isolation session."""
        self.sandbox.emergency_stop()
        self.namespaces.emergency_stop()
        self.processes.terminate_managed()
        self.active = False


class IsolationManager:
    """Create and manage isolated SPOT execution sessions."""

    def __init__(self) -> None:
        self.sessions: Dict[str, IsolationSession] = {}

    def create(
        self,
        session_id: str,
        persona_id: str,
        filesystem: FilesystemIsolation | None = None,
        processes: ProcessIsolation | None = None,
        namespaces: NamespaceManager | None = None,
        sandbox: SandboxManager | None = None,
        containers: ContainerManager | None = None,
        permissions: PermissionManager | None = None,
    ) -> IsolationSession:
        """Create an isolation session."""
        if session_id in self.sessions:
            raise ValueError(
                f"Isolation session already exists: {session_id}"
            )

        session = IsolationSession(
            session_id=session_id,
            persona_id=persona_id,
            filesystem=filesystem or FilesystemIsolation(),
            processes=processes or ProcessIsolation(),
            namespaces=namespaces or NamespaceManager(),
            sandbox=sandbox or SandboxManager(),
            containers=containers or ContainerManager(),
            permissions=permissions or PermissionManager(),
        )

        self.sessions[session_id] = session
        return session

    def get(
        self,
        session_id: str,
    ) -> IsolationSession | None:
        """Return an isolation session."""
        return self.sessions.get(session_id)

    def require(
        self,
        session_id: str,
    ) -> IsolationSession:
        """Return a session or raise an error."""
        session = self.get(session_id)

        if session is None:
            raise KeyError(
                f"Unknown isolation session: {session_id}"
            )

        return session

    def start(
        self,
        session_id: str,
    ) -> IsolationSession:
        """Start an isolation session."""
        session = self.require(session_id)
        session.start()
        return session

    def stop(
        self,
        session_id: str,
    ) -> IsolationSession:
        """Stop an isolation session."""
        session = self.require(session_id)
        session.stop()
        return session

    def remove(
        self,
        session_id: str,
    ) -> None:
        """Remove an inactive isolation session."""
        session = self.require(session_id)

        if session.active:
            raise RuntimeError(
                "Cannot remove an active isolation session."
            )

        del self.sessions[session_id]

    def active(self) -> List[IsolationSession]:
        """Return active isolation sessions."""
        return [
            session
            for session in self.sessions.values()
            if session.active
        ]

    def stop_all(self) -> None:
        """Stop every isolation session."""
        for session in list(self.sessions.values()):
            session.stop()

    def emergency_stop(self) -> None:
        """Emergency-stop all isolation sessions."""
        for session in list(self.sessions.values()):
            session.emergency_stop()

    def clear_stopped(self) -> None:
        """Remove all inactive sessions."""
        self.sessions = {
            session_id: session
            for session_id, session in self.sessions.items()
            if session.active
        }
