"""
Structured Logging Configuration
Outputs to both console (dev) and file (production).
"""

import logging
import sys
from logging.handlers import RotatingFileHandler
from pathlib import Path

# Log file configuration
LOG_FILE = Path(__file__).parent.parent / "app.log"
LOG_FORMAT = "%(asctime)s - %(levelname)s - %(name)s - %(message)s"
LOG_DATE_FORMAT = "%Y-%m-%d %H:%M:%S"
LOG_MAX_BYTES = 5 * 1024 * 1024  # 5 MB
LOG_BACKUP_COUNT = 3


def setup_logger(name: str = "dreamsight", level: int = logging.INFO) -> logging.Logger:
    """
    Create and configure a logger with console and file handlers.
    
    Args:
        name: Logger name (default: "dreamsight")
        level: Logging level (default: INFO)
        
    Returns:
        Configured logger instance
    """
    logger = logging.getLogger(name)
    
    # Avoid duplicate handlers if called multiple times
    if logger.handlers:
        return logger
    
    logger.setLevel(level)
    
    # Formatter
    formatter = logging.Formatter(LOG_FORMAT, datefmt=LOG_DATE_FORMAT)
    
    # Console Handler (for development)
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setLevel(logging.DEBUG)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    # File Handler with rotation (for production history)
    try:
        file_handler = RotatingFileHandler(
            LOG_FILE,
            maxBytes=LOG_MAX_BYTES,
            backupCount=LOG_BACKUP_COUNT,
            encoding="utf-8",
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)
    except Exception as e:
        logger.warning(f"Could not create file handler: {e}")
    
    return logger


# Global logger instance
logger = setup_logger()


# Convenience functions
def log_info(message: str) -> None:
    """Log INFO level message."""
    logger.info(message)


def log_error(message: str, exc_info: bool = False) -> None:
    """Log ERROR level message."""
    logger.error(message, exc_info=exc_info)


def log_warning(message: str) -> None:
    """Log WARNING level message."""
    logger.warning(message)


def log_debug(message: str) -> None:
    """Log DEBUG level message."""
    logger.debug(message)
