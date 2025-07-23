# models
"""Values for common strings used to describe model vendors.

Here is a template on how to add a new vendor. Follow the examples below along with
the template to add support for that vendor. Currently, only vendors that are supported
by Langchain are supported here.

These enums are closely coupled with the model_factory (see mod/model_factory.py) and help
provide context needed to instantiate model interfaces.

Model Enum Template
 <VENDOR NAME>_MODELS = [
        {VendorLookup.ModelIDKey.value: "model id", VendorLookup.ModelDisplayNameKey.value: "model display name"},
]
class <Vendor Name>(Enum):
    APIKey = "The API key environment variable name (e.g. OPENAI_API_KEY)"
    VendorID = "The vendor ID used to identify the vendor in lookups. Use lowercase (e.g. openai)"
    DisplayName = "The vendor display name for the UI"
    LangchainPackage = "The name of the package as it is installed (e.g. langchain-openai)"
    LangchainModuleName = "The name of the module used when importing (e.g. langchain_openai or langchain_openai.models)"
    LangchainInterfaceClass = "The name of the Chat interface class from Langchain (e.g. ChatOpenAI)"
    APIKeyNotFoundError = "A message to display when the APIKeyNotFound error occurs"
    RateLimitError = "A message to display when the RateLimitError error occurs"
    AuthenticationError = "A message to display when the AuthenticationError error occurs"
    APIError = "Handler for generic API error. You must use the following format: '<Vendor Name> API error: {error_msg}'"
    TimeoutError = "A message to display when the TimeoutError error occurs"
    # The format for the card is consistent, just add the models list like below:
    Card = {
        VendorLookup.VendorIDKey.value: VendorID,
        VendorLookup.VendorDisplayNameKey.value: DisplayName,
        VendorLookup.ModelsKey.value: <VENDOR NAME>_MODELS
    }
    # Settings keys (Map the settings keys from your vendors Chat Interface)
    # Check the Langchain documentation for your chat interface to do the mapping
    ModelNameKey = "The field name to enter the model name (e.g. `model_name` or `model`)"
    ModelAPIKey = "The field name for the API key (e.g. `openai_api_key`)"
    TemperatureKey = "The field name for temperature (e.g. `temperature`)"
    MaxTokensKey = "The field name for maximum token output (e.g. `max_tokens`)"
    TopPKey = "The field name for Top P results (e.g. `top_p`)"
    RequestTimeoutKey = "The field name for the timeout request limit setting (e.g. `request_timeout` or `default_request_timeout`)"

To make sure the model_factory sees a vendor it must be added to the `MODEL_VENDORS` list at the end of this file.  
"""
from enum import Enum

# -- Vendor Card Template ----------------------------------
class VendorLookup(Enum):
    VendorIDKey = "id"
    ModelIDKey = "id"
    VendorDisplayNameKey = "name"
    ModelDisplayNameKey = "name"
    ModelsKey = "models"

# -- OpenAI ------------------------------------------------
## List of supported models 
OPENAI_MODELS = [
        {VendorLookup.ModelIDKey.value: "gpt-4.1-mini", VendorLookup.ModelDisplayNameKey.value: "GPT-4.1 Mini"},
        {VendorLookup.ModelIDKey.value: "gpt-4.1-nano", VendorLookup.ModelDisplayNameKey.value: "GPT-4.1 Nano"},
        {VendorLookup.ModelIDKey.value: "gpt-4.1", VendorLookup.ModelDisplayNameKey.value: "GPT-4.1"},
]

class OpenAI(Enum):
    APIKey = "OPENAI_API_KEY"
    VendorID = "openai"
    DisplayName = "OpenAI"
    LangchainPackage = "langchain-openai" # The name of the package as it is installed
    LangchainModuleName = "langchain_openai"
    LangchainInterfaceClass = "ChatOpenAI" # The name of the Chat interface class from Langchain
    APIKeyNotFoundError = "OpenAI API key not found. Please set OPENAI_API_KEY environment variable."
    RateLimitError = "OpenAI rate limit exceeded. Please try again later."
    AuthenticationError = "OpenAI API key is invalid or expired."
    APIError = "OpenAI API error: {error_msg}"
    TimeoutError = "OpenAI API request timed out. Please try again."
    Card = {
        VendorLookup.VendorIDKey.value: VendorID,
        VendorLookup.VendorDisplayNameKey.value: DisplayName,
        VendorLookup.ModelsKey.value: OPENAI_MODELS
    }
    # Settings Keys (https://python.langchain.com/api_reference/openai/chat_models/langchain_openai.chat_models.base.ChatOpenAI.html)
    ModelNameKey = "model_name"
    ModelAPIKey = "openai_api_key"
    TemperatureKey = "temperature"
    MaxTokensKey = "max_tokens"
    TopPKey = "top_p"
    RequestTimeoutKey = "request_timeout"

