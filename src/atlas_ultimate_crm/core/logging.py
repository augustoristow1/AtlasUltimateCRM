import logging
import logging.handlers
from atlas_ultimate_crm.core.paths import get_logs_dir


def configure_logging(level: str = "INFO") -> None:
    logs_dir = get_logs_dir()
    log_file = logs_dir / "atlas_ultimate.log"

    formatter = logging.Formatter(
        "%(asctime)s %(levelname)-8s %(name)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    file_handler = logging.handlers.RotatingFileHandler(
        log_file, maxBytes=10 * 1024 * 1024, backupCount=5
    )
    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    root = logging.getLogger()
    root.setLevel(getattr(logging, level.upper(), logging.INFO))
    root.addHandler(file_handler)
    root.addHandler(console_handler)

    # suppress noisy loggers
    logging.getLogger("sqlalchemy.engine").setLevel(logging.WARNING)
    logging.getLogger("httpx").setLevel(logging.WARNING)
