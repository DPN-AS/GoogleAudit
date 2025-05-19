"""Input validation utilities."""

from __future__ import annotations


def validate_email(value: str) -> bool:
    """Return True if the given string looks like an email address."""
    return "@" in value
