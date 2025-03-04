"""
Implementation of the 'get' command for retrieving assets.

This module provides the GetCommand class that handles retrieving
assets by ID or IDs and displaying the results.
"""
from ..command_base import BaseCommand
from ..output_formatter import OutputFormatter

class GetCommand(BaseCommand):
    """Command handler for retrieving assets."""
    
    def configure_parser(self, parser):
        """Configure the argument parser"""
        group = parser.add_mutually_exclusive_group(required=True)
        group.add_argument('--id', type=int, help='Asset ID to retrieve')
        group.add_argument('--ids', type=str, help='Comma-separated list of asset IDs')
        return super().configure_parser(parser)
    
    def execute(self, args):
        """Execute the get command"""
        try:
            self.setup(args)
            
            if args.id:
                return self._handle_single_asset(args.id)
            elif args.ids:
                return self._handle_multiple_assets(args.ids)
                
            return False
            
        except Exception as e:
            return self.handle_error(e, "retrieving asset(s)")
            
    def _handle_single_asset(self, asset_id):
        """Handle retrieval of a single asset"""
        asset = self.client.get_object(asset_id)
        if not asset:
            self.logger.error(f"Asset with ID {asset_id} not found")
            return False
            
        formatted = OutputFormatter.format_asset_table([asset])
        self.logger.info(f"\nAsset Details:\n{formatted}")
        return True
    
    def _handle_multiple_assets(self, ids_str):
        """Handle retrieval of multiple assets"""
        ids = [int(id.strip()) for id in ids_str.split(',') if id.strip()]
        assets = []
        
        for asset_id in ids:
            asset = self.client.get_object(asset_id)
            if asset:
                assets.append(asset)
            else:
                self.logger.warning(f"Asset with ID {asset_id} not found")
                
        if not assets:
            self.logger.error("No assets found")
            return False
            
        formatted = OutputFormatter.format_asset_table(assets)
        self.logger.info(f"\nAssets:\n{formatted}")
        return True
