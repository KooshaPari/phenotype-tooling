"""
Configuration for prompt caching.

This module provides configuration for prompt caching, including which models support it
and how to enable/disable it.
"""

from typing import Dict, List, Set

# Models that support prompt caching
PROMPT_CACHE_SUPPORTED_MODELS: Set[str] = {
    # Anthropic models
    "anthropic/claude-3-opus",
    "anthropic/claude-3-opus:beta",
    "anthropic/claude-3-sonnet",
    "anthropic/claude-3-sonnet:beta",
    "anthropic/claude-3-haiku",
    "anthropic/claude-3-haiku:beta",
    "anthropic/claude-3.5-sonnet",
    "anthropic/claude-3.5-sonnet:beta",
    "anthropic/claude-3.5-sonnet-20240620",
    "anthropic/claude-3.5-sonnet-20240620:beta",
    "anthropic/claude-3.5-haiku",
    "anthropic/claude-3.5-haiku:beta",
    "anthropic/claude-3.5-haiku-20241022",
    "anthropic/claude-3.5-haiku-20241022:beta",
    "anthropic/claude-3.7-sonnet",
    "anthropic/claude-3.7-sonnet:beta",
    "anthropic/claude-3.7-sonnet:thinking",
    "anthropic/claude-3-7-sonnet",
    "anthropic/claude-3-7-sonnet:beta",
    # OpenAI models via OpenRouter
    "openai/gpt-4o",
    "openai/gpt-4o-mini",
    # DeepSeek models
    "deepseek/deepseek-chat",
}

# Pricing information for prompt caching and normal usage (per million tokens)
PROMPT_CACHE_PRICING: Dict[str, Dict[str, float]] = {
    # Anthropic models
    "anthropic/claude-3-opus": {
        "input": 15.0,
        "output": 75.0,
        "write": 18.75,
        "read": 1.5,
    },
    "anthropic/claude-3-opus:beta": {
        "input": 15.0,
        "output": 75.0,
        "write": 18.75,
        "read": 1.5,
    },
    "anthropic/claude-3-sonnet": {
        "input": 3.0,
        "output": 15.0,
        "write": 3.75,
        "read": 0.3,
    },
    "anthropic/claude-3-sonnet:beta": {
        "input": 3.0,
        "output": 15.0,
        "write": 3.75,
        "read": 0.3,
    },
    "anthropic/claude-3-haiku": {
        "input": 0.25,
        "output": 1.25,
        "write": 0.3,
        "read": 0.03,
    },
    "anthropic/claude-3-haiku:beta": {
        "input": 0.25,
        "output": 1.25,
        "write": 0.3,
        "read": 0.03,
    },
    "anthropic/claude-3.5-sonnet": {
        "input": 3.0,
        "output": 15.0,
        "write": 3.75,
        "read": 0.3,
    },
    "anthropic/claude-3.5-sonnet:beta": {
        "input": 3.0,
        "output": 15.0,
        "write": 3.75,
        "read": 0.3,
    },
    "anthropic/claude-3.5-sonnet-20240620": {
        "input": 3.0,
        "output": 15.0,
        "write": 3.75,
        "read": 0.3,
    },
    "anthropic/claude-3.5-sonnet-20240620:beta": {
        "input": 3.0,
        "output": 15.0,
        "write": 3.75,
        "read": 0.3,
    },
    "anthropic/claude-3.5-haiku": {
        "input": 1.0,
        "output": 5.0,
        "write": 1.25,
        "read": 0.1,
    },
    "anthropic/claude-3.5-haiku:beta": {
        "input": 1.0,
        "output": 5.0,
        "write": 1.25,
        "read": 0.1,
    },
    "anthropic/claude-3.5-haiku-20241022": {
        "input": 1.0,
        "output": 5.0,
        "write": 1.25,
        "read": 0.1,
    },
    "anthropic/claude-3.5-haiku-20241022:beta": {
        "input": 1.0,
        "output": 5.0,
        "write": 1.25,
        "read": 0.1,
    },
    "anthropic/claude-3.7-sonnet": {
        "input": 3.0,
        "output": 15.0,
        "write": 3.75,
        "read": 0.3,
    },
    "anthropic/claude-3.7-sonnet:beta": {
        "input": 3.0,
        "output": 15.0,
        "write": 3.75,
        "read": 0.3,
    },
    "anthropic/claude-3.7-sonnet:thinking": {
        "input": 3.0,
        "output": 15.0,
        "write": 3.75,
        "read": 0.3,
    },
    "anthropic/claude-3-7-sonnet": {
        "input": 3.0,
        "output": 15.0,
        "write": 3.75,
        "read": 0.3,
    },
    "anthropic/claude-3-7-sonnet:beta": {
        "input": 3.0,
        "output": 15.0,
        "write": 3.75,
        "read": 0.3,
    },
    # OpenAI models via OpenRouter
    "openai/gpt-4o": {"input": 5.0, "output": 15.0, "write": 0.0, "read": 0.5},
    "openai/gpt-4o-mini": {"input": 2.5, "output": 7.5, "write": 0.0, "read": 0.25},
    # DeepSeek models
    "deepseek/deepseek-chat": {
        "input": 0.14,
        "output": 0.7,
        "write": 0.14,
        "read": 0.014,
    },
}

# Default prompt caching configuration
DEFAULT_PROMPT_CACHE_CONFIG = {
    "enabled": True,  # Enable prompt caching by default
    "max_cache_size": 1000,  # Maximum number of cached prompts
    "cache_ttl": 86400,  # Cache TTL in seconds (24 hours)
}


def is_prompt_caching_supported(model: str) -> bool:
    """
    Check if prompt caching is supported for the given model.

    Args:
        model: The model ID.

    Returns:
        True if prompt caching is supported, False otherwise.
    """
    return model in PROMPT_CACHE_SUPPORTED_MODELS


def get_prompt_cache_pricing(model: str) -> Dict[str, float]:
    """
    Get the prompt cache pricing for the given model.

    Args:
        model: The model ID.

    Returns:
        A dictionary with "write" and "read" pricing per million tokens.
    """
    return PROMPT_CACHE_PRICING.get(model, {"write": 0.0, "read": 0.0})
