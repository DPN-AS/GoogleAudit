"""Tests for :mod:`secure_store` using a fake in-memory keyring."""

from __future__ import annotations

import importlib
import sys
import types
import unittest


class SecureStoreTests(unittest.TestCase):
    def setUp(self) -> None:
        # Provide a dummy keyring module before importing secure_store
        self.storage: dict[tuple[str, str], str] = {}
        self.fake_keyring = types.SimpleNamespace(
            set_password=lambda svc, user, pw: self.storage.__setitem__((svc, user), pw),
            get_password=lambda svc, user: self.storage.get((svc, user)),
        )
        self.orig_keyring = sys.modules.get("keyring")
        sys.modules["keyring"] = self.fake_keyring
        import secure_store

        self.secure_store = importlib.reload(secure_store)

    def tearDown(self) -> None:
        if self.orig_keyring is not None:
            sys.modules["keyring"] = self.orig_keyring
        else:
            sys.modules.pop("keyring", None)

    def test_round_trip_credentials(self) -> None:
        data = b"secret"
        self.secure_store.save_credentials(data)
        loaded = self.secure_store.load_credentials()
        self.assertEqual(loaded, data)

    def test_load_invalid_data_returns_none(self) -> None:
        self.storage[("GAuditV2", "credentials")] = "not base64"  # type: ignore[index]
        self.assertIsNone(self.secure_store.load_credentials())


if __name__ == "__main__":  # pragma: no cover - manual execution
    unittest.main()

