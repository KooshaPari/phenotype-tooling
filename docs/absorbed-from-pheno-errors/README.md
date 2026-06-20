# pheno-errors

Canonical `AppError` type for the `pheno-*` fleet. Consolidates the 5 most-common
error patterns into a single, dependency-light crate.

## Quick Start

```toml
[dependencies]
pheno-errors = "0.1"
```

```rust
use pheno_errors::AppError;

fn do_thing() -> Result<(), AppError> {
    Err(AppError::NotFound("resource".into()))
}
```

## Design

- **5-variant `AppError` enum** — closed, no `#[non_exhaustive]`
- **No blanket `From<E: Error>`** — explicit error mapping
- **Structured context** via `Kind()` method — no string parsing for routing
- **Minimal dependencies**: `thiserror` + `anyhow` + `tracing`

See [`SPEC.md`](SPEC.md) and [`ARCHITECTURE.md`](ARCHITECTURE.md) for details.

## License

MIT — see [LICENSE](LICENSE).
