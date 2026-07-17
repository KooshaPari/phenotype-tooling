"""
LLM provider services for OpenAI and OpenRouter.
"""

import os
import time
import uuid
import json
import requests
from typing import List, Dict, Any, Optional, Union, Tuple, Iterator, Generator

import openai
from openai import OpenAI
from dotenv import load_dotenv

from .models import ModelInfo

# Load environment variables
load_dotenv()

# API Keys
OPENAI_API_KEY = REDACTED_AIRLOCK"OPENAI_API_KEY")
OPENROUTER_API_KEY = REDACTED_AIRLOCK"OPENROUTER_API_KEY")

# Configure OpenAI client
openai_client = None
if OPENAI_API_KEY:
    REDACTED_AIRLOCK = OpenAI(api_key=REDACTED_AIRLOCK
else:
    print("Warning: OPENAI_API_KEY not found. OpenAI models will not be available.")


def list_openai_models() -> List[ModelInfo]:
    """
    List available models from OpenAI.

    Returns:
        List of ModelInfo objects for OpenAI models.
    """
    if not openai_client:
        return []

    try:
        models = openai_client.models.list()
        # Filter to include only relevant models (e.g., GPT models)
        return [
            ModelInfo(
                # Add provider prefix to model ID for consistent identification
                id=f"openai/{model.id}",
                provider="openai",
                owned_by="openai",
                # Store the original ID without prefix for direct API calls
                original_id=model.id,
            )
            for model in models.data
            if "gpt" in model.id.lower()
        ]
    except Exception as e:
        print(f"Error listing OpenAI models: {e}")
        return []


def list_openrouter_models() -> List[ModelInfo]:
    """
    List available models from OpenRouter.

    Returns:
        List of ModelInfo objects for OpenRouter models.
    """
    if not OPENROUTER_API_KEY:
        REDACTED_AIRLOCK
            "Warning: OPENROUTER_API_KEY not found. OpenRouter models will not be available."
        )
        return []

    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": REDACTED_AIRLOCK"Bearer {OPENROUTER_API_KEY}"},
        )
        response.raise_for_status()
        models_data = response.json().get("data", [])

        # Add provider prefix to model IDs for consistent identification
        return [
            ModelInfo(
                # Add provider prefix to model ID for consistent identification
                id=f"openrouter/{model.get('id')}",
                provider="openrouter",
                source="openrouter",
                owned_by=model.get("owned_by", "openrouter"),
                # Store the original ID without prefix for direct API calls
                original_id=model.get("id"),
            )
            for model in models_data
        ]
    except requests.exceptions.RequestException as e:
        print(f"Error listing OpenRouter models: {e}")
        return []
    except Exception as e:
        print(f"An unexpected error occurred while listing OpenRouter models: {e}")
        return []


def list_all_models() -> List[ModelInfo]:
    """
    List all available models from configured providers.

    Returns:
        List of ModelInfo objects from all providers.
    """
    all_models = []
    all_models.extend(list_openai_models())
    all_models.extend(list_openrouter_models())
    return sorted(all_models, key=lambda x: x.id)


def extract_model_id(model: str, provider: str) -> str:
    """
    Extract the actual model ID from a potentially prefixed model ID.

    Args:
        model: The model ID, which may include a provider prefix.
        provider: The determined provider for this model.

    Returns:
        The model ID without the provider prefix, suitable for API calls.
    """
    print(f"DEBUG: Extracting model ID from '{model}' for provider '{provider}'")

    # If the model has a provider prefix, extract the actual model ID
    if "/" in model:
        prefix, actual_id = model.split("/", 1)
        print(f"DEBUG: Split model into prefix='{prefix}' and actual_id='{actual_id}'")

        # For OpenAI, we always want to remove the prefix
        if provider == "openai":
            print(f"DEBUG: OpenAI provider - returning actual_id: '{actual_id}'")
            return actual_id

        # For OpenRouter, we want to keep the full ID if it's not an openrouter prefix
        # This handles cases like "anthropic/claude-3" correctly
        if provider == "openrouter" and prefix.lower() == "openrouter":
            print(
                f"DEBUG: OpenRouter provider with 'openrouter' prefix - returning actual_id: '{actual_id}'"
            )
            return actual_id

        # For other prefixes with OpenRouter, keep the full model string
        # This handles cases like "anthropic/claude-3" correctly
        if provider == "openrouter":
            print(
                f"DEBUG: OpenRouter provider with non-openrouter prefix - returning full model: '{model}'"
            )
            return model

    # If no prefix, return the model as is
    print(f"DEBUG: No prefix found - returning model as is: '{model}'")
    return model


