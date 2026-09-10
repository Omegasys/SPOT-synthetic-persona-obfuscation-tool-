"""Validation helpers for SPOT."""

from __future__ import annotations

import re
from pathlib import Path
from typing import Any, Iterable, Optional


_IDENTIFIER_PATTERN = re.compile(r"^[A-Za-z0-9][A-Za-z0-9_.-]*$")


class ValidationError(ValueError):
    """Raised when SPOT input fails validation."""


def require_non_empty(
    value: Optional[str],
    field: str = "value",
) -> str:
    """Require a non-empty string."""
    if value is None or not str(value).strip():
        raise ValidationError(f"{field} must not be empty.")

    return str(value).strip()


def validate_identifier(
    value: str,
    field: str = "identifier",
) -> str:
    """Validate a SPOT identifier."""
    value = require_non_empty(value, field)

    if not _IDENTIFIER_PATTERN.fullmatch(value):
        raise ValidationError(
            f"{field} contains invalid characters."
        )

    return value


def validate_range(
    value: float,
    minimum: float,
    maximum: float,
    field: str = "value",
) -> float:
    """Validate that a numeric value falls within a range."""
    if minimum > maximum:
        raise ValidationError(
            "Validation range is invalid."
        )

    if not minimum <= value <= maximum:
        raise ValidationError(
            f"{field} must be between {minimum} and {maximum}."
        )

    return value


def validate_positive(
    value: float,
    field: str = "value",
    allow_zero: bool = False,
) -> float:
    """Validate a positive numeric value."""
    minimum = 0 if allow_zero else 0

    if allow_zero:
        valid = value >= minimum
    else:
        valid = value > minimum

    if not valid:
        comparator = "non-negative" if allow_zero else "positive"
        raise ValidationError(
            f"{field} must be {comparator}."
        )

    return value


def validate_choice(
    value: Any,
    choices: Iterable[Any],
    field: str = "value",
) -> Any:
    """Validate that a value belongs to an allowed set."""
    choices = tuple(choices)

    if value not in choices:
        raise ValidationError(
            f"{field} must be one of: {', '.join(map(str, choices))}."
        )

    return value


def validate_path(
    path: Path,
    field: str = "path",
    must_exist: bool = False,
    directory: Optional[bool] = None,
) -> Path:
    """Validate a filesystem path without modifying it."""
    path = Path(path)

    if must_exist and not path.exists():
        raise ValidationError(
            f"{field} does not exist: {path}"
        )

    if directory is True and path.exists() and not path.is_dir():
        raise ValidationError(
            f"{field} must be a directory: {path}"
        )

    if directory is False and path.exists() and not path.is_file():
        raise ValidationError(
            f"{field} must be a file: {path}"
        )

    return path


def validate_mapping(
    value: Any,
    field: str = "value",
) -> dict:
    """Validate that a value is dictionary-like."""
    if not isinstance(value, dict):
        raise ValidationError(
            f"{field} must be a mapping."
        )

    return value


def validate_list(
    value: Any,
    field: str = "value",
) -> list:
    """Validate that a value is a list."""
    if not isinstance(value, list):
        raise ValidationError(
            f"{field} must be a list."
        )

    return value


def validate_bool(
    value: Any,
    field: str = "value",
) -> bool:
    """Validate a boolean value."""
    if not isinstance(value, bool):
        raise ValidationError(
            f"{field} must be a boolean."
        )

    return value
