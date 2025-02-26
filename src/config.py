"""
Configuration management module.

This module handles loading and providing access to configuration values 
from various sources including environment variables and configuration files.
It centralizes configuration management for the Assets API Client.
"""
import os
import logging
from pathlib import Path
from dotenv import load_dotenv

# Determine the project root directory
PROJECT_ROOT = Path(__file__).parent.parent.absolute()

# Load environment variables from .env file
load_dotenv(PROJECT_ROOT / '.env')

class Config:
    """
    Configuration manager for the Assets API Client.
    
    Provides centralized access to configuration values from environment 
    variables and other sources. Uses sensible defaults when values are 
    not explicitly configured.
    """
    
    # Jira API credentials and settings
    JIRA_API_TOKEN = os.getenv('JIRA_API_TOKEN', '')
    JIRA_EMAIL = os.getenv('JIRA_EMAIL', '')
    JIRA_SITE_NAME = os.getenv('JIRA_SITE_NAME', '')
    
    # Application settings
    DEBUG = os.getenv('DEBUG', 'False').lower() in ('true', '1', 't', 'yes')
    
    # API settings
    API_TIMEOUT = int(os.getenv('API_TIMEOUT', '30'))  # seconds
    API_RETRIES = int(os.getenv('API_RETRIES', '3'))
    
    # Logging settings
    LOG_DIR = os.getenv('LOG_DIR', str(PROJECT_ROOT / 'logs'))
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO').upper()
    LOG_FORMAT = os.getenv('LOG_FORMAT', '%(asctime)s - %(name)s - %(levelname)s - %(message)s')
    
    # Caching settings
    CACHE_DIR = os.getenv('CACHE_DIR', str(PROJECT_ROOT / 'cache'))
    CACHE_EXPIRY = int(os.getenv('CACHE_EXPIRY', '3600'))  # seconds
    
    @classmethod
    def get_log_level(cls):
        """
        Get the configured log level as a logging module constant.
        
        Returns:
            int: The log level (e.g., logging.INFO, logging.DEBUG)
        """
        level_map = {
            'DEBUG': logging.DEBUG,
            'INFO': logging.INFO,
            'WARNING': logging.WARNING,
            'ERROR': logging.ERROR,
            'CRITICAL': logging.CRITICAL
        }
        return level_map.get(cls.LOG_LEVEL, logging.INFO)
    
    @classmethod
    def validate(cls):
        """
        Validate the configuration and check for required values.
        
        Raises:
            ValueError: If required configuration values are missing
        """
        if not cls.JIRA_API_TOKEN:
            raise ValueError("JIRA_API_TOKEN is required but not set in environment or .env file")
        
        if not cls.JIRA_EMAIL:
            raise ValueError("JIRA_EMAIL is required but not set in environment or .env file")
        
        if not cls.JIRA_SITE_NAME:
            raise ValueError("JIRA_SITE_NAME is required but not set in environment or .env file")
        
        # Ensure log directory exists
        log_dir = Path(cls.LOG_DIR)
        if not log_dir.exists():
            log_dir.mkdir(parents=True, exist_ok=True)
        
        # Ensure cache directory exists
        cache_dir = Path(cls.CACHE_DIR)
        if not cache_dir.exists():
            cache_dir.mkdir(parents=True, exist_ok=True)
            
        return True

# Validate configuration on module import
try:
    Config.validate()
except Exception as e:
    print(f"Configuration error: {str(e)}")
