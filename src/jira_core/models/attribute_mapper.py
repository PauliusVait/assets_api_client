"""
Attribute Mapper module for Jira Assets API.

This module provides functionality to map attribute IDs to their names
and maintains a cache to optimize performance during attribute lookups.
"""
from src.logging.logger import Logger


class AttributeMapper:
    """
    Maps attribute IDs to their names and maintains a cache for efficient lookups.
    
    This class builds and maintains a cache of attribute definitions from API responses
    and provides methods to look up attribute names by various identifiers.
    """
    def __init__(self):
        """
        Initialize a new AttributeMapper with an empty cache.
        """
        self._definition_cache = {}
        self.logger = Logger()
        self._cache_limit = 1000  # Limit cache size
    
    def build_definitions(self, response_data):
        """
        Build attribute definitions from API response data.
        
        Extracts attribute IDs and names from the response data and
        updates the internal cache with these mappings.
        
        Args:
            response_data (dict): The API response containing attribute definitions
            
        Returns:
            dict: A dictionary mapping attribute IDs to their names
        """
        definitions = {}
        
        # Handle list response (from direct attributes endpoint)
        if isinstance(response_data, list):
            for attr in response_data:
                if isinstance(attr, dict):
                    attr_id = str(attr.get('id', ''))
                    attr_name = attr.get('name', '')
                    if attr_id and attr_name:
                        definitions[attr_id] = attr_name
            
            # If we got definitions, update cache and return
            if definitions:
                self._definition_cache.update(definitions)
                self.trim_cache()
                return definitions
        
        # Handle dict response
        if isinstance(response_data, dict):
            # Check different possible locations for attributes
            for attr_key in ['objectTypeAttributes', 'objecttypeattributes', 'attributes']:
                if attr_key in response_data and not definitions:
                    for attr in response_data[attr_key]:
                        attr_id = str(attr.get('id', ''))
                        attr_name = attr.get('name', '')
                        if attr_id and attr_name:
                            definitions[attr_id] = attr_name
        
        # Update cache with what we found
        if definitions:
            self._definition_cache.update(definitions)
            self.trim_cache()
        
        return definitions
    
    def get_attribute_name(self, attr):
        """
        Get attribute name from attribute data.
        
        Attempts to retrieve an attribute name using various strategies:
        1. Direct name lookup in the attribute
        2. Lookup via ID in the cache
        3. Fallback to other ID fields
        
        Args:
            attr (dict): The attribute data to extract a name from
            
        Returns:
            str: The attribute name or ID if name couldn't be determined
        """
        # Try direct name first
        name = (attr.get('objectTypeAttribute', {}).get('name') or 
               attr.get('name'))
        if name:
            return name
            
        # Try ID lookup
        attr_id = str(attr.get('objectTypeAttributeId', ''))
        if attr_id in self._definition_cache:
            return self._definition_cache[attr_id]
            
        # Fallback to other ID fields
        attr_id = (attr.get('objectTypeAttribute', {}).get('id') or 
                  attr.get('id') or
                  attr_id)
        return self._definition_cache.get(attr_id, attr_id)
    
    def clear_cache(self):
        """
        Clear the attribute definition cache.
        
        Removes all cached attribute definitions to free memory or force fresh lookups.
        """
        self._definition_cache.clear()
        
    def trim_cache(self):
        """
        Trim the cache if it exceeds the size limit.
        
        Keeps only the most recent half of the cached items if the cache
        exceeds the configured size limit.
        """
        if len(self._definition_cache) > self._cache_limit:
            # Keep the most recent half of the items
            items = list(self._definition_cache.items())
            self._definition_cache = dict(items[-self._cache_limit//2:])
            self.logger.debug(f"Trimmed attribute definition cache to {len(self._definition_cache)} items")
