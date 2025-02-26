"""
Base client module for Jira Assets API.

This module provides the BaseClient class which handles authentication,
caching, and common functionality for the Jira Assets API.
"""
import os
from dotenv import load_dotenv
from base64 import b64encode
import certifi
from src.logging.logger import Logger
import json
from pathlib import Path

class BaseClient:
    """
    Base client for Jira Assets API interactions.
    
    This class handles authentication, configuration loading from environment
    variables, and caching of workspace and schema information.
    """
    def __init__(self):
        """
        Initialize a new BaseClient instance.
        
        Loads configuration from environment variables, sets up authentication,
        and initializes caching.
        """
        self.logger = Logger()
        self.schema_info = None  # Will be populated with schema ID and object types
        load_dotenv()
        self.email = os.getenv('JIRA_EMAIL')
        self.api_token = os.getenv('JIRA_API_TOKEN')
        self.site_name = os.getenv('JIRA_SITE_NAME')
        
        credentials = f"{self.email}:{self.api_token}"
        self.basic_auth = b64encode(credentials.encode()).decode()
        
        self.base_url = None
        
        # Use certifi's built-in certificate bundle
        self.verify = certifi.where()
        
        self.cache_dir = Path.home() / '.assets_api_cache'
        self.cache_dir.mkdir(exist_ok=True)
        self._load_cache()

    def _load_cache(self):
        """
        Load cached workspace and schema data.
        
        Attempts to load workspace ID and schema information from a local
        cache file. If the file doesn't exist or can't be read, the
        cache values remain None.
        """
        cache_file = self.cache_dir / f'{self.site_name}_cache.json'
        if cache_file.exists():
            try:
                with open(cache_file) as f:
                    cache = json.load(f)
                    self.workspace_id = cache.get('workspace_id')
                    self.schema_info = cache.get('schema_info')
            except:
                self.workspace_id = None
                self.schema_info = None

    def _save_cache(self):
        """
        Save workspace and schema data to cache.
        
        Saves the current workspace ID and schema information to a local
        cache file for faster initialization in subsequent runs.
        """
        cache_file = self.cache_dir / f'{self.site_name}_cache.json'
        cache = {
            'workspace_id': self.workspace_id,
            'schema_info': self.schema_info
        }
        with open(cache_file, 'w') as f:
            json.dump(cache, f)
