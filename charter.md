# Charter — phenotype-tooling

> **Boundary class:** tooling  
> **Role:** platform/tooling  
> **Lifecycle:** active  
> **Genesis template:** HexaKit `templates/genesis/` v1.0.0

## Mission

Consolidated Rust workspace and absorbed developer tooling for Phenotype-org — CI wrappers, quality gates, release support, and standalone tools merged under the `platform/tooling` domain role.

## Scope

### In scope

- Rust workspace crates (`docs-health`, `quality-gate`, `fr-trace`, `release-cut`, `sbom-gen`, etc.)
- Absorbed standalone tools under `crates/` (byteport, heliosapp, nanovms, policystack, worktree-manager)
- Reusable GitHub workflow federation (cargo-deny, trufflehog, journey-gate)
- Templates: `just/`, `hooks/`, `templates/`
- Genesis governance: intent, charter, review, SOTA, OKF

### Out of scope

| Boundary | Owner repo |
|----------|------------|
| Go platform modules (devhex, devenv) | `phenotype-go-sdk` |
| Python domain kits | `phenotype-python-sdk` |
| Static analysis runtime (vibes engine) | `KodeVibe` |
| LLM validation | `kwality` |
| Genesis templates and bootstrap scaffolds | `HexaKit` |
| Application / product logic | product repos |
| nanovms VM runtime in production fleets | consumer repos (tooling ships the crate) |

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
| New absorbed repo subtree | Absorption proof + registry update |

**Agent autonomy:** Level 2 — agents may edit crates/docs within charter; new absorbed tools need charter row.

## Dependencies

- Genesis bootstrap: HexaKit templates version `v1.0.0`
- Scripting policy: Rust default per phenotype-infrakit governance
- Fleet registry: `phenotype-registry` (`platform/tooling` role)

## Retirement

If this repo is absorbed: require **100% boundary coverage** in a single canonical owner before delete. Update `phenotype-registry` and OKF manifest.

## Changelog

| Date | Change | Author |
|------|--------|--------|
| 2026-06-16 | Initial charter from genesis template | agent |

## Attestation

This charter supersedes informal README scope claims. On conflict, charter wins.
