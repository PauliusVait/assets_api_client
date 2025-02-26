"""
Asset retrieval command for the Assets CLI.

This module provides the command-line interface for retrieving
individual assets by their ID from the Jira Assets API.
"""
from ..base import BaseCommand
from ..formatter import format_asset_output

class GetCommand(BaseCommand):
    """Command to retrieve a single asset by ID"""
    
    def configure_parser(self, parser):
        """
        Configure argument parser for the Get command.
        
        Args:
            parser: ArgumentParser instance to configure
            
        Returns:
            Configured parser
        """
        id_group = parser.add_mutually_exclusive_group(required=True)
        id_group.add_argument('--id', type=int, help='Object ID to retrieve')
        id_group.add_argument('--ids', type=str, help='Comma-separated list of asset IDs to retrieve')
        parser.add_argument('--debug', action='store_true', help='Enable debug logging')
        return parser
        
    def execute(self, args):
        """
        Execute the Get command with the parsed arguments.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.setup(args)
        
        try:
            asset_ids = []
            
            if args.id:
                asset_ids = [args.id]
            elif args.ids:
                try:
                    asset_ids = [int(id.strip()) for id in args.ids.split(',')]
                except ValueError:
                    return self.handle_error(ValueError("IDs must be valid integers"), "parsing asset IDs")
                
            if not asset_ids:
                self.logger.error("You must specify either --id or --ids")
                return False
                
            for asset_id in asset_ids:
                self.logger.info(f"Fetching object data for ID: {asset_id}...")
                try:
                    result = self.client.get_object(asset_id)
                    self.logger.info("Object data retrieved successfully")
                    self.logger.info("\n" + format_asset_output(result))
                except Exception as e:
                    self.handle_error(e, f"retrieving asset {asset_id}")
                    continue
                
            return True
        except Exception as e:
            return self.handle_error(e, "executing get command")
