import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import db

class DBValidationErrorTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.original_path = db.DB_PATH
        db.DB_PATH = Path(self.tmp.name) / "test.db"
        db.init_db()

    def tearDown(self) -> None:
        db.DB_PATH = self.original_path
        self.tmp.cleanup()

    def test_start_section_invalid_run_id(self):
        with self.assertRaises(ValueError):
            db.start_section(0, "name")

    def test_complete_section_invalid_id(self):
        with self.assertRaises(ValueError):
            db.complete_section(-1)

    def test_insert_raw_invalid_bytes(self):
        with self.assertRaises(ValueError):
            db.insert_raw(1, "not bytes")  # type: ignore[arg-type]

if __name__ == "__main__":
    unittest.main()
