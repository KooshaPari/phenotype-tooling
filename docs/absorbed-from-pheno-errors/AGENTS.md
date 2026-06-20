# AGENTS.md — pheno-errors

This file contains onboarding and operational context for AI agents working on this repository.

## Purpose

`pheno-errors` provides the canonical `AppError` type for the `pheno-*` fleet. It is a dependency-light crate focused on the 5 most-common error patterns.

## Key Constraints

- The 5-variant `AppError` enum is **closed** (no `#[non_exhaustive]`) — growing past 5 is a breaking change.
- No blanket `From<E: Error>` impl — callers must explicitly map their error types.
- Keep dependencies minimal — only `thiserror`, `anyhow`, and `tracing` in production.

## Design Principles

1. **Explicit boundaries**: No silent error conversions.
2. **Lean dependencies**: Avoid pulling in heavy frameworks.
3. **Structured context**: `Kind()` method enables routing to metrics/logs without string parsing.

## Stack

- **Language**: Rust (edition 2021)
- **CI**: cargo test, clippy, fmt on ubuntu-latest
- **Security**: cargo-audit (weekly), cargo-deny (weekly), CodeQL, OpenSSF Scorecard
