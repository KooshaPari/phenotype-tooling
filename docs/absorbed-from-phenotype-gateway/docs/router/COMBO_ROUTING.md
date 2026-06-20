# Combo routing — extracted from OmniRoute interim MVP

> **Source:** [OmniRoute `docs/routing/AUTO-COMBO.md`](https://github.com/KooshaPari/OmniRoute/blob/main/docs/routing/AUTO-COMBO.md)  
> **Target owner:** `packages/router` revamp (`spikes/rust/router` primary)

## Scope for gateway revamp

OmniRoute implements **14 routing strategies** with **Auto-combo 9-factor scoring** and zero-config `auto/` prefix routing. phenotype-gateway must **not** fork OmniRoute piecemeal; extract spec here and reimplement in Rust/Zig spike.

## Auto-combo variants (subset)

| Model ID | Behavior |
|----------|----------|
| `auto` | All connected providers, LKGP, balanced weights |
| `auto/coding` | Quality-first for code generation |
| `auto/fast` | Low-latency weighted selection |
| `auto/cheap` | Cost-optimized |
| `auto/offline` | Quota-availability first |
| `auto/smart` | Quality-first + higher exploration |

## Revamp requirements

1. Virtual combo built in-memory per request (no DB persistence for interim path)
2. Multi-account aware: each provider connection is a candidate
3. Session stickiness via LKGP (last-known-good provider)
4. OpenAI-compatible `/v1/chat/completions` entry — delegate provider HTTP to cliproxy++ plane (`spikes/rust/router/src/delegate.rs`)
5. Scoring factors port to Rust (`spikes/rust/router`) or Mojo experiment lane

## Non-goals (defer)

- Full OmniRoute Next.js dashboard
- 37-tool MCP surface (see [MCP_SUBSET.md](./MCP_SUBSET.md))
