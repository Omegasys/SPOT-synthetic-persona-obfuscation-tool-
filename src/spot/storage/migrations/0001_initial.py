from __future__ import annotations

from ..database import Database
from .manager import Migration


def upgrade(database: Database) -> None:
    """Create the initial SPOT schema."""
    database.initialize()


MIGRATION = Migration(
    version=1,
    name="initial",
    upgrade=upgrade,
)
