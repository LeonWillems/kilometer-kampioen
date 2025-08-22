import logging
import pandas as pd
from ..settings import Settings


def setup_logger(version: str, timestamp: pd.Timestamp) -> logging.Logger:
    """Setup logger for the route finding algorithm.
    
    Args:
    - version (str): Version of the timetable being used
        
    Returns:
    - logging.Logger: Configured logger instance
    """
    # Create logs directory if it doesn't exist
    log_dir = Settings.VERSIONED_LOGS_PATH[version]
    log_dir.mkdir(exist_ok=True)
    
    # Create log file with timestamp
    log_file = log_dir / \
        f"{timestamp}_{Settings.VERSION_NAMES[version]}.log"
    
    # Configure logger
    logger = logging.getLogger(Settings.VERSION_NAMES[version])
    logger.setLevel(logging.INFO)
    
    # File handler
    fh = logging.FileHandler(log_file)
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

