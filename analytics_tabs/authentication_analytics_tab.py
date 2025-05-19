"""Authentication analysis UI components.

This tab presents the results of the authentication audit section as
summaries and simple charts.  Metrics include 2FA enforcement,
password policy status and whether SSO is configured as referenced in
the :mod:`audit_engine` description in the reference guide.
"""

from __future__ import annotations

from PyQt6.QtWidgets import (
    QLabel,
    QTableWidget,
    QTableWidgetItem,
    QVBoxLayout,
    QWidget,
)

from audit_visuals import ChartFactory
from report_db import fetch_last_run


class AuthenticationAnalyticsTab(QWidget):
    """Widget displaying authentication-related analytics."""

    def __init__(self) -> None:
        super().__init__()
        self._chart_factory = ChartFactory()

        # Layout with a simple label and table of metrics.
        self._layout = QVBoxLayout(self)

        self._summary_label = QLabel("Authentication Overview")
        self._layout.addWidget(self._summary_label)

        self._metrics_table = QTableWidget(0, 2)
        self._metrics_table.setHorizontalHeaderLabels(["Metric", "Value"])
        self._layout.addWidget(self._metrics_table)

    def refresh(self) -> None:
        """Refresh displayed data from the most recent audit run."""

        run_data = fetch_last_run() or {}
        section = next(
            (s for s in run_data.get("sections", []) if s.get("name") == "Authentication"),
            None,
        )
        metrics = {}
        if section:
            metrics = {item["key"]: item["value"] for item in section.get("stats", [])}

        self._metrics_table.setRowCount(len(metrics))
        for row, (key, value) in enumerate(metrics.items()):
            self._metrics_table.setItem(row, 0, QTableWidgetItem(str(key)))
            self._metrics_table.setItem(row, 1, QTableWidgetItem(str(value)))

        # Example chart generation for MFA statistics.
        if "mfa_enabled_percent" in metrics:
            percent = float(metrics["mfa_enabled_percent"])
            self._chart_factory.create_pie_chart(
                {
                    "MFA Enabled": percent,
                    "Other": 100 - percent,
                }
            )
