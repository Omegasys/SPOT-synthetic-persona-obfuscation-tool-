from __future__ import annotations

from ..database import Database
from .manager import Migration


def upgrade(database: Database) -> None:
    """Add indexes used by activity and audit queries."""
    database.executescript(
        """
        CREATE INDEX IF NOT EXISTS idx_activity_log_type
            ON activity_log(activity_type);

        CREATE INDEX IF NOT EXISTS idx_activity_log_created
            ON activity_log(created_at);

        CREATE INDEX IF NOT EXISTS idx_audit_log_persona
            ON audit_log(persona_id);

        CREATE INDEX IF NOT EXISTS idx_settings_updated
            ON settings(updated_at);
        """
    )


MIGRATION = Migration(
    version=2,
    name="activity_indexes",
    upgrade=upgrade,
)
