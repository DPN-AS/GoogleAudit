"""Entry point for GAudit V2."""

from __future__ import annotations

import sys
from PyQt6.QtWidgets import QApplication

import logger

import db
from main_window import MainWindow


def main() -> None:
    """Launch the GAudit GUI application."""
    logger.init_logging()
    logger.logging.getLogger(__name__).info("Application starting")
    db.init_db()
    app = QApplication(sys.argv)
    window = MainWindow()
    window.show()
    exit_code = app.exec()
    logger.logging.getLogger(__name__).info("Application exiting")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()
