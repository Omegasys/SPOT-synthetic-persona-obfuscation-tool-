"""Logging utilities for SPOT."""

from __future__ import annotations

import logging
import sys
from pathlib import Path
from typing import Optional


DEFAULT_LOG_FORMAT = (
    "%(asctime)s %(levelname)s %(name)s: %(message)s"
)


def get_logger(name: str = "spot") -> logging.Logger:
    """Return a named SPOT logger."""
    return logging.getLogger(name)


def configure_logging(
    level: int = logging.INFO,
    log_file: Optional[Path] = None,
    console: bool = True,
    fmt: str = DEFAULT_LOG_FORMAT,
) -> None:
    """Configure application logging.

    Existing handlers are removed so configuration is deterministic.
    """
    logger = logging.getLogger("spot")
    logger.setLevel(level)
    logger.propagate = False

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()

    formatter = logging.Formatter(fmt)

    if console:
        console_handler = logging.StreamHandler(sys.stderr)
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    if log_file is not None:
        log_file.parent.mkdir(parents=True, exist_ok=True)

        file_handler = logging.FileHandler(
            log_file,
            encoding="utf-8",
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)


def set_level(level: int) -> None:
    """Change the SPOT logger level."""
    logging.getLogger("spot").setLevel(level)


def disable_logging() -> None:
    """Disable SPOT logging output."""
    logger = logging.getLogger("spot")
    logger.disabled = True


def enable_logging() -> None:
    """Re-enable SPOT logging output."""
    logger = logging.getLogger("spot")
    logger.disabled = False


def close_logging() -> None:
    """Close and remove all SPOT logging handlers."""
    logger = logging.getLogger("spot")

    for handler in list(logger.handlers):
        logger.removeHandler(handler)
        handler.close()
