import json
import os
from pathlib import Path
from typing import Any, Dict

DEFAULT_SETTINGS = {
    "api_services": [
        "admin_sdk",
        "drive_api",
        "gmail_api",
        "groups_settings_api",
    ]
}

CONFIG_FILENAME = "config.json"


def load_settings(path: Path | None = None) -> Dict[str, Any]:
    """Load configuration from ``path`` or the default location."""
    if path is None:
        path = Path(os.getenv("GAUDIT_CONFIG", CONFIG_FILENAME))
    try:
        with path.open(encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        data = {}
    # Merge with defaults
    merged = {**DEFAULT_SETTINGS, **data}
    return merged
