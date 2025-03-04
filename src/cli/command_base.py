"""
Base command infrastructure for the Assets CLI.

This module provides the foundational abstractions and utilities
for all command-line interface commands in the Assets CLI.
"""
import argparse
from abc import ABC, abstractmethod
from ..jira_core.asset_client import AssetsClient  
from ..logging.logger import Logger
from .error_handler import ErrorHandler

class BaseCommand(ABC):
    """Base class for all CLI commands"""
    
    def __init__(self):
        """Initialize the base command with empty client and logger"""
        self.logger = None
        self.client = None
        self.debug = False
    
    @abstractmethod
    def configure_parser(self, parser):
        """
        Configure command-specific arguments.
        
        Args:
            parser: ArgumentParser instance to configure
            
        Returns:
            Configured parser
        """
        pass
    
    @abstractmethod
    def execute(self, args):
        """
        Execute the command with parsed arguments.
        
        Args:
            args: Parsed command-line arguments
            
        Returns:
            bool: True if successful, False otherwise
        """
        pass
    
    def setup(self, args):
        """
        Setup logging and client.
        
        Args:
            args: Parsed command-line arguments with debug and refresh_cache options
        """
        # Configure logging
        self.debug = args.debug if hasattr(args, 'debug') else False
        log_level = "DEBUG" if self.debug else "INFO"
        self.logger = Logger.configure(console_level=log_level)
        
        # Initialize client
        self.client = AssetsClient()
        
        # Handle schema refresh if requested
        if hasattr(args, 'refresh_cache') and args.refresh_cache:
            self.logger.info("Refreshing schema cache")
            self.refresh_schema()
    
    def handle_error(self, exception, context=None):
        """
        Standardized error handling
        
        Args:
            exception: The exception to handle
            context: Additional context about the operation
            
        Returns:
            False (to indicate operation failure)
        """
        return ErrorHandler.handle_error(self.logger, exception, self.debug, context)
            
    def refresh_schema(self):
        """
        Force refresh of schema information.
        
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            self.logger.info("Refreshing schema information from API")
            # Force clear the cached schema info
            self.client.schema_info = {}
            self.client._save_cache()
            # Reload schema info
            self.client.schema_info = self.client.refresh_schema()
            self.logger.info("Schema information refreshed successfully")
        except Exception as e:
            self.handle_error(e, "refreshing schema")
