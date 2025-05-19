"""Main application window and related classes for GAudit V2.
This module contains the high level PyQt6 GUI components.
"""

from __future__ import annotations

from typing import Optional

from PyQt6 import QtCore, QtWidgets
from PyQt6.QtGui import QAction

import audit_engine


class MainWindow(QtWidgets.QMainWindow):
    """Main application window acting as the UI controller."""

    def __init__(self) -> None:
        super().__init__()
        self.setWindowTitle("GAudit V2")
        self._tabs = QtWidgets.QTabWidget()
        self.setCentralWidget(self._tabs)
        self._create_status_bar()
        self._create_menus()
        self._populate_tabs()

    def _create_status_bar(self) -> None:
        self._status = QtWidgets.QStatusBar()
        self.setStatusBar(self._status)
        self._status.showMessage("Ready")

    def _create_menus(self) -> None:
        menubar = self.menuBar()
        audit_menu = menubar.addMenu("Audit")
        validate_action = QAction("Validate API", self)
        validate_action.triggered.connect(self._validate_api)
        run_action = QAction("Run Audit", self)
        run_action.triggered.connect(self._run_audit)
        audit_menu.addAction(validate_action)
        audit_menu.addAction(run_action)

    def _populate_tabs(self) -> None:
        # Placeholders for analytics tabs
        for name in [
            "Authentication",
            "Drive",
            "Email Security",
            "Groups",
            "Users/OUs",
        ]:
            widget = QtWidgets.QWidget()
            layout = QtWidgets.QVBoxLayout(widget)
            layout.addWidget(QtWidgets.QLabel(f"{name} analytics coming soon"))
            self._tabs.addTab(widget, name)

    def _validate_api(self) -> None:
        dialog = ApiValidationStatusDialog(self)
        thread = ApiValidationThread(dialog)
        thread.finished.connect(dialog.accept)
        dialog.show()
        thread.start()

    def _run_audit(self) -> None:
        settings_dialog = RunAuditSettingsDialog(self)
        if settings_dialog.exec() == QtWidgets.QDialog.DialogCode.Accepted:
            worker_dialog = QtWidgets.QProgressDialog(
                "Running audit...", "Cancel", 0, 0, self
            )
            worker_dialog.setWindowTitle("Audit Progress")
            worker_dialog.setModal(True)
            worker_dialog.show()

            worker = AuditWorker()
            worker.progress_updated.connect(
                lambda msg: worker_dialog.setLabelText(msg)
            )
            worker.finished.connect(worker_dialog.accept)
            worker.start()

    def show(self) -> None:
        """Display the main window."""
        super().show()


class ApiValidationThread(QtCore.QThread):
    """Background thread for validating API access."""

    progress = QtCore.pyqtSignal(str)

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)

    def run(self) -> None:  # type: ignore[override]
        self.progress.emit("Validating APIs...")
        audit_engine.validate_api_services()
        self.progress.emit("Validation complete")


class ApiValidationStatusDialog(QtWidgets.QDialog):
    """Dialog to show API validation status."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("API Validation")
        self._label = QtWidgets.QLabel("Starting validation...", self)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(self._label)

    def update_status(self, message: str) -> None:
        self._label.setText(message)


class RunAuditSettingsDialog(QtWidgets.QDialog):
    """Dialog for configuring audit run parameters."""

    def __init__(self, parent: Optional[QtWidgets.QWidget] = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Run Audit")
        layout = QtWidgets.QVBoxLayout(self)
        self.create_new_db = QtWidgets.QCheckBox("Create new database", self)
        self.intensive_mode = QtWidgets.QCheckBox("Intensive mode", self)
        layout.addWidget(self.create_new_db)
        layout.addWidget(self.intensive_mode)
        btn_box = QtWidgets.QDialogButtonBox(
            QtWidgets.QDialogButtonBox.StandardButton.Ok
            | QtWidgets.QDialogButtonBox.StandardButton.Cancel
        )
        btn_box.accepted.connect(self.accept)
        btn_box.rejected.connect(self.reject)
        layout.addWidget(btn_box)


class AuditWorker(QtCore.QThread):
    """Worker that runs audit tasks in the background."""

    progress_updated = QtCore.pyqtSignal(str)

    def run(self) -> None:  # type: ignore[override]
        tasks = [
            audit_engine.audit_users_and_ous,
            audit_engine.audit_authentication,
            audit_engine.audit_admin_privileges,
            audit_engine.audit_groups,
            audit_engine.audit_drive_data_security,
            audit_engine.audit_email_security,
            audit_engine.audit_application_security,
            audit_engine.audit_logging_and_alerts,
            audit_engine.audit_mdm_basics,
            audit_engine.audit_chromeos_devices,
        ]
        for task in tasks:
            self.progress_updated.emit(f"Running {task.__name__}...")
            task()
        self.progress_updated.emit("Audit complete")