# -- Anthropic ------------------------------------------------
ANTHROPIC_MODELS = [
    {VendorLookup.ModelIDKey.value: "claude-3-opus-latest", VendorLookup.ModelDisplayNameKey.value: "Claude 3 Opus"},
    {VendorLookup.ModelIDKey.value: "claude-3-7-sonnet-latest", VendorLookup.ModelDisplayNameKey.value: "Claude 3.7 Sonnet"},
    {VendorLookup.ModelIDKey.value: "claude-3-5-haiku-latest", VendorLookup.ModelDisplayNameKey.value: "Claude 3.5 Haiku"},
]

class Anthropic(Enum):
    APIKey = "ANTHROPIC_API_KEY"
    VendorID = "anthropic"
    DisplayName = "Anthropic"
    LangchainPackage = "langchain-anthropic"
    LangchainModuleName = "langchain_anthropic"
    LangchainInterfaceClass = "ChatAnthropic"
    APIKeyNotFoundError = "Anthropic API key not found. Please set OPENAI_API_KEY environment variable."
    RateLimitError = "Anthropic rate limit exceeded. Please try again later."
    AuthenticationError = "Anthropic API key is invalid or expired."
    APIError = "Anthropic API error: {error_msg}"
    TimeoutError = "Anthropic API request timed out. Please try again."
    Card = {
        VendorLookup.VendorIDKey.value: VendorID,
        VendorLookup.VendorDisplayNameKey.value: DisplayName,
        VendorLookup.ModelsKey.value: ANTHROPIC_MODELS
    }
    # Settings Keys (https://python.langchain.com/api_reference/anthropic/chat_models/langchain_anthropic.chat_models.ChatAnthropic.html)
    ModelNameKey = "model"
    ModelAPIKey = "anthropic_api_key"
    TemperatureKey = "temperature"
    MaxTokensKey = "max_tokens"
    TopPKey = "top_p"
    RequestTimeoutKey = "default_request_timeout"

# -- Google ------------------------------------------------
GOOGLE_MODELS = [
    {VendorLookup.ModelIDKey.value: "gemini-2.5-flash", VendorLookup.ModelDisplayNameKey.value: "Gemini 2.5 Flash"}
]
class Google(Enum):
    APIKey = "GEMINI_API_KEY"
    VendorID = "google"
    DisplayName = "Google"
    LangchainPackage = "langchain-google-genai"
    LangchainModuleName = "langchain_google_genai"
    LangchainInterfaceClass = "ChatGoogleGenerativeAI"
    APIKeyNotFoundError = "Gemini API key not found. Please set OPENAI_API_KEY environment variable."
    RateLimitError = "Gemini rate limit exceeded. Please try again later."
    AuthenticationError = "Gemini API key is invalid or expired."
    APIError = "Gemini API error: {error_msg}"
    TimeoutError = "Gemini API request timed out. Please try again."
    Card = {
        VendorLookup.VendorIDKey.value: VendorID,
        VendorLookup.VendorDisplayNameKey.value: DisplayName,
        VendorLookup.ModelsKey.value: GOOGLE_MODELS
    }
    # Settings Keys (https://python.langchain.com/api_reference/google_genai/chat_models/langchain_google_genai.chat_models.ChatGoogleGenerativeAI.html)
    ModelNameKey = "model"
    ModelAPIKey = "google_api_key"
    TemperatureKey = "temperature"
    MaxTokensKey = "max_output_tokens"
    TopPKey = "top_p"
    RequestTimeoutKey = "timeout"

OLLAMA_MODELS = [
    {VendorLookup.ModelIDKey.value: "llama3.1", VendorLookup.ModelDisplayNameKey.value: "Llama 3.1"}
]
class Ollama(Enum):
    APIKey = ""
    VendorID = "ollama"
    DisplayName = "Ollama"
    LangchainPackage = "langchain-ollama"
    LangchainModuleName = "langchain_ollama"
    LangchainInterfaceClass = "ChatOllama"
    APIKeyNotFoundError = "Ollama API key not found. Please set OPENAI_API_KEY environment variable."
    RateLimitError = "Ollama rate limit exceeded. Please try again later."
    AuthenticationError = "Ollama API key is invalid or expired."
    APIError = "Ollama API error: {error_msg}"
    TimeoutError = "Ollama API request timed out. Please try again."
    Card = {
        VendorLookup.VendorIDKey.value: VendorID,
        VendorLookup.VendorDisplayNameKey.value: DisplayName,
        VendorLookup.ModelsKey.value: OLLAMA_MODELS
    }
    # Settings Keys (https://python.langchain.com/api_reference/google_genai/chat_models/langchain_google_genai.chat_models.ChatGoogleGenerativeAI.html)
    ModelNameKey = "model"
    ModelAPIKey = ""
    TemperatureKey = "temperature"
    MaxTokensKey = ""
    TopPKey = "top_p"
    RequestTimeoutKey = "timeout"

MODEL_VENDORS = [OpenAI, Anthropic, Google, Ollama]

AVAILABLE_VENDORS = [
    vendor.Card.value for vendor in MODEL_VENDORS
]