"""
Workspace discovery functionality for Jira Assets API.

This module provides functionality to automatically discover
the workspace ID from Jira Service Management.
"""
import requests
from .base_handler import BaseHandler

def discover_workspace(client):
    """
    Discover the workspace ID from Jira Service Management.
    
    Args:
        client: AssetsClient instance with site name configured
        
    Returns:
        str: Workspace ID if found, None otherwise
    """
    if not client.site_name.endswith('atlassian.net'):
        client.logger.debug(f"Adding atlassian.net suffix to site name: {client.site_name}")
        url = f"https://{client.site_name}.atlassian.net/rest/servicedeskapi/assets/workspace"
    else:
        url = f"https://{client.site_name}/rest/servicedeskapi/assets/workspace"
    
    workspace_data = BaseHandler.make_request(
        client=client,
        method='GET',
        endpoint=url,
        use_base_url=False
    )
    
    if 'values' in workspace_data and workspace_data['values']:
        return workspace_data['values'][0].get('workspaceId')
    return None
