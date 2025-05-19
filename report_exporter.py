"""Report generation utilities for GAudit V2."""

from __future__ import annotations

from typing import Any, Dict, List

import report_db


def _format_findings(findings: List[Dict[str, Any]]) -> str:
    rows = []
    for finding in findings:
        severity = finding.get("severity", "")
        message = finding.get("message", "")
        rows.append(f"<tr><td>{severity}</td><td>{message}</td></tr>")
    if not rows:
        rows.append("<tr><td colspan='2'>No findings</td></tr>")
    return "\n".join(rows)


def _format_stats(stats: Dict[str, Any]) -> str:
    if not stats:
        return "<li>No statistics available</li>"
    return "\n".join(f"<li>{key}: {value}</li>" for key, value in stats.items())


def generate_html_report() -> str:
    """Create an HTML report and return the contents."""
    run_data = report_db.fetch_last_run() or {}

    summary = run_data.get("summary", "No summary available")
    findings = run_data.get("findings", [])
    stats = run_data.get("stats", {})

    html = (
        "<html>\n"
        "  <head><title>GAudit Report</title></head>\n"
        "  <body>\n"
        "    <h1>GAudit Report</h1>\n"
        "    <h2>Executive Summary</h2>\n"
        f"    <p>{summary}</p>\n"
        "    <h2>Findings</h2>\n"
        "    <table border='1'>\n"
        "      <tr><th>Severity</th><th>Description</th></tr>\n"
        f"      {_format_findings(findings)}\n"
        "    </table>\n"
        "    <h2>Statistics</h2>\n"
        "    <ul>\n"
        f"      {_format_stats(stats)}\n"
        "    </ul>\n"
        "  </body>\n"
        "</html>"
    )
    return html


def export_html_report(path: str) -> None:
    """Save an HTML report to a file."""
    html = generate_html_report()
    with open(path, "w", encoding="utf-8") as f:
        f.write(html)


def export_pdf_report(path: str) -> None:
    """Generate a PDF version of the report."""
    html = generate_html_report()
    try:
        import pdfkit
    except ImportError as exc:  # pragma: no cover - optional dependency
        raise RuntimeError("pdfkit is required for PDF export") from exc
    pdfkit.from_string(html, path)
