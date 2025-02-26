"""
Asset update command for the Assets CLI.

This module provides the command-line interface for updating
asset attributes using the Jira Assets API.
"""
import json
import sys
from ..command_base import BaseCommand
from ..output_formatter import format_asset_output

class UpdateCommand(BaseCommand):
    """Command to update an asset"""
    
    def configure_parser(self, parser):
        """
        Configure argument parser for the Update command.
        
        Args:
            parser: ArgumentParser instance to configure
            
        Returns:
            Configured parser
        """
        id_group = parser.add_mutually_exclusive_group(required=True)
        id_group.add_argument('--id', type=int, help='Object ID to update')
        id_group.add_argument('--ids', type=str, help='Comma-separated list of asset IDs to update')
        parser.add_argument('--attrs', type=str, help='JSON string of attribute name/value pairs')
        parser.add_argument('--attr', action='append', help='Attribute in name=value format (can be used multiple times)')
        parser.add_argument('--debug', action='store_true', help='Enable debug logging')
        parser.add_argument('--refresh-cache', action='store_true', 
                          help='Force refresh of schema cache')
        return parser
        
    def execute(self, args):
        """
        Execute the Update command with the parsed arguments.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            bool: True if at least one asset was updated successfully, False otherwise
        """
        self.setup(args)
        
        try:
            # Process attribute updates from either JSON or individual flags
            updates = {}
            
            if args.attrs:
                try:
                    updates = json.loads(args.attrs)
                    if not isinstance(updates, dict):
                        self.logger.error("--attrs must be a JSON object")
                        return False
                except json.JSONDecodeError as e:
                    return self.handle_error(e, "parsing JSON attributes")
                    
            if args.attr:
                for attr_pair in args.attr:
                    if '=' not in attr_pair:
                        return self.handle_error(
                            ValueError(f"Invalid attribute format: {attr_pair}. Must be name=value"),
                            "parsing attribute"
                        )
                    name, value = attr_pair.split('=', 1)
                    updates[name.strip()] = value.strip()
            
            if not updates:
                self.logger.error("No attributes specified for update. Use --attrs or --attr")
                return False
            
            # Determine asset IDs to update
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
            
            # Update each asset
            success_count = 0
            for asset_id in asset_ids:    
                self.logger.info(f"Updating asset {asset_id} with attributes: {json.dumps(updates, indent=2)}")
                try:
                    result = self.client.update_object(asset_id, updates)
                    self.logger.info(f"Asset {asset_id} updated successfully")
                    self.logger.info("\n" + format_asset_output(result))
                    success_count += 1
                except Exception as e:
                    self.handle_error(e, f"updating asset {asset_id}")
                    continue
            
            if success_count > 0:
                self.logger.info(f"Successfully updated {success_count} out of {len(asset_ids)} assets")
                return True
            else:
                return False
                
        except Exception as e:
            return self.handle_error(e, "executing update command")
