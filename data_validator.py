"""Input validation and sanitization helpers.

This module centralizes common routines used throughout GAudit for checking and
cleaning user supplied data.  Each function is intentionally lightweight and
designed for reuse across both the UI and core audit logic.

The functionality implemented here is referenced in the project's
``REFERENCE_GUIDE.md`` under the *Utilities* section which describes this file
as providing "input validation and data sanitization helpers".
"""

from __future__ import annotations

import re
import string

EMAIL_PATTERN = re.compile(r"^[^@\s]+@[^@\s]+\.[^@\s]+$")
DOMAIN_PATTERN = re.compile(r"^(?:[a-zA-Z0-9-]+\.)+[a-zA-Z]{2,}$")
URL_PATTERN = re.compile(
    r"^https?://"
    r"(?:[a-zA-Z0-9-_]+\.)*"  # subdomains
    r"[a-zA-Z0-9-]+\.[a-zA-Z]{2,}"  # base domain
    r"(?:/[^\s]*)?$"  # optional path
)


def validate_email(value: str) -> bool:
    """Return ``True`` if ``value`` looks like a valid email address."""
    return bool(EMAIL_PATTERN.match(value))


def validate_domain(value: str) -> bool:
    """Return ``True`` if ``value`` resembles a fully-qualified domain name."""
    return bool(DOMAIN_PATTERN.match(value))


def validate_url(value: str) -> bool:
    """Return ``True`` if ``value`` appears to be a valid HTTP or HTTPS URL."""
    return bool(URL_PATTERN.match(value))


def is_positive_int(value: str) -> bool:
    """Return ``True`` if ``value`` represents a positive integer."""
    return value.isdigit() and int(value) > 0


def ensure_positive_int(value: int, name: str = "value") -> int:
    """Return ``value`` if it is a positive ``int`` else raise ``ValueError``."""

    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")
    return value


def ensure_non_empty_str(value: str, name: str = "value") -> str:
    """Return ``value`` if it is a non-empty ``str`` else raise ``ValueError``."""

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")
    return value


def sanitize_filename(name: str, replacement: str = "_") -> str:
    """Return ``name`` stripped of path separators and invalid characters."""

    safe_chars = f"-_. {string.ascii_letters}{string.digits}"
    sanitized = [c if c in safe_chars else replacement for c in name]
    cleaned = "".join(sanitized)
    return cleaned.replace("/", replacement).replace("\\", replacement)



