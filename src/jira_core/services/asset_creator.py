"""
Asset creation service for Jira Assets API.

This module provides the AssetCreator class which implements business logic
for creating assets in the Jira Assets API, including proper attribute formatting.
"""
from typing import Dict, List, Any, Optional
from ...jira_core.asset_client import AssetsClient
from ...logging.logger import Logger
from ...jira_core.models.attribute_mapper import AttributeMapper
from ...jira_core.api.base_handler import BaseHandler
from ...jira_core.api.attribute_discovery import get_object_type_attributes, get_attributes_from_sample_object

class AssetCreator:
    """
    Handles asset creation according to business rules.
    
    This class provides methods to create assets with properly formatted
    attributes according to Jira Assets API requirements.
    """
    
    def __init__(self, client: AssetsClient, logger=None):
        """
        Initialize a new AssetCreator instance.
        
        Args:
            client (AssetsClient): The AssetsClient instance for API interactions
            logger (Logger, optional): A custom logger instance. If not provided,
                a new Logger will be configured.
        """
        self.client = client
        self.logger = logger or Logger.configure()
        # Initialize attribute mapper for dynamic attribute ID discovery
        self.attribute_mapper = AttributeMapper()
    
    def create_asset(self, object_type_name: str, attributes_dict: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """
        Create a new asset with the given object type and attributes.
        
        Args:
            object_type_name (str): The name of the object type (e.g., "Laptop", "Mobile Device")
            attributes_dict (Dict[str, Any]): Dictionary of attribute names and values
            
        Returns:
            Dict or None: The created asset or None if creation failed
        """
        try:
            # Get object type ID from name
            object_type_id = self._get_object_type_id(object_type_name)
            if not object_type_id:
                self.logger.error(f"Object type '{object_type_name}' not found in schema")
                return None
            
            # Format attributes for API call
            formatted_attributes = self._format_attributes_for_api(object_type_name, attributes_dict)
            if not formatted_attributes:
                self.logger.error(f"Failed to format attributes for object type '{object_type_name}'")
                return None
                
            # Create the asset
            self.logger.debug(f"Sending create request with type ID: {object_type_id}, attributes: {formatted_attributes}")
            result = self.client.create_object(object_type_id, formatted_attributes)
            
            # Ensure result is a dictionary
            if not isinstance(result, dict):
                self.logger.error(f"Unexpected result type: {type(result).__name__}, expected dict")
                return None
                
            return result
        
        except Exception as e:
            self.logger.error(f"Error creating asset: {str(e)}")
            raise
    
    def _get_object_type_id(self, object_type_name: str) -> Optional[str]:
        """
        Get the object type ID from its name.
        
        Args:
            object_type_name (str): The name of the object type
            
        Returns:
            str or None: The object type ID or None if not found
        """
        schema_info = self.client.schema_info
        if not schema_info:
            self.logger.error("Schema information is empty or not loaded")
            return None
            
        object_types = schema_info.get('object_types', {})
        if not object_types:
            self.logger.error("No object types found in schema")
            self.logger.debug(f"Available schema keys: {list(schema_info.keys())}")
            return None
        
        # First, check if object_type_name is directly an ID in the schema
        if object_type_name in object_types:
            self.logger.debug(f"Object type '{object_type_name}' is a direct ID match")
            return object_type_name
        
        # Try case-insensitive match against names
        object_type_name_lower = object_type_name.lower()
        
        # Handle both dictionary and string type values
        for type_id, type_info in object_types.items():
            # If type_info is a dictionary with a 'name' key
            if isinstance(type_info, dict) and 'name' in type_info:
                name = type_info['name'].lower()
                if name == object_type_name_lower:
                    self.logger.debug(f"Found object type '{object_type_name}' with ID {type_id}")
                    return type_id
            # If type_info is directly a string (the name)
            elif isinstance(type_info, str) and type_info.lower() == object_type_name_lower:
                self.logger.debug(f"Found object type '{object_type_name}' with ID {type_id}")
                return type_id
        
        # Log available types to help with troubleshooting
        available_types = []
        for type_id, type_info in object_types.items():
            if isinstance(type_info, dict) and 'name' in type_info:
                available_types.append(f"{type_info['name']} (ID: {type_id})")
            elif isinstance(type_info, str):
                available_types.append(f"{type_info} (ID: {type_id})")
            else:
                available_types.append(f"ID: {type_id}")
        
        sample_types = available_types[:10]
        self.logger.error(f"Object type '{object_type_name}' not found. Sample available types: {', '.join(sample_types)}")
        
        if len(available_types) > 10:
            self.logger.debug(f"All available types: {', '.join(available_types)}")
        
        return None
    
    def _format_attributes_for_api(self, object_type_name: str, attributes_dict: Dict[str, Any]) -> List[Dict[str, Any]]:
        """
        Format attributes for the API call according to Jira Assets API requirements.
        
        Required format:
        [
            {
                "objectTypeAttributeId": "5063",  # This is specific to the object type!
                "objectAttributeValues": [
                    {"value": "Some value"}
                ]
            }
        ]
        
        Args:
            object_type_name (str): The name of the object type
            attributes_dict (Dict[str, Any]): Dictionary of attribute names and values
            
        Returns:
            List[Dict[str, Any]]: Formatted attributes for the API
        """
        schema_info = self.client.schema_info
        if not schema_info:
            self.logger.error("Schema information is empty")
            return []
            
        object_types = schema_info.get('object_types', {})
        
        # Get the object type ID
        object_type_id = None
        if object_type_name in object_types:
            # Direct match
            value = object_types[object_type_name]
            if isinstance(value, str) and value.isdigit():
                object_type_id = value
                self.logger.debug(f"Found object type ID: {object_type_id} for {object_type_name}")
            else:
                self.logger.debug(f"Object type match found but value is not a numeric ID: {value}")
        
        if not object_type_id:
            # Try to get the ID using the regular method
            object_type_id = self._get_object_type_id(object_type_name)
            if not object_type_id:
                self.logger.error(f"Could not determine a valid ID for object type '{object_type_name}'")
                return []
        
        # Ensure we have required attributes
        if len(attributes_dict) == 0:
            self.logger.error("No attributes provided")
            return []
        
        # Discover attribute IDs for this object type
        object_type_attributes = self._discover_object_type_attributes(object_type_id)
        if not object_type_attributes:
            self.logger.warning(f"No attribute definitions found for object type {object_type_name} ({object_type_id})")
        
        # Format attributes strictly according to the API documentation format
        formatted_attributes = []
        
        for attr_name, attr_value in attributes_dict.items():
            # Try to map attribute name to its ID for this specific object type
            attr_id = self._find_attribute_id(attr_name, object_type_attributes)
            
            if attr_id:
                self.logger.debug(f"Found attribute ID '{attr_id}' for '{attr_name}' in object type {object_type_name}")
            else:
                self.logger.warning(f"No mapping found for attribute '{attr_name}' in object type '{object_type_name}'")
                # Skip attributes we don't have mappings for
                continue
            
            # Format the attribute according to API documentation format
            formatted_attribute = {
                "objectTypeAttributeId": str(attr_id),
                "objectAttributeValues": [
                    {
                        "value": str(attr_value)
                    }
                ]
            }
            formatted_attributes.append(formatted_attribute)
        
        # Log the final formatted attributes
        self.logger.debug(f"Formatted attributes: {formatted_attributes}")
        
        if not formatted_attributes:
            self.logger.warning(f"No valid attribute mappings found for object type '{object_type_name}'")
        
        return formatted_attributes

    def _discover_object_type_attributes(self, object_type_id: str) -> Dict[str, Any]:
        """
        Discover attribute definitions for a specific object type.
        
        Args:
            object_type_id: The ID of the object type
            
        Returns:
            Dict[str, Any]: Mapping of attribute names to their IDs
        """
        # First, try the dedicated attributes endpoint (most reliable and efficient)
        attribute_map = get_object_type_attributes(self.client, object_type_id)
        
        if attribute_map:
            self.logger.debug(f"Successfully discovered {len(attribute_map)} attributes using direct attributes endpoint")
            return attribute_map
        
        # If direct endpoint fails, try sample object approach (which is still quite reliable)
        attribute_map = get_attributes_from_sample_object(self.client, object_type_id)
        if attribute_map:
            self.logger.debug(f"Discovered {len(attribute_map)} attributes from sample object")
            return attribute_map
        
        # Only as a last resort, try the schema definition approach
        try:
            url = f"objectschema/{self.client.schema_info.get('id')}"
            self.logger.debug(f"Trying schema definition as last resort for attribute discovery")
            
            response = BaseHandler.make_request(
                self.client,
                'GET',
                url,
                params={
                    'expand': 'objectTypes.attributes',
                    'includeAttributes': 'true'
                }
            )
            
            attribute_map = {}
            
            # Look for object types section
            object_types = response.get('objectTypes', [])
            for obj_type in object_types:
                if str(obj_type.get('id')) == str(object_type_id):
                    self.logger.debug(f"Found object type {object_type_id} in schema definition")
                    
                    # Look for attributes
                    attributes = obj_type.get('attributes', [])
                    for attr in attributes:
                        attr_id = str(attr.get('id', ''))
                        attr_name = attr.get('name', '')
                        if attr_id and attr_name:
                            attribute_map[attr_name.lower()] = attr_id
                            self.logger.debug(f"Found attribute in schema: {attr_name} -> {attr_id}")
                    
                    break
            
            return attribute_map
            
        except Exception as e:
            self.logger.debug(f"Failed to get attributes from schema definition: {str(e)}")
            
        self.logger.warning(f"Failed to discover any attributes for object type {object_type_id} using all available methods")
        return {}

    def _find_attribute_id(self, attr_name: str, object_type_attributes: Dict[str, Any]) -> Optional[str]:
        """
        Find attribute ID by name in the object type attributes.
        
        Args:
            attr_name: The attribute name to look for
            object_type_attributes: Mapping of attribute names to IDs
            
        Returns:
            str or None: The attribute ID if found, None otherwise
        """
        # Try exact match (case-insensitive)
        attr_name_lower = attr_name.lower()
        if attr_name_lower in object_type_attributes:
            return object_type_attributes[attr_name_lower]
        
        # Try common standardized names
        common_attributes = {
            'name': ['name', 'title', 'asset name'],
            'serial number': ['serial', 'serialnumber', 'serial number', 'serialnum'],
            'status': ['status', 'state', 'condition'],
            'model': ['model', 'device model'],
            'manufacturer': ['manufacturer', 'vendor', 'make'],
        }
        
        # Check if this attribute name is in our common attribute mappings
        for common_name, variations in common_attributes.items():
            if attr_name_lower in variations:
                # Look for any of the common variations in the attribute map
                for variation in variations:
                    if variation in object_type_attributes:
                        self.logger.debug(f"Mapped '{attr_name}' to common attribute '{variation}'")
                        return object_type_attributes[variation]
        
        # Try partial match as a last resort
        for name, id in object_type_attributes.items():
            if name in attr_name_lower or attr_name_lower in name:
                self.logger.debug(f"Using partial match: '{name}' for '{attr_name}'")
                return id
        
        return None

