"""Secure credential storage for GAudit V2."""

from __future__ import annotations

import base64
from typing import Final

import keyring


_SERVICE_NAME: Final[str] = "GAuditV2"
_USERNAME: Final[str] = "credentials"


def save_credentials(creds: bytes) -> None:
    """Persist credentials securely using the system keychain."""

    encoded = base64.b64encode(creds).decode()
    keyring.set_password(_SERVICE_NAME, _USERNAME, encoded)


def load_credentials() -> bytes | None:
    """Retrieve stored credentials if available from the system keychain."""

    encoded = keyring.get_password(_SERVICE_NAME, _USERNAME)
    if not encoded:
        return None

    try:
        return base64.b64decode(encoded.encode())
    except Exception:
        return None
