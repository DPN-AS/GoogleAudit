"""Utility for generating synthetic audit data for testing.

This module provides a helper that populates a SQLite database with a
complete audit run.  The schema mirrors the one described in the project
reference guide and loosely matches the helpers in :mod:`db`.
"""

from __future__ import annotations

from datetime import datetime
import json
import os
import random
import sqlite3
from typing import Iterable


DB_PATH = "synthetic_audit.db"


def _ensure_schema(conn: sqlite3.Connection) -> None:
    """Create tables if they do not already exist."""

    conn.executescript(
        """
        CREATE TABLE IF NOT EXISTS run (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            started_at TEXT NOT NULL,
            completed_at TEXT,
            domain TEXT,
            cli_args_json TEXT,
            skipped_services_json TEXT,
            overall_status TEXT
        );

        CREATE TABLE IF NOT EXISTS section (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            run_id INTEGER NOT NULL REFERENCES run(id) ON DELETE CASCADE,
            name TEXT NOT NULL,
            status TEXT,
            duration_s REAL
        );

        CREATE TABLE IF NOT EXISTS finding (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            section_id INTEGER NOT NULL REFERENCES section(id) ON DELETE CASCADE,
            severity TEXT,
            message TEXT
        );

        CREATE TABLE IF NOT EXISTS stat (
            section_id INTEGER NOT NULL REFERENCES section(id) ON DELETE CASCADE,
            key TEXT,
            value TEXT
        );

        CREATE TABLE IF NOT EXISTS raw_object (
            section_id INTEGER NOT NULL REFERENCES section(id) ON DELETE CASCADE,
            object_json TEXT
        );
        """
    )


def _insert_run(conn: sqlite3.Connection) -> int:
    """Insert a run record and return its ID."""

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO run (started_at, completed_at, domain, cli_args_json,
                         skipped_services_json, overall_status)
        VALUES (?, ?, ?, ?, ?, ?)""",
        (
            datetime.utcnow().isoformat(),
            None,
            "example.com",
            json.dumps({"intensive": False}),
            json.dumps([]),
            "IN_PROGRESS",
        ),
    )
    return int(cur.lastrowid)


def _complete_run(conn: sqlite3.Connection, run_id: int) -> None:
    """Mark the run as completed."""

    conn.execute(
        "UPDATE run SET completed_at = ?, overall_status = ? WHERE id = ?",
        (datetime.utcnow().isoformat(), "COMPLETED", run_id),
    )


def _insert_section(conn: sqlite3.Connection, run_id: int, name: str) -> int:
    """Insert a section and return its ID."""

    cur = conn.cursor()
    cur.execute(
        """
        INSERT INTO section (run_id, name, status, duration_s)
        VALUES (?, ?, ?, ?)""",
        (run_id, name, "COMPLETED", round(random.uniform(0.5, 3.0), 2)),
    )
    return int(cur.lastrowid)


def _insert_findings(conn: sqlite3.Connection, section_id: int) -> None:
    """Insert a few sample findings."""

    severities = ["LOW", "MEDIUM", "HIGH"]
    for i in range(random.randint(1, 3)):
        conn.execute(
            "INSERT INTO finding (section_id, severity, message) VALUES (?, ?, ?)",
            (
                section_id,
                random.choice(severities),
                f"Sample finding {i + 1}",
            ),
        )


def _insert_stats(conn: sqlite3.Connection, section_id: int) -> None:
    """Insert example statistics for a section."""

    stats = {
        "items_checked": str(random.randint(20, 200)),
        "items_flagged": str(random.randint(0, 10)),
    }
    for key, value in stats.items():
        conn.execute(
            "INSERT INTO stat (section_id, key, value) VALUES (?, ?, ?)",
            (section_id, key, value),
        )


def _insert_raw(conn: sqlite3.Connection, section_id: int) -> None:
    """Insert a JSON object representing raw data."""

    payload = json.dumps({"dummy": True})
    conn.execute(
        "INSERT INTO raw_object (section_id, object_json) VALUES (?, ?)",
        (section_id, payload),
    )


def _create_sections(conn: sqlite3.Connection, run_id: int, names: Iterable[str]) -> None:
    """Create sections with sample data for each name."""

    for name in names:
        sec_id = _insert_section(conn, run_id, name)
        _insert_findings(conn, sec_id)
        _insert_stats(conn, sec_id)
        _insert_raw(conn, sec_id)


def create_fake_run(db_path: str | None = None) -> None:
    """Generate a complete fake audit run.

    Parameters
    ----------
    db_path:
        Optional path to the SQLite database.  If omitted, a file named
        ``synthetic_audit.db`` in the current working directory is used.
    """

    path = db_path or DB_PATH
    os.makedirs(os.path.dirname(path) or ".", exist_ok=True)
    conn = sqlite3.connect(path)
    try:
        _ensure_schema(conn)

        run_id = _insert_run(conn)
        section_names = [
            "Users and OUs",
            "Authentication",
            "Admin Privileges",
            "Groups",
            "Drive Data Security",
            "Email Security",
            "Application Security",
            "Logging and Alerts",
            "MDM Basics",
            "ChromeOS Devices",
        ]
        _create_sections(conn, run_id, section_names)
        _complete_run(conn, run_id)
        conn.commit()
    finally:
        conn.close()

