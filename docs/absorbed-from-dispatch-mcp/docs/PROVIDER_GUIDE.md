# Provider Guide — dispatch-mcp Local LLM Provider

dispatch-mcp ships with a built-in local LLM provider based on
[llama-cpp-python](https://github.com/abetlen/llama-cpp-python).
This guide explains how to configure and use it.

## Overview

The `LlamaCppProvider` operates in one of two modes:

| Mode | Configuration | Use case |
|------|---------------|----------|
| **Server mode** | `LLAMA_CPP_SERVER_URL` | Connect to a running [llama.cpp](https://github.com/ggerganov/llama.cpp) server instance |
| **Direct mode** | `LLAMA_CPP_MODEL_PATH` | Load a GGUF model directly in-process |

## Quickstart

### Server mode (recommended for production)

1. Start a llama.cpp server:

```bash
# With Docker (see docker/llama-compose.yml)
docker compose -f docker/llama-compose.yml up llama-cpp

# Or bare metal:
./server -m /path/to/model.gguf --host 0.0.0.0 --port 8080
```

2. Set environment variables and start dispatch-mcp:

```bash
export LLAMA_CPP_SERVER_URL=http://localhost:8080
dispatch-mcp
```

3. Use the MCP tools:

```python
# Via MCP client
await call_tool("dispatch_local_complete", {
    "message": "Write a hello world in Rust",
    "system_prompt": "You are a helpful coding assistant",
    "temperature": 0.2,
})
```

### Direct mode (single-process, dev/offline)

```bash
export LLAMA_CPP_MODEL_PATH=/path/to/model.gguf
export LLAMA_CPP_N_CTX=4096
export LLAMA_CPP_N_GPU_LAYERS=-1  # -1 for all layers on GPU
dispatch-mcp
```

Requires `llama-cpp-python`:
```bash
pip install dispatch-mcp[llama]
```

## Tools

### `dispatch_local_complete`

Generate a completion using the local provider.

| Parameter | Type | Default | Description |
|-----------|------|---------|-------------|
| `message` | `str` | required | The user message |
| `system_prompt` | `str` | `""` | Optional system-level instruction |
| `max_tokens` | `int` | `4096` | Maximum tokens to generate |
| `temperature` | `float` | `0.2` | Sampling temperature |

### `dispatch_local_health`

Check that the local provider is healthy. Returns status, latency, and mode info.

### `dispatch_local_info`

Return configuration metadata (mode, model path, context window size, GPU layers).

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LLAMA_CPP_SERVER_URL` | No (mode select) | — | URL of running llama.cpp server |
| `LLAMA_CPP_MODEL_PATH` | No (mode select) | — | Path to GGUF model file |
| `LLAMA_CPP_N_CTX` | No | `4096` | Context window size |
| `LLAMA_CPP_N_GPU_LAYERS` | No | `0` | GPU layers (-1 = all) |

One of `LLAMA_CPP_SERVER_URL` or `LLAMA_CPP_MODEL_PATH` must be set.

## Architecture

The provider is registered as a lazy singleton (`_local_provider`) in
`dispatch_mcp.server` and exposed as three MCP tools:

```
dispatch_mcp.server
  ├── dispatch_local_complete()     # single completion
  ├── dispatch_local_health()        # health check
  └── dispatch_local_info()          # configuration info
```

The provider itself lives in `dispatch_mcp.providers`:

```
dispatch_mcp.providers
  ├── base.py          # Provider protocol, Message, Completion
  ├── __init__.py      # Registry
  └── llama_cpp.py     # LlamaCppProvider (server + direct mode)
```

## Docker

See `docker/Dockerfile.llama` for the dispatch-mcp image and
`docker/llama-compose.yml` for the full stack including a
llama.cpp sidecar.

```bash
# Build the dispatch-mcp image with llama extras
docker build -f docker/Dockerfile.llama -t dispatch-mcp-llama .

# Run with compose (llama.cpp server + dispatch-mcp)
docker compose -f docker/llama-compose.yml up
```