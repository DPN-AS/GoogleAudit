"""UI and logic for comparing multiple audit runs."""

from __future__ import annotations

import json
from dataclasses import dataclass
from typing import List

from PyQt6.QtWidgets import (
    QFileDialog,
    QHBoxLayout,
    QListWidget,
    QMessageBox,
    QPushButton,
    QVBoxLayout,
    QDialog,
    QWidget,
)


@dataclass
class AuditResult:
    """Container for an individual audit result."""

    path: str
    findings: List[str]

    @classmethod
    def from_json(cls, path: str) -> "AuditResult":
        """Load an audit result from a JSON file."""
        with open(path, "r", encoding="utf-8") as fh:
            data = json.load(fh)
        return cls(path=path, findings=data.get("findings", []))


class CompareAuditsDialog(QDialog):
    """Dialog for loading and comparing multiple audit results."""

    def __init__(self, parent: QWidget | None = None) -> None:
        super().__init__(parent)
        self.setWindowTitle("Compare Audits")

        self._audits: List[AuditResult] = []

        self._audit_list = QListWidget(self)
        self._load_button = QPushButton("Load Audit", self)
        self._compare_button = QPushButton("Compare", self)

        button_row = QHBoxLayout()
        button_row.addWidget(self._load_button)
        button_row.addWidget(self._compare_button)

        layout = QVBoxLayout(self)
        layout.addWidget(self._audit_list)
        layout.addLayout(button_row)

        self._load_button.clicked.connect(self._load_audit)
        self._compare_button.clicked.connect(self._compare_audits)

    def _load_audit(self) -> None:
        """Prompt the user to load an audit JSON file."""
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Audit File", "", "Audit JSON (*.json)"
        )
        if not path:
            return

        try:
            audit = AuditResult.from_json(path)
        except (OSError, json.JSONDecodeError) as exc:  # pragma: no cover - UI
            QMessageBox.warning(self, "Load Error", str(exc))
            return

        self._audits.append(audit)
        self._audit_list.addItem(path)

    def _compare_audits(self) -> None:
        """Compare loaded audits and display a summary dialog."""
        if len(self._audits) < 2:
            QMessageBox.information(
                self,
                "Select Audits",
                "Please load at least two audits to compare.",
            )
            return

        base_findings = set(self._audits[0].findings)
        results = []
        for audit in self._audits[1:]:
            new_findings = set(audit.findings) - base_findings
            results.append(f"{audit.path}: {len(new_findings)} new findings")

        QMessageBox.information(self, "Comparison Results", "\n".join(results))

    def exec(self) -> None:  # pragma: no cover - UI
        """Launch the dialog."""
        super().exec()

