from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

from ..database import Database


MigrationFunction = Callable[[Database], None]


@dataclass(frozen=True)
class Migration:
    """A single database schema migration."""

    version: int
    name: str
    upgrade: MigrationFunction


class MigrationManager:
    """Applies SPOT database migrations in deterministic order."""

    def __init__(
        self,
        database: Database,
        migrations: list[Migration] | None = None,
    ) -> None:
        self.database = database
        self.migrations = sorted(
            migrations or [],
            key=lambda migration: migration.version,
        )

        self._validate_migrations()

    def _validate_migrations(self) -> None:
        versions = [
            migration.version
            for migration in self.migrations
        ]

        if len(versions) != len(set(versions)):
            raise ValueError(
                "Duplicate migration versions detected."
            )

        if any(version < 1 for version in versions):
            raise ValueError(
                "Migration versions must be positive."
            )

    def current_version(self) -> int:
        """Return the current database schema version."""
        row = self.database.execute(
            """
            SELECT value
            FROM schema_metadata
            WHERE key = 'schema_version'
            """
        ).fetchone()

        if row is None:
            return 0

        return int(row["value"])

    def set_version(self, version: int) -> None:
        """Set the current schema version."""
        self.database.execute(
            """
            INSERT INTO schema_metadata(key, value)
            VALUES('schema_version', ?)
            ON CONFLICT(key)
            DO UPDATE SET value = excluded.value
            """,
            (str(version),),
        )

    def pending(self) -> list[Migration]:
        """Return migrations that still need to run."""
        current = self.current_version()

        return [
            migration
            for migration in self.migrations
            if migration.version > current
        ]

    def migrate(self) -> int:
        """Apply all pending migrations."""
        applied = 0

        for migration in self.pending():
            with self.database.transaction():
                migration.upgrade(self.database)
                self.set_version(migration.version)

            applied += 1

        return applied
