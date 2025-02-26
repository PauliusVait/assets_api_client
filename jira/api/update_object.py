"""
Asset update functionality for Jira Assets API.

This module provides functionality to update existing assets in Jira 
by their ID with new attribute values.
"""
from typing import Dict, List, Union
from ..models.asset import Asset
from ..exceptions import AssetNotFoundError, InvalidUpdateError
from .base_handler import BaseHandler

def update_object(client, object_id: Union[str, int], updates: Dict[str, object]) -> Asset:
    """
    Update an asset object with the provided attribute updates.
    
    Args:
        client: AssetsClient instance
        object_id: ID of the object to update
        updates: Dictionary of attribute names and their new values
    
    Returns:
        Updated Asset object
    
    Raises:
        AssetNotFoundError: If the asset doesn't exist
        InvalidUpdateError: If the update format is invalid
        SchemaError: If the attribute doesn't exist in schema
    """
    # First get the current object to validate it exists and get its type
    current = BaseHandler.make_request(client, 'GET', f'object/{object_id}')
    BaseHandler.validate_schema_and_types(client, current, object_id)
    
    object_type_id = current.get('objectType', {}).get('id')
    if not object_type_id:
        raise InvalidUpdateError(f"Could not determine object type for asset {object_id}")
    
    # Convert attribute names to IDs and build the update payload
    attributes_to_update = []
    
    # Get all attribute definitions for this object type if not already cached
    if not client.schema_info.get('attribute_definitions'):
        client.logger.debug(f"Fetching attribute definitions for object type {object_type_id}")
        attr_response = BaseHandler.make_request(
            client, 'GET', f'objecttype/{object_type_id}/attributes')
        
        # Cache the attribute definitions
        attr_defs = {}
        # Handle response which could be a list or an object with a values property
        attributes_list = attr_response if isinstance(attr_response, list) else attr_response.get('values', [])
        
        for attr in attributes_list:
            attr_name = attr.get('name')
            attr_id = str(attr.get('id'))
            if attr_name and attr_id:
                attr_defs[attr_name] = attr_id
                
        client.schema_info['attribute_definitions'] = attr_defs
    
    attr_defs = client.schema_info.get('attribute_definitions', {})
    
    # Build the update payload
    for attr_name, value in updates.items():
        attr_id = attr_defs.get(attr_name)
        if not attr_id:
            available_attrs = ", ".join(sorted(attr_defs.keys()))
            raise InvalidUpdateError(
                f"Attribute '{attr_name}' not found for this object type. "
                f"Available attributes: {available_attrs}")
        
        # Handle different value types
        attr_values = []
        if isinstance(value, (list, tuple)):
            for val in value:
                attr_values.append({"value": val})
        else:
            attr_values.append({"value": value})
            
        attributes_to_update.append({
            "objectTypeAttributeId": attr_id,
            "objectAttributeValues": attr_values
        })
    
    # Create the update payload
    payload = {
        "attributes": attributes_to_update,
        "objectTypeId": object_type_id,
    }
    
    client.logger.debug(f"Updating asset {object_id} with attributes: {list(updates.keys())}")
    
    # Make the update request
    response = BaseHandler.make_request(
        client=client,
        method='PUT',
        endpoint=f'object/{object_id}',
        json=payload
    )
    
    # Return the updated asset
    return Asset(response)