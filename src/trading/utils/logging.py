import sys
from pathlib import Path
from loguru import logger
from .config import config

def setup_logging():
    """Configure logging for the trading system.
    
    This setup:
    - Removes default logger
    - Adds console handler with colors
    - Adds file handler with rotation
    - Sets proper log levels
    - Formats messages with timestamps and context
    """
    # Remove default logger
    logger.remove()
    
    # Add console handler
    logger.add(
        sys.stderr,
        format="<green>{time:YYYY-MM-DD HH:mm:ss.SSS}</green> | <level>{level: <8}</level> | <cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> - <level>{message}</level>",
        level=config.get("logging.level", "INFO"),
        colorize=True,
    )
    
    # Add file handler with rotation
    log_file = config.get_path("logging.file")
    logger.add(
        str(log_file),
        rotation="500 MB",
        retention="10 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level=config.get("logging.level", "INFO"),
    )
    
    # Add error file handler
    error_log = log_file.parent / "error.log"
    logger.add(
        str(error_log),
        rotation="100 MB",
        retention="30 days",
        compression="zip",
        format="{time:YYYY-MM-DD HH:mm:ss.SSS} | {level: <8} | {name}:{function}:{line} - {message}",
        level="ERROR",
    )
    
    return logger

# Initialize logging
logger = setup_logging()

# Example usage:
# from trading.utils.logging import logger
# logger.info("Starting trading system")
# logger.error("Failed to fetch data", exc_info=True) 