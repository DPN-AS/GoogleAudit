"""OAuth2 credential loading for GAudit V2."""

from __future__ import annotations

from typing import Sequence
from pathlib import Path
import json

from google.auth.transport.requests import Request
from google.oauth2 import service_account
from google.oauth2.credentials import Credentials

from secure_store import load_credentials as secure_load_credentials
from secure_store import save_credentials as secure_save_credentials


SERVICE_ACCOUNT_FILE = Path("service_account.json")

# Default scopes required for the application. Additional scopes can be supplied
# by callers as needed.
DEFAULT_SCOPES = [
    "https://www.googleapis.com/auth/admin.directory.user.readonly",
    "https://www.googleapis.com/auth/admin.directory.group.readonly",
    "https://www.googleapis.com/auth/admin.reports.audit.readonly",
]


def _load_cached_credentials(scopes: Sequence[str]) -> Credentials | None:
    """Return cached credentials if available and valid."""
    cached = secure_load_credentials()
    if not cached:
        return None

    try:
        info = json.loads(cached.decode("utf-8"))
        creds = Credentials.from_authorized_user_info(info, scopes=scopes)
    except Exception:
        return None

    if creds.expired and creds.refresh_token:
        try:
            creds.refresh(Request())
        except Exception:
            return None

    return creds


def _store_credentials(creds: Credentials) -> None:
    """Persist credentials for future use."""
    try:
        secure_save_credentials(creds.to_json().encode("utf-8"))
    except Exception:
        # Storage errors are non-fatal for credential loading
        pass


def load_credentials(
    scopes: Sequence[str] | None = None, subject: str | None = None
) -> Credentials:
    """Load application credentials.

    Credentials are loaded from secure storage if available. Otherwise a new
    service account credential is created from ``SERVICE_ACCOUNT_FILE``. When a
    ``subject`` is provided, domain-wide delegation is applied.
    """
    scopes = scopes or DEFAULT_SCOPES

    creds = _load_cached_credentials(scopes)
    if creds:
        return creds

    if not SERVICE_ACCOUNT_FILE.exists():
        msg = (
            f"Service account file '{SERVICE_ACCOUNT_FILE}' not found. "
            "Refer to the reference guide to configure credentials."
        )
        raise FileNotFoundError(msg)

    creds = service_account.Credentials.from_service_account_file(
        str(SERVICE_ACCOUNT_FILE), scopes=scopes
    )
    if subject:
        creds = creds.with_subject(subject)

    _store_credentials(creds)
    return creds
