"""
Logging module for WhatsApp AI Automation
Provides centralized logging configuration with file and console output
"""

import logging
import sys
import os
from pathlib import Path
from datetime import datetime
from .config import Config

class Logger:
    """Centralized logger configuration"""
    
    _loggers = {}
    _session_log_path = None  # Stores the path for the current app session

    @classmethod
    def _get_session_logfile(cls):
        """Generates a unique log file path for the current session"""
        if cls._session_log_path is None:
            log_dir = Path("logs")
            log_dir.mkdir(exist_ok=True)
            
            # Generate filename: session_20260321_214500.log
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            cls._session_log_path = log_dir / f"session_{timestamp}.log"
        return cls._session_log_path

    @classmethod
    def get_logger(cls, name):
        """
        Get or create a logger with the specified name
        """
        if name in cls._loggers:
            return cls._loggers[name]
        
        logger = logging.getLogger(name)
        # Use the level from Config
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
        
        # File handler - Uses the NEW session-based path
        file_handler = logging.FileHandler(
            cls._get_session_logfile(),
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
        logger.info(f"Session Log: {cls._get_session_logfile()}")
        logger.info(f"Session started at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
        logger.info("="*80)
    
    @classmethod
    def log_exception(cls, logger, exc, context=""):
        """Log exception with context"""
        error_msg = f"{context}: {type(exc).__name__} - {str(exc)}" if context else f"{type(exc).__name__} - {str(exc)}"
        logger.error(error_msg, exc_info=True)