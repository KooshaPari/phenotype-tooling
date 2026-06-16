# Archived skeleton repos — absorption history

This directory documents migrations from archived KooshaPari skeleton libraries
into `phenotype-tooling` crates.

## Absorptions

| Source repo | Target crate | Migration date | Notes |
|-------------|--------------|----------------|-------|
| [KooshaPari/Diffuse](https://github.com/KooshaPari/Diffuse) | `crates/phenotype-diff` | 2026-06-16 | Line-level unified diff and patch apply (`patch` crate intent). See `phenotype-diff/src/lib.rs`. |
| [KooshaPari/phenoPatch](https://github.com/KooshaPari/phenoPatch) | `crates/phenotype-diff` | 2026-06-16 | Same absorption target as Diffuse; patch/diff primitives consolidated. |
| [KooshaPari/Servion](https://github.com/KooshaPari/Servion) | `crates/phenotype-service-registry` | 2026-06-16 | Service registration, discovery, and health (`nexus` crate intent). See `phenotype-service-registry/src/lib.rs`. |
| [KooshaPari/Guardrail](https://github.com/KooshaPari/Guardrail) | `crates/phenotype-resilience` | 2026-06-16 | Resilience primitives (rate limiter, circuit breaker, bulkhead). Also seeded from tracely-sentinel per hexagonal audit. |

## Deletion readiness

The source repositories listed above are cleared for deletion once this note is
merged and the corresponding crate implementations are present on `main`.
