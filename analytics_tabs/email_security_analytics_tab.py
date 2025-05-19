"""Email security analysis UI components.

This module defines :class:`EmailSecurityAnalyticsTab`, a PyQt6 ``QWidget`` that
displays statistics and findings related to Gmail security.  The reference guide
describes several areas of interest for email security including forwarding
rules, delegation, and IMAP/POP settings.  The tab queries the most recent audit
run via :func:`report_db.fetch_last_run` and presents a simple table of
configuration values along with a list of findings.
"""

from __future__ import annotations

from typing import Any, Dict

from PyQt6.QtWidgets import (
    QLabel,
    QListWidget,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

import report_db


class EmailSecurityAnalyticsTab(QWidget):
    """Display Gmail security statistics and findings."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)

        layout = QVBoxLayout(self)

        layout.addWidget(QLabel("Email Security Configuration"))

        self._table = QTableWidget(0, 2, self)
        self._table.setHorizontalHeaderLabels(["Control", "Value"])
        layout.addWidget(self._table)

        layout.addWidget(QLabel("Findings"))
        self._findings = QListWidget(self)
        layout.addWidget(self._findings)

        self.setLayout(layout)

    def refresh(self) -> None:
        """Reload data from the latest audit run."""

        self._table.setRowCount(0)
        self._findings.clear()

        run_data: Dict[str, Any] | None = report_db.fetch_last_run()
        if not run_data:
            return

        section = next(
            (s for s in run_data.get("sections", []) if s.get("name") == "Email Security"),
            None,
        )
        if not section:
            return

        email_info = {
            "stats": {item["key"]: item["value"] for item in section.get("stats", [])},
            "findings": section.get("findings", []),
        }

        for row, (key, value) in enumerate(email_info.get("stats", {}).items()):
            self._table.insertRow(row)
            self._table.setItem(row, 0, QTableWidgetItem(str(key)))
            self._table.setItem(row, 1, QTableWidgetItem(str(value)))

        for finding in email_info.get("findings", []):
            severity = finding.get("severity", "").upper()
            message = finding.get("message", "")
            self._findings.addItem(f"[{severity}] {message}")
