"""SQLite database helpers for GAudit V2.

The location of the SQLite database can be configured with the
``GAUDIT_DB_PATH`` environment variable.  If not set, ``gaudit.db`` in the
current working directory is used.
"""

from __future__ import annotations

import logging
import sqlite3
import time
import json
from datetime import datetime
from pathlib import Path
from typing import Dict, Any, Iterable
import os
from typing import Dict
import queue
from contextlib import contextmanager
import logging

DB_PATH = Path(os.environ.get("GAUDIT_DB_PATH", "gaudit.db"))

# Pool of reusable SQLite connections
# Connection pools keyed by database path
_CONN_POOLS: dict[Path, queue.LifoQueue[sqlite3.Connection]] = {}
# Tracks which DB path each connection belongs to
_CONN_PATHS: dict[sqlite3.Connection, Path] = {}

# Tracks section start times to calculate duration

_section_start_times: Dict[int, float] = {}


logger = logging.getLogger(__name__)


def _validate_positive_int(value: int, name: str) -> None:
    """Raise ``ValueError`` if ``value`` is not a positive integer."""

    if not isinstance(value, int) or value <= 0:
        raise ValueError(f"{name} must be a positive integer")


def _validate_non_empty(value: str, name: str) -> None:
    """Raise ``ValueError`` if ``value`` is empty or only whitespace."""

    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string")


def _get_conn() -> sqlite3.Connection:
    """Retrieve a connection from the pool or create a new one."""
    pool = _CONN_POOLS.setdefault(DB_PATH, queue.LifoQueue(maxsize=5))
    try:
        conn = pool.get_nowait()
    except queue.Empty:
        conn = sqlite3.connect(DB_PATH)
        conn.execute("PRAGMA foreign_keys = ON")
        _CONN_PATHS[conn] = DB_PATH
    return conn


def _release_conn(conn: sqlite3.Connection) -> None:
    """Return ``conn`` to the pool or close it if the pool is full."""
    path = _CONN_PATHS.get(conn, DB_PATH)
    pool = _CONN_POOLS.setdefault(Path(path), queue.LifoQueue(maxsize=5))
    try:
        pool.put_nowait(conn)
    except queue.Full:
        conn.close()
        _CONN_PATHS.pop(conn, None)


@contextmanager
def _managed_conn() -> sqlite3.Connection:
    """Context manager that handles commits and rollbacks."""
    conn = _get_conn()
    try:
        yield conn
        conn.commit()
    except sqlite3.Error:
        conn.rollback()
        raise
    finally:
        _release_conn(conn)


def init_db() -> None:
    """Initialize the database schema."""
    conn = _get_conn()
    try:

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
    except sqlite3.DatabaseError as exc:  # pragma: no cover - error path
        conn.rollback()
        logger.exception("Failed to initialize database")
        raise RuntimeError("Database error during init_db") from exc
    finally:
        conn.close()


def create_run(
    *,
    domain: str | None = None,
    cli_args: dict[str, Any] | None = None,
    skipped_services: Iterable[str] | None = None,
) -> int:
    """Create a new audit run record.

    Parameters
    ----------
    domain:
        Domain being audited if applicable.
    cli_args:
        Mapping of command line arguments used for the run.
    skipped_services:
        Iterable of services that were intentionally skipped.
    """

    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        """INSERT INTO run (started_at, domain, cli_args_json, 
                         skipped_services_json, overall_status)
           VALUES (?, ?, ?, ?, ?)""",
        (
            datetime.utcnow().isoformat(),
            domain,
            json.dumps(cli_args) if cli_args is not None else None,
            json.dumps(list(skipped_services))
            if skipped_services is not None
            else None,
            "IN_PROGRESS",
        ),
    )
    run_id = int(cur.lastrowid)
    conn.commit()
    conn.close()
    return run_id



def start_section(run_id: int, name: str) -> int:
    """Start tracking an audit section."""
    _validate_positive_int(run_id, "run_id")
    _validate_non_empty(name, "name")
    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO section (run_id, name, status) VALUES (?, ?, ?)",
            (run_id, name, "in_progress"),
        )
        section_id = cur.lastrowid
        conn.commit()
        _section_start_times[section_id] = time.monotonic()
        return section_id
    except sqlite3.DatabaseError as exc:  # pragma: no cover - error path
        conn.rollback()
        logger.exception("Failed to start section")
        raise RuntimeError("Database error during start_section") from exc
    finally:
        conn.close()


def complete_section(section_id: int) -> None:
    """Mark an audit section as complete."""
    _validate_positive_int(section_id, "section_id")

    start_time = _section_start_times.pop(section_id, None)
    duration = None
    if start_time is not None:
        duration = time.monotonic() - start_time

    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "UPDATE section SET status = ?, duration_s = ? WHERE id = ?",
            ("complete", duration, section_id),
        )
        conn.commit()
    except sqlite3.DatabaseError as exc:  # pragma: no cover - error path
        conn.rollback()
        logger.exception("Failed to complete section")
        raise RuntimeError("Database error during complete_section") from exc
    finally:
        conn.close()


def insert_finding(section_id: int, severity: str, message: str) -> None:
    """Record a security finding."""
    _validate_positive_int(section_id, "section_id")
    _validate_non_empty(severity, "severity")
    _validate_non_empty(message, "message")

    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO finding (section_id, severity, message) VALUES (?, ?, ?)",
            (section_id, severity, message),
        )
        conn.commit()
    except sqlite3.DatabaseError as exc:  # pragma: no cover - error path
        conn.rollback()
        logger.exception("Failed to insert finding")
        raise RuntimeError("Database error during insert_finding") from exc
    finally:
        conn.close()


def insert_stat(section_id: int, key: str, value: str) -> None:
    """Store a statistic for an audit section."""
    _validate_positive_int(section_id, "section_id")
    _validate_non_empty(key, "key")

    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO stat (section_id, key, value) VALUES (?, ?, ?)",
            (section_id, key, value),
        )
        conn.commit()
    except sqlite3.DatabaseError as exc:  # pragma: no cover - error path
        conn.rollback()
        logger.exception("Failed to insert stat")
        raise RuntimeError("Database error during insert_stat") from exc
    finally:
        conn.close()


def insert_raw(section_id: int, raw_data: bytes) -> None:
    """Save raw audit data."""
    _validate_positive_int(section_id, "section_id")
    if not isinstance(raw_data, (bytes, bytearray)):
        raise ValueError("raw_data must be bytes-like")

    conn = _get_conn()
    try:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO raw_object (section_id, data) VALUES (?, ?)",
            (section_id, sqlite3.Binary(raw_data)),
        )
        conn.commit()
    except sqlite3.DatabaseError as exc:  # pragma: no cover - error path
        conn.rollback()
        logger.exception("Failed to insert raw data")
        raise RuntimeError("Database error during insert_raw") from exc
    finally:
        conn.close()


def finalize_run(run_id: int, overall_status: str) -> None:
    """Mark a run as completed with ``overall_status``."""

    conn = _get_conn()
    cur = conn.cursor()
    cur.execute(
        "UPDATE run SET completed_at = ?, overall_status = ? WHERE id = ?",
        (datetime.utcnow().isoformat(), overall_status, run_id),
    )
    conn.commit()
    conn.close()

