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
from ..output_formatter import format_query_results, format_asset

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
        parser.add_argument('--limit', type=int, default=50,
                           help='Maximum number of results to return (default: 50)')
        parser.add_argument('--offset', type=int, default=0,
                           help='Result offset (default: 0)')
        parser.add_argument('--detailed', action='store_true', 
                           help='Show detailed information for each asset')
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
        try:
            # Setup basics
            self.setup(args)
            
            # Execute the query using the correct method name: get_objects_aql
            self.logger.info(f"Executing AQL query: {args.query}")
            results = self.client.get_objects_aql(
                query=args.query,
                start_at=args.offset,
                max_results=args.limit
            )
            
            if not results:
                self.logger.info("No results found for the query")
                return True
            
            # Format and display the results
            self.logger.info(f"Found {len(results)} results")
            
            # Display results summary table
            formatted = format_query_results(results)
            self.logger.info(f"\nQuery Results:\n{formatted}")
            
            # If detailed or debug mode is enabled, show each asset's details
            if args.detailed or args.debug:
                self.logger.info("\nDetailed Asset Information:")
                for i, asset in enumerate(results):
                    self.logger.info(f"\nAsset {i+1} of {len(results)}:")
                    detailed = format_asset(asset)
                    self.logger.info(f"\n{detailed}")
            
            return True
            
        except Exception as e:
            return self.handle_error(e, "executing AQL query")
