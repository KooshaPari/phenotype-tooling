# Charter — phenotype-go-sdk

> **Boundary class:** sdk-domain  
> **Role:** platform  
> **Lifecycle:** active  
> **Genesis template:** HexaKit `templates/genesis/` v1.0.0

## Mission

Consolidated Go platform modules (devhex, devenv abstractions, MCP Go workspace) for Phenotype-org — the canonical Go edge for the `platform` domain role.

## Scope

### In scope

- `packages/devhex/` — hexagonal Go library for dev environment abstractions (`github.com/KooshaPari/devenv-abstraction`)
- `packages/mcpkit/` — MCP framework Go workspace (when modules restored)
- `packages/platformkit/` — docs/specs for absorbed PlatformKit boundary
- Root `go.work` — workspace orchestration across Go packages
- Genesis governance: intent, charter, review, SOTA, OKF

### Out of scope

| Boundary | Owner repo |
|----------|------------|
| Python domain kits (auth, MCP, testing, observability) | `phenotype-python-sdk` |
| Rust developer tooling, CI wrappers, absorbed apps | `phenotype-tooling` |
| Static analysis runtime | `KodeVibe` |
| LLM validation | `kwality` |
| Genesis templates and bootstrap scaffolds | `HexaKit` |
| Application / product logic | product repos |
| Fleet registry and domain role authority | `phenotype-registry` |

## Governance artifacts

| Artifact | Path |
|----------|------|
| Intent | [intent.md](intent.md) |
| Review (Kilo Code Stand) | [review.md](review.md) |
| SOTA | [SOTA.md](SOTA.md) |
| OKF manifest | [okf/manifest.okf.yaml](okf/manifest.okf.yaml) |

Specs: [HexaKit docs/genesis/STANDARD.md](https://github.com/KooshaPari/HexaKit/blob/main/docs/genesis/STANDARD.md)

## Decision rights

| Action | Authority |
|--------|-----------|
| Merge to `main` | KooshaPari + 1 reviewer |
| Agent-authored PR | Allowed per [review.md](review.md) |
| Scope expansion | Charter amendment + intent synthesis update |
| New Go module without SOTA | **Blocked** — requires `docs/sota/technical.md` Tier 3 justification |

**Agent autonomy:** Level 2 — agents may edit packages/docs within charter scope; new Go surfaces need SOTA paragraph.

## Dependencies

- Genesis bootstrap: HexaKit templates version `v1.0.0`
- Absorbed sources: PlatformKit, McpKit (Go side)
- Fleet registry: `phenotype-registry` (`platform` role)

## Retirement

If this repo is absorbed: require **100% boundary coverage** in a single canonical owner before delete. Update `phenotype-registry` and OKF manifest.

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-06-16 | Initial charter from genesis template | agent |

## Attestation

This charter supersedes informal README scope claims. On conflict, charter wins.
