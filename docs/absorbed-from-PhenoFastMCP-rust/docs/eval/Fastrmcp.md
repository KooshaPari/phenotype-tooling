# FastRMCP evaluation — PhenoFastMCP-rust side-DAG

**Date:** 2026-06-17  
**Side-DAG:** `sd-fastrmcp-01` … `sd-fastrmcp-05` (phenodag `mcp-fleet-90`)  
**Evaluator:** Phenotype fleet (issue #8 / SUPERSET.md checklist item 2)  
**Scope:** Evaluation only — **not** a fork parent or merge target.

## Boundary (ADR-017)

| Repo | Role |
|------|------|
| **KooshaPari/PhenoFastMCP-rust** | Tier-0 framework fork; parent **`Dicklesworthstone/fastmcp_rust`** |
| **JSBtechnologies/FastRMCP** | Cherry-pick reference only (this doc) |
| **KooshaPari/PhenoRMCP** | Official `rmcp` spec SDK — separate lane |

FastRMCP must **never** become the PhenoFastMCP-rust parent or wholesale merge source.

## Repo snapshot

| Metric | fastmcp_rust (parent) | FastRMCP (eval) |
|--------|----------------------|-----------------|
| Stars | 27 | 2 |
| Last push | 2026-06-11 | 2025-11-30 |
| Runtime | **asupersync** (cancel-correct) | **tokio** + `async_trait` |
| HTTP server | External integration | **Axum 0.7** built-in (SSE/WS) |
| crates.io | `fastmcp-rust` v0.3.x | Not published |
| Community | Active upstream author | Tiny, single maintainer |

---

## sd-fastrmcp-01 — Middleware audit

### fastmcp_rust (baseline in PhenoFastMCP-rust)

Location: `crates/fastmcp-server/src/middleware.rs` plus built-ins.

| Capability | Implementation |
|------------|----------------|
| Trait hooks | `on_request`, `on_response`, `on_error` (sync) |
| Short-circuit | `MiddlewareDecision::Respond(value)` skips handler |
| Ordering | Request: registration order; response/error: reverse for entered stack |
| Built-ins | `ResponseCachingMiddleware` (TTL per method), `RateLimitingMiddleware` (token bucket), `SlidingWindowRateLimitingMiddleware` |
| Tests | Unit tests in `middleware.rs`; E2E chain in `crates/fastmcp/tests/e2e_middleware.rs` |

Design is intentionally **minimal and synchronous** — fits asupersync cancel semantics without `async_trait` overhead.

### FastRMCP

Location: `fastrmcp-core/src/middleware.rs`, `fastrmcp/src/middleware.rs`.

| Capability | Implementation |
|------------|----------------|
| Trait hooks | `before_request`, `after_response`, `on_error` (**async**) |
| Short-circuit | `before_request` returns `Err` — no typed respond shortcut |
| Ordering | Same onion model; `on_error` runs forward (not reverse) on handler errors |
| Built-ins | `LoggingMiddleware`, `AuthMiddleware`, `RateLimitMiddleware` |
| Tests | Chain order unit test; auth/rate-limit tests **disabled** (Context metadata refactor TODO) |

### Audit verdict

fastmcp_rust middleware is **strictly ahead** for Phenotype needs:

- Short-circuit without error conversion
- Production-grade caching + dual rate-limit strategies
- E2E coverage with real server/client flow
- No pending refactor blocking auth tests

FastRMCP adds only **tracing-based logging ergonomics** and async metadata mutation patterns that do not justify a runtime bridge. Auth/rate-limit there are documented as "simplified" in v0.2.0.

**Status:** ✅ Complete — no middleware cherry-picks recommended.

---

## sd-fastrmcp-02 — SSE patterns

### fastmcp_rust

Location: `crates/fastmcp-transport/src/sse.rs` (~1.4k LOC).

| Aspect | Detail |
|--------|--------|
| Protocol | MCP-standard `event: endpoint` then `event: message` |
| Scope | Framing only — **no bundled HTTP server** |
| Cancel-safety | `Cx::is_cancel_requested()` on read/write |
| Resilience | Line/size limits, keep-alive comments, Last-Event-ID support |
| Tests | Extensive unit + E2E transport flow tests |

### FastRMCP

Location: `fastrmcp/src/transport/sse.rs` (~380 LOC).

| Aspect | Detail |
|--------|--------|
| Protocol | Custom first event: `{"type":"connection","connectionId":"…"}` — **not** MCP `endpoint` event |
| Scope | Full Axum router (`/mcp/sse`, `/mcp/message`) with CORS |
| Multi-client | Per-connection channels via UUID; POST requires `connectionId` |
| Keep-alive | Axum `KeepAlive` (15s interval) |
| Tests | Creation/close only — no wire-format conformance tests |

### SSE verdict

fastmcp_rust already implements **spec-aligned SSE framing** with stronger test coverage. FastRMCP's integrated Axum server is the only differentiator, but its wire protocol diverges from MCP SSE (`endpoint` vs `connectionId` JSON).

Porting Axum integration would require:

1. tokio ↔ asupersync bridge (ADR-017 mitigation: bridge at server boundary)
2. Rewriting event types to MCP-standard `endpoint`/`message`
3. Ongoing maintenance of a 2-star, 7-month-stale dependency tree

**Status:** ✅ Complete — defer Axum/SSE server bundle; prefer substrate/PhenoMCPServers HTTP edges (tier-1 Go) or future fastmcp_rust HTTP adapter.

---

## sd-fastrmcp-03 — Cherry-pick plan

| Candidate | Source | Effort | Value | Decision |
|-----------|--------|--------|-------|----------|
| Logging middleware (tracing) | FastRMCP | Low | Low — fastmcp_rust has hooks; fleet uses substrate tracing | **Reject** |
| Auth bearer middleware | FastRMCP | Medium | Low — tests disabled; metadata API unstable | **Reject** |
| Rate limit middleware | FastRMCP | Medium | None — fastmcp_rust has superior dual-strategy impl | **Reject** |
| Axum SSE router | FastRMCP | High | Medium — convenience only; wrong SSE event shape | **Defer** |
| WebSocket transport | FastRMCP | High | Low — fastmcp_rust has `websocket.rs` framing | **Reject** |
| Middleware chain builder | FastRMCP | Low | Low — `Server::middleware()` already exists | **Reject** |

### If Axum integration is revisited (deferred)

Prerequisites before any pick:

1. Upstream `fastmcp_rust` documents asupersync↔tokio bridge pattern
2. MCP SSE `endpoint` event used (not `connectionId` JSON)
3. FastRMCP shows renewed activity OR PhenoMCPServers dogfood requires Rust HTTP edge

Estimated cost: **3–5 engineer-days** for bridge + rewrite + tests — poor ROI vs Go tier-1 edges today.

**Status:** ✅ Complete — empty cherry-pick queue.

---

## sd-fastrmcp-04 — ADR note

### Alignment with ADR-017

- ✅ PhenoFastMCP-rust parent remains `Dicklesworthstone/fastmcp_rust`
- ✅ FastRMCP classified as **ergonomics cherry-pick source** (PHENO.md table) — evaluation confirms no picks
- ✅ rmcp spec work stays in PhenoRMCP
- ✅ asupersync constraint preserved — no tokio runtime adoption

### Proposed ADR appendix (no new ADR required)

Add to ADR-017 consequences or PhenoFastMCP-rust FORK-NOTES:

> **FastRMCP (JSBtechnologies):** Evaluated 2026-06-17. Closed as merge source. Middleware and MCP-aligned SSE already covered by fastmcp_rust. Axum HTTP integration deferred until upstream bridge exists or fleet mandates Rust HTTP edge.

### Registry

`PhenoMCPServers/catalog/registry.yaml` `framework.rust.parent` = `fastmcp_rust` — no change needed.

**Status:** ✅ Complete — note captured here; FORK-NOTES cross-link sufficient.

---

## sd-fastrmcp-05 — Close or defer

### Recommendation: **CLOSE evaluation**

| Criterion | Outcome |
|-----------|---------|
| Parent correctness (ADR-017) | fastmcp_rust confirmed correct |
| Net new capabilities | None that justify tokio bridge |
| Maintenance burden | High (stale dep, 2 stars, protocol divergence) |
| Superset queue | Empty |
| Re-open trigger | FastRMCP >10 stars + 2026 activity, OR fastmcp_rust upstream adds HTTP adapter |

### Actions taken

1. Document findings in `docs/eval/Fastrmcp.md` (this file)
2. SUPERSET.md checklist item 2 marked **closed**
3. No code cherry-picks to `phenotype/superset`
4. Issue #8 side-DAG `sd-fastrmcp-*` tasks: **done / closed**

### Deferred (not closed forever)

- Axum-integrated MCP HTTP server in Rust — revisit when asupersync bridge is upstream-documented
- Cross-link from PhenoRMCP if streamable HTTP patterns become relevant (different protocol generation)

**Status:** ✅ Complete — **CLOSE** with defer on Axum-only integration.

---

## Summary table

| Task ID | Title | Status | Outcome |
|---------|-------|--------|---------|
| sd-fastrmcp-01 | Middleware audit | ✅ Closed | fastmcp_rust ahead; no picks |
| sd-fastrmcp-02 | SSE patterns | ✅ Closed | MCP-aligned SSE in parent; FastRMCP diverges |
| sd-fastrmcp-03 | Cherry-pick plan | ✅ Closed | Empty queue |
| sd-fastrmcp-04 | ADR note | ✅ Closed | ADR-017 affirmed; appendix text above |
| sd-fastrmcp-05 | Close or defer | ✅ Closed | **CLOSE** eval; defer Axum bundle |

## References

- [ADR-017](https://github.com/KooshaPari/PhenoSpecs/blob/main/adrs/017-mcp-polyrepo-boundaries.md)
- [Dicklesworthstone/fastmcp_rust](https://github.com/Dicklesworthstone/fastmcp_rust)
- [JSBtechnologies/FastRMCP](https://github.com/JSBtechnologies/FastRMCP)
- PhenoFastMCP-rust: `PHENO.md`, `FORK-NOTES.md`, `SUPERSET.md`
- phenodag preset: `mcp-fleet-90` side-DAG `sd-fastrmcp`
