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
from ..output_formatter import format_asset, format_update_results, format_process_details

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
        parser.add_argument('--detailed', action='store_true',
                           help='Show detailed information for each updated asset')
    
    def execute(self, args: argparse.Namespace) -> bool:
        """
        Execute the update command.
        
        Args:
            args: Parsed command arguments
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Setup the client, logger, etc.
            self.setup(args)
            
            # Parse attributes
            attributes = {}
            for attr in args.attr:
                if '=' not in attr:
                    self.logger.error(f"Invalid attribute format: {attr}. Expected format: name=value")
                    return False
                
                name, value = attr.split('=', 1)
                attributes[name] = value
            
            if args.id:
                # Update a single asset
                asset_id = args.id
                self.logger.info(f"Updating asset {asset_id} with attributes: {attributes}")
                success = self.client.update_object(asset_id, attributes)
                
                results = {asset_id: success}
                updated_assets = []
                
                if success:
                    # Only log success at debug level
                    self.logger.debug(f"Successfully updated asset {asset_id}")
                    try:
                        asset = self.client.get_object(asset_id)
                        updated_assets.append(asset)
                    except Exception as e:
                        self.logger.error(f"Error retrieving updated asset {asset_id}: {str(e)}")
                else:
                    self.logger.error(f"Failed to update asset {asset_id}")
                
                # Display summary
                summary = format_update_results(results)
                self.logger.info(f"\nUpdate Summary:\n{summary}")
                
                # Display asset details table
                if updated_assets:
                    details = format_process_details(results, updated_assets)
                    self.logger.info(f"\nUpdated Asset Details:\n{details}")
                    
                    # Show full details if requested
                    if args.detailed or args.debug:
                        self.logger.info(f"\nFull Asset Details:")
                        formatted = format_asset(asset)
                        self.logger.info(f"\n{formatted}")
                
                return success
                    
            elif args.ids:
                # Update multiple assets
                ids = [int(id.strip()) for id in args.ids.split(',') if id.strip()]
                self.logger.info(f"Updating {len(ids)} assets with attributes: {attributes}")
                
                results = {}
                updated_assets = []
                failed_ids = []
                
                # Process updates
                for asset_id in ids:
                    try:
                        success = self.client.update_object(asset_id, attributes)
                        results[asset_id] = success
                        
                        # Only log status at debug level
                        status = "Success" if success else "Failed"
                        self.logger.debug(f"Asset {asset_id}: {status}")
                        
                        # Collect updated assets for summary display
                        if success:
                            try:
                                asset = self.client.get_object(asset_id)
                                if asset:
                                    updated_assets.append(asset)
                            except Exception as e:
                                self.logger.debug(f"Error retrieving updated asset {asset_id}: {str(e)}")
                        else:
                            failed_ids.append(asset_id)
                    except Exception as e:
                        self.logger.error(f"Error updating asset {asset_id}: {str(e)}")
                        results[asset_id] = False
                        failed_ids.append(asset_id)
                
                # Log any failures
                if failed_ids:
                    self.logger.error(f"Failed to update {len(failed_ids)} assets: {failed_ids}")
                
                # Display summary of results
                summary = format_update_results(results)
                self.logger.info(f"\nUpdate Summary:\n{summary}")
                
                # Display details of updated assets in a table format
                if updated_assets:
                    details = format_process_details(results, updated_assets)
                    self.logger.info(f"\nUpdated Asset Details:\n{details}")
                    
                    # Show full details for each asset if requested
                    if args.detailed:
                        self.logger.info("\nFull Asset Details:")
                        for i, asset in enumerate(updated_assets):
                            self.logger.info(f"\nAsset {i+1} of {len(updated_assets)}:")
                            formatted = format_asset(asset)
                            self.logger.info(f"\n{formatted}")
                
                success_count = sum(1 for status in results.values() if status)
                return success_count > 0
                
            return False
            
        except Exception as e:
            return self.handle_error(e, "updating asset(s)")
