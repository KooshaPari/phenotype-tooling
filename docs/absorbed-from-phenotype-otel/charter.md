# Charter — phenotype-otel

> **Boundary class:** sdk-domain  
> **Role:** observe  
> **Lifecycle:** active  
> **Genesis template:** HexaKit `templates/genesis/` v1.0.0

## Mission

Thin OTLP init bridge (`pheno_otel::init`) — no tracing domain logic.

## Scope

### In scope

- OTLP HTTP exporter + tracing-subscriber registry bootstrap
- Optional shutdown / re-export surface only

### Out of scope

| Boundary | Owner repo |
|----------|------------|
| Traceon hexagonal core / tracingkit | `PhenoObservability` |
| Python observability-kit facade | `phenotype-python-sdk` |
| Genesis templates | `HexaKit` |

## Governance artifacts

| Artifact | Path |
|----------|------|
| Intent | [intent.md](intent.md) |
| Review | [review.md](review.md) |
| SOTA | [SOTA.md](SOTA.md) |
| OKF | [okf/manifest.okf.yaml](okf/manifest.okf.yaml) |

Authority: [phenotype-registry DOMAIN_ROLES](https://github.com/KooshaPari/phenotype-registry/blob/main/DOMAIN_ROLES.md)

## Decision rights

| Action | Authority |
|--------|-----------|
| Merge to `main` | KooshaPari + 1 reviewer |

## Changelog

| Date | Change |
|------|--------|
| 2026-06-17 | Genesis rollout Wave 4 |
