"""
Logging configuration module for the Assets API Client.

Provides a singleton Logger class that handles application logging to both
console and file outputs with configurable log levels.
"""
import logging
import os
from datetime import datetime
from typing import Union

class Logger:
    """
    Singleton logger class for consistent logging across the application.
    
    This class implements the singleton pattern to ensure that the same
    logger instance is used throughout the application. It provides
    methods for different log levels and configuration options.
    """
    _instance = None
    _initialized = False

    # Constants for log levels, mirroring the standard logging module
    DEBUG = logging.DEBUG
    INFO = logging.INFO
    WARNING = logging.WARNING
    ERROR = logging.ERROR
    CRITICAL = logging.CRITICAL
    
    def __new__(cls):
        """
        Create a new Logger instance or return the existing one.
        
        Returns:
            Logger: The singleton Logger instance.
        """
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self):
        """
        Initialize the Logger instance if not already initialized.
        """
        if not Logger._initialized:
            self.logger = logging.getLogger()
            Logger._initialized = True

    @staticmethod
    def configure(console_level=INFO, file_level=DEBUG):
        """
        Configure the logging system with file and console handlers.
        
        Creates a timestamped log file in the 'logs' directory and sets up
        both console and file logging with specified log levels.
        
        Args:
            console_level: Logging level for console output.
                Can be an int constant or a string ('DEBUG', 'INFO', etc.)
            file_level: Logging level for file output.
                Can be an int constant or a string ('DEBUG', 'INFO', etc.)
            
        Returns:
            Logger: The configured Logger instance.
        """
        # Convert string level names to numeric values if needed
        if isinstance(console_level, str):
            console_level = getattr(logging, console_level.upper(), logging.INFO)
        if isinstance(file_level, str):
            file_level = getattr(logging, file_level.upper(), logging.DEBUG)
            
        if not os.path.exists('logs'):
            os.makedirs('logs')

        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        log_filename = f'logs/assets_api_{timestamp}.log'
        formatter = logging.Formatter('%(asctime)s - %(name)s - %(levelname)s - %(message)s')

        # Setup handlers
        file_handler = logging.FileHandler(log_filename)
        file_handler.setLevel(file_level)
        file_handler.setFormatter(formatter)

        console_handler = logging.StreamHandler()
        console_handler.setLevel(console_level)
        console_handler.setFormatter(formatter)

        # Configure root logger
        root_logger = logging.getLogger()
        root_logger.setLevel(logging.DEBUG)
        
        # Clear existing handlers and add new ones
        root_logger.handlers.clear()
        root_logger.addHandler(file_handler)
        root_logger.addHandler(console_handler)

        return Logger()

    def debug(self, message):
        """
        Log a debug message.
        
        Args:
            message (str): The debug message to log.
        """
        self.logger.debug(message)

    def info(self, message):
        """
        Log an info message.
        
        Args:
            message (str): The info message to log.
        """
        self.logger.info(message)

    def warning(self, message):
        """
        Log a warning message.
        
        Args:
            message (str): The warning message to log.
        """
        self.logger.warning(message)

    def error(self, message):
        """
        Log an error message.
        
        Args:
            message (str): The error message to log.
        """
        self.logger.error(message)

    def critical(self, message):
        """
        Log a critical message.
        
        Args:
            message (str): The critical message to log.
        """
        self.logger.critical(message)