def get_chat_completion(
    model: str,
    messages: List[Dict[str, Any]],
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    use_prompt_cache: bool = True,  # Enable prompt caching by default
    request_id: Optional[str] = None,
    force_cache_miss: bool = False,
) -> Union[Dict[str, Any], Any]:
    """
    Get a chat completion from the appropriate provider based on the model.

    Args:
        model: The model to use.
        messages: The messages to send to the model.
        temperature: The temperature to use.
        max_tokens: The maximum number of tokens to generate.
        stream: Whether to stream the response.
        tool_choice: Optional tool choice parameter for OpenAI models.
        tools: Optional tools to provide to the model.
        use_prompt_cache: Whether to use prompt caching (for supported models).
        request_id: Optional request ID for tracking and monitoring.
        force_cache_miss: Whether to force a cache miss even if caching is enabled.

    Returns:
        The chat completion response.
    """
    # Determine the provider based on the model
    provider = determine_model_provider(model)

    # Log the model and provider for debugging
    print(f"Using provider '{provider}' for model '{model}'")

    # Extract the actual model ID for API calls
    model_id = extract_model_id(model, provider)
    print(f"Extracted model ID: '{model_id}' from '{model}'")

    if provider == "openai":
        # For OpenAI models, pass the tool_choice parameter only if appropriate
        kwargs = {
            "model": model_id,
            "messages": messages,
            "temperature": temperature,
            "max_tokens": max_tokens,
            "stream": stream,
        }

        # Add tools if provided
        if tools:
            kwargs["tools"] = tools

        # Only pass tool_choice if it's not "none" to avoid API errors
        # The OpenAI API will return an error if tool_choice is specified but no tools are available
        if tool_choice is not None and tool_choice != "none":
            kwargs["tool_choice"] = tool_choice

        return get_openai_chat_completion(**kwargs)
    elif provider == "openrouter":
        # For OpenRouter models (including Anthropic models)
        return get_openrouter_chat_completion(
            model=model_id,
            messages=messages,
            temperature=temperature,
            max_tokens=max_tokens,
            stream=stream,
            tool_choice=tool_choice,
            tools=tools,
            use_prompt_cache=use_prompt_cache,
            request_id=request_id,
            force_cache_miss=force_cache_miss,
        )
    else:
        raise ValueError(f"Unsupported provider for model {model}")


def determine_model_provider(model: str) -> str:
    """
    Determine the provider for a given model.

    Args:
        model: The model ID, which may include a provider prefix.

    Returns:
        The provider name ("openai" or "openrouter").
    """
    print(f"DEBUG: Determining provider for model: '{model}'")

    # First check if the model has a provider prefix
    if "/" in model:
        provider_prefix = model.split("/")[0].lower()
        print(f"DEBUG: Found provider prefix: '{provider_prefix}'")

        if provider_prefix == "openai":
            print(f"DEBUG: Detected OpenAI provider for model: '{model}'")
            return "openai"
        elif provider_prefix in [
            "anthropic",
            "openrouter",
            "meta",
            "google",
            "mistral",
            "cohere",
            "qwen",  # Add qwen to the list of OpenRouter providers
            "deepseek",  # Add deepseek to the list
        ]:
            print(
                f"DEBUG: Detected OpenRouter provider for model: '{model}' (prefix: {provider_prefix})"
            )
            return "openrouter"  # Use OpenRouter for these providers
        else:
            # All other prefixed models should go through OpenRouter
            print(
                f"DEBUG: Using OpenRouter for unknown prefix '{provider_prefix}' in model: '{model}'"
            )
            return "openrouter"

    # If no prefix, check against our list of known models
    try:
        all_models = list_all_models()
        for model_info in all_models:
            # Check against both prefixed ID and original ID
            if model_info.id == model or model_info.original_id == model:
                print(
                    f"DEBUG: Found model in known models list, provider: {model_info.provider}"
                )
                return model_info.provider
    except Exception as e:
        print(f"Error checking model against known models: {e}")

    # Use pattern matching for common model naming conventions
    if model.startswith("gpt-") or model.startswith("text-"):
        print(f"DEBUG: Detected OpenAI model by pattern: '{model}'")
        return "openai"
    elif any(
        name in model.lower()
        for name in ["claude", "llama", "mistral", "gemini", "qwen"]
    ):
        print(f"DEBUG: Detected OpenRouter model by pattern: '{model}'")
        return "openrouter"

    # For all other cases, try OpenRouter
    # This is a fallback and might not be accurate for all models
    print(f"DEBUG: Using OpenRouter as fallback provider for unknown model: {model}")
    return "openrouter"


