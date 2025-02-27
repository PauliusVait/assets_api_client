"""
Implementation of the AQL (Asset Query Language) command.

This module provides the AqlCommand class for executing AQL queries
against the Jira Assets API and displaying the results.
"""
import argparse
from typing import Optional

from ...jira_core.asset_client import AssetsClient
from ...logging.logger import Logger
from ..command_base import BaseCommand
from ..output_formatter import format_query_results

class AqlCommand(BaseCommand):
    """Command handler for executing AQL queries."""
    
    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure the argument parser for this command.
        
        Args:
            parser: The parser to configure
        """
        parser.add_argument('--query', type=str, required=True, 
                            help='AQL query string (e.g., objectType = "iPhone")')
        parser.add_argument('--debug', action='store_true', help='Enable debug logging')
        parser.add_argument('--refresh-cache', action='store_true', 
                           help='Refresh schema cache before processing')
    
    def execute(self, args: argparse.Namespace) -> bool:
        """
        Execute the AQL command.
        
        Args:
            args: Parsed command arguments
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Configure logging with our custom Logger class
        logger = Logger.configure(console_level="DEBUG" if args.debug else "INFO")
        
        # Initialize client
        client = AssetsClient(refresh_cache=args.refresh_cache)
        
        # Execute the query
        logger.info(f"Executing AQL query: {args.query}")
        results = client.query_objects_aql(args.query)
        
        if not results or not results.get('values'):
            logger.info("No results found for the query")
            return True
        
        # Format and display the results
        values = results.get('values', [])
        logger.info(f"Found {len(values)} results")
        formatted = format_query_results(results)
        logger.info(f"\n{formatted}")  # Only log, don't use print()
        
        return True
