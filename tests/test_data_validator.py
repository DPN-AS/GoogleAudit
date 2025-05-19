"""Unit tests for :mod:`data_validator`."""

from __future__ import annotations

import unittest

import data_validator


class DataValidatorTests(unittest.TestCase):
    """Validate the small helper functions used for input checking."""

    def test_validate_email(self) -> None:
        self.assertTrue(data_validator.validate_email("user@example.com"))
        self.assertFalse(data_validator.validate_email("invalid"))

    def test_validate_domain(self) -> None:
        self.assertTrue(data_validator.validate_domain("example.com"))
        self.assertFalse(data_validator.validate_domain("no spaces"))

    def test_validate_url(self) -> None:
        self.assertTrue(data_validator.validate_url("https://example.com"))
        self.assertTrue(data_validator.validate_url("http://foo.bar/baz"))
        self.assertFalse(data_validator.validate_url("ftp://example.com"))

    def test_is_positive_int(self) -> None:
        self.assertTrue(data_validator.is_positive_int("5"))
        self.assertFalse(data_validator.is_positive_int("0"))
        self.assertFalse(data_validator.is_positive_int("-3"))
        self.assertFalse(data_validator.is_positive_int("abc"))

    def test_sanitize_filename(self) -> None:
        name = data_validator.sanitize_filename("bad/name\\file.txt")
        self.assertNotIn("/", name)
        self.assertNotIn("\\", name)

    def test_ensure_positive_int(self) -> None:
        self.assertEqual(data_validator.ensure_positive_int(5), 5)
        with self.assertRaises(ValueError):
            data_validator.ensure_positive_int(0)

    def test_ensure_non_empty_str(self) -> None:
        self.assertEqual(data_validator.ensure_non_empty_str("ok"), "ok")
        with self.assertRaises(ValueError):
            data_validator.ensure_non_empty_str("  ")


if __name__ == "__main__":  # pragma: no cover - manual execution
    unittest.main()