def get_openai_chat_completion(
    model: str,
    messages: List[Dict[str, Any]],
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
) -> Union[Dict[str, Any], Any]:
    """
    Get a chat completion from OpenAI.

    Args:
        model: The model to use.
        messages: The messages to send to the model.
        temperature: The temperature to use.
        max_tokens: The maximum number of tokens to generate.
        stream: Whether to stream the response.
        tool_choice: Optional tool choice parameter. Can be "none", "auto", or a specific tool configuration.
        tools: Optional tools to provide to the model.

    Returns:
        The chat completion response.
    """
    if not openai_client:
        raise ValueError(
            "OpenAI client not initialized. Make sure OPENAI_API_KEY is set."
        )

    try:
        kwargs = {
            "model": model,
            "messages": messages,
            "temperature": temperature,
            "stream": stream,
        }

        if max_tokens:
            kwargs["max_tokens"] = max_tokens

        # Add tools if provided
        if tools:
            kwargs["tools"] = tools

        # Add tool_choice if specified and we have tools
        # Only add tool_choice if we're using a model that supports it
        if tool_choice is not None and model.startswith("gpt-"):
            # For OpenAI models, we need to ensure we're only sending tool_choice
            # when tools are specified, otherwise we'll get an error
            if tool_choice != "none" and tools:
                # For "auto" or specific tool configurations, we need to have tools
                kwargs["tool_choice"] = tool_choice

        return openai_client.chat.completions.create(**kwargs)
    except Exception as e:
        print(f"Error getting OpenAI chat completion: {e}")
        raise


