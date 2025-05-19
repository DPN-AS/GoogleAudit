import unittest
import db

class DBValidationErrorTests(unittest.TestCase):
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
