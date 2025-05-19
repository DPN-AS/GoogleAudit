"""Helper functions for PyQt6 widgets.

This module contains small convenience wrappers used by the PyQt6 based
UI.  They keep widget construction consistent across the application and
help reduce repetitive boilerplate code.
"""

from __future__ import annotations

from PyQt6.QtCore import QSize
from PyQt6.QtWidgets import (
    QCheckBox,
    QComboBox,
    QLabel,
    QLineEdit,
    QMessageBox,
    QPushButton,
    QWidget,
)


def create_button(text: str, *, width: int | None = None, height: int | None = None) -> QPushButton:
    """Return a :class:`QPushButton` with optional fixed size."""

    button = QPushButton(text)
    if width is not None or height is not None:
        size = QSize(width or button.sizeHint().width(), height or button.sizeHint().height())
        button.setFixedSize(size)
    return button


def create_label(text: str) -> QLabel:
    """Return a word-wrapped :class:`QLabel`."""

    label = QLabel(text)
    label.setWordWrap(True)
    return label


def create_line_edit(placeholder: str = "") -> QLineEdit:
    """Return a :class:`QLineEdit` with placeholder text."""

    line_edit = QLineEdit()
    line_edit.setPlaceholderText(placeholder)
    return line_edit


def create_check_box(text: str, checked: bool = False) -> QCheckBox:
    """Return a :class:`QCheckBox` optionally prechecked."""

    box = QCheckBox(text)
    box.setChecked(checked)
    return box


def create_combo_box(items: list[str] | tuple[str, ...]) -> QComboBox:
    """Return a :class:`QComboBox` populated with ``items``."""

    combo = QComboBox()
    combo.addItems(list(items))
    return combo


def show_info_message(parent: QWidget | None, title: str, message: str) -> None:
    """Display an information message box."""

    QMessageBox.information(parent, title, message)


def show_error_message(parent: QWidget | None, title: str, message: str) -> None:
    """Display an error message box."""

    QMessageBox.critical(parent, title, message)
