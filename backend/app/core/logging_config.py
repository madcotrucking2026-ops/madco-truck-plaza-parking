import logging
from logging.handlers import RotatingFileHandler
from pathlib import Path

_LOG_DIR = Path(__file__).resolve().parent.parent.parent / "logs"
_LOG_FILE = _LOG_DIR / "mtpms.log"

# One shared application logger. Use `get_logger(__name__)` in modules so log
# lines are attributed to where they came from.
_ROOT_NAME = "mtpms"
_configured = False


def configure_logging() -> None:
    """Console + rotating-file logging for the app. Called once at startup.
    File rotates at ~2 MB, keeps 5 backups, so logs never grow unbounded but
    recent history is always on disk for troubleshooting a real payment/renew
    issue after the fact."""
    global _configured
    if _configured:
        return

    _LOG_DIR.mkdir(exist_ok=True)
    logger = logging.getLogger(_ROOT_NAME)
    logger.setLevel(logging.INFO)
    logger.propagate = False

    fmt = logging.Formatter("%(asctime)s %(levelname)-7s %(name)s: %(message)s", datefmt="%Y-%m-%d %H:%M:%S")

    console = logging.StreamHandler()
    console.setFormatter(fmt)
    logger.addHandler(console)

    file_handler = RotatingFileHandler(_LOG_FILE, maxBytes=2_000_000, backupCount=5, encoding="utf-8")
    file_handler.setFormatter(fmt)
    logger.addHandler(file_handler)

    _configured = True


def get_logger(name: str) -> logging.Logger:
    """Child of the app logger, named for the calling module."""
    short = name.split(".")[-1]
    return logging.getLogger(f"{_ROOT_NAME}.{short}")
