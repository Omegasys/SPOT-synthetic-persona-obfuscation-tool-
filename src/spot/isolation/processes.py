"""SPOT process isolation."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ProcessPolicy:
    """Limits for processes managed by SPOT."""

    allow_child_processes: bool = True

    max_processes: int = 20

    allow_shell: bool = False
    allow_privilege_escalation: bool = False

    terminate_on_session_stop: bool = True

    allowed_executables: List[str] = field(
        default_factory=list
    )

    blocked_executables: List[str] = field(
        default_factory=lambda: [
            "sudo",
            "su",
            "doas",
            "pkexec",
        ]
    )


@dataclass
class ManagedProcess:
    """Metadata about a process managed by SPOT."""

    process_id: int
    executable: str
    active: bool = True


class ProcessIsolation:
    """Track and constrain processes belonging to SPOT."""

    def __init__(
        self,
        policy: ProcessPolicy | None = None,
    ) -> None:
        self.policy = (
            policy
            or ProcessPolicy()
        )

        self.processes: Dict[
            int,
            ManagedProcess,
        ] = {}

    def can_start(
        self,
        executable: str,
    ) -> bool:
        """Check whether an executable may be started."""
        if not self.policy.allow_child_processes:
            return False

        if len(self.active()) >= self.policy.max_processes:
            return False

        executable_name = executable.split("/")[-1]

        if (
            executable_name
            in self.policy.blocked_executables
        ):
            return False

        if (
            self.policy.allowed_executables
            and executable_name
            not in self.policy.allowed_executables
        ):
            return False

        return True

    def register(
        self,
        process_id: int,
        executable: str,
    ) -> ManagedProcess:
        """Register an already-started process."""
        if not self.can_start(executable):
            raise PermissionError(
                "Process is blocked by SPOT process policy."
            )

        if process_id in self.processes:
            raise ValueError(
                f"Process is already registered: {process_id}"
            )

        process = ManagedProcess(
            process_id=process_id,
            executable=executable,
        )

        self.processes[process_id] = process

        return process

    def mark_stopped(
        self,
        process_id: int,
    ) -> None:
        """Mark a managed process as stopped."""
        process = self.processes.get(process_id)

        if process is not None:
            process.active = False

    def active(self) -> List[ManagedProcess]:
        """Return active managed processes."""
        return [
            process
            for process in self.processes.values()
            if process.active
        ]

    def terminate_managed(self) -> None:
        """Mark all managed processes as terminated.

        Actual OS process termination should be implemented by a
        narrowly scoped execution backend.
        """
        for process in self.processes.values():
            process.active = False

    def clear_stopped(self) -> None:
        """Remove stopped process records."""
        self.processes = {
            pid: process
            for pid, process in self.processes.items()
            if process.active
        }
