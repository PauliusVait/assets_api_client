"""
Base request handler for Jira Assets API.

This module provides core functionality for making API requests
to the Jira Assets API, handling errors, and validating responses.
"""
import requests
from typing import Optional, Dict, Any, List
from ..exceptions import AssetNotFoundError, AssetsError, SchemaError, InvalidQueryError

class BaseHandler:
    """
    Base handler for making API requests to Jira Assets API.
    
    Provides static methods for making requests and validating responses.
    """
    
    GET_PARAMS = {
        'includeAttributes': 'true',
        'attributeNames': '*',
        'expand': 'attributes,objectType,attributeValues'
    }
    
    @staticmethod
    def make_request(
        client, 
        method: str, 
        endpoint: str, 
        params: Optional[Dict] = None, 
        json: Optional[Dict] = None,
        include_type_attributes: bool = False,
        use_base_url: bool = True
    ) -> Dict[str, Any]:
        """
        Make an API request to the Jira Assets API.
        
        Args:
            client: AssetsClient instance
            method: HTTP method (GET, POST, PUT, DELETE)
            endpoint: API endpoint path
            params: Query parameters (optional)
            json: JSON body for POST/PUT requests (optional)
            include_type_attributes: Whether to include object type attributes (optional)
            use_base_url: Whether to prefix the endpoint with the base URL (optional)
            
        Returns:
            JSON response as a dictionary
            
        Raises:
            AssetNotFoundError: If the requested resource was not found
            InvalidQueryError: If the query is invalid
            SchemaError: If there's a schema-related error
            AssetsError: For general API errors
            requests.exceptions.RequestException: For network-related errors
        """
        url = f"{client.base_url}/{endpoint.lstrip('/')}" if use_base_url else endpoint
        
        client.logger.debug(f"Making {method} request to: {url}")
        
        request_params = params or {}
        if method.upper() == 'GET':
            request_params = BaseHandler.GET_PARAMS.copy()
            if include_type_attributes:
                request_params['expand'] = f"{request_params['expand']},objectTypeAttributes"
            if params:
                request_params.update(params)
            
        headers = {"Accept": "application/json", "Authorization": f"Basic {client.basic_auth}"}
        if method.upper() == 'POST':
            headers["Content-Type"] = "application/json"

        try:
            response = requests.request(
                method=method, url=url, headers=headers,
                params=request_params, json=json, verify=client.verify
            )
            
            client.logger.debug(f"Response status: {response.status_code}")
            
            if response.status_code == 404:
                if 'object/' in endpoint:
                    object_id = endpoint.split('/')[-1]
                    raise AssetNotFoundError(
                        f"Asset with ID '{object_id}' was not found. "
                        "Please verify the ID is correct."
                    )
                raise AssetNotFoundError("Requested resource was not found")
                
            if response.status_code == 400:
                error_data = response.json()
                error_msg = error_data.get('errorMessage', '')
                client.logger.error(f"API error: {error_msg}")
                
                if any(x in error_msg.lower() for x in ['invalid', 'syntax', 'malformed']):
                    raise InvalidQueryError(f"Invalid query: {error_msg}")
                elif 'schema' in error_msg.lower():
                    raise SchemaError(error_msg)
                else:
                    raise AssetsError(error_msg)
                    
            response.raise_for_status()
            data = response.json()
            
            # Check for empty results
            if method.upper() == 'POST' and 'aql' in endpoint:
                if not data.get('values'):
                    client.logger.info("No results found")
                    
            return data
            
        except requests.exceptions.RequestException as e:
            error_msg = str(e)
            if hasattr(e, 'response') and e.response:
                client.logger.error(f"Response status: {e.response.status_code}")
                try:
                    error_data = e.response.json()
                    if 'errorMessage' in error_data:
                        error_msg = error_data['errorMessage']
                except (ValueError, KeyError):
                    error_msg = e.response.text
                
            client.logger.error(f"API request failed: {error_msg}")
            raise

    @staticmethod
    def validate_schema_and_types(client, result: Dict, object_id: Optional[str] = None, types: Optional[List[str]] = None) -> None:
        """
        Validate that an object belongs to the expected schema and that requested types exist.
        
        Args:
            client: AssetsClient instance
            result: API response to validate
            object_id: Optional object ID for error messages
            types: Optional list of object types to validate
            
        Raises:
            SchemaError: If the object is from a different schema or types don't exist
        """
        if types:
            invalid_types = [t for t in types if t not in client.schema_info['object_types']]
            if invalid_types:
                raise SchemaError(
                    f"Invalid object type(s) for schema {client.schema_info['name']}: {', '.join(invalid_types)}\n"
                    f"Available types: {', '.join(client.schema_info['object_types'].keys())}"
                )
        
        if result:
            schema_id = str(result.get('objectType', {}).get('objectSchemaId'))
            if schema_id != client.schema_info['id']:
                raise SchemaError(
                    f"Object{f' {object_id}' if object_id else ''} belongs to schema {schema_id}, "
                    f"not to {client.schema_info['name']} ({client.schema_info['id']})"
                )
