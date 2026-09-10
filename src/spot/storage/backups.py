from __future__ import annotations

import shutil
import sqlite3
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path


@dataclass
class BackupResult:
    """Result of a database backup operation."""

    path: Path
    size_bytes: int
    created_at: float


class BackupManager:
    """Creates and validates local SQLite backups."""

    def __init__(
        self,
        database_path: str | Path,
        backup_directory: str | Path,
        *,
        max_backups: int = 5,
    ) -> None:
        self.database_path = Path(database_path).expanduser()
        self.backup_directory = Path(
            backup_directory
        ).expanduser()

        if max_backups < 1:
            raise ValueError("max_backups must be positive.")

        self.max_backups = max_backups

    def create_backup(
        self,
        *,
        label: str = "manual",
    ) -> BackupResult:
        """Create a consistent SQLite backup."""
        if not self.database_path.exists():
            raise FileNotFoundError(
                f"Database does not exist: {self.database_path}"
            )

        self.backup_directory.mkdir(
            parents=True,
            exist_ok=True,
        )

        timestamp = datetime.now(timezone.utc).strftime(
            "%Y%m%dT%H%M%SZ"
        )

        safe_label = self._safe_label(label)

        destination = (
            self.backup_directory
            / f"spot-{safe_label}-{timestamp}.db"
        )

        source_connection = sqlite3.connect(
            self.database_path
        )

        destination_connection = sqlite3.connect(
            destination
        )

        try:
            source_connection.backup(
                destination_connection
            )
        finally:
            destination_connection.close()
            source_connection.close()

        size = destination.stat().st_size
        created_at = destination.stat().st_mtime

        self._enforce_retention()

        return BackupResult(
            path=destination,
            size_bytes=size,
            created_at=created_at,
        )

    def restore(
        self,
        backup_path: str | Path,
        *,
        destination: str | Path | None = None,
    ) -> Path:
        """
        Restore a backup to a database path.

        The existing destination is replaced only after the backup
        passes SQLite integrity validation.
        """
        backup = Path(backup_path).expanduser()

        if not backup.exists():
            raise FileNotFoundError(
                f"Backup does not exist: {backup}"
            )

        if not self.validate(backup):
            raise ValueError("Backup failed SQLite integrity check.")

        target = (
            Path(destination).expanduser()
            if destination is not None
            else self.database_path
        )

        target.parent.mkdir(
            parents=True,
            exist_ok=True,
        )

        temporary = target.with_suffix(
            target.suffix + ".restore.tmp"
        )

        shutil.copy2(backup, temporary)

        if not self.validate(temporary):
            temporary.unlink(missing_ok=True)
            raise ValueError(
                "Temporary restored database failed validation."
            )

        temporary.replace(target)

        return target

    def validate(self, backup_path: str | Path) -> bool:
        """Check whether a backup is a valid SQLite database."""
        path = Path(backup_path).expanduser()

        if not path.exists():
            return False

        connection = sqlite3.connect(path)

        try:
            result = connection.execute(
                "PRAGMA integrity_check"
            ).fetchone()

            return bool(result and result[0] == "ok")
        except sqlite3.DatabaseError:
            return False
        finally:
            connection.close()

    def list_backups(self) -> list[Path]:
        """Return available SPOT database backups."""
        if not self.backup_directory.exists():
            return []

        return sorted(
            self.backup_directory.glob("spot-*.db"),
            key=lambda path: path.stat().st_mtime,
            reverse=True,
        )

    def delete_backup(self, backup_path: str | Path) -> None:
        """Delete a backup file."""
        path = Path(backup_path).expanduser()

        if path.parent != self.backup_directory:
            raise ValueError(
                "Backup must be located inside the backup directory."
            )

        path.unlink(missing_ok=True)

    def _enforce_retention(self) -> None:
        """Remove backups beyond the configured retention count."""
        backups = self.list_backups()

        for backup in backups[self.max_backups :]:
            backup.unlink(missing_ok=True)

    @staticmethod
    def _safe_label(label: str) -> str:
        """Create a filesystem-safe backup label."""
        cleaned = "".join(
            character
            if character.isalnum() or character in "-_"
            else "_"
            for character in label
        )

        return cleaned[:64] or "backup"
