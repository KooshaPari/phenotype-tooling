# Prompt Caching

This document provides an overview of the prompt caching feature in the SWE Agent project.

## Overview

Prompt caching is a feature that allows the SWE Agent to cache prompts and their responses, reducing costs and improving response times. When enabled, the agent will cache prompts and reuse them for subsequent requests, avoiding the need to regenerate the same response multiple times.

## Supported Models

Prompt caching is currently supported for the following models:

- **Anthropic Models**:
  - Claude 3 Opus
  - Claude 3 Sonnet
  - Claude 3 Haiku
  - Claude 3.5 Sonnet
  - Claude 3.5 Haiku
  - Claude 3.7 Sonnet

- **OpenAI Models** (via OpenRouter):
  - GPT-4o
  - GPT-4o Mini

- **DeepSeek Models**:
  - DeepSeek Chat

## How It Works

Prompt caching works by adding special headers and parameters to API requests that tell the provider to cache the prompt and its response. When a subsequent request with the same prompt is made, the provider will return the cached response instead of generating a new one.

The caching mechanism works as follows:

1. **Cache Control**: The agent adds `cache_control` parameters to user messages and system prompts, marking them as "ephemeral" (cacheable).

2. **Headers**: For Anthropic models, the agent adds the `anthropic-beta: prompt-caching-2024-07-31` header to enable prompt caching.

3. **Message Selection**: The agent applies caching to:
   - The last two user messages
   - System messages

4. **Cache Hits**: When a cached prompt is encountered, the provider returns the cached response, which is significantly faster and cheaper than generating a new response.

## Cost Benefits

Prompt caching can significantly reduce costs, especially for frequently used prompts. The cost structure is as follows:

- **Cache Writes**: When a prompt is cached for the first time, you pay the normal input and output token costs, plus a small additional fee for writing to the cache.

- **Cache Reads**: When a cached prompt is reused, you only pay a small fee for reading from the cache, which is typically 5-10% of the normal input token cost.

For example, with Claude 3.5 Sonnet:
- Normal input cost: $3.00 per million tokens
- Normal output cost: $15.00 per million tokens
- Cache write cost: $3.75 per million tokens
- Cache read cost: $0.30 per million tokens

This means that after the first use, subsequent uses of the same prompt can be up to 90% cheaper.

## Configuration

Prompt caching is enabled by default for all supported models. You can configure it using the following options:

### In API Calls

When making API calls, you can enable or disable prompt caching using the `use_prompt_cache` parameter:

```python
response = get_chat_completion(
    model="anthropic/claude-3.5-sonnet",
    messages=[{"role": "user", "content": "Hello, world!"}],
    use_prompt_cache=True,  # Enable prompt caching
)
```

### In Configuration Files

The prompt caching configuration is defined in `src/config/prompt_cache_config.py`:

```python
DEFAULT_PROMPT_CACHE_CONFIG = {
    "enabled": True,  # Enable prompt caching by default
    "max_cache_size": 1000,  # Maximum number of cached prompts
    "cache_ttl": 86400,  # Cache TTL in seconds (24 hours)
}
```

## Best Practices

To get the most out of prompt caching, follow these best practices:

1. **Consistent Prompts**: Try to use consistent prompts for similar tasks to maximize cache hits.

2. **System Prompts**: Use consistent system prompts across requests to increase cache hit rates.

3. **Monitoring**: Monitor your cache hit rates and costs to ensure you're getting the expected benefits.

4. **Model Selection**: Choose models that support prompt caching for cost-sensitive applications.

## Limitations

Prompt caching has some limitations to be aware of:

1. **Cache Expiration**: Cached prompts expire after a certain period (typically 24 hours).

2. **Provider Support**: Not all providers and models support prompt caching.

3. **Exact Matches**: Caching typically requires exact matches of prompts, so even small changes can result in cache misses.

4. **Tool Calls**: Prompt caching may not work as effectively with tool calls, as the tool responses can vary.

## Conclusion

Prompt caching is a powerful feature that can significantly reduce costs and improve response times for the SWE Agent. By enabling prompt caching for supported models, you can make your agent more efficient and cost-effective.
