"""SPOT scheduler routines."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Dict, List


@dataclass
class ScheduledRoutine:
    """A recurring synthetic persona routine."""

    routine_id: str
    persona_id: str

    activity_types: List[str] = field(
        default_factory=list
    )

    preferred_days: List[str] = field(
        default_factory=list
    )

    preferred_times: List[str] = field(
        default_factory=list
    )

    enabled: bool = True

    metadata: Dict[str, str] = field(
        default_factory=dict
    )


class RoutineManager:
    """Manage recurring persona routines."""

    def __init__(
        self,
        max_routines: int = 100,
    ) -> None:
        self.max_routines = max_routines

        self.routines: Dict[
            str,
            ScheduledRoutine,
        ] = {}

    def add(
        self,
        routine: ScheduledRoutine,
    ) -> None:
        """Add a routine."""
        if len(self.routines) >= self.max_routines:
            raise RuntimeError(
                "Maximum number of routines reached."
            )

        if routine.routine_id in self.routines:
            raise ValueError(
                f"Routine already exists: {routine.routine_id}"
            )

        if not routine.persona_id:
            raise ValueError(
                "Routine requires a persona ID."
            )

        self.routines[
            routine.routine_id
        ] = routine

    def get(
        self,
        routine_id: str,
    ) -> ScheduledRoutine | None:
        """Return a routine."""
        return self.routines.get(routine_id)

    def require(
        self,
        routine_id: str,
    ) -> ScheduledRoutine:
        """Return a routine or raise an error."""
        routine = self.get(routine_id)

        if routine is None:
            raise KeyError(
                f"Unknown routine: {routine_id}"
            )

        return routine

    def remove(
        self,
        routine_id: str,
    ) -> None:
        """Remove a routine."""
        self.require(routine_id)
        del self.routines[routine_id]

    def enable(
        self,
        routine_id: str,
    ) -> None:
        """Enable a routine."""
        self.require(routine_id).enabled = True

    def disable(
        self,
        routine_id: str,
    ) -> None:
        """Disable a routine."""
        self.require(routine_id).enabled = False

    def for_persona(
        self,
        persona_id: str,
    ) -> List[ScheduledRoutine]:
        """Return routines belonging to a persona."""
        return [
            routine
            for routine in self.routines.values()
            if routine.persona_id == persona_id
            and routine.enabled
        ]
