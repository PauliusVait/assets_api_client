"""
Base request handler for Jira Assets API.

This module provides core functionality for making API requests
to the Jira Assets API, handling errors, and validating responses.
"""
import requests
from typing import Optional, Dict, Any, List
import json
from ..exceptions import AssetNotFoundError, AssetsError, SchemaError, InvalidQueryError, ApiError, ValidationError
from .response_validator import ResponseValidator

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
    def handle_response(response, logger=None):
        """Process API response and handle any errors."""
        try:
            # Get response body
            response_data = response.json()
            
            # Skip validation for array responses
            if isinstance(response_data, list):
                return response_data
                
            # Validate dict responses
            ResponseValidator.validate_response(response_data, logger)
            
            return response_data
            
        except json.JSONDecodeError:
            error_msg = f"Invalid JSON response from API (status {response.status_code})"
            if logger:
                logger.error(error_msg)
            raise ApiError(error_msg)
        except ValidationError as e:
            # Pass through validation errors
            raise
        except Exception as e:
            error_msg = f"Error processing API response: {str(e)}"
            if logger:
                logger.error(error_msg)
            raise ApiError(error_msg)
    
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
            # Start with default parameters
            if not params or 'includeAttributes' not in params:
                request_params['includeAttributes'] = 'true'
            if not params or 'attributeNames' not in params:
                request_params['attributeNames'] = '*'
            
            # Handle expand parameters
            expand_values = set()
            
            # Start with default expands
            default_expands = ['attributes', 'objectType', 'attributeValues']
            for value in default_expands:
                expand_values.add(value)
            
            # Add objectTypeAttributes if requested
            if include_type_attributes or ('objecttype/' in endpoint and 'objectTypeAttributes' not in expand_values):
                expand_values.add('objectTypeAttributes')
                
            # If params has an 'expand' parameter, add those values too
            if params and 'expand' in params:
                for value in params['expand'].split(','):
                    if value:
                        expand_values.add(value)
                        
            # Set the final combined expand parameter
            request_params['expand'] = ','.join(expand_values)
            
            # Update with any remaining parameters
            if params:
                for key, value in params.items():
                    if key != 'expand':  # We've already handled expand
                        request_params[key] = value
        
        # Debug parameters
        client.logger.debug(f"Request parameters: {request_params}")
        
        headers = {"Accept": "application/json", "Authorization": f"Basic {client.basic_auth}"}
        if json:
            client.logger.debug(f"Request payload: {json}")
            
        if method.upper() in ['POST', 'PUT']:
            headers["Content-Type"] = "application/json"

        try:
            response = requests.request(
                method=method, url=url, headers=headers,
                params=request_params, json=json, verify=client.verify
            )
            
            client.logger.debug(f"Response status: {response.status_code}")
            
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    # Try validation first
                    try:
                        ResponseValidator.validate_response(error_data, client.logger)
                    except ValidationError as ve:
                        raise
                    except:
                        # Fall back to generic error handling
                        error_msg = ResponseValidator.extract_error_details(error_data)
                        raise AssetsError(error_msg)
                        
                except ValidationError:
                    raise
                except Exception as e:
                    raise AssetsError(f"Bad request: {str(e)}")
            
            # For successful responses, log more details for debugging
            if response.status_code >= 200 and response.status_code < 300:
                try:
                    # Try to peek at response content for debugging
                    response_data = response.json()
                    if isinstance(response_data, dict):
                        keys = list(response_data.keys())
                        client.logger.debug(f"Response contains these keys: {keys}")
                        
                        # If this is an object type response, log specific information
                        if 'id' in response_data:
                            client.logger.debug(f"Object ID: {response_data['id']}")
                        if 'name' in response_data:
                            client.logger.debug(f"Object name: {response_data['name']}")
                        if 'attributes' in response_data:
                            client.logger.debug(f"Found {len(response_data['attributes'])} attributes in response")
                        if 'objectTypeAttributes' in response_data:
                            client.logger.debug(f"Found {len(response_data['objectTypeAttributes'])} objectTypeAttributes in response")
                    
                except Exception:
                    # Don't fail if we can't parse the JSON for debugging
                    pass
            
            # For debugging errors
            if response.status_code >= 400:
                client.logger.debug(f"Response headers: {response.headers}")
                try:
                    error_data = response.json()
                    client.logger.debug(f"Response body: {error_data}")
                except Exception:
                    client.logger.debug(f"Response raw text: {response.text}")
            
            if response.status_code == 404:
                if 'object/' in endpoint:
                    object_id = endpoint.split('/')[-1]
                    raise AssetNotFoundError(
                        f"Asset with ID '{object_id}' was not found. "
                        "Please verify the ID is correct."
                    )
                raise AssetNotFoundError("Requested resource was not found")
                
            if response.status_code == 400:
                try:
                    error_data = response.json()
                    error_msg = error_data.get('errorMessage', '')
                    if not error_msg:
                        if 'errors' in error_data:
                            # Handle array of errors
                            error_msgs = []
                            for err in error_data['errors']:
                                if isinstance(err, dict):
                                    error_msgs.append(err.get('message', str(err)))
                                else:
                                    error_msgs.append(str(err))
                            error_msg = " | ".join(error_msgs)
                        elif 'message' in error_data:
                            error_msg = error_data['message']
                        else:
                            error_msg = f"Bad request: {error_data}"
                except Exception:
                    # If we can't parse the JSON, use the raw text
                    error_msg = f"Bad request: {response.text}"
                    
                client.logger.error(f"API error: {error_msg}")
                
                if any(x in error_msg.lower() for x in ['invalid', 'syntax', 'malformed']):
                    raise InvalidQueryError(f"Invalid query: {error_msg}")
                elif 'schema' in error_msg.lower():
                    raise SchemaError(error_msg)
                else:
                    raise AssetsError(error_msg)
                    
            response.raise_for_status()
            data = BaseHandler.handle_response(response, client.logger)
            
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
                    elif 'message' in error_data:
                        error_msg = error_data['message']
                    elif 'errors' in error_data:
                        error_msg = str(error_data['errors'])
                    else:
                        error_msg = str(error_data)
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
