import json
import os
import unittest
from pathlib import Path
from tempfile import TemporaryDirectory

import settings
import audit_engine


class SettingsTests(unittest.TestCase):
    def test_default_settings_loaded_when_file_missing(self) -> None:
        tmp = TemporaryDirectory()
        path = Path(tmp.name) / "missing.json"
        loaded = settings.load_settings(path)
        self.assertIn("admin_sdk", loaded["api_services"])
        tmp.cleanup()

    def test_custom_settings_file(self) -> None:
        with TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "cfg.json"
            cfg.write_text(json.dumps({"api_services": ["one", "two"]}))
            loaded = settings.load_settings(cfg)
            self.assertEqual(loaded["api_services"], ["one", "two"])

    def test_default_file_created(self) -> None:
        with TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "auto.json"
            os.environ["GAUDIT_CONFIG"] = str(cfg)
            try:
                loaded = settings.load_settings()
            finally:
                os.environ.pop("GAUDIT_CONFIG", None)
            self.assertTrue(cfg.exists())
            self.assertIn("admin_sdk", loaded["api_services"])

    def test_invalid_json_raises(self) -> None:
        with TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "bad.json"
            cfg.write_text("{invalid")
            with self.assertRaises(ValueError):
                settings.load_settings(cfg)


class ValidateApiServicesTests(unittest.TestCase):
    def test_validate_api_services_uses_custom_config(self) -> None:
        with TemporaryDirectory() as tmp:
            cfg = Path(tmp) / "c.json"
            cfg.write_text(json.dumps({"api_services": ["svc1", "svc2"]}))
            os.environ["GAUDIT_CONFIG"] = str(cfg)
            try:
                result = audit_engine.validate_api_services()
            finally:
                os.environ.pop("GAUDIT_CONFIG", None)
            self.assertEqual(set(result.keys()), {"svc1", "svc2"})


class EnvHelperTests(unittest.TestCase):
    def test_env_int_and_bool(self) -> None:
        os.environ["TEST_INT"] = "5"
        os.environ["TEST_BOOL"] = "yes"
        try:
            self.assertEqual(audit_engine._env_int("TEST_INT", 0), 5)
            self.assertTrue(audit_engine._env_bool("TEST_BOOL", False))
            os.environ["TEST_INT"] = "notint"
            self.assertEqual(audit_engine._env_int("TEST_INT", 3), 3)
        finally:
            os.environ.pop("TEST_INT", None)
            os.environ.pop("TEST_BOOL", None)


if __name__ == "__main__":  # pragma: no cover - manual execution
    unittest.main()

