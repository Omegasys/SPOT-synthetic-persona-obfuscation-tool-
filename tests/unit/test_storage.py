from pathlib import Path

import pytest

from spot.storage.database import Database
from spot.storage.models import (
    PersonaRecord,
    MemoryRecord,
    ActivityRecord,
)
from spot.storage.encryption import StorageEncryption


def test_database_initialization(tmp_path):
    database_path = tmp_path / "spot.db"

    database = Database(database_path)
    database.connect()
    database.initialize()

    result = database.integrity_check()

    assert result is True

    database.close()


def test_database_transaction(tmp_path):
    database = Database(tmp_path / "spot.db")

    database.connect()
    database.initialize()

    with database.transaction():
        database.execute(
            """
            INSERT INTO settings (key, value)
            VALUES (?, ?)
            """,
            ("test", "value"),
        )

    row = database.execute(
        "SELECT value FROM settings WHERE key = ?",
        ("test",),
    ).fetchone()

    assert row["value"] == "value"

    database.close()


def test_persona_record_serialization():
    record = PersonaRecord(
        id="test",
        name="Test Persona",
        description="Synthetic persona",
        enabled=True,
    )

    data = record.to_dict()

    assert data["id"] == "test"
    assert data["name"] == "Test Persona"
    assert data["enabled"] is True


def test_memory_record_serialization():
    record = MemoryRecord(
        id="memory-1",
        persona_id="persona-1",
        topic="technology",
        content="Synthetic memory",
    )

    data = record.to_dict()

    assert data["persona_id"] == "persona-1"
    assert data["topic"] == "technology"


def test_activity_record_serialization():
    record = ActivityRecord(
        id="activity-1",
        persona_id="persona-1",
        activity_type="search",
        status="success",
    )

    data = record.to_dict()

    assert data["activity_type"] == "search"
    assert data["status"] == "success"


def test_storage_encryption_round_trip():
    encryption = StorageEncryption()

    plaintext = "synthetic secret data"

    encrypted = encryption.encrypt(plaintext)
    decrypted = encryption.decrypt(encrypted)

    assert decrypted == plaintext


def test_storage_encryption_changes_ciphertext():
    encryption = StorageEncryption()

    plaintext = "test data"

    first = encryption.encrypt(plaintext)
    second = encryption.encrypt(plaintext)

    assert first != second


def test_storage_encryption_wrong_key_fails():
    first = StorageEncryption()
    second = StorageEncryption()

    encrypted = first.encrypt("secret")

    with pytest.raises(Exception):
        second.decrypt(encrypted)
