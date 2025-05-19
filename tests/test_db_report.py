"""Tests covering :mod:`db` and :mod:`report_db`."""

from __future__ import annotations

import sqlite3
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import db
import report_db


class DBReportTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.db_path = Path(self.tmp.name) / "gaudit.db"
        self.original_path = db.DB_PATH
        db.DB_PATH = self.db_path
        db.init_db()

    def tearDown(self) -> None:
        db.DB_PATH = self.original_path
        self.tmp.cleanup()

    def test_init_db_creates_tables(self) -> None:
        """Verify that all expected tables are created."""

        conn = sqlite3.connect(self.db_path)
        cur = conn.execute(
            "SELECT name FROM sqlite_master WHERE type='table' ORDER BY name"
        )
        names = {row[0] for row in cur.fetchall()}
        conn.close()

        expected = {"finding", "raw_object", "run", "section", "stat"}
        self.assertTrue(expected.issubset(names))

    def test_insert_and_fetch_data(self) -> None:
        """Insert records via :mod:`db` and read them back with :mod:`report_db`."""

        run_id = db.create_run()
        sec_id = db.start_section(run_id, "Example")
        db.insert_finding(sec_id, "ERROR", "oops")
        db.insert_stat(sec_id, "k", "v")
        db.complete_section(sec_id)

        fetched = report_db.fetch_run(run_id, db_path=self.db_path)

        self.assertEqual(fetched["id"], run_id)
        self.assertEqual(len(fetched["sections"]), 1)

        section = fetched["sections"][0]
        self.assertEqual(section["name"], "Example")
        self.assertEqual(section["status"], "complete")
        self.assertEqual(section["findings"][0]["message"], "oops")
        self.assertEqual(section["stats"][0]["value"], "v")

    def test_fetch_last_run_empty(self) -> None:
        """``fetch_last_run`` should return an empty dict with no data."""

        self.assertEqual(report_db.fetch_last_run(db_path=self.db_path), {})

    def test_fetch_last_run_returns_latest(self) -> None:
        run1 = db.create_run()
        sec1 = db.start_section(run1, "One")
        db.complete_section(sec1)

        run2 = db.create_run()
        sec2 = db.start_section(run2, "Two")
        db.complete_section(sec2)

        last = report_db.fetch_last_run(db_path=self.db_path)
        self.assertEqual(last["id"], run2)


if __name__ == "__main__":  # pragma: no cover - manual execution
    unittest.main()

