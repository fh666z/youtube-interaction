"""Logging configuration and setup."""

import logging
import warnings
from typing import List

from src.core.constants import LoggingConfig


def setup_logging(
    level: str = LoggingConfig.DEFAULT_LEVEL,
    suppress_third_party: bool = True
) -> None:
    """
    Configure application-wide logging.
    
    Args:
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        suppress_third_party: Whether to suppress third-party library logs
    """
    # Configure root logger
    logging.basicConfig(
        level=getattr(logging, level.upper()),
        format=LoggingConfig.LOG_FORMAT,
        datefmt=LoggingConfig.DATE_FORMAT,
        force=True  # Override any existing configuration
    )
    
    # Suppress warnings
    warnings.filterwarnings("ignore")
    
    # Suppress third-party library logs if requested
    if suppress_third_party:
        for logger_name in LoggingConfig.THIRD_PARTY_LOGGERS:
            third_party_logger = logging.getLogger(logger_name)
            third_party_logger.setLevel(logging.ERROR)


def get_logger(name: str) -> logging.Logger:
    """
    Get a logger instance for a module.
    
    Args:
        name: Logger name (typically __name__)
        
    Returns:
        Configured logger instance
    """
    return logging.getLogger(name)
