"""
Implementation of the 'get' command for retrieving assets.

This module provides the GetCommand class that handles retrieving
assets by ID or IDs and displaying the results.
"""
import argparse
from typing import Optional, List

from ...jira_core.asset_client import AssetsClient
from ...logging.logger import Logger
from ..command_base import BaseCommand
from ..output_formatter import format_asset, format_assets

class GetCommand(BaseCommand):
    """Command handler for retrieving assets."""
    
    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure the argument parser for this command.
        
        Args:
            parser: The parser to configure
        """
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--id', type=int, help='Asset ID to retrieve')
        group.add_argument('--ids', type=str, help='Comma-separated list of asset IDs')
        parser.add_argument('--debug', action='store_true', help='Enable debug logging')
        parser.add_argument('--refresh-cache', action='store_true', 
                           help='Refresh schema cache before processing')
    
    def execute(self, args: argparse.Namespace) -> bool:
        """
        Execute the get command.
        
        Args:
            args: Parsed command arguments
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Configure logging with our custom Logger class
        logger = Logger.configure(console_level="DEBUG" if args.debug else "INFO")
        
        # Initialize client
        client = AssetsClient(refresh_cache=args.refresh_cache)
        
        if args.id:
            # Get a single asset
            asset = client.get_object(args.id)
            if not asset:
                logger.error(f"Asset with ID {args.id} not found")
                return False
            
            # Display the asset - only log, don't use print()
            formatted = format_asset(asset)
            logger.info(f"\n{formatted}")
            return True
            
        elif args.ids:
            # Get multiple assets
            ids = [int(id.strip()) for id in args.ids.split(',') if id.strip()]
            assets = []
            
            for asset_id in ids:
                asset = client.get_object(asset_id)
                if asset:
                    assets.append(asset)
                else:
                    logger.warning(f"Asset with ID {asset_id} not found")
            
            if not assets:
                logger.error("No assets found")
                return False
                
            # Display the assets summary - only log, don't use print()
            formatted = format_assets(assets)
            logger.info(f"\n{formatted}")
            
            # Display detailed information for each asset
            for asset in assets:
                logger.info("\nDetailed information:")
                detailed = format_asset(asset)
                logger.info(f"\n{detailed}")
                
            return True
            
        return False
