"""
AQL query functionality for the Jira Assets API.

This module provides functions to execute AQL (Atlassian Query Language)
queries against the Jira Assets API, with support for pagination and
attribute filtering.
"""
import re
from typing import List, Dict, Any, Optional
from ..models.asset import Asset
from ..exceptions import InvalidQueryError, SchemaError
from .base_handler import BaseHandler

def get_objects_aql(client, query, start_at=0, max_results=50, include_attributes=True):
    """
    Execute AQL query to retrieve assets.
    
    Args:
        client: AssetsClient instance
        query: AQL query string
        start_at: Index of first result 
        max_results: Maximum number of results
        include_attributes: Whether to include asset attributes
        
    Returns:
        list: List of Asset objects matching the query
    """
    from ..models.asset import Asset
    
    # Ensure query has schema filter - constrain query to client's schema
    if 'objectSchemaId' not in query:
        schema_id = client.schema_info.get('id')
        if schema_id:
            query = f"({query}) AND objectSchemaId = {schema_id}"
    
    client.logger.debug(f"Full AQL query: {query}")
    
    # Set up service info for attribute inclusion
    service_info = {
        'includeAttributes': include_attributes,
        'includeAttributeValues': include_attributes,
        'includeTypeAttributes': include_attributes,
        'includeAttributeNames': include_attributes
    }
    
    # Make the API request
    response = BaseHandler.make_request(
        client,
        'POST',
        'object/aql',
        params={
            'startAt': start_at,
            'maxResults': max_results
        },
        json={
            'qlQuery': query,
            'serviceInfo': service_info
        }
    )
    
    # Extract the values (list of objects)
    result_values = response.get('values', [])
    client.logger.debug(f"Got {len(result_values)} objects from AQL query")
    
    # Extract object type attributes for mapping
    attr_defs = {}
    obj_type_attrs = response.get('objectTypeAttributes', {})
    
    # Check if objectTypeAttributes is actually a dict before calling .items()
    if isinstance(obj_type_attrs, dict):
        client.logger.debug(f"Processing {len(obj_type_attrs)} object type attributes (dict)")
        for attr_id, attr_info in obj_type_attrs.items():
            attr_name = attr_info.get('name')
            if attr_id and attr_name:
                attr_defs[attr_id] = attr_name
    elif isinstance(obj_type_attrs, list):
        # Sometimes it might be a list instead of a dict
        client.logger.debug(f"Processing {len(obj_type_attrs)} object type attributes (list)")
        for attr_info in obj_type_attrs:
            attr_id = str(attr_info.get('id', ''))
            attr_name = attr_info.get('name')
            if attr_id and attr_name:
                attr_defs[attr_id] = attr_name
    
    # Convert raw API results to Asset objects
    assets = []
    for value in result_values:
        try:
            # Create Asset object and add to list
            asset = Asset(value, attr_defs)
            assets.append(asset)
        except Exception as e:
            client.logger.error(f"Error creating Asset object from response: {str(e)}")
            # Continue processing other assets even if one fails
    
    client.logger.debug(f"Converted {len(assets)} raw objects to Asset objects")
    return assets