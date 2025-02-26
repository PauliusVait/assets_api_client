"""
Asset processing command for the Assets CLI.

This module provides the command-line interface for processing
assets according to defined business rules using the Jira Assets API.
"""
from ..base import BaseCommand
from ..formatter import format_asset_output
from jira.asset_processor import AssetProcessor

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
        parser.add_argument('--refresh-cache', action='store_true', 
            help='Force refresh of schema cache (use after object types are renamed in Jira)')
        parser.add_argument('--debug', action='store_true', help='Enable debug logging')
        return parser
        
    def execute(self, args):
        """
        Execute the Process command with the parsed arguments.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            bool: True if at least one asset was processed successfully, False otherwise
        """
        self.setup(args)
        
        try:
            # Determine the mode: specific IDs or query
            asset_ids = None
            query = None
            
            if args.query:
                query = args.query
            elif args.ids:
                try:
                    asset_ids = args.ids
                except Exception as e:
                    return self.handle_error(e, "parsing asset IDs")
            elif args.id:
                asset_ids = [args.id]
            else:
                self.logger.error("You must specify either --id, --ids, or --query")
                return False
            
            # Process assets
            processor = AssetProcessor(self.client, self.logger)
            
            # Get assets to process either by IDs or by AQL query
            assets_to_process = []
            
            if query:
                # Use AQL query to find assets
                self.logger.info(f"Finding assets using query: {query}")
                try:
                    results = self.client.get_objects_aql(query, 0, 500, True)
                    if not results:
                        self.logger.info("No assets found matching the query")
                        return True
                        
                    self.logger.info(f"Found {len(results)} assets matching query")
                    assets_to_process = [asset.id for asset in results]
                except Exception as e:
                    return self.handle_error(e, "executing query")
            elif asset_ids:
                # Convert comma-separated string to list if needed
                if isinstance(asset_ids, str):
                    try:
                        asset_ids = [int(id.strip()) for id in asset_ids.split(',')]
                    except ValueError:
                        return self.handle_error(ValueError("IDs must be valid integers"), "parsing asset IDs")
                    
                assets_to_process = asset_ids
            
            if not assets_to_process:
                self.logger.info("No assets to process")
                return True
                
            # Process the assets
            self.logger.info(f"Processing {len(assets_to_process)} assets...")
            try:
                results = processor.update_multiple_assets(assets_to_process)
                
                # Display results
                success_count = sum(1 for status in results.values() if status)
                self.logger.info(f"Successfully processed {success_count} out of {len(assets_to_process)} assets")
                
                # Show details for each processed asset (limit to first 5 if there are many)
                display_count = min(5, len(assets_to_process))
                if len(assets_to_process) > 5:
                    self.logger.info(f"Showing details for first {display_count} assets:")
                    
                for i, asset_id in enumerate(list(results.keys())[:display_count]):
                    success = results[asset_id]
                    status = "Success" if success else "Failed"
                    self.logger.info(f"Asset {asset_id}: {status}")
                    
                    # If successful, get the updated asset data to show
                    if success:
                        try:
                            updated_asset = self.client.get_object(asset_id)
                            self.logger.info("\n" + format_asset_output(updated_asset))
                        except Exception as e:
                            self.handle_error(e, f"retrieving updated asset {asset_id}")
                
                return success_count > 0
            except Exception as e:
                return self.handle_error(e, "processing assets")
            
        except Exception as e:
            return self.handle_error(e, "executing process command")
