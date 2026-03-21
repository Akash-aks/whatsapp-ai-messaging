"""
Logging module for WhatsApp AI Automation
Provides centralized logging configuration with file and console output
"""

import logging
import sys
from pathlib import Path
from datetime import datetime
from .config import Config

class Logger:
    """Centralized logger configuration"""
    
    _loggers = {}
    
    @classmethod
    def get_logger(cls, name):
        """
        Get or create a logger with the specified name
        
        Args:
            name (str): Logger name (typically __name__ of the module)
            
        Returns:
            logging.Logger: Configured logger instance
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        logger.setLevel(getattr(logging, Config.LOG_LEVEL))
        
        # Prevent duplicate handlers
        if logger.handlers:
            return logger
        
        # Create formatters
        file_formatter = logging.Formatter(
            Config.LOG_FORMAT,
            datefmt=Config.LOG_DATE_FORMAT
        )
        
        console_formatter = logging.Formatter(
            '%(levelname)s - %(message)s'
        )
        
        # File handler - logs everything
        file_handler = logging.FileHandler(
            Config.LOG_FILE,
            encoding='utf-8'
        )
        file_handler.setLevel(logging.DEBUG)
        file_handler.setFormatter(file_formatter)
        
        # Console handler - logs INFO and above
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setLevel(logging.INFO)
        console_handler.setFormatter(console_formatter)
        
        # Add handlers to logger
        logger.addHandler(file_handler)
        logger.addHandler(console_handler)
        
        cls._loggers[name] = logger
        return logger
    
    @classmethod
    def log_session_start(cls):
        """Log the start of a new application session"""
        logger = cls.get_logger("APP")
        logger.info("="*80)
        logger.info(f"{Config.APP_NAME} v{Config.APP_VERSION}")
        logger.info(f"Session started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)
    
    @classmethod
    def log_exception(cls, logger, exc, context=""):
        """
        Log exception with context
        
        Args:
            logger: Logger instance
            exc: Exception object
            context: Additional context string
        """
        error_msg = f"{context}: {type(exc).__name__} - {str(exc)}" if context else f"{type(exc).__name__} - {str(exc)}"
        logger.error(error_msg, exc_info=True)

