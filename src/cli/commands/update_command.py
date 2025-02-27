"""
Implementation of the 'update' command for updating assets.

This module provides the UpdateCommand class that handles updating
assets by ID or IDs with specified attributes.
"""
import argparse
from typing import Dict, List, Any

from ...jira_core.asset_client import AssetsClient
from ...logging.logger import Logger
from ..command_base import BaseCommand
from ..output_formatter import format_asset

class UpdateCommand(BaseCommand):
    """Command handler for updating assets."""
    
    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure the argument parser for this command.
        
        Args:
            parser: The parser to configure
        """
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--id', type=int, help='Asset ID to update')
        group.add_argument('--ids', type=str, help='Comma-separated list of asset IDs')
        
        parser.add_argument('--attr', action='append', required=True,
                           help='Attribute to update in format "name=value". Can be specified multiple times.')
        parser.add_argument('--debug', action='store_true', help='Enable debug logging')
        parser.add_argument('--refresh-cache', action='store_true', 
                           help='Refresh schema cache before processing')
    
    def execute(self, args: argparse.Namespace) -> bool:
        """
        Execute the update command.
        
        Args:
            args: Parsed command arguments
            
        Returns:
            bool: True if successful, False otherwise
        """
        # Configure logging with our custom Logger class
        logger = Logger.configure(console_level="DEBUG" if args.debug else "INFO")
        
        # Parse attributes
        attributes = {}
        for attr in args.attr:
            if '=' not in attr:
                logger.error(f"Invalid attribute format: {attr}. Expected format: name=value")
                return False
            
            name, value = attr.split('=', 1)
            attributes[name] = value
        
        # Initialize client
        client = AssetsClient(refresh_cache=args.refresh_cache)
        
        if args.id:
            # Update a single asset
            logger.info(f"Updating asset {args.id} with attributes: {attributes}")
            success = client.update_object(args.id, attributes)
            
            if success:
                logger.info(f"Successfully updated asset {args.id}")
                asset = client.get_object(args.id)
                formatted = format_asset(asset)
                logger.info(f"\n{formatted}")  # Only log, don't use print()
                return True
            else:
                logger.error(f"Failed to update asset {args.id}")
                return False
                
        elif args.ids:
            # Update multiple assets
            ids = [int(id.strip()) for id in args.ids.split(',') if id.strip()]
            logger.info(f"Updating {len(ids)} assets with attributes: {attributes}")
            
            results = {}
            for asset_id in ids:
                success = client.update_object(asset_id, attributes)
                results[asset_id] = success
                status = "Success" if success else "Failed"
                logger.info(f"Asset {asset_id}: {status}")
                
                # Display the updated asset information
                if success:
                    try:
                        asset = client.get_object(asset_id)
                        formatted = format_asset(asset)
                        logger.info(f"\n{formatted}")  # Only log, don't use print()
                    except Exception as e:
                        logger.error(f"Error retrieving updated asset {asset_id}: {str(e)}")
            
            success_count = sum(1 for status in results.values() if status)
            logger.info(f"Successfully updated {success_count} out of {len(ids)} assets")
            
            return success_count > 0
            
        return False
