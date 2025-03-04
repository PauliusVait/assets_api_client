"""Centralized error handling for the CLI."""
import traceback
from typing import Optional
from src.jira_core.exceptions import (
    AssetNotFoundError, 
    SchemaError,
    InvalidQueryError, 
    ApiError,
    ValidationError
)

class ErrorHandler:
    """Centralized error handling with consistent messaging."""
    
    ERROR_MESSAGES = {
        AssetNotFoundError: "Asset not found",
        SchemaError: "Schema error",
        InvalidQueryError: "Invalid query",
        ApiError: "API error",
        ValidationError: "Validation error"
    }
    
    SUGGESTIONS = {
        SchemaError: "Try using --refresh-cache if object types were renamed",
        ApiError: "Check your API credentials and network connection",
        InvalidQueryError: "Verify your query syntax and object type names",
        ValidationError: "Check the required fields and data formats"
    }
    
    @classmethod
    def handle_error(cls, logger, exception: Exception, debug: bool = False, 
                    context: Optional[str] = None) -> bool:
        """Handle exceptions with consistent messaging"""
        error_type = type(exception)
        base_message = cls.ERROR_MESSAGES.get(error_type, "Error occurred")
        context_msg = f" while {context}" if context else ""
        
        # Format the error message
        error_message = f"{base_message}{context_msg}: {str(exception)}"
        logger.error(error_message)
        
        # Show debug information if requested
        if debug:
            logger.debug(f"Error details:\n{traceback.format_exc()}")
        
        # Show suggestion if available
        if suggestion := cls.SUGGESTIONS.get(error_type):
            logger.info(f"Suggestion: {suggestion}")
            
        return False
