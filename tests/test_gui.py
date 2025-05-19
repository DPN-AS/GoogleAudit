"""Automated GUI tests for the PyQt6 main window."""

from __future__ import annotations

import os
from pathlib import Path
from tempfile import TemporaryDirectory
import unittest
from unittest.mock import patch

try:
    from PyQt6.QtWidgets import QApplication, QDialog
except ModuleNotFoundError:  # pragma: no cover - optional dependency
    QApplication = None  # type: ignore[assignment]
    QDialog = None  # type: ignore[assignment]

if QApplication is not None:
    import db
    from main_window import MainWindow, RunAuditSettingsDialog, AuditWorker
else:  # pragma: no cover - optional dependency
    db = None  # type: ignore[assignment]


@unittest.skipIf(QApplication is None, "PyQt6 not available")
class MainWindowGUITests(unittest.TestCase):
    """Basic GUI tests exercising the main window."""

    @classmethod
    def setUpClass(cls) -> None:
        os.environ.setdefault("QT_QPA_PLATFORM", "offscreen")
        cls._app = QApplication([])

    @classmethod
    def tearDownClass(cls) -> None:
        cls._app.quit()
        cls._app = None  # type: ignore[assignment]

    def setUp(self) -> None:
        self.tmp = TemporaryDirectory()
        self.original_db_path = db.DB_PATH
        db.DB_PATH = Path(self.tmp.name) / "test.db"
        db.init_db()
        self.window = MainWindow()
        self.window.show()

    def tearDown(self) -> None:
        self.window.close()
        db.DB_PATH = self.original_db_path
        self.tmp.cleanup()

    def _get_run_audit_action(self):
        audit_menu = self.window.menuBar().actions()[0].menu()
        for action in audit_menu.actions():
            if action.text() == "Run Audit":
                return action
        self.fail("Run Audit action not found")

    def test_window_has_expected_tabs(self) -> None:
        self.assertEqual(self.window.windowTitle(), "GAudit V2")
        expected = [
            "Authentication",
            "Drive",
            "Email Security",
            "Groups",
            "Users/OUs",
        ]
        texts = [self.window._tabs.tabText(i) for i in range(self.window._tabs.count())]
        self.assertEqual(texts, expected)

    def test_run_audit_menu_triggers_dialog(self) -> None:
        action = self._get_run_audit_action()
        with patch.object(RunAuditSettingsDialog, "exec", return_value=QDialog.DialogCode.Rejected) as exec_mock, patch.object(AuditWorker, "start") as start_mock:
            action.trigger()
            exec_mock.assert_called_once()
            start_mock.assert_not_called()

    def test_run_audit_menu_runs_worker_when_accepted(self) -> None:
        action = self._get_run_audit_action()
        with patch.object(RunAuditSettingsDialog, "exec", return_value=QDialog.DialogCode.Accepted) as exec_mock, patch.object(AuditWorker, "start") as start_mock:
            action.trigger()
            exec_mock.assert_called_once()
            start_mock.assert_called_once()


if __name__ == "__main__":  # pragma: no cover - manual execution
    unittest.main()
