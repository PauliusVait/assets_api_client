"""
Base command infrastructure for the Assets CLI.

This module provides the foundational abstractions and utilities
for all command-line interface commands in the Assets CLI.
"""
from abc import ABC, abstractmethod
from ..jira_core.asset_client import AssetsClient  
from ..logging.logger import Logger
from .error_handler import ErrorHandler

class BaseCommand(ABC):
    """Base class for all CLI commands"""
    
    def __init__(self):
        """Initialize the base command"""
        self.logger = None
        self.client = None
        self.debug = False

    def add_common_arguments(self, parser):
        """Add arguments common to all commands"""
        parser.add_argument('--debug', action='store_true', 
                          help='Enable debug logging')
        parser.add_argument('--refresh-cache', action='store_true', 
                          help='Refresh schema cache before processing')
        return parser

    @abstractmethod
    def configure_parser(self, parser):
        """Configure command-specific arguments"""
        self.add_common_arguments(parser)
        return parser

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
        """Setup logging and client with common configuration"""
        # Configure logging once
        self.debug = getattr(args, 'debug', False)
        self.logger = Logger.configure(
            console_level="DEBUG" if self.debug else "INFO"
        )
        
        # Initialize client with our logger and handle refresh cache
        refresh_cache = getattr(args, 'refresh_cache', False)
        self.client = AssetsClient(logger=self.logger, refresh_cache=refresh_cache)

        # Remove redundant schema refresh since it's now handled in AssetsClient init
        if refresh_cache:
            self.logger.debug("Schema refresh handled during client initialization")
    
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