def get_openrouter_chat_completion(
    model: str,
    messages: List[Dict[str, Any]],
    temperature: float = 0.7,
    max_tokens: Optional[int] = None,
    stream: bool = False,
    tool_choice: Optional[Union[str, Dict[str, Any]]] = None,
    tools: Optional[List[Dict[str, Any]]] = None,
    use_prompt_cache: bool = False,
    request_id: Optional[str] = None,
    force_cache_miss: bool = False,
) -> Union[Dict[str, Any], Any]:
    """
    Get a chat completion from OpenRouter.

    Args:
        model: The model to use.
        messages: The messages to send to the model.
        temperature: The temperature to use.
        max_tokens: The maximum number of tokens to generate.
        stream: Whether to stream the response.
        tool_choice: Optional tool choice parameter.
        tools: Optional tools to provide to the model.
        use_prompt_cache: Whether to use prompt caching.
        request_id: Optional request ID for tracking.
        force_cache_miss: Whether to force a cache miss.

    Returns:
        The chat completion response.
    """
    if not OPENROUTER_API_KEY:
        REDACTED_AIRLOCK ValueError(
            "OpenRouter API key not set. Make sure OPENROUTER_API_KEY is set."
        )

    # Generate a request ID if not provided
    if request_id is None:
        request_id = f"req-{uuid.uuid4().hex}"

    try:
        # Import necessary modules
        try:
            from ..config.prompt_cache_config import is_prompt_caching_supported
            from ..utils.prompt_cache_monitor import prompt_cache_monitor
        except Exception as import_error:
            print(f"Warning: Could not import prompt cache modules: {import_error}")

            # Define fallback functions
            def is_prompt_caching_supported(model):
                return False

            class MockPromptCacheMonitor:
                def log_request(self, **kwargs):
                    pass

            prompt_cache_monitor = MockPromptCacheMonitor()

        # Set up headers
        headers = {
            "Authorization": REDACTED_AIRLOCK"Bearer {OPENROUTER_API_KEY}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/KooshaPari/swe_agent_project",  # Required for OpenRouter
            "X-Title": "SWE Agent Project",  # Optional but helpful for OpenRouter
            "X-Request-ID": request_id,  # Add request ID for tracking
        }

        # Add prompt caching header for supported models
        cache_enabled = (
            use_prompt_cache
            and is_prompt_caching_supported(model)
            and not force_cache_miss
        )

        if cache_enabled:
            # Add the appropriate headers for prompt caching
            if "anthropic" in model:
                headers["anthropic-beta"] = "prompt-caching-2024-07-31"

            # Add cache control header if forcing a cache miss
            if force_cache_miss:
                headers["Cache-Control"] = "no-cache"

        # Prepare the request data
        data = {
            "model": model,
            "messages": messages.copy(),  # Create a copy to avoid modifying the original
            "temperature": temperature,
            "stream": stream,
        }

        if max_tokens:
            data["max_tokens"] = max_tokens

        # Add tools and tool_choice if provided
        if tools:
            data["tools"] = tools

        if tool_choice:
            data["tool_choice"] = tool_choice

        # Add prompt caching for supported models
        if cache_enabled:
            # Find the last two user messages to apply caching
            user_msg_indices = [
                i for i, msg in enumerate(data["messages"]) if msg.get("role") == "user"
            ]
            last_user_msg_index = user_msg_indices[-1] if user_msg_indices else -1
            second_last_user_msg_index = (
                user_msg_indices[-2] if len(user_msg_indices) > 1 else -1
            )

            # Apply cache_control to the last two user messages
            if last_user_msg_index >= 0:
                if isinstance(
                    data["messages"][last_user_msg_index].get("content"), str
                ):
                    data["messages"][last_user_msg_index]["cache_control"] = {
                        "type": "ephemeral"
                    }

            if second_last_user_msg_index >= 0:
                if isinstance(
                    data["messages"][second_last_user_msg_index].get("content"), str
                ):
                    data["messages"][second_last_user_msg_index]["cache_control"] = {
                        "type": "ephemeral"
                    }

            # Also apply cache_control to system messages if present
            for i, msg in enumerate(data["messages"]):
                if msg.get("role") == "system" and isinstance(msg.get("content"), str):
                    data["messages"][i]["cache_control"] = {"type": "ephemeral"}

        # Start timing the request
        start_time = time.time()

        if stream:
            # For streaming, we need to handle the response differently
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                stream=True,
            )
            response.raise_for_status()

            # For streaming, return the raw response iterator
            # This allows real-time streaming to the client
            return response.iter_lines(decode_unicode=True)
        else:
            # For non-streaming, we can process the response directly
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
            )
            response.raise_for_status()

            # Get the response data
            response_data = response.json()

            # Process the response to detect cache hits
            _process_openrouter_response(
                response_data,
                model=model,
                request_id=request_id,
                cache_enabled=cache_enabled,
                duration=time.time() - start_time,
            )

            return response_data
    except Exception as e:
        print(f"Error getting OpenRouter chat completion: {e}")
        raise


def _process_openrouter_response(
    response_data: Dict[str, Any],
    model: str,
    request_id: str,
    cache_enabled: bool,
    duration: float,
) -> None:
    """
    Process an OpenRouter response to detect cache hits and track metrics.

    Args:
        response_data: The response data from OpenRouter.
        model: The model used.
        request_id: The request ID.
        cache_enabled: Whether prompt caching was enabled.
        duration: The request duration in seconds.
    """
    from ..utils.prompt_cache_monitor import prompt_cache_monitor

    # Extract usage information
    usage = response_data.get("usage", {})
    input_tokens = usage.get("prompt_tokens", 0)
    output_tokens = usage.get("completion_tokens", 0)

    # Check for cache hit indicators
    cache_hit = False
    cache_read_tokens = None
    cache_write_tokens = None

    # Check for cache hit indicators in the response
    if "cached" in response_data:
        cache_hit = response_data.get("cached", False)

    # Check for cache tokens in the usage
    if "prompt_cache_hit_tokens" in usage:
        cache_read_tokens = usage.get("prompt_cache_hit_tokens", 0)
        cache_hit = cache_read_tokens > 0
    elif "cached_tokens" in usage:
        cache_read_tokens = usage.get("cached_tokens", 0)
        cache_hit = cache_read_tokens > 0
    elif "cache_read_tokens" in usage:
        cache_read_tokens = usage.get("cache_read_tokens", 0)
        cache_hit = cache_read_tokens > 0

    # Check for cache write tokens
    if "prompt_cache_write_tokens" in usage:
        cache_write_tokens = usage.get("prompt_cache_write_tokens", 0)
    elif "cache_write_tokens" in usage:
        cache_write_tokens = usage.get("cache_write_tokens", 0)

    # If cache was enabled but no explicit cache hit indicators,
    # use heuristics to determine if it was a cache hit
    if cache_enabled and cache_read_tokens is None and cache_hit is False:
        # If the response was very fast, it might be a cache hit
        if duration < 0.5:  # Less than 500ms is suspiciously fast
            cache_hit = True
            cache_read_tokens = input_tokens

    # Log the request to the cache monitor
    prompt_cache_monitor.log_request(
        request_id=request_id,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_write_tokens=cache_write_tokens,
        cache_read_tokens=cache_read_tokens,
        cache_hit=cache_hit if cache_enabled else None,
    )


