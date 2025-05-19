import logging
from pathlib import Path
from typing import Optional


LOG_FILE = Path("gaudit.log")


def init_logging(level: int = logging.INFO, log_file: Optional[Path] = None) -> None:
    """Configure basic logging for the application.

    Parameters
    ----------
    level:
        The minimum severity level to record. Defaults to ``logging.INFO``.
    log_file:
        Optional path to the log file. If omitted, ``gaudit.log`` in the
        current directory is used.
    """

    file_path = log_file or LOG_FILE
    logging.basicConfig(
        level=level,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        handlers=[logging.FileHandler(file_path), logging.StreamHandler()],
    )


