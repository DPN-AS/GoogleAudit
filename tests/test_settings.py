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


if __name__ == "__main__":  # pragma: no cover - manual execution
    unittest.main()

