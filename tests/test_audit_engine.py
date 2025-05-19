"""Tests for :mod:`audit_engine`."""

from __future__ import annotations

import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import db
import audit_engine
import report_db


class AuditEngineTests(unittest.TestCase):
    """Validate that running the audit writes expected records."""

    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.original_path = db.DB_PATH
        db.DB_PATH = Path(self.tmp.name) / "audit.db"
        db.init_db()

    def tearDown(self) -> None:
        db.DB_PATH = self.original_path
        self.tmp.cleanup()

    def test_run_audit_creates_db_and_sections(self) -> None:
        """Ensure ``run_audit`` creates all sections and the DB file."""

        results = audit_engine.run_audit()

        # Database file should be created
        self.assertTrue(db.DB_PATH.exists())

        # There should be a result for every audit section
        self.assertEqual(len(results), 10)
        self.assertTrue(all(r.status == "PASS" for r in results))

        # Verify records persisted via the reporting helper
        run = report_db.fetch_last_run(db_path=db.DB_PATH)
        self.assertEqual(len(run.get("sections", [])), 10)


if __name__ == "__main__":  # pragma: no cover - manual execution
    unittest.main()

