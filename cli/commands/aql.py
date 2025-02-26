"""
AQL query command for the Assets CLI.

This module provides the command-line interface for executing
AQL (Atlassian Query Language) queries against the Jira Assets API.
"""
from ..base import BaseCommand
from ..formatter import format_asset_output

class AqlCommand(BaseCommand):
    """Command to execute AQL queries"""
    
    def configure_parser(self, parser):
        """
        Configure argument parser for the AQL command.
        
        Args:
            parser: ArgumentParser instance to configure
            
        Returns:
            Configured parser
        """
        parser.add_argument('--query', type=str, required=True, 
            help='AQL query string. Use objectType = "Type Name" for type filtering')
        parser.add_argument('--start-at', type=int, default=0, 
            help='Starting index for pagination (default: 0)')
        parser.add_argument('--max-results', type=int, default=50, 
            help='Maximum number of results (default: 50)')
        parser.add_argument('--no-attributes', action='store_false', 
            dest='include_attributes', help='Exclude attributes from results')
        parser.add_argument('--refresh-cache', action='store_true', 
            help='Force refresh of schema cache')
        parser.add_argument('--debug', action='store_true', 
            help='Enable debug logging')
        return parser
        
    def execute(self, args):
        """
        Execute the AQL command with the parsed arguments.
        
        Args:
            args: Parsed command line arguments
            
        Returns:
            bool: True if successful, False otherwise
        """
        self.setup(args)
        
        try:
            self.logger.info(f"Executing AQL query: {args.query}")
            try:
                results = self.client.get_objects_aql(
                    args.query, 
                    args.start_at, 
                    args.max_results, 
                    args.include_attributes
                )
                
                if results:
                    self.logger.info(f"Query returned {len(results)} results")
                    for asset in results:
                        self.logger.info("\n" + format_asset_output(asset))
                else:
                    self.logger.info("No results found")
                    
                return True
            except Exception as e:
                return self.handle_error(e, "executing AQL query")
                
        except Exception as e:
            return self.handle_error(e, "executing AQL command")
