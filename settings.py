import json
import logging
import os
from pathlib import Path
from typing import Any, Dict

from pydantic import BaseModel, ValidationError

DEFAULT_SETTINGS = {
    "api_services": [
        "admin_sdk",
        "drive_api",
        "gmail_api",
        "groups_settings_api",
    ]
}

CONFIG_FILENAME = "config.json"


logger = logging.getLogger(__name__)


class SettingsModel(BaseModel):
    api_services: list[str]


def ensure_config_exists(path: Path | None = None) -> Path:
    """Ensure a configuration file exists at ``path``."""
    if path is None:
        path = Path(os.getenv("GAUDIT_CONFIG", CONFIG_FILENAME))
    if not path.exists():
        logger.info("Creating default config at %s", path)
        path.write_text(json.dumps(DEFAULT_SETTINGS, indent=2))
    return path


def load_settings(path: Path | None = None) -> Dict[str, Any]:
    """Load configuration from ``path`` or the default location."""
    if path is None:
        path = ensure_config_exists()
    try:
        with path.open(encoding="utf-8") as fh:
            data = json.load(fh)
    except FileNotFoundError:
        logger.warning("Config file %s not found, using defaults", path)
        data = {}
    except json.JSONDecodeError as exc:
        logger.error("Invalid JSON in config file %s", path)
        raise ValueError("Invalid configuration file") from exc

    merged = {**DEFAULT_SETTINGS, **data}
    try:
        validated = SettingsModel(**merged)
    except ValidationError as exc:
        logger.error("Configuration validation error: %s", exc)
        raise ValueError("Invalid configuration structure") from exc
    return validated.dict()
