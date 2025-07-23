# factory.py
"""
Factory module for creating LLM instances based on vendor and model.
"""

import os
import importlib
import logging
from enum import Enum
from typing import Dict, Any, Optional

# Import error handlers
from resume2practice.models.error import ModelInitializationError, APIKeyError, handle_vendor_exception
from resume2practice.models import MODEL_VENDORS, VendorLookup
# Configure logging
logger = logging.getLogger(__name__)

class ModelFactory:
    """Factory class for creating language model instances."""
    
    def __init__(self):
        """Initialize the model factory."""
        # Get vendors and create lookup
        self._vendor_lookup = {
            vendor.VendorID.value: vendor 
            for vendor in MODEL_VENDORS
        }
        
        # Cache of instantiated models to avoid recreating them
        self._model_cache = {}

    def get_model(self, 
                 vendor: str, 
                 model_id: str, 
                 settings: Optional[Dict[str, Any]] = None) -> Any:
        """
        Get a language model instance.
        
        Args:
            vendor: The vendor name (e.g., 'openai', 'anthropic')
            model_id: The model identifier
            settings: Dictionary of model settings
            
        Returns:
            A language model instance
            
        Raises:
            ModelInitializationError: If model initialization fails
            APIKeyError: If API key is missing or invalid
        """
        settings = settings or {}
        
        # Normalize vendor name
        vendor_name = vendor.lower()
        # Check if vendor is supported
        if vendor_name not in self._vendor_lookup:
            raise ModelInitializationError(f"Unsupported vendor: {vendor_name}")
        model_vendor = self._vendor_lookup[vendor_name]
        # Check if model is supported
        if not any([
            True for model in model_vendor.Card.value[VendorLookup.ModelsKey.value]
            if model[VendorLookup.ModelIDKey.value] == model_id
        ]):
            raise ModelInitializationError(f"Unsupported model: {model_id}")
        # Generate a cache key
        cache_key = f"{vendor_name}:{model_id}:{hash(frozenset(settings.items()))}"
        
        # Check cache first
        if cache_key in self._model_cache:
            logger.debug(f"Using cached model instance for {vendor_name}:{model_id}")
            return self._model_cache[cache_key]
        
        # Create a new model instance
        try:
            logger.info(f"Creating new model instance for {vendor}:{model_id}")
            # model = self._vendor_handlers[vendor](model_id, settings)
            model = self._create_model_class(vendor=model_vendor, model_id=model_id, settings=settings)
            
            # Cache the model
            self._model_cache[cache_key] = model
            
            return model
        except Exception as e:
            # Handle vendor-specific exceptions
            return self._handle_vendor_error(e, model_vendor)
    
    def _create_model_class(self, vendor: Enum, model_id: str, settings: Dict[str, Any]) -> Any:
        """Creates an instance of a LangChain ChatModel class
        
        Args:
            model_id: The model identifier
            settings: Dictionary of model settings
            
        Returns:
            A Langchain Chat model instance
        """
        try:
            module = importlib.import_module(vendor.LangchainModuleName.value)
            chat_model = getattr(module, vendor.LangchainInterfaceClass.value)
        except (AttributeError, ImportError, ModuleNotFoundError) as ae:
            raise ModelInitializationError(f"Error while importing {vendor.LangchainPackage.value}: {str(ae)}")
        
        # Get API key
        api_key = os.getenv(vendor.APIKey.value)
        if not api_key:
            raise APIKeyError(vendor.APIKeyNotFoundError.value)
        
         # Extract settings with validation
        temperature = float(settings.get('temperature', 0.7))
        temperature = max(0, min(1, temperature))  # Clamp to [0,1]
        
        max_tokens = int(settings.get('contextLength', 4000))
        max_tokens = max(1, min(32000, max_tokens))  # Reasonable limits
        
        top_p = float(settings.get('topP', 1.0))
        top_p = max(0, min(1, top_p))
        
        model_config = {
            vendor.ModelNameKey.value: model_id,
            # vendor.ModelAPIKey.value: api_key,
            vendor.TemperatureKey.value: temperature,
            # vendor.MaxTokensKey.value: max_tokens,
            vendor.TopPKey.value: top_p,
            vendor.RequestTimeoutKey.value: 60
        }
        if vendor.ModelAPIKey.value != "":
            model_config[vendor.ModelAPIKey.value] = api_key
        if vendor.MaxTokensKey.value != "":
            model_config[vendor.MaxTokensKey.value] = max_tokens
        # Create model
        return chat_model(**model_config)

    def _handle_vendor_error(self, error: Exception, vendor: Enum) -> None:
        """
        Handle vendor-specific errors.
        
        Args:
            error: The exception that occurred
            vendor: The vendor name
            
        Raises:
            ModelInitializationError: With appropriate message
        """
        logger.error(f"Error initializing {vendor.DisplayName.value} model: {str(error)}")
        raise handle_vendor_exception(error, vendor)
    
    def clear_cache(self) -> None:
        """Clear the model cache."""
        self._model_cache.clear()
    
    def get_supported_vendors(self) -> list:
        """Get list of supported vendors."""
        return list(self._vendor_lookup.keys())

# Singleton instance
model_factory = ModelFactory()