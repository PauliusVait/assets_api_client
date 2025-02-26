"""
Single asset retrieval functionality for Jira Assets API.

This module provides functionality to fetch individual assets by their ID.
"""
from ..models.asset import Asset
from ..exceptions import AssetNotFoundError
from .base_handler import BaseHandler

def get_object(client, object_id: str) -> Asset:
    """
    Retrieve a single asset object by ID.
    
    Args:
        client: AssetsClient instance
        object_id: ID of the asset to retrieve
        
    Returns:
        Asset object with the requested ID
        
    Raises:
        AssetNotFoundError: If the asset with the given ID doesn't exist
    """
    try:
        result = BaseHandler.make_request(client, 'GET', f'object/{object_id}')
        BaseHandler.validate_schema_and_types(client, result, object_id)
        return Asset(result)
    except AssetNotFoundError:
        client.logger.error(f"Asset with ID '{object_id}' does not exist")
        raise
