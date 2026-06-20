# ARCHITECTURE.md — pheno-errors

## Overview

`pheno-errors` is a dependency-light Rust crate that provides the canonical `AppError` type used across the `pheno-*` fleet. It consolidates the 5 most-common error patterns observed in the L1/L2 fleet audit (2026-06-10) into a single enum.

## Design

### Core Type

```rust
pub enum AppError {
    Domain(String),
    NotFound { entity: String, id: String },
    Conflict(String),
    Validation(String),
    Storage(String),
}
```

The enum is intentionally closed (no `#[non_exhaustive]`) so that `match` exhaustiveness checks are useful at consumer call sites.

### Key Decisions

- **Built on `thiserror`** for `Display` + `Error` derives — no per-variant boilerplate.
- **Drops into `anyhow`** via the blanket `impl From<T: Error> for anyhow::Error`.
- **Provides `From` impls** for `std::io::Error` => `Storage`, `anyhow::Error` => `Domain`, `&str`/`String` => `Domain`.
- **No blanket `From<E: Error>`** — avoids coherence conflicts with the concrete `std::io::Error` impl.

### Consumers

Consumed by L5 #81–85 across the `pheno-*` fleet.

## Dependencies

| Crate      | Purpose                           |
|------------|-----------------------------------|
| `thiserror`| Derive `Error` + `Display`        |
| `anyhow`   | Context/error wrapping interop    |
| `tracing`  | Structured logging helpers        |
