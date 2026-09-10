from __future__ import annotations

import base64
import hashlib
import hmac
import os
from dataclasses import dataclass


@dataclass
class EncryptedValue:
    """Representation of an encrypted storage value."""

    version: int
    salt: bytes
    nonce: bytes
    ciphertext: bytes
    tag: bytes

    def serialize(self) -> str:
        """Serialize the encrypted value."""
        parts = [
            str(self.version).encode(),
            self.salt,
            self.nonce,
            self.ciphertext,
            self.tag,
        ]

        return "spot1:" + ":".join(
            base64.urlsafe_b64encode(part).decode()
            for part in parts
        )

    @classmethod
    def deserialize(cls, value: str) -> "EncryptedValue":
        """Deserialize an encrypted value."""
        if not value.startswith("spot1:"):
            raise ValueError("Unsupported encrypted value format.")

        parts = value[6:].split(":")

        if len(parts) != 5:
            raise ValueError("Invalid encrypted value.")

        decoded = [
            base64.urlsafe_b64decode(part.encode())
            for part in parts
        ]

        return cls(
            version=int(decoded[0]),
            salt=decoded[1],
            nonce=decoded[2],
            ciphertext=decoded[3],
            tag=decoded[4],
        )


class StorageEncryption:
    """
    Lightweight authenticated encryption helper.

    This class is intended to protect sensitive fields before they are
    stored. The database itself should still be protected by filesystem
    permissions and, where appropriate, an encrypted filesystem.

    The implementation uses a standard-library-only construction:
    PBKDF2-HMAC-SHA256 for key derivation and an HMAC-authenticated
    XOR keystream for confidentiality.
    """

    VERSION = 1
    SALT_SIZE = 16
    NONCE_SIZE = 16
    KEY_SIZE = 32

    def __init__(
        self,
        key: bytes,
        *,
        iterations: int = 600_000,
    ) -> None:
        if not key:
            raise ValueError("Encryption key cannot be empty.")

        if iterations < 100_000:
            raise ValueError("PBKDF2 iteration count is too low.")

        self.key = key
        self.iterations = iterations

    def _derive_key(self, salt: bytes) -> bytes:
        """Derive a per-value encryption key."""
        return hashlib.pbkdf2_hmac(
            "sha256",
            self.key,
            salt,
            self.iterations,
            dklen=self.KEY_SIZE,
        )

    @staticmethod
    def _keystream(key: bytes, nonce: bytes, length: int) -> bytes:
        """Generate a deterministic HMAC-based keystream."""
        output = bytearray()
        counter = 0

        while len(output) < length:
            block = hmac.new(
                key,
                nonce + counter.to_bytes(8, "big"),
                hashlib.sha256,
            ).digest()

            output.extend(block)
            counter += 1

        return bytes(output[:length])

    @staticmethod
    def _xor(data: bytes, stream: bytes) -> bytes:
        return bytes(
            left ^ right
            for left, right in zip(data, stream)
        )

    def encrypt(self, plaintext: str) -> str:
        """Encrypt and authenticate a UTF-8 string."""
        if not isinstance(plaintext, str):
            raise TypeError("plaintext must be a string.")

        salt = os.urandom(self.SALT_SIZE)
        nonce = os.urandom(self.NONCE_SIZE)

        derived_key = self._derive_key(salt)
        plaintext_bytes = plaintext.encode("utf-8")

        stream = self._keystream(
            derived_key,
            nonce,
            len(plaintext_bytes),
        )

        ciphertext = self._xor(plaintext_bytes, stream)

        tag = hmac.new(
            derived_key,
            nonce + ciphertext,
            hashlib.sha256,
        ).digest()

        return EncryptedValue(
            version=self.VERSION,
            salt=salt,
            nonce=nonce,
            ciphertext=ciphertext,
            tag=tag,
        ).serialize()

    def decrypt(self, encrypted: str) -> str:
        """Authenticate and decrypt a stored value."""
        value = EncryptedValue.deserialize(encrypted)

        if value.version != self.VERSION:
            raise ValueError("Unsupported encryption version.")

        derived_key = self._derive_key(value.salt)

        expected_tag = hmac.new(
            derived_key,
            value.nonce + value.ciphertext,
            hashlib.sha256,
        ).digest()

        if not hmac.compare_digest(value.tag, expected_tag):
            raise ValueError("Encrypted value failed authentication.")

        stream = self._keystream(
            derived_key,
            value.nonce,
            len(value.ciphertext),
        )

        plaintext = self._xor(value.ciphertext, stream)

        return plaintext.decode("utf-8")

    @staticmethod
    def generate_key() -> bytes:
        """Generate a cryptographically random storage key."""
        return os.urandom(StorageEncryption.KEY_SIZE)

    @staticmethod
    def derive_key_from_password(
        password: str,
        salt: bytes,
        *,
        iterations: int = 600_000,
    ) -> bytes:
        """Derive a storage key from a user-provided password."""
        if not password:
            raise ValueError("Password cannot be empty.")

        if len(salt) < 16:
            raise ValueError("Salt must be at least 16 bytes.")

        return hashlib.pbkdf2_hmac(
            "sha256",
            password.encode("utf-8"),
            salt,
            iterations,
            dklen=StorageEncryption.KEY_SIZE,
        )
