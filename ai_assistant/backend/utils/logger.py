# backend/utils/logger.py

import logging
from logging.handlers import RotatingFileHandler
import os
from .config import LOG_LEVEL, LOG_FILE

def setup_logger(name: str, log_file: str = LOG_FILE, level: str = LOG_LEVEL):
    """
    Set up a logger with console and file handlers.
    """
    # Create logs directory if it doesn't exist
    os.makedirs(os.path.dirname(log_file), exist_ok=True)

    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Create console handler and set level
    console_handler = logging.StreamHandler()
    console_handler.setLevel(level)

    # Create file handler and set level
    file_handler = RotatingFileHandler(log_file, maxBytes=1024*1024, backupCount=5)
    file_handler.setLevel(level)

    # Create formatter
    formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

    # Add formatter to handlers
    console_handler.setFormatter(formatter)
    file_handler.setFormatter(formatter)

    # Add handlers to logger
    logger.addHandler(console_handler)
    logger.addHandler(file_handler)

    return logger

# Create a default logger
logger = setup_logger('ai_assistant')

def log_function_call(func):
    """
    A decorator to log function calls.
    """
    def wrapper(*args, **kwargs):
        logger.debug(f"Calling function: {func.__name__}")
        result = func(*args, **kwargs)
        logger.debug(f"Function {func.__name__} completed")
        return result
    return wrapper