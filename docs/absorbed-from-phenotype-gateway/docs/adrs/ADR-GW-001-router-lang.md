# ADR-GW-001 — Router implementation language

**Status:** accepted (spike)  
**Date:** 2026-06-18  
**Wave:** H13

## Context

OmniRoute is interim TypeScript MVP. Long-term router logic belongs in phenotype-gateway `packages/router`, not OmniRoute.

## Decision

| Lane | Language | Role |
|------|----------|------|
| **Primary** | Rust (`spikes/rust/router`) | Combo routing, scoring, `/v1` delegate design |
| **Integration** | Go | cliproxy++/agentapi++/bifrost submodule planes |
| **Alt perf** | Zig (`spikes/zig/router`) | Optional fallback-chain hot path |
| **ML scoring** | Mojo (`spikes/mojo/router`) | Auto-combo factor experiments only |

## Consequences

- Do not rebuild cliproxy/agentapi/bifrost in Rust piecemeal
- OmniRoute remains canonical **route peer** until revamp spike passes parity checklist
- Promotion gated by [GATEWAY_FEATURE_PARITY.md](https://github.com/KooshaPari/phenotype-registry/blob/main/docs/rationalization/GATEWAY_FEATURE_PARITY.md)
