# SOTA — phenotype-go-sdk

> **Last researched:** 2026-06-16  
> **Methods:** ADR-011 Go convergence audit, PlatformKit absorption review, phenotype-registry LANGUAGE_PLACEMENT, internal dogfood

## Executive summary

| Dimension | Our choice | Confidence | Deep dive |
|-----------|------------|------------|-----------|
| Technical | Go workspace monorepo for platform modules | high | [docs/sota/technical.md](docs/sota/technical.md) |
| DX | `go work sync` + per-package README | med | [docs/sota/dx.md](docs/sota/dx.md) |
| UX | N/A (library/SDK repo) | n/a | [docs/sota/ux.md](docs/sota/ux.md) |
| AX | Genesis doc set + charter scope for Go packages | high | [docs/sota/ax.md](docs/sota/ax.md) |
| Security | Kilo Code Stand + secret scan in CI | med | [docs/sota/security.md](docs/sota/security.md) |
| Ops | Targeted `go test` per changed package | med | [docs/sota/ops.md](docs/sota/ops.md) |
| Cost | One Go SDK workspace vs N PlatformKit repos | high | [docs/sota/cost.md](docs/sota/cost.md) |

## Why this is optimal (for our constraints)

Go is a **Tier 3 justified edge** for the `platform` role: devhex/devenv modules already exist in Go, K8s/dev-tooling ecosystem alignment, and absorption of PlatformKit/McpKit Go surfaces is cheaper than a Rust rewrite. Consolidating into `phenotype-go-sdk` with genesis governance prevents duplicate module paths and gives agents a single charter boundary.

## Fork status

- **Is fork:** no

## Evolution triggers

Re-open research when:

- McpKit Go workspace modules are restored — re-evaluate monorepo vs split
- Rust platform crate covers devenv with parity — revisit Go necessity
- Upstream Go module policy changes (e.g. workspace std) affect layout

## Linkage

- Charter scope: [charter.md](charter.md)
- Review enforcement: [review.md](review.md)
- Intent goals: [intent.md](intent.md)
