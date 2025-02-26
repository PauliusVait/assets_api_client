"""
Error handling utilities for the Assets CLI.

This module provides centralized error handling functionality
for standardized error messaging and suggestions across the CLI.
"""
import json
import sys
import traceback
from src.jira_core.exceptions import (
    AssetNotFoundError, 
    SchemaError, 
    InvalidQueryError,
    ApiError
)

class ErrorHandler:
    """Centralized error handling for CLI commands"""
    
    @staticmethod
    def handle_error(logger, exception, debug=False, context=None):
        """
        Handle exceptions in a standardized way
        
        Args:
            logger: Logger instance
            exception: The exception that was raised
            debug: Whether to include debug information
            context: Additional context about the operation (e.g. "updating asset 12345")
            
        Returns:
            False (to indicate operation failure)
        """
        # Get error type-specific message or fallback to generic message
        error_message = ErrorHandler._get_error_message(exception, context)
        
        # Log the error
        logger.error(error_message)
        
        # If in debug mode, log the full traceback
        if debug:
            error_details = traceback.format_exc()
            logger.debug(f"Error details:\n{error_details}")
            
        # Include suggestions for specific errors
        ErrorHandler._provide_suggestions(logger, exception)
        
        # Return False to indicate operation failure
        return False
    
    @staticmethod
    def _get_error_message(exception, context=None):
        """
        Generate appropriate error message based on exception type.
        
        Args:
            exception: The exception to format
            context: Optional context about the operation
            
        Returns:
            str: Formatted error message
        """
        context_msg = f" while {context}" if context else ""
        
        if isinstance(exception, AssetNotFoundError):
            return f"Asset not found: {str(exception)}"
        elif isinstance(exception, SchemaError):
            return f"Schema error{context_msg}: {str(exception)}"
        elif isinstance(exception, InvalidQueryError):
            return f"Invalid query{context_msg}: {str(exception)}"
        elif isinstance(exception, ApiError):
            return f"API error{context_msg}: {str(exception)}"
        elif isinstance(exception, json.JSONDecodeError):
            return f"Invalid JSON format{context_msg}: {str(exception)}"
        elif isinstance(exception, ValueError):
            return f"Value error{context_msg}: {str(exception)}"
        else:
            return f"Error occurred{context_msg}: {str(exception)}"
    
    @staticmethod
    def _provide_suggestions(logger, exception):
        """
        Provide helpful suggestions based on the error type.
        
        Args:
            logger: Logger to use for output
            exception: Exception that was raised
        """
        if isinstance(exception, SchemaError):
            logger.info("If object types have been renamed, try using --refresh-cache option")
        elif isinstance(exception, ApiError):
            logger.info("Check your API credentials and network connection")
        elif isinstance(exception, InvalidQueryError):
            logger.info("Verify your query syntax and object type names")
