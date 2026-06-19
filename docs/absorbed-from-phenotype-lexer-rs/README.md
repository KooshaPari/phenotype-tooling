# phenotype-lexer-rs

Hexagonal lexer/parser substrate for the Phenotype fleet.

**Absorbed from:** `KooshaPari/NetScript` (deleted 2026-06-18 per ADR-001)
**Original package:** `netscript` v0.1.0
**Layout:** Hexagonal (domain/ports/adapters)
**Status:** SOTA substrate

## Why

NetScript was a complete Rust implementation of a network scripting language with proper hexagonal layout. The repo was small and orphaned. Absorbing into a Phenotype substrate preserves the lexer/parser logic for fleet reuse.

## Architecture

- `src/domain/` — Token types, lexer logic, parser logic (pure)
- `src/ports/` — Port traits (lexer input/output contracts)
- `src/adapters/` — REPL, CLI, file adapters
- `src/app/` — Application orchestration
- `tests/` — Proptest, snapshot, unit, CLI integration tests
- `benches/` — Criterion benchmarks

## Build

```bash
cargo build --release
cargo test
cargo bench
```

## License

MIT (inherited from NetScript)
