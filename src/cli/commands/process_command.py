"""
Asset processing command for the Assets CLI.

This module provides the command-line interface for processing
assets according to defined business rules using the Jira Assets API.
"""
import argparse
from ..command_base import BaseCommand
from ..output_formatter import format_asset, format_process_results, format_process_details
from ...jira_core.services.asset_processor import AssetProcessor

class ProcessCommand(BaseCommand):
    """Command to process assets according to business rules"""
    
    def configure_parser(self, parser):
        """
        Configure argument parser for the Process command.
        
        Args:
            parser: ArgumentParser instance to configure
            
        Returns:
            Configured parser
        """
        parser.add_argument('--ids', type=str, help='Comma-separated list of asset IDs to process')
        parser.add_argument('--id', type=int, help='Single asset ID to process')
        parser.add_argument('--query', type=str, help='AQL query to select assets for processing')
        parser.add_argument('--limit', type=int, default=100, 
            help='Maximum number of assets to process (default: 100)')
        parser.add_argument('--details', action='store_true',
            help='Show detailed information about processed assets')
        parser.add_argument('--refresh-cache', action='store_true', 
            help='Force refresh of schema cache (use after object types are renamed in Jira)')
        parser.add_argument('--debug', action='store_true', help='Enable debug logging')
        parser.add_argument('--recalculate-buyout', action='store_true',
            help='Force recalculation of buyout prices even if they exist')
        return parser
        
    def setup(self, args):
        """
        Set up the command with necessary services.
        
        Args:
            args: Parsed command arguments
        """
        # Call parent setup first
        super().setup(args)
        
        # Create the asset processor
        self.processor = AssetProcessor(
            client=self.client,
            logger=self.logger,
            force_recalculate=getattr(args, 'recalculate_buyout', False)
        )
        
        # Return self for chaining
        return self

    def execute(self, args: argparse.Namespace) -> bool:
        """
        Execute the process command.
        
        Args:
            args: Parsed command arguments
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Setup the client, logger, etc.
            self.setup(args)
            
            # Set a default limit if not specified
            max_results = getattr(args, 'limit', 100)
            
            # Find assets to process
            if args.query:
                self.logger.info(f"Finding assets using query: {args.query}")
                assets = self.client.get_objects_aql(args.query, max_results=max_results)
            elif args.ids:
                asset_ids = [int(id.strip()) for id in args.ids.split(',') if id.strip()]
                self.logger.info(f"Processing {len(asset_ids)} assets by ID")
                assets = []
                for asset_id in asset_ids:
                    asset = self.client.get_object(asset_id)
                    if asset:
                        assets.append(asset)
                    else:
                        self.logger.warning(f"Asset with ID {asset_id} not found")
            else:
                self.logger.error("No query or IDs provided")
                return False

            if not assets:
                self.logger.info("No assets found to process")
                return True

            self.logger.info(f"Found {len(assets)} assets matching query")
            self.logger.info(f"Processing {len(assets)} assets...")

            # Process assets
            results = {}
            processed_assets = []  # Keep track of the assets we process
            
            for asset in assets:
                asset_id = asset.id
                try:
                    # Process the asset
                    self.processor.process_asset(asset)
                    self.logger.info(f"Successfully updated asset {asset_id}")
                    results[asset_id] = True
                    processed_assets.append(asset)
                except Exception as e:
                    self.logger.error(f"Failed to process asset {asset_id}: {str(e)}")
                    results[asset_id] = False

            # Display summary of results
            success_count = sum(1 for status in results.values() if status)
            self.logger.info(f"Updated {success_count} out of {len(assets)} assets")
            
            # Show formatted summary table
            summary = format_process_results(results)
            self.logger.info(f"\nProcess Summary:\n{summary}")
            
            # Show details for a subset of assets
            if args.details or args.debug:
                details = format_process_details(results, processed_assets, 
                                              max_details=args.limit if args.limit else 10)
                self.logger.info(f"\nProcessed Asset Details:\n{details}")
            
            return True
            
        except Exception as e:
            return self.handle_error(e, "processing assets")
