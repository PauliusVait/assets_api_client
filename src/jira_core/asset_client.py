"""
Jira Assets API client module.

This module provides the AssetsClient class which implements the core
functionality for interacting with the Jira Assets API, including
querying, retrieving, and updating assets.
"""
from .client_base import BaseClient
from .models.asset import Asset
from .models.attribute_mapper import AttributeMapper
from .exceptions import AssetsError, InvalidUpdateError, SchemaError, InvalidQueryError
from .api.base_handler import BaseHandler
from .api.workspace_discovery import discover_workspace
from .api.schema_discovery import discover_schema
from .api.asset_query import get_objects_aql as get_objects_aql_func
from .api.asset_retrieval import get_object as get_object_func
from .api.asset_update import update_object as update_object_func
import re

class AssetsClient(BaseClient):
    """
    Client for interacting with the Jira Assets API.
    
    This class extends BaseClient to provide specific functionality for
    the Jira Assets API, including workspace and schema discovery,
    asset querying, and asset updates.
    """
    def __init__(self, refresh_cache=False):
        """
        Initialize a new AssetsClient instance.
        
        Args:
            refresh_cache (bool, optional): Whether to force refresh of cached
                workspace and schema information. Default is False.
        """
        super().__init__()
        
        # If refresh_cache is True, force rediscovery of workspace and schema
        if refresh_cache:
            self.logger.info("Forced cache refresh requested")
            self.workspace_id = None
            self.schema_info = {}
            self._save_cache()
        
        # Use cached workspace_id if available
        if not hasattr(self, 'workspace_id') or not self.workspace_id:
            self.workspace_id = self._discover_workspace()
            self._save_cache()

        self.base_url = f"https://api.atlassian.com/jsm/assets/workspace/{self.workspace_id}/v1"
        
        # Use cached schema_info if available
        if not self.schema_info or refresh_cache:
            self.logger.info("Refreshing schema information from API")
            self.schema_info = self._discover_schema()
            self._save_cache()
    
    def _discover_workspace(self):
        """
        Discover the workspace ID from Jira Service Management.
        
        Returns:
            str: The discovered workspace ID
        """
        return discover_workspace(self)
        
    def _discover_schema(self):
        """
        Discover the Assets schema (ID: 22) and its object types.
        
        Returns:
            dict: Schema information including schema ID and object types
        """
        return discover_schema(self)

    def refresh_schema(self):
        """
        Force a refresh of the schema information.
        
        Refreshes schema information from the API and updates the cache.
        
        Returns:
            dict: Updated schema information
        """
        self.logger.info("Manually refreshing schema information")
        self.schema_info = self._discover_schema()
        self._save_cache()
        return self.schema_info

    def get_object(self, object_id):
        """
        Retrieve a single asset by ID.
        
        Args:
            object_id (int or str): The ID of the asset to retrieve
            
        Returns:
            Asset: The retrieved asset object
            
        Raises:
            AssetNotFoundError: When the asset doesn't exist
            SchemaError: When the asset belongs to a different schema
        """
        try:
            return get_object_func(self, object_id)
        except Exception as e:
            self.logger.error(f"Failed to get object {object_id}: {str(e)}")
            raise

    def get_objects_aql(self, query, start_at=0, max_results=50, include_attributes=True):
        """
        Execute AQL query to retrieve assets.
        
        Args:
            query (str): The AQL query string
            start_at (int, optional): The index of the first result. Default is 0.
            max_results (int, optional): The maximum number of results. Default is 50.
            include_attributes (bool, optional): Whether to include asset attributes in the response. Default is True.
            
        Returns:
            list: List of Asset objects matching the query
            
        Raises:
            SchemaError: When referenced object types don't exist in schema
            InvalidQueryError: When the query syntax is invalid
        """
        return get_objects_aql_func(
            client=self,
            query=query,
            start_at=start_at,
            max_results=max_results,
            include_attributes=include_attributes
        )

    def update_object(self, object_id, updates):
        """
        Update an asset with the provided attribute updates.
        
        Args:
            object_id (int or str): ID of the object to update
            updates (dict): Dictionary mapping attribute names to new values
            
        Returns:
            Asset: Updated Asset object
            
        Raises:
            AssetNotFoundError: When the asset doesn't exist
            SchemaError: When an attribute doesn't exist in schema
            InvalidUpdateError: When the update format is invalid
        """
        if not updates or not isinstance(updates, dict):
            raise InvalidUpdateError("Updates must be a non-empty dictionary of attribute name/value pairs")
            
        return update_object_func(self, object_id, updates)
