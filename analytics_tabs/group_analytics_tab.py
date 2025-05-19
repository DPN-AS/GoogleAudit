"""Group management analysis UI components.

This tab presents insights about Google Workspace groups and their
permissions.  It relies on :func:`audit_engine.audit_groups` to obtain
the latest information about group memberships and sharing settings.

The layout consists of a summary label and a table displaying details
for each group.  The table columns cover group name, member counts,
external membership counts and whether external members are allowed.
"""

from __future__ import annotations

from typing import Iterable, Mapping

try:  # PyQt6 is optional for documentation builds
    from PyQt6.QtWidgets import (
        QHeaderView,
        QLabel,
        QPushButton,
        QTableWidget,
        QTableWidgetItem,
        QVBoxLayout,
        QWidget,
    )
except Exception:  # pragma: no cover - fallback for environments without PyQt6
    QWidget = object  # type: ignore
    QVBoxLayout = QLabel = QTableWidget = QTableWidgetItem = QPushButton = object  # type: ignore
    QHeaderView = object  # type: ignore

import audit_engine


class GroupAnalyticsTab(QWidget):
    """UI widget for displaying group management analysis results."""

    def __init__(self) -> None:
        """Initialise the widget and set up the UI."""

        super().__init__()
        self._init_ui()

    # ------------------------------------------------------------------
    # UI setup
    # ------------------------------------------------------------------
    def _init_ui(self) -> None:
        """Create widgets and layout."""
        self._layout = QVBoxLayout(self)

        self._header = QLabel("Group Management Insights")
        self._table = QTableWidget(0, 2)
        self._table.setHorizontalHeaderLabels(["Metric", "Value"])
        if hasattr(self._table, "horizontalHeader"):
            self._table.horizontalHeader().setSectionResizeMode(
                QHeaderView.ResizeMode.Stretch  # type: ignore[attr-defined]
            )

        self._refresh_button = QPushButton("Refresh")
        if hasattr(self._refresh_button, "clicked"):
            self._refresh_button.clicked.connect(self.refresh)  # type: ignore[attr-defined]

        self._layout.addWidget(self._header)
        self._layout.addWidget(self._table)
        self._layout.addWidget(self._refresh_button)

    # ------------------------------------------------------------------
    # Data handling
    # ------------------------------------------------------------------
    def refresh(self) -> None:
        """Populate the table with the latest group audit results."""

        result = audit_engine.audit_groups()
        stats = result.stats

        self._table.setRowCount(len(stats))

        for row_index, (key, value) in enumerate(stats.items()):
            self._table.setItem(row_index, 0, QTableWidgetItem(str(key)))
            self._table.setItem(row_index, 1, QTableWidgetItem(str(value)))
