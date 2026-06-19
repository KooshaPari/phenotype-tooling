<!-- AI-DD-META:START -->
<!-- This repository is planned, maintained, and managed by AI Agents only. -->
<!-- Slop issues are expected and intentionally present as part of an HITL-less -->
<!-- /minimized AI-DD metaproject of learning, refining, and building brute-force -->
<!-- training for both agents and the human operator. -->
![Downloads](https://img.shields.io/github/downloads/KooshaPari/dispatch-mcp/total?style=flat-square&label=downloads&color=blue)
![GitHub release](https://img.shields.io/github/v/release/KooshaPari/dispatch-mcp?style=flat-square&label=release)
![License](https://img.shields.io/github/license/KooshaPari/dispatch-mcp?style=flat-square)
![AI-Slop](https://img.shields.io/badge/AI--DD-Slop%20Expected-orange?style=flat-square)
![AI-Only-Maintained](https://img.shields.io/badge/Planned%20%26%20Maintained%20by-AI%20Agents%20Only-red?style=flat-square)
![HITL-less](https://img.shields.io/badge/HITL--less%20AI--DD-metaproject-yellow?style=flat-square)

> ⚠️ **AI-Agent-Only Repository**
>
> This repo is **planned, maintained, and managed exclusively by AI Agents**.
> Slop issues, rough edges, and AI artifacts are **expected and intentionally
> present** as part of an **HITL-less / minimized AI-DD** metaproject focused
> on learning, refining, and brute-force training both the agents and the
> human operator. Bug reports and contributions are still welcome, but please
> expect AI-generated code, comments, and documentation throughout.
<!-- AI-DD-META:END -->
## Work State

| Field | Value |
|---|---|
| Last commit | 2026-06-08 16:14:41 -0700 |
| Open issues | 0 |
| Open PRs | 3 |
| Focus | omniroute-dispatch |

Progress: ████████░░ 80%

# dispatch-mcp

MCP server for tier-based dispatch delegation via OmniRoute.

## Tools

### Per-tier dispatch tools

| Tool name | Tier |
|---|---|
| `dispatch_worker` | `worker` |
| `dispatch_main` | `main` |
| `dispatch_codeman` | `codeman` |
| `dispatch_freetier` | `freetier` |
| `dispatch_kimi` | `kimi` |
| `dispatch_kimi_thinking` | `kimi_thinking` |
| `dispatch_minimax` | `minimax` |
| `dispatch_opus` | `opus` |
| `dispatch_haiku` | `haiku` |
| `dispatch_gemini` | `gemini` |

Each accepts a single `message: str` argument and dispatches it to the configured OmniRoute backend under the corresponding tier.

### Custom dispatch

`dispatch_custom(tier: str, message: str)` — dispatch to any tier from `VALID_TIERS` above.

### Health

- `dispatch_health()` — probe the OmniRoute backend health endpoint. Requires `OMNIROUTE_URL` to be set.
- `dispatch_liveness()` — returns server liveness status without contacting OmniRoute.

### Health module (production)

`dispatch_mcp.health` exposes three pure-Python functions intended for
production probes and observability:

| Function | Purpose | I/O |
|---|---|---|
| `liveness()` | Cheap process-liveness probe (kubelet `livenessProbe`). | None |
| `readiness(*, check_omniroute=False, timeout=2.0)` | Readiness probe. Validates `OMNIROUTE_URL` config; opt-in upstream check via `check_omniroute=True`. | Optional HTTP `GET /health` |
| `metrics()` | Prometheus text exposition placeholder with `dispatch_mcp_up`, `dispatch_mcp_uptime_seconds`, and dispatch counter gauges. | None |

Wire them into FastMCP tools, an HTTP wrapper, or invoke them directly
from tests. Default `readiness()` is config-only to avoid stampeding the
backend.

## Configuration

| Variable | Required | Default | Description |
|---|---|---|---|
| `OMNIROUTE_URL` | Yes | — | Base URL of the OmniRoute dispatch backend (e.g. `http://localhost:8080`). Must use `http://` or `https://` scheme. |
| `LOG_LEVEL` | No | (root logger) | Logging verbosity. Accepted values: `DEBUG`, `INFO`, `WARNING`, `ERROR`, `CRITICAL`. Invalid values fall through to the root logger's level. |

### Constraints

- `message` must not exceed **4096 bytes** (UTF-8 encoded).
- `tier` must be one of the known tiers listed above.
- `OMNIROUTE_URL` must use `http://` or `https://` scheme. Other schemes (e.g. `file://`, `javascript:`) are rejected at startup with a `ValueError`.
- HTTP redirects are **not followed** — only direct requests to `OMNIROUTE_URL` are made.

## Build

Install the package in editable mode with the `dev` extras (pulls in
`pytest`, `pytest-cov`):

```bash
python -m pip install -e ".[dev]"
```

The runtime dependencies are `fastmcp>=3.2.4` and `httpx>=0.27.0`.
Requires Python 3.13+.

## Test

```bash
# Run the full test suite with coverage (uses pyproject.toml addopts)
pytest

# Or with an explicit report
pytest --cov-report=term-missing
```

The default `addopts` (see `[tool.pytest.ini_options]`) enables branch
coverage, missing-line reporting, and fails the run if coverage drops
below 80%.

### Lint & type check

```bash
# Format
ruff format .

# Lint
ruff check .

# Strict type check
mypy src/ --strict
```

The same checks run in CI (see `.github/workflows/ci.yml`).

## Run

```bash
# Set the backend URL
export OMNIROUTE_URL=http://localhost:20128

# Via entry point
dispatch-mcp

# Or directly
python -m dispatch_mcp.server
```