def _process_openrouter_stream(
    stream_iter: Iterator[bytes],
    model: str,
    request_id: str,
    cache_enabled: bool,
) -> Generator[bytes, None, None]:
    """
    Process an OpenRouter streaming response to detect cache hits and track metrics.

    Args:
        stream_iter: The stream iterator from OpenRouter.
        model: The model used.
        request_id: The request ID.
        cache_enabled: Whether prompt caching was enabled.

    Yields:
        The stream chunks.
    """
    from ..utils.prompt_cache_monitor import prompt_cache_monitor

    # Initialize metrics
    start_time = time.time()
    input_tokens = 0
    output_tokens = 0
    cache_hit = False
    cache_read_tokens = None
    cache_write_tokens = None
    first_chunk_time = None

    # Process the stream
    for chunk in stream_iter:
        # If this is the first chunk, record the time
        if first_chunk_time is None:
            first_chunk_time = time.time()

        # Yield the chunk to the caller
        yield chunk

        # Try to parse the chunk as JSON to extract metrics
        try:
            if chunk.startswith(b"data: "):
                chunk_data = json.loads(chunk[6:])

                # Check for usage information
                if "usage" in chunk_data:
                    usage = chunk_data["usage"]
                    input_tokens = usage.get("prompt_tokens", input_tokens)
                    output_tokens = usage.get("completion_tokens", output_tokens)

                    # Check for cache hit indicators
                    if "prompt_cache_hit_tokens" in usage:
                        cache_read_tokens = usage.get("prompt_cache_hit_tokens", 0)
                        cache_hit = cache_read_tokens > 0
                    elif "cached_tokens" in usage:
                        cache_read_tokens = usage.get("cached_tokens", 0)
                        cache_hit = cache_read_tokens > 0
                    elif "cache_read_tokens" in usage:
                        cache_read_tokens = usage.get("cache_read_tokens", 0)
                        cache_hit = cache_read_tokens > 0

                    # Check for cache write tokens
                    if "prompt_cache_write_tokens" in usage:
                        cache_write_tokens = usage.get("prompt_cache_write_tokens", 0)
                    elif "cache_write_tokens" in usage:
                        cache_write_tokens = usage.get("cache_write_tokens", 0)
        except Exception:
            # Ignore parsing errors
            pass

    # If we didn't get explicit cache hit indicators but cache was enabled,
    # use heuristics to determine if it was a cache hit
    if (
        cache_enabled
        and cache_read_tokens is None
        and cache_hit is False
        and first_chunk_time is not None
    ):
        # If the first chunk arrived very quickly, it might be a cache hit
        if first_chunk_time - start_time < 0.5:  # Less than 500ms is suspiciously fast
            cache_hit = True
            cache_read_tokens = input_tokens

    # Log the request to the cache monitor
    prompt_cache_monitor.log_request(
        request_id=request_id,
        model=model,
        input_tokens=input_tokens,
        output_tokens=output_tokens,
        cache_write_tokens=cache_write_tokens,
        cache_read_tokens=cache_read_tokens,
        cache_hit=cache_hit if cache_enabled else None,
    )
