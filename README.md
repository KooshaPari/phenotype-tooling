> **Work state:** ACTIVE · **Progress:** `███████░░░ 75%`
> Reusable-workflow federation hub (cargo-deny/trufflehog/journey-gate); cargo-deny converged to one mechanism. · updated 2026-06-02

# phenotype-tooling

[cheap-llm-mcp has moved to the canonical phenotype-ops-mcp provider.](deprecation_notice.md)

[![Build](https://img.shields.io/github/actions/workflow/status/KooshaPari/phenotype-tooling/ci.yml?branch=main&label=build)](https://github.com/KooshaPari/phenotype-tooling/actions)
[![Release](https://img.shields.io/github/v/release/KooshaPari/phenotype-tooling?include_prereleases&sort=semver)](https://github.com/KooshaPari/phenotype-tooling/releases)
[![License](https://img.shields.io/github/license/KooshaPari/phenotype-tooling)](LICENSE)
[![Phenotype](https://img.shields.io/badge/Phenotype-org-blueviolet)](https://github.com/KooshaPari)
[![AI Slop Inside](https://sladge.net/badge.svg)](https://sladge.net)


Consolidated Rust workspace for Phenotype-org developer tooling. It replaces
duplicated shell and Python scripts scattered across repos with a focused set
of clap-based CLIs aligned to the
[scripting language hierarchy](https://github.com/KooshaPari/phenotype-infrakit/blob/main/docs/governance/scripting_policy.md)
(Rust default; no new Bash).

## Overview

`phenotype-tooling` centralizes build verification, code-quality checks,
documentation validation, release support, and software-bill-of-materials
generation into a single Rust workspace. Each crate is independently usable and
can be adopted by other Phenotype repos without copying implementation logic.

## Crates

### Pre-FocalPoint Lift
| Crate | Purpose | Replaces |
|-------|---------|----------|
| [`docs-health`](crates/docs-health/) | Markdown vale/markdownlint + broken-link scanner | `phenodocs/.airlock/lint.sh`, `phenodocs/scripts/check_docs_links.py` |
| [`fr-trace`](crates/fr-trace/) | FR-NNN -> test traceability scanner | `repos/scripts/traceability-check.py` (+3 duplicates) |
| [`quality-gate`](crates/quality-gate/) | Aggregates `cargo fmt`/`clippy`/`test` pass-fail | 30+ duplicated `scripts/quality-gate.sh` files |
| [`legacy-scan`](crates/legacy-scan/) | Detects shell/Python anti-patterns per scripting policy | `docs/governance/scripting_policy.md` rubric |

### FocalPoint Lift (10 tools from Section 6 of PLAN.md)
| Crate | Purpose | Source |
|-------|---------|--------|
| [`agent-orchestrator`](crates/agent-orchestrator/) | Multi-lane agent task dispatcher and state tracker | FocalPoint `tooling/agent-orchestrator/` |
| [`audit-privacy`](crates/audit-privacy/) | iOS privacy manifest auditing (scope: Apple plist analysis) | FocalPoint `apps/ios/FocalPoint/scripts/audit-privacy/` |
| [`bench-guard`](crates/bench-guard/) | Benchmark regression detection and thresholds | FocalPoint `tooling/bench-guard/` |
| [`commit-msg-check`](crates/commit-msg-check/) | Enforces conventional commits + linkage rules | FocalPoint `tooling/commit-msg-check/` |
| [`doc-link-check`](crates/doc-link-check/) | Validates markdown links without crawling | FocalPoint `tooling/doc-link-check/` |
| [`fr-coverage`](crates/fr-coverage/) | Functional Requirement test coverage analyzer | FocalPoint `tooling/fr-coverage/` |
| [`release-cut`](crates/release-cut/) | Automated semver release and changelog generation | FocalPoint `tooling/release-cut/` |
| [`sbom-gen`](crates/sbom-gen/) | SBOM (CycloneDX/SPDX) generation from Cargo.lock | FocalPoint `tooling/sbom-gen/` |
| [`fuzz-setup`](crates/fuzz-setup/) | Fuzzing corpus reference and setup templates | FocalPoint `fuzz/` |

### Absorbed standalone tooling

Full upstream repos absorbed under `crates/` (history-preserving subtree merges).
These are NOT Rust workspace members — each keeps its own build system. Do not
force a single toolchain; build each from its own subdir.

| Subdir | Upstream | Stack | Build / install (cheap sanity) |
|--------|----------|-------|--------------------------------|
| [`crates/worktree-manager`](crates/worktree-manager/) | `KooshaPari/worktree-manager` | Rust (workspace member) | `cargo build -p worktree-manager` |
| [`crates/byteport`](crates/byteport/) | `KooshaPari/BytePort` | TS frontend + Rust/Go backend | per-subdir: `npm ci` (frontend), backend per its README |
| [`crates/heliosapp`](crates/heliosapp/) | `KooshaPari/heliosApp` | TS (Electrobun) | `npm ci` |
| [`crates/heliosbench`](crates/heliosbench/) | `KooshaPari/heliosBench` | TS | `npm ci` |
| [`crates/nanovms`](crates/nanovms/) | `KooshaPari/nanovms` | Rust crate (standalone) | `cargo build` inside subdir |
| [`crates/policystack`](crates/policystack/) | `KooshaPari/PolicyStack` | TS (`package.json`) + Python (`pyproject.toml`, `policy-federation`) | `npm ci`; `uv pip install -e .` (or `pip install -e .`) |

> **PolicyStack note:** absorbed via `git filter-repo` after dropping 8 empty
> glob-artifact files (`scripts/federation/f2{01..16}_*`) whose `*` in the
> filename is illegal on NTFS and blocked the earlier subtree merge (PR #78).
> Upstream repo-hygiene fix recommended: `git rm` those 8 empty stubs at source.

## Migration plan

1. **Scaffold (this repo):** clap skeletons emitting stub JSON reports.
2. **Port logic:** port each source script into its crate, preserving exit
   codes and expected output; retain the shell script as a thin wrapper calling
   the Rust binary during the transition.
3. **Roll out:** replace `scripts/quality-gate.sh` in each consumer repo with
   a one-line shim that invokes the released `quality-gate` binary; then
   delete the shim once CI is green.
4. **Decommission:** remove the Python `traceability-check.py` and
   `check_docs_links.py` variants.

Target consumer repos (partial list):
`AgilePlus`, `HexaKit`, `PhenoKits`, `heliosApp`, `Civis`, `PolicyStack`,
`thegent`, `portage`, `phenodocs`, `Pyron`, `phenoDesign`.

## Install

Each binary can be installed independently via `cargo install`:

```bash
# Install a single tool
cargo install --path crates/quality-gate

# Or install all tools
for crate in agent-orchestrator bench-guard commit-msg-check doc-link-check fr-coverage release-cut sbom-gen fuzz-setup; do
  cargo install --path crates/$crate
done

# Verify installed
cargo install --list
```

## Adoption in Other Repos

Use the provided `scripts/adopt-tooling.sh` to symlink phenotype-tooling binaries into any Phenotype repo:

```bash
# In your target repo
cd /path/to/my-repo
bash /path/to/phenotype-tooling/scripts/adopt-tooling.sh

# Now you can use tools from tooling/ symlinks
./tooling/quality-gate
./tooling/fr-coverage --help
```

## Build

```bash
cargo check --workspace
cargo test --workspace
cargo clippy --workspace -- -D warnings
cargo fmt --check
cargo build --release --workspace
```

## Governance & Worklogs

- `CLAUDE.md` documents repo-specific conventions and workspace rules.
- `AGENTS.md` gives AI agents the local routing and quality-gate pointers.
- `worklogs/` captures repo-local research, architecture, and governance notes.
- `CHANGELOG.md` tracks release-visible changes.

## License

MIT. See [LICENSE](LICENSE).
