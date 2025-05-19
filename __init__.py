"""Top-level package for GAudit V2.

This package organizes the core modules used by the GAudit application.
The architecture is intentionally simple:

- :mod:`main_window` contains the PyQt6 based GUI used to run and review
  audits.
- :mod:`audit_engine` houses the security checks executed during an audit
  and records results in the SQLite database managed by :mod:`db`.
- :mod:`report_exporter` and :mod:`report_db` provide helpers for
  generating human readable reports from stored audit data.
- :mod:`analytics_tabs` offers small widgets that visualise results for
  specific areas such as authentication or Drive security.

Additional utilities such as :mod:`credential_loader` and
:mod:`secure_store` handle authentication and credential storage.  The
application entry point is :func:`main.main` which launches the GUI.
"""
