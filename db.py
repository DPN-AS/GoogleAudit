"""SQLite database helpers for GAudit V2."""

from __future__ import annotations


def init_db() -> None:
    """Initialize the database schema."""
    pass


def create_run() -> int:
    """Create a new audit run record."""
    pass


def start_section(run_id: int, name: str) -> int:
    """Start tracking an audit section."""
    pass


def complete_section(section_id: int) -> None:
    """Mark an audit section as complete."""
    pass


def insert_finding(section_id: int, severity: str, message: str) -> None:
    """Record a security finding."""
    pass


def insert_stat(section_id: int, key: str, value: str) -> None:
    """Store a statistic for an audit section."""
    pass


def insert_raw(section_id: int, raw_data: bytes) -> None:
    """Save raw audit data."""
    pass
