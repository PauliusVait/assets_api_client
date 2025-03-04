"""
Attribute discovery module for Jira Assets API.

This module provides functions to discover attribute definitions
for object types in the Jira Assets API.
"""
from typing import Dict, Any, Optional
from ..exceptions import AssetsError

def get_object_type_attributes(client, object_type_id: str) -> Dict[str, str]:
    """
    Get attributes for a specific object type using the direct attributes endpoint.
    
    This function queries the dedicated attributes endpoint for an object type
    to get its attribute definitions.
    
    Args:
        client: AssetsClient instance
        object_type_id: ID of the object type
        
    Returns:
        Dict[str, str]: A mapping of attribute names (lowercase) to their IDs
    """
    from .base_handler import BaseHandler
    
    client.logger.debug(f"Getting attributes for object type {object_type_id} using direct attributes endpoint")
    
    try:
        # Use the dedicated endpoint for object type attributes
        url = f"objecttype/{object_type_id}/attributes"
        
        response = BaseHandler.make_request(
            client,
            'GET',
            url,
            include_type_attributes=True
        )
        
        attribute_map = {}
        
        # Handle response being either a list or a dict
        attributes_list = []
        if isinstance(response, list):
            attributes_list = response
        elif isinstance(response, dict) and 'attributes' in response:
            attributes_list = response['attributes']
        
        # Process list into a name -> ID mapping
        for attr in attributes_list:
            if not isinstance(attr, dict):
                continue
                
            # Try multiple paths to get ID and name
            attr_id = str(attr.get('id', '') or 
                        attr.get('objectTypeAttributeId', '') or
                        attr.get('objectTypeAttribute', {}).get('id', ''))
                        
            attr_name = (attr.get('name', '') or 
                        attr.get('objectTypeAttribute', {}).get('name', ''))
                        
            if attr_id and attr_name:
                attribute_map[attr_name.lower()] = attr_id
                client.logger.debug(f"Found attribute: {attr_name} -> {attr_id}")
        
        if attribute_map:
            client.logger.debug(f"Got {len(attribute_map)} attributes from direct endpoint")
        else:
            client.logger.warning(f"No attributes found for object type {object_type_id}")
            
        return attribute_map
            
    except Exception as e:
        client.logger.error(f"Failed to get attributes for object type {object_type_id}: {str(e)}")
        return {}

def get_attributes_from_sample_object(client, object_type_id: str) -> Dict[str, str]:
    """
    Get attributes for an object type by querying a sample object of that type.
    
    This function is used as a fallback when the direct attributes endpoint fails.
    
    Args:
        client: AssetsClient instance
        object_type_id: ID of the object type
        
    Returns:
        Dict[str, str]: A mapping of attribute names (lowercase) to their IDs
    """
    from .base_handler import BaseHandler
    
    client.logger.debug(f"Getting attributes from sample object of type {object_type_id}")
    
    try:
        # Query for objects of this type
        query = f'objectType = {object_type_id} ORDER BY created DESC'
        
        response = BaseHandler.make_request(
            client,
            'POST',
            'object/aql',
            json={
                'qlQuery': query,
                'startAt': 0,
                'maxResults': 1
            }
        )
        
        # Check if we have results
        if 'values' not in response or not response['values']:
            client.logger.debug(f"No sample objects found for type {object_type_id}")
            return {}
        
        # Get the first object
        sample_object = response['values'][0]
        object_id = sample_object.get('id')
        client.logger.debug(f"Found sample object ID: {object_id}")
        
        # Get the full object details
        object_response = BaseHandler.make_request(
            client,
            'GET',
            f"object/{object_id}",
            params={
                'expand': 'attributes,objectTypeAttribute',
                'includeAttributes': 'true'
            }
        )
        
        # Extract attribute information
        attribute_map = {}
        attributes = object_response.get('attributes', [])
        
        for attr in attributes:
            attr_id = attr.get('objectTypeAttributeId')
            attr_name = None
            
            # Try to get the attribute name
            if 'objectTypeAttribute' in attr and 'name' in attr['objectTypeAttribute']:
                attr_name = attr['objectTypeAttribute']['name']
            
            if attr_id and attr_name:
                attribute_map[attr_name.lower()] = str(attr_id)
                client.logger.debug(f"Found attribute from sample: {attr_name} -> {attr_id}")
        
        return attribute_map
        
    except Exception as e:
        client.logger.debug(f"Error getting attributes from sample object: {str(e)}")
        return {}
