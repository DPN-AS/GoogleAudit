"""Drive security analysis UI components.

This module implements the ``DriveAnalyticsTab`` which displays Drive security
metrics and sharing analysis results.  The design is intentionally simple so the
UI can serve as an example implementation for the other analytics tabs described
in the reference guide.
"""

from __future__ import annotations

from typing import Iterable, Mapping

from PyQt6.QtWidgets import (QPushButton, QTableWidget, QTableWidgetItem,
                             QVBoxLayout, QWidget)

import audit_engine


class DriveAnalyticsTab(QWidget):
    """Widget showing Drive security statistics and findings."""

    def __init__(self) -> None:
        super().__init__()
        self._setup_ui()

    def _setup_ui(self) -> None:
        """Initialize child widgets and layout."""
        layout = QVBoxLayout(self)

        self.refresh_btn = QPushButton("Refresh")
        self.refresh_btn.clicked.connect(self.refresh)
        layout.addWidget(self.refresh_btn)

        # Table with two columns: Issue description and severity.
        self.table = QTableWidget(0, 2)
        self.table.setHorizontalHeaderLabels(["Issue", "Severity"])
        layout.addWidget(self.table)

    def refresh(self) -> None:
        """Run Drive data security audit and display the findings."""
        results = audit_engine.audit_drive_data_security()
        if not results:
            # ``audit_drive_data_security`` currently returns ``None``.  The
            # table is cleared so the UI remains responsive when the function
            # is later implemented.
            self.table.setRowCount(0)
            return

        self._populate_results(results)

    def _populate_results(self, findings: Iterable[Mapping[str, str]]) -> None:
        """Populate ``self.table`` with the given findings."""
        self.table.setRowCount(0)
        for row, finding in enumerate(findings):
            self.table.insertRow(row)
            issue = finding.get("message", "")
            severity = finding.get("severity", "")
            self.table.setItem(row, 0, QTableWidgetItem(issue))
            self.table.setItem(row, 1, QTableWidgetItem(severity))
