"""User and OU analysis UI components."""

from __future__ import annotations

from typing import Dict

from PyQt6.QtWidgets import (
    QLabel,
    QTreeWidget,
    QTreeWidgetItem,
    QVBoxLayout,
    QWidget,
)

from report_db import fetch_last_run


class UsersOUsAnalyticsTab(QWidget):
    """Display analytics for users and organizational units."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self._layout = QVBoxLayout(self)
        self._title = QLabel("User and OU Analysis", self)
        self._tree = QTreeWidget(self)
        self._tree.setColumnCount(2)
        self._tree.setHeaderLabels(["Metric", "Value"])
        self._layout.addWidget(self._title)
        self._layout.addWidget(self._tree)

    def refresh(self) -> None:
        """Reload statistics from the latest audit run."""
        run_data = fetch_last_run() or {}
        section = next(
            (s for s in run_data.get("sections", []) if s.get("name") == "Users and OUs"),
            None,
        )
        stats = {}
        if section:
            stats = {item["key"]: item["value"] for item in section.get("stats", [])}
        self._populate_tree(stats)

    def _populate_tree(self, stats: Dict[str, int]) -> None:
        self._tree.clear()
        for key, value in stats.items():
            QTreeWidgetItem(self._tree, [key, str(value)])
