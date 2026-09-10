"""SPOT task representation."""

from __future__ import annotations

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict


class TaskStatus(str, Enum):
    """Possible task states."""

    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"


@dataclass
class Task:
    """Represents one unit of SPOT work."""

    task_id: str
    name: str
    payload: Dict[str, Any] = field(default_factory=dict)

    status: TaskStatus = TaskStatus.PENDING
    result: Any = None
    error: str | None = None

    def start(self) -> None:
        """Mark the task as running."""
        if self.status != TaskStatus.PENDING:
            raise RuntimeError(
                f"Task cannot start from state: {self.status.value}"
            )

        self.status = TaskStatus.RUNNING

    def complete(self, result: Any = None) -> None:
        """Mark the task as completed."""
        if self.status != TaskStatus.RUNNING:
            raise RuntimeError(
                f"Task cannot complete from state: {self.status.value}"
            )

        self.result = result
        self.status = TaskStatus.COMPLETED

    def fail(self, error: str) -> None:
        """Mark the task as failed."""
        self.error = error
        self.status = TaskStatus.FAILED

    def cancel(self) -> None:
        """Cancel the task."""
        if self.status in (
            TaskStatus.COMPLETED,
            TaskStatus.FAILED,
            TaskStatus.CANCELLED,
        ):
            return

        self.status = TaskStatus.CANCELLED
