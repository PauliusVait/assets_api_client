"""
Asset model module for Jira Assets API.

This module defines the Asset class which represents a Jira asset with
its attributes and provides methods to process and extract asset data.
"""
from typing import Any, Dict, Optional
from .attribute_mapper import AttributeMapper

class Asset:
    """
    Represents a Jira asset with its attributes.
    
    This class encapsulates asset data from the Jira Assets API and provides
    methods to access and transform this data. It uses a shared AttributeMapper
    to resolve attribute names from IDs.
    """
    # Create class-level mapper that's shared across all instances
    _mapper = AttributeMapper()
    
    def __init__(self, data: Dict[str, Any], attribute_definitions=None):
        """
        Initialize a new Asset instance from API response data.
        
        Args:
            data (dict): The raw asset data from the API response
            attribute_definitions (dict, optional): Additional attribute definitions
                to update the mapper cache
        """
        self.id = str(data.get('id', ''))
        self.name = data.get('name', '')
        self.object_key = data.get('objectKey', '')
        self.object_type = data.get('objectType', {}).get('name', '')
        self.created = data.get('created', '')
        self.updated = data.get('updated', '')
        
        # Get attributes either from top-level or nested in objectTypeAttributes
        attributes = data.get('attributes', [])
        if not attributes and 'objectTypeAttributes' in data:
            attributes = data.get('objectTypeAttributes', [])
        
        # Update the class-level mapper's definitions if provided
        if attribute_definitions:
            Asset._mapper._definition_cache.update(attribute_definitions)
            Asset._mapper.trim_cache()  # Call trim_cache after updating the cache
            
        self.attributes = self._process_attributes(attributes)
        self._raw_data = data

    def _process_attributes(self, attributes):
        """
        Process raw attribute data into a structured format.
        
        Converts the raw attribute data array into a dictionary mapping
        attribute names to their values.
        
        Args:
            attributes (list): List of raw attribute objects from the API
            
        Returns:
            dict: Processed attributes with names as keys and processed values as values
        """
        processed = {}
        for attr in attributes:
            name = self._mapper.get_attribute_name(attr)
            if not name:
                continue
                
            values = self._extract_values(attr)
            if not values:
                processed[name] = None
                continue
                
            # Single value processing
            if len(values) == 1:
                processed[name] = self._extract_single_value(values[0])
            else:
                processed[name] = [self._extract_single_value(v) for v in values]
                
        return processed
    
    def _extract_values(self, attr):
        """
        Extract values from attribute data.
        
        Handles different attribute value formats in the API response.
        
        Args:
            attr (dict): The attribute data from which to extract values
            
        Returns:
            list: List of value objects extracted from the attribute
        """
        if 'objectAttributeValues' in attr:
            return attr['objectAttributeValues']
        if 'value' in attr:
            return [{'value': attr['value']}]
        if isinstance(attr.get('attributeValue'), dict):
            return [attr['attributeValue']]
        if isinstance(attr.get('attributeValues'), list):
            return attr['attributeValues']
        return []
    
    def _extract_single_value(self, value):
        """
        Extract a single value from a value object.
        
        Handles different types of value objects (references, status, simple values).
        
        Args:
            value (dict): The value object to extract from
            
        Returns:
            str: The extracted value as a string
        """
        if 'referencedObject' in value:
            return value['referencedObject'].get('name', '')
        if 'status' in value:
            return value.get('status', {}).get('name', '')
        return (value.get('value') or 
                value.get('displayValue') or 
                value.get('searchValue', ''))

    def get_attribute(self, name: str, default: Any = None) -> Any:
        """
        Get attribute value by name.
        
        Args:
            name: Attribute name
            default: Default value if attribute not found
            
        Returns:
            Attribute value or default
        """
        return self.attributes.get(name, default)

    def to_dict(self):
        """
        Convert the asset to a dictionary representation.
        
        Returns:
            dict: A dictionary containing the asset's properties and attributes
        """
        return {
            'id': self.id,
            'name': self.get_attribute('Name', ''),
            'object_key': self.object_key,
            'type': self.object_type,
            'created': self.created,
            'updated': self.updated,
            'attributes': self.attributes
        }
