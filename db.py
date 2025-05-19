"""SQLite database helpers for GAudit V2."""

from __future__ import annotations

import sqlite3
import time
from datetime import datetime
from pathlib import Path
from typing import Dict

DB_PATH = Path("gaudit.db")

# Tracks section start times to calculate duration
_section_start_times: Dict[int, float] = {}


def _get_conn() -> sqlite3.Connection:
    """Return a connection to the GAudit database."""
    conn = sqlite3.connect(DB_PATH)
    conn.execute("PRAGMA foreign_keys = ON")
    return conn


def init_db() -> None:
    """Initialize the database schema."""
    conn = _get_conn()
    cur = conn.cursor()

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS run (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            domain TEXT,
            cli_args_json TEXT,
            skipped_services_json TEXT,
            overall_status TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS section (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL REFERENCES run(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            status TEXT,
            duration_s REAL
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS finding (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id INTEGER NOT NULL REFERENCES section(id) ON DELETE CASCADE,
            severity TEXT,
            message TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS stat (
            section_id INTEGER NOT NULL REFERENCES section(id) ON DELETE CASCADE,
            key TEXT,
            value TEXT
        )
        """
    )

    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS raw_object (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id INTEGER NOT NULL REFERENCES section(id) ON DELETE CASCADE,
            data BLOB
        )
        """
    )

    conn.commit()
    conn.close()


def create_run() -> int:
    """Create a new audit run record."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO run (started_at) VALUES (?)",
        (datetime.utcnow().isoformat(),),
    )
    run_id = cur.lastrowid
    conn.commit()
    conn.close()
    return run_id


def start_section(run_id: int, name: str) -> int:
    """Start tracking an audit section."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO section (run_id, name, status) VALUES (?, ?, ?)",
        (run_id, name, "in_progress"),
    )
    section_id = cur.lastrowid
    conn.commit()
    conn.close()

    _section_start_times[section_id] = time.monotonic()
    return section_id


def complete_section(section_id: int) -> None:
    """Mark an audit section as complete."""
    start_time = _section_start_times.pop(section_id, None)
    duration = None
    if start_time is not None:
        duration = time.monotonic() - start_time

    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE section SET status = ?, duration_s = ? WHERE id = ?",
        ("complete", duration, section_id),
    )
    conn.commit()
    conn.close()


def insert_finding(section_id: int, severity: str, message: str) -> None:
    """Record a security finding."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO finding (section_id, severity, message) VALUES (?, ?, ?)",
        (section_id, severity, message),
    )
    conn.commit()
    conn.close()


def insert_stat(section_id: int, key: str, value: str) -> None:
    """Store a statistic for an audit section."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO stat (section_id, key, value) VALUES (?, ?, ?)",
        (section_id, key, value),
    )
    conn.commit()
    conn.close()


def insert_raw(section_id: int, raw_data: bytes) -> None:
    """Save raw audit data."""
    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "INSERT INTO raw_object (section_id, data) VALUES (?, ?)",
        (section_id, sqlite3.Binary(raw_data)),
    )
    conn.commit()
    conn.close()

