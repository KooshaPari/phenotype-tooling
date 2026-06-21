# Provider Guide — `pheno-mcp-router` LLM Adapters

`pheno-mcp-router` is the substrate for all `pheno-mcp-*` servers
(per ADR-013). It defines a single narrow contract — the
`LlmPort` protocol (`async chat(messages, model) -> str`) — and
ships concrete adapters for every provider the fleet currently
talks to.

This guide explains how to choose and configure an adapter. For
the cost / budget / quota / audit layer that wraps every adapter,
see [§ Cost pipeline](#cost-pipeline).

## Adapter inventory

| Adapter | Class | Transport | Use case |
|---------|-------|-----------|----------|
| **OpenAI** | `OpenAIAdapter` | HTTPS | OpenAI Cloud (`api.openai.com`) |
| **Anthropic** | `AnthropicAdapter` | HTTPS | Anthropic Cloud (`api.anthropic.com`) |
| **OpenAI-compatible** | `OpenAICompatAdapter` | HTTPS | Any OpenAI-spec endpoint (vLLM, llama.cpp server, Together, Fireworks, OpenRouter, etc.) |
| **llama.cpp** | `LlamaAdapter` | HTTPS or in-process | Local llama.cpp server, or in-process GGUF load |

All four implement `LlmPort` and are interchangeable behind the
`LlmPort` Protocol:

```python
from pheno_mcp_router import LlmPort, OpenAIAdapter

llm: LlmPort = OpenAIAdapter(api_key="sk-...")
text = await llm.chat([{"role": "user", "content": "hi"}], "gpt-4o-mini")
```

## Choosing an adapter

| Need | Adapter |
|------|---------|
| OpenAI hosted models | `OpenAIAdapter` |
| Anthropic Claude models | `AnthropicAdapter` |
| vLLM, Together, OpenRouter, llama.cpp server, any other OpenAI-spec endpoint | `OpenAICompatAdapter` |
| Direct GGUF load (offline / dev / no network) | `LlamaAdapter` (direct mode) |
| llama.cpp server (local, with a sidecar) | `LlamaAdapter` (server mode) — or `OpenAICompatAdapter` pointed at the server |

## Quickstart per adapter

### `OpenAIAdapter`

```python
from pheno_mcp_router import OpenAIAdapter

llm = OpenAIAdapter(api_key="sk-...", timeout=60.0)
text = await llm.chat(
    [{"role": "user", "content": "Hello"}],
    model="gpt-4o-mini",
)
```

Env vars (optional, used by the `pheno-mcp-router` CLI):
- `OPENAI_API_KEY`
- `OPENAI_TIMEOUT_SECONDS` (default `60.0`)

### `AnthropicAdapter`

```python
from pheno_mcp_router import AnthropicAdapter

llm = AnthropicAdapter(api_key="sk-ant-...", timeout=60.0)
text = await llm.chat(
    [
        {"role": "system", "content": "be terse"},
        {"role": "user", "content": "Hello"},
    ],
    model="claude-3-5-haiku-20241022",
)
```

`AnthropicAdapter` splits out the first `system` message from the
message list and sends it in the `system` field per the
Anthropic Messages API.

Env vars:
- `ANTHROPIC_API_KEY`
- `ANTHROPIC_TIMEOUT_SECONDS` (default `60.0`)
- `ANTHROPIC_MAX_TOKENS` (default `4096`)

### `OpenAICompatAdapter`

`OpenAICompatAdapter` speaks the OpenAI `/v1/chat/completions`
schema against any endpoint that implements it. It adds 429 / 5xx
exponential backoff (3 attempts) on top of the base contract.

```python
from pheno_mcp_router.openai_compat_adapter import OpenAICompatAdapter

llm = OpenAICompatAdapter(
    base_url="http://localhost:8080/v1",   # vLLM, llama.cpp server, etc.
    api_key="not-required",                 # some servers accept any key
    timeout=60.0,
)
text = await llm.chat(
    [{"role": "user", "content": "Hello"}],
    model="meta-llama/Meta-Llama-3-8B-Instruct",
)
```

Common endpoints:
- **vLLM** — `http://<host>:8000/v1`
- **llama.cpp server** — `http://<host>:8080/v1`
- **Together** — `https://api.together.xyz/v1`
- **Fireworks** — `https://api.fireworks.ai/inference/v1`
- **OpenRouter** — `https://openrouter.ai/api/v1`
- **LM Studio** — `http://localhost:1234/v1`
- **Ollama (with OpenAI-compat shim)** — `http://localhost:11434/v1`

### `LlamaAdapter` (local llama.cpp)

`LlamaAdapter` operates in one of two modes:

| Mode | Configuration | Use case |
|------|---------------|----------|
| **Server mode** | `LLAMA_CPP_SERVER_URL` | Connect to a running [llama.cpp](https://github.com/ggerganov/llama.cpp) server |
| **Direct mode** | `LLAMA_CPP_MODEL_PATH` | Load a GGUF model directly in-process |

#### Server mode (recommended for production)

1. Start a llama.cpp server:

```bash
# With Docker (see phenotype-ops/agent-devops-setups/llama-cpp)
docker compose -f agent-devops-setups/llama-cpp/docker-compose.yml up llama-cpp

# Or bare metal:
./server -m /path/to/model.gguf --host 0.0.0.0 --port 8080
```

2. Configure the substrate:

```python
from pheno_mcp_router.llama_adapter import LlamaAdapter

llm = LlamaAdapter(server_url="http://localhost:8080", timeout=60.0)
text = await llm.chat(
    [{"role": "user", "content": "Write a hello world in Rust"}],
    model="local",
)
```

#### Direct mode (single-process, dev/offline)

```python
from pheno_mcp_router.llama_adapter import LlamaAdapter

llm = LlamaAdapter(
    model_path="/path/to/model.gguf",
    n_ctx=4096,
    n_gpu_layers=-1,  # -1 = all layers on GPU
)
text = await llm.chat(
    [{"role": "user", "content": "Hello"}],
    model="local",
)
```

Requires `llama-cpp-python`:

```bash
pip install pheno-mcp-router[llama]
```

The `[llama]` extra is declared in `pyproject.toml`.

## Cost pipeline

Every adapter should be composed with the `CostAwareLlmAdapter`
middleware to participate in cost / budget / quota / audit
tracking. The middleware wraps any `LlmPort` and exposes the
tier-aware `dispatch(messages, model, tier=...)` and
`dispatch_with_metadata(...)` APIs in addition to the bare
`LlmPort.chat` surface.

```python
from pheno_mcp_router import OpenAIAdapter
from pheno_mcp_router.cost_middleware import CostAwareLlmAdapter

inner: LlmPort = OpenAIAdapter(api_key="sk-...")
llm = CostAwareLlmAdapter(inner)

# Tier-aware dispatch (records cost / budget / quota / audit)
text = await llm.dispatch(
    [{"role": "user", "content": "hi"}],
    model="gpt-4o-mini",
    tier="worker",
)

# Or, if you only have an LlmPort handle, just use chat():
# cost tracking still happens under the "unknown" tier.
text = await llm.chat([{"role": "user", "content": "hi"}], "gpt-4o-mini")
```

## Architecture

All four adapters live in `pheno_mcp_router`:

```
pheno_mcp_router
  ├── adapters.py         # OpenAIAdapter, AnthropicAdapter, storage/tool adapters
  ├── ports.py            # LlmPort, StoragePort, ToolPort Protocols + ABCs
  ├── llama_adapter.py    # LlamaAdapter (server + direct mode)
  ├── openai_compat_adapter.py  # OpenAICompatAdapter (any OpenAI-spec endpoint)
  ├── cost_middleware.py  # CostAwareLlmAdapter (wraps any LlmPort)
  ├── tiers.py            # TierRegistry + DEFAULT_REGISTRY (10 tiers)
  ├── cost.py             # CostCalculator + TokenEstimator
  ├── budget.py           # BudgetTracker
  ├── quota.py            # QuotaTracker (rolling-window)
  └── audit.py            # AuditLog (append-only + JSONL sink)
```

`pheno-mcp-router` exports `LlmPort`, `LlmAdapter`, `OpenAIAdapter`,
`AnthropicAdapter` from the top-level package; the newer adapters
(`LlamaAdapter`, `OpenAICompatAdapter`) are imported from their
sub-modules until they graduate to the top-level export in a
follow-up release.

## Docker

The `phenotype-ops` repo ships a `llama-cpp` stack under
`agent-devops-setups/llama-cpp/` (Dockerfile + docker-compose.yml).
That stack runs a llama.cpp server as a sidecar; point
`LlamaAdapter` (server mode) or `OpenAICompatAdapter` at it.

```bash
# Build the llama-cpp image
docker build -f agent-devops-setups/llama-cpp/Dockerfile \
  -t pheno-llama-cpp .

# Run the full stack (llama.cpp server)
docker compose -f agent-devops-setups/llama-cpp/docker-compose.yml up
```

## Environment variables

| Variable | Used by | Default | Description |
|----------|---------|---------|-------------|
| `OPENAI_API_KEY` | `OpenAIAdapter` | — | OpenAI API key |
| `OPENAI_TIMEOUT_SECONDS` | `OpenAIAdapter` | `60.0` | Per-request timeout |
| `ANTHROPIC_API_KEY` | `AnthropicAdapter` | — | Anthropic API key |
| `ANTHROPIC_TIMEOUT_SECONDS` | `AnthropicAdapter` | `60.0` | Per-request timeout |
| `ANTHROPIC_MAX_TOKENS` | `AnthropicAdapter` | `4096` | Max output tokens |
| `LLAMA_CPP_SERVER_URL` | `LlamaAdapter` | — | URL of running llama.cpp server |
| `LLAMA_CPP_MODEL_PATH` | `LlamaAdapter` | — | Path to GGUF model file |
| `LLAMA_CPP_N_CTX` | `LlamaAdapter` | `4096` | Context window (direct mode) |
| `LLAMA_CPP_N_GPU_LAYERS` | `LlamaAdapter` | `0` | GPU layers (-1 = all, direct mode) |

One of `LLAMA_CPP_SERVER_URL` or `LLAMA_CPP_MODEL_PATH` must be set
for `LlamaAdapter` to operate.
