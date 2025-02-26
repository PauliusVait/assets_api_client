"""
Schema discovery functionality for Jira Assets API.

This module provides functionality to automatically discover
the Assets schema (standard ID: 22) and its object types.
"""
from .base_handler import BaseHandler

def discover_schema(client):
    """
    Discover the Assets schema (ID: 22) and its object types.
    
    Args:
        client: AssetsClient instance
        
    Returns:
        dict: Schema information including ID, name, and object types mapping
        
    Raises:
        ValueError: If the Assets schema cannot be found
    """
    schemas = BaseHandler.make_request(client, 'GET', 'objectschema/list')
    
    # Handle both possible response formats and find schema 22
    schema_list = schemas if isinstance(schemas, list) else schemas.get('values', [])
    assets_schema = next((s for s in schema_list 
                         if isinstance(s, dict) and str(s.get('id')) == '22'), None)
    
    if not assets_schema:
        available = [f"- {s.get('name', 'Unknown')} (ID: {s.get('id', 'Unknown')})" 
                    for s in schema_list if isinstance(s, dict)]
        raise ValueError(
            "Could not find Assets schema (ID: 22). Available schemas:\n" + 
            "\n".join(available)
        )
    
    # Get object types
    types_data = BaseHandler.make_request(
        client, 'GET', f"objectschema/{assets_schema['id']}/objecttypes/flat"
    )
    
    object_types = (types_data if isinstance(types_data, list) 
                   else types_data.get('values', []))
    
    return {
        'id': str(assets_schema.get('id')),
        'name': assets_schema.get('name'),
        'object_types': {
            t.get('name'): str(t.get('id')) 
            for t in object_types 
            if isinstance(t, dict) and t.get('name')
        }
    }
