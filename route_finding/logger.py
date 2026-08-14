import logging
from pathlib import Path

from settings import VersionSettings
SETTINGS = VersionSettings.get_version_settings()


def setup_logger(run_path: Path) -> logging.Logger:
    """Setup logger for the route finding algorithm.

    Args:
    - run_path (Path): Path to store files for current run

    Returns:
    - logging.Logger: Configured logger instance
    """
    # Create log file path including timestamp
    log_file_path = (run_path / 'logs').with_suffix('.log')

    # Configure logger
    logger = logging.getLogger(SETTINGS.VERSION_NAME)
    logger.setLevel(logging.INFO)

    # File handler
    fh = logging.FileHandler(log_file_path)
    fh.setLevel(logging.INFO)

    # Console handler
    ch = logging.StreamHandler()
    ch.setLevel(logging.INFO)

    # Format
    formatter = logging.Formatter(
        '%(asctime)s - %(levelname)s - %(message)s',
        datefmt='%H:%M:%S'
    )
    fh.setFormatter(formatter)
    ch.setFormatter(formatter)

    logger.addHandler(fh)
    logger.addHandler(ch)

    return logger
