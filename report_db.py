"""Database access layer for report generation.

This module exposes helper functions for retrieving audit data from the
SQLite database defined in :mod:`db`.  The schema for the database is
documented in ``REFERENCE_GUIDE.md`` and consists of the following core
tables::

    run(id, started_at, completed_at, domain, cli_args_json,
        skipped_services_json, overall_status)
    section(id, run_id, name, status, duration_s)
    finding(id, section_id, severity, message)
    stat(section_id, key, value)
    raw_object(...)

Only a subset of the schema is required for report generation.  The
functions below provide convenient read access returning dictionaries so
that report generation code can easily consume the stored audit data.

The database location defaults to ``gaudit.db`` in the current working
directory but can be overridden via the ``GAUDIT_DB_PATH`` environment
variable.
"""

from __future__ import annotations

from pathlib import Path
import os
import sqlite3
from typing import Any, Iterable


DB_FILE = Path(os.environ.get("GAUDIT_DB_PATH", "gaudit.db"))


def _ensure_conn(
    db_path: str | Path | None = None,
    conn: sqlite3.Connection | None = None,
) -> tuple[sqlite3.Connection, bool]:
    """Return a connection to ``db_path`` and whether it should be closed."""

    if conn is not None:
        return conn, False

    path = Path(db_path) if db_path is not None else DB_FILE
    connection = sqlite3.connect(path)
    connection.row_factory = sqlite3.Row
    return connection, True


def fetch_last_run(*, db_path: str | Path = DB_FILE) -> dict:
    """Return information about the most recent audit run.

    Parameters
    ----------
    db_path:
        Path to the SQLite database.  Defaults to ``gaudit.db`` in the
        current working directory.

    Returns
    -------
    dict
        A dictionary describing the run and its sections.  If the database
        contains no runs an empty dictionary is returned.
    """

    conn, close_conn = _ensure_conn(db_path)
    try:
        row = conn.execute(
            "SELECT id, started_at, completed_at, domain, cli_args_json, "
            "skipped_services_json, overall_status "
            "FROM run ORDER BY id DESC LIMIT 1"
        ).fetchone()
        if row is None:
            return {}

        run = dict(row)
        run["sections"] = fetch_sections(row["id"], conn=conn)
        return run
    finally:
        if close_conn:
            conn.close()


def fetch_run(run_id: int, *, db_path: str | Path = DB_FILE) -> dict:
    """Return a specific run by ``run_id`` including its sections."""

    conn, close_conn = _ensure_conn(db_path)
    try:
        row = conn.execute(
            "SELECT id, started_at, completed_at, domain, cli_args_json, "
            "skipped_services_json, overall_status FROM run WHERE id = ?",
            (run_id,),
        ).fetchone()
        if row is None:
            return {}

        run = dict(row)
        run["sections"] = fetch_sections(run_id, conn=conn)
        return run
    finally:
        if close_conn:
            conn.close()


def fetch_sections(
    run_id: int,
    *,
    db_path: str | Path = DB_FILE,
    conn: sqlite3.Connection | None = None,
) -> list[dict]:
    """Return a list of sections for ``run_id`` with findings and stats."""

    conn, close_conn = _ensure_conn(db_path, conn)
    try:
        cur = conn.execute(
            "SELECT id, name, status, duration_s FROM section "
            "WHERE run_id = ? ORDER BY id",
            (run_id,),
        )
        sections = []
        for row in cur.fetchall():
            section = dict(row)
            sec_id = section["id"]
            section["findings"] = fetch_findings(sec_id, conn=conn)
            section["stats"] = fetch_stats(sec_id, conn=conn)
            sections.append(section)
        return sections
    finally:
        if close_conn:
            conn.close()


def fetch_findings(
    section_id: int,
    *,
    db_path: str | Path = DB_FILE,
    conn: sqlite3.Connection | None = None,
) -> list[dict]:
    """Return all findings for ``section_id``."""

    conn, close_conn = _ensure_conn(db_path, conn)
    try:
        cur = conn.execute(
            "SELECT severity, message FROM finding "
            "WHERE section_id = ? ORDER BY id",
            (section_id,),
        )
        results = [dict(row) for row in cur.fetchall()]
        return results
    finally:
        if close_conn:
            conn.close()


def fetch_stats(
    section_id: int,
    *,
    db_path: str | Path = DB_FILE,
    conn: sqlite3.Connection | None = None,
) -> list[dict]:
    """Return all statistics for ``section_id``."""

    conn, close_conn = _ensure_conn(db_path, conn)
    try:
        cur = conn.execute(
            "SELECT key, value FROM stat WHERE section_id = ? ORDER BY rowid",
            (section_id,),
        )
        return [dict(row) for row in cur.fetchall()]
    finally:
        if close_conn:
            conn.close()


def fetch_raw_objects(
    section_id: int,
    *,
    db_path: str | Path = DB_FILE,
    conn: sqlite3.Connection | None = None,
) -> list[dict]:
    """Return raw objects associated with ``section_id`` if available."""

    conn, close_conn = _ensure_conn(db_path, conn)
    try:
        # The schema for ``raw_object`` is not fully specified.  We fetch all
        # columns so that callers can interpret the data as needed.
        cur = conn.execute(
            "PRAGMA table_info(raw_object)"
        )
        columns = [row[1] for row in cur.fetchall()]
        if not columns:
            return []

        query = (
            "SELECT * FROM raw_object WHERE section_id = ? ORDER BY rowid"
        )
        cur = conn.execute(query, (section_id,))
        return [dict(zip(columns, row)) for row in cur.fetchall()]
    finally:
        if close_conn:
            conn.close()
