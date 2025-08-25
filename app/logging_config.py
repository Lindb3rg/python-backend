import sys
import os
from loguru import logger
from pathlib import Path

def setup_logging():
    """Configure application logging"""
    

    logger.remove()
    
    
    log_dir = Path("logs")
    log_dir.mkdir(exist_ok=True)
    
    # Console logging (colorful for development)
    logger.add(
        sys.stdout,
        format="<green>{time:YYYY-MM-DD HH:mm:ss}</green> | "
               "<level>{level: <8}</level> | "
               "<cyan>{name}</cyan>:<cyan>{function}</cyan>:<cyan>{line}</cyan> | "
               "<level>{message}</level>",
        level=os.getenv("LOG_LEVEL", "INFO"),
        colorize=True
    )
    
    # File logging (structured for production)
    logger.add(
        "logs/app_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="INFO",
        rotation="1 day",      # New file each day
        retention="30 days",   # Keep logs for 30 days
        compression="zip"      # Compress old logs
    )
    
    # Error-only log file
    logger.add(
        "logs/errors_{time:YYYY-MM-DD}.log",
        format="{time:YYYY-MM-DD HH:mm:ss} | {level: <8} | {name}:{function}:{line} | {message}",
        level="ERROR",
        rotation="1 day",
        retention="90 days"    # Keep error logs longer
    )
    
    logger.info("Logging configuration complete")


app_logger = logger