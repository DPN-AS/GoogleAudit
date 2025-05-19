"""Entry point for GAudit V2."""

from __future__ import annotations

import sys
from PyQt6.QtWidgets import QApplication

import db
from main_window import MainWindow


def main() -> None:
    """Launch the GAudit GUI application."""
    db.init_db()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec())


if __name__ == "__main__":
    main()
