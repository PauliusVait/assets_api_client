"""
Response validation module for Jira Assets API.

Provides centralized validation and error handling for API responses.
"""
from typing import Dict, Any, Optional
from ..exceptions import ApiError, ValidationError

class ResponseValidator:
    """Validates API responses and extracts error information."""
    
    @staticmethod
    def validate_response(response: Dict[str, Any], logger=None) -> None:
        """
        Validate API response and raise appropriate exceptions.
        
        Args:
            response: API response dictionary
            logger: Optional logger instance
            
        Raises:
            ValidationError: If response contains validation errors
            ApiError: For other API errors
        """
        # Check for error messages array
        error_messages = response.get('errorMessages', [])
        if error_messages:
            if logger:
                logger.error(f"API returned error messages: {error_messages}")
            raise ApiError('; '.join(error_messages))
            
        # Check for errors dictionary
        errors = response.get('errors', {})
        if errors:
            validation_errors = []
            
            for field_key, error_msg in errors.items():
                # Handle attribute validation errors (format: rlabs-insight-attribute-XXXX)
                if 'rlabs-insight-attribute' in field_key:
                    attr_id = field_key.split('-')[-1]
                    # Try to get a friendly name for the attribute
                    attr_name = ResponseValidator._get_attribute_name(attr_id, error_msg)
                    error_text = ResponseValidator._format_validation_error(error_msg, attr_name)
                    validation_errors.append(error_text)
                else:
                    # Handle other validation errors
                    validation_errors.append(str(error_msg))
            
            error_message = '; '.join(validation_errors)
            if logger:
                logger.error(f"Validation errors: {error_message}")
            raise ValidationError(error_message)
    
    @staticmethod
    def _get_attribute_name(attr_id: str, error_msg: str) -> str:
        """Extract attribute name from error message."""
        # Try to find attribute name in quotes from error message
        import re
        match = re.search(r"'([^']+)'", str(error_msg))
        if match:
            return match.group(1)
        return f"attribute {attr_id}"
    
    @staticmethod
    def _format_validation_error(error_msg: str, attr_name: str) -> str:
        """Format validation error message to be user-friendly."""
        msg = str(error_msg)
        
        # Common error patterns
        if "has to be unique" in msg.lower():
            return f"The {attr_name} you provided is already in use. Please use a different value."
        elif "is required" in msg.lower():
            return f"The {attr_name} is required but was not provided."
        elif "invalid" in msg.lower():
            return f"The value provided for {attr_name} is invalid."
        
        # Default to original message with attribute name
        return f"Error with {attr_name}: {msg}"
            
    @staticmethod
    def extract_error_details(error_dict: Dict[str, Any]) -> str:
        """
        Extract human-readable error details from error dictionary.
        
        Args:
            error_dict: Error dictionary from API response
            
        Returns:
            str: Formatted error message
        """
        if 'rlabs-insight-attribute' in str(error_dict):
            # Handle attribute validation errors
            for key, msg in error_dict.items():
                if 'attribute' in key.lower() and isinstance(msg, str):
                    return msg
        return str(error_dict)
