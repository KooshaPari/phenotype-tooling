# SPEC.md — pheno-errors

## Name

`pheno-errors` — Canonical `AppError` type for the `pheno-*` fleet.

## Version

0.1.0

## License

MIT

## Purpose

Provide a single, dependency-light error type that consolidates the 5 most-common error patterns across the fleet.

## Variants

| Variant | Meaning | Wire code |
|---------|---------|-----------|
| `Domain` | Invariant / business-rule violation | `INTERNAL_ERROR` / `INVALID_ARGUMENT` |
| `NotFound` | Entity lookup failure | `NOT_FOUND` |
| `Conflict` | Optimistic-concurrency / duplicate | `ALREADY_EXISTS` / `CONFLICT` |
| `Validation` | Input validation failure | `VALIDATION_ERROR` / `INVALID_ARGUMENT` |
| `Storage` | Persistence / I/O failure | `INTERNAL_ERROR` |

## Traits

- `AppError` implements `std::error::Error`, `std::fmt::Display` (via `thiserror`).
- `AppResult<T>` is a type alias for `Result<T, AppError>`.

## Conversions

- `std::io::Error` => `AppError::Storage`
- `&'static str` => `AppError::Domain`
- `String` => `AppError::Domain`
- `anyhow::Error` => `AppError::Domain` (preserves cause chain)
