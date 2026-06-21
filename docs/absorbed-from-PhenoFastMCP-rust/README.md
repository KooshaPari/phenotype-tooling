# PhenoFastMCP-rust

FastMCP (Model Context Protocol) substrate for the Phenotype fleet.

**Absorbed from:** `KooshaPari/McpKit/rust/` (deprecated 2026-06-17 per ADR-017)
**Status:** SOTA substrate

## Tenets

McpKit's charter tenets are inherited and continued here (per McpKit ADR-017 retirement and absorption):

1. **First-Class Extensibility** — The framework must make it easy to add new transports, protocols, and server types without modifying core code.
2. **Isolation by Default** — Every server, client, and transport must be independently testable and deployable.
3. **Declarative Configuration** — All server and client configuration must be expressible in a standard format (YAML/JSON) without code changes.
4. **Observable Integration** — Every component must expose structured metrics, tracing, and health check endpoints.
5. **Semantic Versioning Contracts** — All public interfaces must follow semantic versioning with clear compatibility guarantees.
6. **Graduated Quality Gates** — Code must pass automated quality gates (lint, type-check, test, audit) before integration.

## Crates

- `phenotype-mcp-core` — Core MCP types and traits
- `phenotype-mcp-asset` — Asset/transport layer
- `phenotype-mcp-fast` — FastMCP implementation (Rust binding)
- `phenotype-mcp-fast-macros` — Procedural macros for trait derivation
- `mcp-forge` — Code-gen tooling

## Build

```bash
cargo build --release --workspace
cargo test --workspace
```

## License

MIT OR Apache-2.0 (inherited from McpKit)
