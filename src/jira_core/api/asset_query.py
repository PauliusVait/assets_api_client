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

def get_objects_aql(client, query: str, start_at: int = 0, max_results: int = 50, include_attributes: bool = True) -> List[Asset]:
    """
    Query assets using Atlassian Query Language (AQL).
    
    Args:
        client: AssetsClient instance
        query: AQL query string
        start_at: Pagination start index (default: 0)
        max_results: Maximum number of results to return (default: 50)
        include_attributes: Whether to include asset attributes in results (default: True)
    
    Returns:
        List of Asset objects matching the query
    
    Raises:
        InvalidQueryError: If the query is empty or malformed
        SchemaError: If referenced object types don't exist in the schema
    """
    # Basic query validation
    if not query.strip():
        raise InvalidQueryError("Query cannot be empty")
        
    # Extract all objectType values from query
    object_type_matches = re.findall(r'objectType\s*=\s*["\']([^"\']*)["\']', query)
    if not object_type_matches:
        raise InvalidQueryError(
            "Query must include at least one objectType condition with a quoted value.\n"
            "Example: objectType = \"Hardware\" OR objectType = \"Software\""
        )
    
    # Validate all object types exist in schema
    invalid_types = [t for t in object_type_matches if t not in client.schema_info['object_types']]
    if invalid_types:
        available_types = "\n".join(sorted(client.schema_info['object_types'].keys()))
        raise SchemaError(
            f"Object type(s) {', '.join(invalid_types)} do not exist in schema {client.schema_info['name']}.\n"
            f"Available types:\n{available_types}"
        )

    full_query = f"({query}) AND objectSchemaId = {client.schema_info['id']}"
    client.logger.debug(f"Full AQL query: {full_query}")

    response_data = BaseHandler.make_request(
        client=client,
        method='POST',
        endpoint='object/aql',
        params={'startAt': start_at, 'maxResults': max_results},
        json={
            "qlQuery": full_query,
            "serviceInfo": {
                "includeAttributes": include_attributes,
                "includeAttributeValues": include_attributes,
                "includeTypeAttributes": True,
                "includeAttributeNames": True
            }
        },
        include_type_attributes=True
    )
    
    assets = [Asset(obj, Asset._mapper.build_definitions(response_data)) 
              for obj in response_data.get('values', [])]
    return assets