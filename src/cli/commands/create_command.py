"""
Implementation of the 'create' command for creating assets.

This module provides the CreateCommand class that handles creating
new assets in the Jira Assets API with specified attributes.
"""
import argparse
import json
from typing import Dict, Any

from ...jira_core.asset_client import AssetsClient
from ...jira_core.services.asset_creator import AssetCreator
from ...logging.logger import Logger
from ..command_base import BaseCommand
from ..output_formatter import format_asset

class CreateCommand(BaseCommand):
    """Command handler for creating assets."""
    
    def configure_parser(self, parser: argparse.ArgumentParser) -> None:
        """
        Configure the argument parser for this command.
        
        Args:
            parser: The parser to configure
        """
        parser.add_argument('--type', type=str, required=True, 
                            help='Object type name (e.g., "Laptop", "Mobile Device")')
        parser.add_argument('--attributes', type=str, required=True,
                           help='JSON string of attribute key-value pairs (e.g., \'{"Name": "MacBook Pro", "Serial Number": "C02XL0GYJHD3"}\')')
        parser.add_argument('--attributes-file', type=str,
                           help='Path to JSON file containing attribute key-value pairs')
        parser.add_argument('--debug', action='store_true', help='Enable debug logging')
        parser.add_argument('--refresh-cache', action='store_true', 
                           help='Refresh schema cache before processing')
    
    def execute(self, args: argparse.Namespace) -> bool:
        """
        Execute the create command.
        
        Args:
            args: Parsed command arguments
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Setup basics
            self.setup(args)
            
            # Debug schema info 
            self.logger.debug(f"Schema info keys: {list(self.client.schema_info.keys())}")
            
            # Parse attributes
            attributes = self._parse_attributes(args)
            if not attributes:
                self.logger.error("No valid attributes provided")
                return False
                
            # Add debug information about the attributes being used
            self.logger.debug(f"Using attributes: {attributes}")
            
            # Validate object type against schema
            if not self._validate_object_type(args.type):
                self.logger.error(f"Invalid object type: {args.type}")
                return False
                
            # Create the asset - only with the attributes provided, no auto-generated Key
            self.logger.info(f"Creating new asset of type '{args.type}' with attributes: {attributes}")
            creator = AssetCreator(self.client, self.logger)
            result = creator.create_asset(args.type, attributes)
            
            if not result:
                self.logger.error("Failed to create asset")
                return False
            
            # Display the created asset
            asset_id = result.get('id')
            if not asset_id:
                self.logger.error("Created asset is missing ID")
                return False
                
            self.logger.info(f"Successfully created asset with ID: {asset_id}")
            
            # Get the full asset details and display them
            asset = self.client.get_object(asset_id)
            if asset:
                formatted = format_asset(asset)
                self.logger.info(f"\nCreated asset details:\n{formatted}")
            
            return True
            
        except Exception as e:
            return self.handle_error(e, f"creating asset of type '{args.type}'")
    
    def _parse_attributes(self, args) -> Dict[str, Any]:
        """
        Parse attributes from command line arguments or file.
        
        Args:
            args: Parsed command arguments
            
        Returns:
            Dict[str, Any]: Parsed attributes
        """
        try:
            # Try to use attributes file first if provided
            attributes = {}
            if args.attributes_file:
                self.logger.info(f"Loading attributes from file: {args.attributes_file}")
                with open(args.attributes_file, 'r') as f:
                    attributes = json.load(f)
            else:
                # Otherwise use the attributes string argument
                attributes = json.loads(args.attributes)
            
            # Ensure we have required attributes
            if not attributes:
                self.logger.error("No attributes provided")
                return {}
                
            # Normalize attribute names to title case if needed
            normalized = {}
            for key, value in attributes.items():
                # Convert "name" to "Name", "key" to "Key", etc.
                if key.lower() == "name":
                    normalized["Name"] = value
                elif key.lower() == "key":
                    normalized["Key"] = value
                else:
                    normalized[key] = value
                    
            return normalized
                
        except json.JSONDecodeError as e:
            self.logger.error(f"Invalid JSON format in attributes: {e}")
            self.logger.info("Attributes must be a valid JSON object, e.g., '{\"Name\": \"MacBook Pro\", \"Serial Number\": \"C02XL0GYJHD3\"}'")
            return {}
        except FileNotFoundError:
            self.logger.error(f"Attributes file not found: {args.attributes_file}")
            return {}
        except Exception as e:
            self.logger.error(f"Error parsing attributes: {e}")
            return {}
    
    def _validate_object_type(self, object_type: str) -> bool:
        """
        Validate that the object type exists in the schema.
        
        Args:
            object_type: Object type name to validate
            
        Returns:
            bool: True if valid, False otherwise
        """
        schema_info = self.client.schema_info
        object_types = schema_info.get('object_types', {})
        
        # Debug the object types structure
        self.logger.debug(f"Object types structure: {type(object_types)}")
        first_few = list(object_types.items())[:5]
        self.logger.debug(f"First few object types: {first_few}")
        
        # Create mappings to help find types by name
        name_to_id_map = {}
        all_type_names = []
        
        # Build name-to-id mapping
        for type_id, type_info in object_types.items():
            if isinstance(type_info, dict) and 'name' in type_info:
                name = type_info['name']
                name_to_id_map[name.lower()] = type_id
                all_type_names.append(name)
            elif isinstance(type_info, str):
                name_to_id_map[type_info.lower()] = type_id
                all_type_names.append(type_info)
        
        # Debug the name mapping
        self.logger.debug(f"Found {len(name_to_id_map)} named object types")
        
        # Try direct match on the ID first (in case the user provided an ID)
        if object_type in object_types:
            self.logger.debug(f"Found object type by direct ID match: '{object_type}'")
            return True
            
        # Try match by name (case insensitive)
        object_type_lower = object_type.lower()
        if object_type_lower in name_to_id_map:
            matched_id = name_to_id_map[object_type_lower]
            self.logger.debug(f"Found object type '{object_type}' with ID {matched_id}")
            return True
        
        # If not found, try partial matching
        partial_matches = [name for name in all_type_names 
                          if object_type_lower in name.lower()]
        
        if partial_matches:
            self.logger.error(f"Object type '{object_type}' not found. Did you mean one of: {', '.join(partial_matches)}?")
        else:
            # Show available type names for easier selection
            formatted_types = ", ".join(sorted(all_type_names))
            if len(formatted_types) > 100:
                formatted_types = formatted_types[:100] + "... (truncated)"
            self.logger.error(f"Object type '{object_type}' not found.")
            self.logger.error(f"Available types: {formatted_types}")
        
        return False
