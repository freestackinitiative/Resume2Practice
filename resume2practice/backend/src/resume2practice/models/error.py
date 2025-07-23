from enum import Enum

class ModelInitializationError(Exception):
    pass

class RateLimitError(Exception):
     pass

class APIKeyError(Exception):
     pass

def handle_vendor_exception(e: Exception, vendor: Enum) -> Exception:
    """
    Maps vendor-specific exceptions to our custom exceptions.
    
    Args:
        e: The original exception
        vendor: The vendor name (e.g., 'openai', 'anthropic')
        
    Returns:
        An appropriate LLMChatError subclass
    """
    error_class = e.__class__.__name__
    error_msg = str(e)
    
    # Add details for logging
    details = {
        'original_exception': error_class,
        'vendor': vendor.VendorID.value
    }
    if 'RateLimitError' in error_class:
            return RateLimitError(vendor.RateLimitError.value, details)
    elif 'AuthenticationError' in error_class:
        return APIKeyError(vendor.AuthenticationError.value, details)
    elif 'APIError' in error_class:
        return ModelInitializationError(vendor.APIError.value.format(error_msg=error_msg), details)
    elif 'Timeout' in error_class:
        return ModelInitializationError(vendor.TimeoutError.value, details)
    
    # Default case
    return ModelInitializationError(f"{vendor.DisplayName.value} error: {error_msg}", details)