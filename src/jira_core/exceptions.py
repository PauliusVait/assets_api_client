"""
Custom exceptions for the Jira Assets API client.

This module defines various exception classes that represent different
error conditions that can occur when interacting with the Jira Assets API.
"""

class AssetsError(Exception):
    """Base exception for all Assets API errors."""
    pass

class AssetNotFoundError(AssetsError):
    """
    Exception raised when a requested asset cannot be found.
    
    This typically occurs when an asset ID doesn't exist or the user
    doesn't have access to the asset.
    """
    pass

class SchemaError(AssetsError):
    """
    Exception raised for schema-related errors.
    
    This occurs when there are issues with object types, attribute definitions,
    or other schema-related problems.
    """
    pass

class InvalidQueryError(AssetsError):
    """
    Exception raised when an AQL query is invalid.
    
    This occurs when the syntax of an Asset Query Language (AQL) query
    is incorrect or references invalid fields.
    """
    pass

class InvalidUpdateError(AssetsError):
    """
    Exception raised when an asset update request is invalid.
    
    This occurs when the update data format is incorrect or contains
    invalid attribute values.
    """
    pass

class EmptyResultError(AssetsError):
    """
    Exception raised when a query returns no results.
    
    This occurs when a valid query executes successfully but doesn't
    match any assets.
    """
    pass

class ApiError(Exception):
    """
    Exception raised for API-related errors.
    
    This represents errors related to the API itself, such as authentication
    failures, rate limiting, or server errors.
    
    Args:
        message (str): The error message
        status_code (int, optional): The HTTP status code
        response (object, optional): The raw API response
    """
    
    def __init__(self, message, status_code=None, response=None):
        """
        Initialize a new ApiError with optional status code and response.
        
        Args:
            message (str): The error message
            status_code (int, optional): The HTTP status code
            response (object, optional): The raw API response
        """
        self.status_code = status_code
        self.response = response
        super().__init__(message)
