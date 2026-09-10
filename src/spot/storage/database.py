from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator


class Database:
    """Small SQLite database wrapper for local SPOT storage."""

    def __init__(
        self,
        path: str | Path,
        *,
        timeout: float = 5.0,
    ) -> None:
        self.path = Path(path).expanduser()
        self.timeout = timeout
        self._connection: sqlite3.Connection | None = None

    @property
    def connection(self) -> sqlite3.Connection:
        """Return the active database connection."""
        if self._connection is None:
            raise RuntimeError("Database is not connected.")

        return self._connection

    def connect(self) -> None:
        """Open the database."""
        if self._connection is not None:
            return

        self.path.parent.mkdir(parents=True, exist_ok=True)

        self._connection = sqlite3.connect(
            self.path,
            timeout=self.timeout,
        )

        self._connection.row_factory = sqlite3.Row

        self.connection.execute("PRAGMA foreign_keys = ON")
        self.connection.execute("PRAGMA journal_mode = WAL")
        self.connection.execute("PRAGMA synchronous = NORMAL")

    def close(self) -> None:
        """Close the database."""
        if self._connection is None:
            return

        self._connection.close()
        self._connection = None

    def execute(
        self,
        sql: str,
        parameters: tuple | dict = (),
    ) -> sqlite3.Cursor:
        """Execute one SQL statement."""
        return self.connection.execute(sql, parameters)

    def executemany(
        self,
        sql: str,
        parameters: list[tuple] | list[dict],
    ) -> sqlite3.Cursor:
        """Execute a statement for multiple parameter sets."""
        return self.connection.executemany(sql, parameters)

    def executescript(self, sql: str) -> None:
        """Execute a SQL script."""
        self.connection.executescript(sql)

    def commit(self) -> None:
        """Commit the current transaction."""
        self.connection.commit()

    def rollback(self) -> None:
        """Roll back the current transaction."""
        self.connection.rollback()

    @contextmanager
    def transaction(self) -> Iterator[sqlite3.Connection]:
        """Run operations inside a transaction."""
        try:
            yield self.connection
            self.connection.commit()
        except Exception:
            self.connection.rollback()
            raise

    def initialize(self) -> None:
        """Create the base SPOT storage schema."""
        self.executescript(
            """
            CREATE TABLE IF NOT EXISTS schema_metadata (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL
            );

            CREATE TABLE IF NOT EXISTS personas (
                id TEXT PRIMARY KEY,
                name TEXT NOT NULL,
                description TEXT NOT NULL DEFAULT '',
                enabled INTEGER NOT NULL DEFAULT 0,
                memory_enabled INTEGER NOT NULL DEFAULT 1,
                synthetic_only INTEGER NOT NULL DEFAULT 1,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL
            );

            CREATE TABLE IF NOT EXISTS persona_memory (
                id TEXT PRIMARY KEY,
                persona_id TEXT NOT NULL,
                category TEXT NOT NULL,
                key TEXT NOT NULL,
                value TEXT NOT NULL,
                created_at REAL NOT NULL,
                updated_at REAL NOT NULL,
                FOREIGN KEY (persona_id)
                    REFERENCES personas(id)
                    ON DELETE CASCADE
            );

            CREATE INDEX IF NOT EXISTS idx_persona_memory_persona
                ON persona_memory(persona_id);

            CREATE TABLE IF NOT EXISTS activity_log (
                id TEXT PRIMARY KEY,
                persona_id TEXT,
                activity_type TEXT NOT NULL,
                target TEXT,
                status TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}',
                created_at REAL NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_activity_log_persona
                ON activity_log(persona_id);

            CREATE TABLE IF NOT EXISTS audit_log (
                id TEXT PRIMARY KEY,
                event_type TEXT NOT NULL,
                severity TEXT NOT NULL,
                persona_id TEXT,
                message TEXT NOT NULL,
                metadata TEXT NOT NULL DEFAULT '{}',
                created_at REAL NOT NULL
            );

            CREATE INDEX IF NOT EXISTS idx_audit_log_created
                ON audit_log(created_at);

            CREATE TABLE IF NOT EXISTS settings (
                key TEXT PRIMARY KEY,
                value TEXT NOT NULL,
                updated_at REAL NOT NULL
            );
            """
        )

        self.commit()

    def vacuum(self) -> None:
        """Compact the database."""
        self.connection.execute("VACUUM")

    def checkpoint(self) -> None:
        """Checkpoint the SQLite WAL."""
        self.connection.execute("PRAGMA wal_checkpoint(TRUNCATE)")

    def integrity_check(self) -> bool:
        """Run SQLite's integrity check."""
        row = self.connection.execute(
            "PRAGMA integrity_check"
        ).fetchone()

        return bool(row and row[0] == "ok")
