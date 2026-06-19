# Changelog

All notable changes to `dispatch-mcp` are recorded here. Versions follow
[Semantic Versioning](https://semver.org/).

## [Unreleased]

### Added

- **MCP protocol compliance (W2.1)** — full handshake, version
  discovery, and typed message schemas:
  - **`core/protocol.py`** — typed Pydantic v2 schemas for the
    MCP-style handshake surface: `ProtocolInfo`, `ServerInfo`,
    `ServerCapabilities`, `ClientInfo`, `InitializeRequest`,
    `InitializeRequestParams`, `InitializeResult`, `PingRequest`,
    `PingResult`, `DispatchRequest`, `DispatchResponse`,
    `ProtocolError`. Version constants
    `SUPPORTED_PROTOCOL_VERSIONS` and `DEFAULT_NEGOTIATED_VERSION`
    (current: `2025-11-25`) plus the
    `PROTOCOL_DISCOVERY_DESCRIPTION` for the discovery tool.
    `negotiate_version(requested, supported=...)` performs the
    spec-compliant version negotiation (exact match, no future
    versions, fallback to the highest mutually-supported
    version, default if `None`, raise `ProtocolError` on
    incompatibility).
  - **`dispatch_protocol`** MCP tool — returns the full
    `ProtocolInfo` payload (server name, version, vendor,
    supported versions, default version, capabilities, and
    negotiated version). Accepts optional `requested_version`,
    `client_name`, `client_version` to drive the negotiation and
    echo back the client's self-identification.
  - **`dispatch_ping`** MCP tool — upstream liveness probe that
    returns `JobResult(status="alive"|"unreachable", ...)` and
    never raises.
  - **`build_handshake(negotiated_version, client=...)`**
    helper — produces an `InitializeResult` ready for
    handshake-step consumers.
  - **`Router` / `Worker` protocols (`core/port.py`)** —
    `@runtime_checkable` Protocols with documented legacy and
    new method surfaces. `Router` declares `dispatch_message`,
    `worker`, `ping`, `protocol_info`, `close`, `client`,
    `health`, `cancel`. `Worker` declares a sync positional
    `dispatch` and an async `__call__` returning `JobResult`.
  - **`OmniHttpAdapter`** — extended to satisfy the new
    `Router` protocol: `worker(tier)` factory, async
    `dispatch_message(*, tier, message, payload=None)`,
    `ping()` returning `JobResult`, `protocol_info()` returning
    `ProtocolInfo`, and `close()`. The legacy positional
    `dispatch` and the cost-aware middleware surface are
    preserved.
  - **Tests** — `tests/unit/test_core_protocol.py` with 52 tests
    across 16 test classes covering: version constants,
    `negotiate_version` (exact / fallback / unsupported /
    `None`), every Pydantic schema (round-trip, defaults, model
    dump, type validation, optional fields), `ProtocolError`
    (string repr + serializable detail), `build_handshake` (with
    / without `client`), the `dispatch_protocol` tool
    (default negotiation, custom version, unknown client
    version, full payload shape), the `dispatch_ping` tool
    (alive / unreachable / never raises), and the full
    handshake sequence (`discovery → handshake → ping → work`).
- **Cost tracking system** — five new modules in `src/dispatch_mcp/core/`:
  - **`tiers.py`** — single source of truth for tier metadata and
    pricing (`TierPricing`, `TierRegistry`, `DEFAULT_REGISTRY`).
    Covers `worker`, `main`, `codeman`, `freetier`, `kimi`,
    `kimi_thinking`, `minimax`, `opus`, `haiku`, `gemini`.
  - **`cost.py`** — `CostCalculator` and `TokenEstimator` compute
    USD cost from token usage; works with both real `usage` blocks
    from OmniRoute responses and character-based estimates when
    usage is absent. Includes `TokenUsage` and `CostEstimate` value
    objects.
  - **`budget.py`** — `BudgetTracker` enforces cumulative USD
    spending caps (global and per-tier). The unpriced-tier floor
    prevents unregistered tiers from bypassing the cap with
    `cost_usd=0`. Raises typed `BudgetExceeded` with structured
    `detail` payload.
  - **`quota.py`** — `QuotaTracker` enforces rolling-window caps
    on token count and request count (global and per-tier). The
    sliding window is exact, supports an injected monotonic clock
    for tests, and prunes events strictly older than
    `now - window_seconds`. Raises typed `QuotaExceeded`.
  - **`audit.py`** — `AuditLog` is the append-only trail of every
    dispatch decision (`allowed`, `blocked`, with reason).
    Supports filter, summary, JSONL persistence sink, and is
    thread-safe.
  - **`cost_middleware.py`** — `CostAwareRouter` composes the
    calculator, budget, quota, and audit subsystems around the
    base `OmniHttpAdapter`. Pre-dispatch gating via quota then
    budget; post-dispatch accounting with budget, quota, and audit
    recorded. Refused dispatches do not consume upstream capacity
    and do not charge the budget. `TierWorker` is the per-tier
    async callable returned by `router.worker(tier)`.
- **Server wiring** — `server.py` constructs `CostAwareRouter`
  wrapping `OmniHttpAdapter`. Set `DISPATCH_COST_TRACKING=disabled`
  in the environment to bypass the cost layer (kill switch for
  emergency debugging).
- **Tests** — six new test modules in `tests/unit/` covering every
  new subsystem: `test_core_tiers.py`, `test_core_cost.py`,
  `test_core_budget.py`, `test_core_quota.py`, `test_core_audit.py`,
  `test_core_cost_middleware.py`. 271 tests pass, 95.42%
  coverage.

### Changed

- `JobResult` (`core/types.py`) — extended with `cost_usd`,
  `input_tokens`, `output_tokens`, `model`, and `request_id` so
  tool responses carry cost metadata without a separate payload.
- `OmniHttpAdapter` (`adapters/omni_http.py`) — `dispatch_message`
  (Router protocol), `ping`, and `protocol_info` are now part of
  the adapter surface; `_sanitize_response` defensively coerces
  upstream response dicts into `JobResult`.
- `Router` protocol (`core/port.py`) — `dispatch_message` is the
  primary entrypoint; the port advertises `client`, `health`,
  `cancel`, `worker`, `ping`, `protocol_info`, and `close` to
  match the cost-aware middleware surface.
- T0 hygiene pass (`chore/t0-python-hygiene-2026-06-08`):
  - **Tooling** — extended `[tool.ruff]` configuration:
    - `line-length` raised from 88 to 100.
    - Lint rule set expanded to `["E", "F", "W", "I", "N", "UP", "B",
      "A", "C4", "DTZ", "T20", "PT", "Q", "RET", "SIM", "ARG", "PL",
      "RUF"]`.
    - Added `[tool.ruff.lint.per-file-ignores]` to allow `PLC0415`
      (inline imports) in `tests/**` — required for the existing
      late-binding `from dispatch_mcp.server import ...` pattern used
      inside `with patch(...)` blocks.
  - **Test config** — added `addopts` to `[tool.pytest.ini_options]`:
    `-v --tb=short --cov=dispatch_mcp --cov-report=term-missing
    --cov-fail-under=80`. Plain `pytest` now produces a coverage report
    and enforces the 80% threshold.
  - **gitleaks** — added `.github/workflows/gitleaks.yml` to scan pushes
    and pull requests for leaked secrets.
  - **`.env.example`** — documents `OMNIROUTE_URL` (default
    `http://localhost:20128`) and the optional `LOG_LEVEL` knob.
  - **`py.typed` marker** — added `src/dispatch_mcp/py.typed` so
    downstream type checkers consume the inline annotations as a
    typed distribution.
  - **README** — added explicit `## Build`, `## Test` (with
    `Lint & type check` subsection), and clarified `## Run` to use
    the canonical OmniRoute default port.
  - **CHANGELOG** — this file.

### Changed

- `src/dispatch_mcp/server.py` — five `raise ValueError(...)` /
  `raise RuntimeError(...)` statements that previously wrapped onto
  two lines now fit on a single line under the new `line-length = 100`
  budget (auto-applied by `ruff format`).
- `src/dispatch_mcp/server.py:164` — `_handle_signal` second parameter
  renamed `frame` → `_frame` to satisfy `ARG001` (the parameter is
  required by the `signal.signal` callback contract but unused).
- `README.md` — `OMNIROUTE_URL` example port changed from
  `localhost:8080` to `localhost:20128` to match the documented
  OmniRoute default.

### Notes

- `[tool.mypy]` already matched the T0 spec (`strict = true`,
  `python_version = "3.13"`); no change.
- Existing CI workflow (`.github/workflows/ci.yml`) already runs ruff
  format/lint, mypy strict, bandit, safety, and pytest with coverage.
  No new CI steps were added to avoid duplication.

## [0.2.0] - 2026-06-12

### Added

- **`dispatch_mcp.health` module** — production-hardening surface
  with three pure-Python functions:
  - `liveness()` — cheap process-liveness probe. Returns
    `{"status": "alive", "server", "uptime_seconds"}`. No I/O.
  - `readiness(*, check_omniroute=False, timeout=2.0)` — readiness
    probe. Validates the `OMNIROUTE_URL` configuration and, when
    `check_omniroute=True`, performs a lightweight `GET /health`
    against the upstream. Defaults to a config-only check so
    kubelet probes do not stampede the dispatch backend.
  - `metrics()` — Prometheus text exposition placeholder with `dispatch_mcp_up`,
    `dispatch_mcp_uptime_seconds`, `dispatch_mcp_dispatches_total`,
    and `dispatch_mcp_dispatch_errors_total`. Counter values are
    zeroed pending future instrumentation.
- **Tests** — `tests/test_health.py` covers liveness, readiness (config
  + upstream variants), and metrics serialization.

## [0.1.0] - 2026-06-08

### Added

- Initial MCP server with tier-based dispatch tools via OmniRoute.
- Per-tier dispatch tools (`dispatch_worker`, `dispatch_main`, … `dispatch_gemini`).
- `dispatch_custom` for arbitrary tier dispatch.
- `dispatch_health` and `dispatch_liveness` FastMCP tools.
