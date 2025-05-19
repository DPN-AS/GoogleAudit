"""Application help dialog implementation.

This module provides a small ``QDialog`` that displays the contents of
``REFERENCE_GUIDE.md``.  It is intended to act as the in-application help
system and documentation browser described in :mod:`REFERENCE_GUIDE.md`.
"""

from __future__ import annotations

from pathlib import Path

from PyQt6.QtCore import Qt
from PyQt6.QtWidgets import (
    QDialog,
    QHBoxLayout,
    QPushButton,
    QTextBrowser,
    QVBoxLayout,
)


class HelpDialog(QDialog):
    """Dialog displaying help information for GAudit V2."""

    def __init__(self, parent: object | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("GAudit Help")
        self.resize(700, 500)

        self._browser = QTextBrowser()
        layout = QVBoxLayout(self)
        layout.addWidget(self._browser)

        close_button = QPushButton("Close")
        close_button.clicked.connect(self.close)

        button_layout = QHBoxLayout()
        button_layout.addStretch()
        button_layout.addWidget(close_button)

        layout.addLayout(button_layout)

        self._load_help()

    # ------------------------------------------------------------------
    def _load_help(self) -> None:
        """Load ``REFERENCE_GUIDE.md`` into the text browser."""

        guide_path = Path(__file__).with_name("REFERENCE_GUIDE.md")
        try:
            text = guide_path.read_text(encoding="utf-8")
        except OSError:
            text = "# Documentation\n\nUnable to load help content."
        self._browser.setMarkdown(text)

    # ------------------------------------------------------------------
    def exec(self) -> int:  # type: ignore[override]
        """Display the dialog modally."""

        return super().exec()
