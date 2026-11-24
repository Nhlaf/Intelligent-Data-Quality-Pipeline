import logging

from pathlib import Path
from logging.handlers import RotatingFileHandler


PROJECT_ROOT = Path(__file__).resolve().parents[2]

LOG_DIR = PROJECT_ROOT / "logs"


def setup_logger(
    name="data_quality_pipeline",
    log_dir=LOG_DIR,
    level=logging.INFO
):

    log_dir = Path(log_dir)

    log_dir.mkdir(
        parents=True,
        exist_ok=True
    )

    logger = logging.getLogger(name)

    logger.setLevel(level)

    logger.propagate = False

    if logger.handlers:
        return logger

    formatter = logging.Formatter(
        "%(asctime)s | %(levelname)s | "
        "%(name)s | %(message)s"
    )

    file_handler = RotatingFileHandler(
        log_dir / "pipeline.log",
        maxBytes=5 * 1024 * 1024,
        backupCount=3,
        encoding="utf-8"
    )

    file_handler.setFormatter(formatter)

    console_handler = logging.StreamHandler()

    console_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    logger.addHandler(console_handler)

    return logger