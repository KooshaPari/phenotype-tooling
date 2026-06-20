# Rust spike — router revamp (OmniRoute successor)

**Interim MVP:** [OmniRoute](https://github.com/KooshaPari/OmniRoute) — not long-term canonical.

## Goal

Replace OmniRoute interim TS router with non-sloppy Rust (or Zig) implementation.

## Features to port (from parity matrix)

- Combo routing (14 strategies, Auto-combo)
- Multi-provider OpenAI-compatible gateway
- MCP tool surface (subset)
- Deploy: defer to phenotype-gateway ops docs

## Status

`spikes/rust/router/` — **H13 scaffold**: `Cargo.toml`, `RouterPlane` trait sketch, unit test.
