<!-- AI-DD-META:START -->
<!-- This repository is planned, maintained, and managed by AI Agents only. -->
<!-- Slop issues are expected and intentionally present as part of an HITL-less -->
<!-- /minimized AI-DD metaproject of learning, refining, and building brute-force -->
<!-- training for both agents and the human operator. -->
![Downloads](https://img.shields.io/github/downloads/KooshaPari/phenotype-dep-guard/total?style=flat-square&label=downloads&color=blue)
![GitHub release](https://img.shields.io/github/v/release/KooshaPari/phenotype-dep-guard?style=flat-square&label=release)
![License](https://img.shields.io/github/license/KooshaPari/phenotype-dep-guard?style=flat-square)
![AI-Slop](https://img.shields.io/badge/AI--DD-Slop%20Expected-orange?style=flat-square)
![AI-Only-Maintained](https://img.shields.io/badge/Planned%20%26%20Maintained%20by-AI%20Agents%20Only-red?style=flat-square)
![HITL-less](https://img.shields.io/badge/HITL--less%20AI--DD-metaproject-yellow?style=flat-square)

> ⚠️ **AI-Agent-Only Repository**
>
> This repo is **planned, maintained, and managed exclusively by AI Agents**.
> Slop issues, rough edges, and AI artifacts are **expected and intentionally
> present** as part of an **HITL-less / minimized AI-DD** metaproject focused
> on learning, refining, and brute-force training both the agents and the
> human operator. Bug reports and contributions are still welcome, but please
> expect AI-generated code, comments, and documentation throughout.
<!-- AI-DD-META:END -->
## Work State

| Field | Value |
|---|---|
| Last commit | 2026-06-08 |
| Open issues | 4 |
| Open PRs | 2 |
| Focus | Phenotype-org dependency policy, supply-chain guardrails, and CI gate enforcement |

Progress: ████████░░ 80%

> **Work state:** ACTIVE · **Progress:** `████████░░ 80%`
> Consolidated Python SDK (6 kits); de-nested pheno-kits; next: publish to PyPI per ADR-011. · updated 2026-06-02

# phenotype-python-sdk

Monorepo of Phenotype org Python (and polyglot) SDK kits, consolidated from standalone kit repositories.

## Workspace kits

| Kit | Path | Role |
|-----|------|------|
| **mcp-kit** | `packages/mcp-kit` | Model Context Protocol tooling (Python, Rust, Go) |
| **testing-kit** | `packages/testing-kit` | QA, quality CLI, analysis, and test harnesses |
| **auth-kit** | `packages/auth-kit` | Authentication and security helpers |
| **resilience-kit** | `packages/resilience-kit` | Deploy, CI/CD, and resilience utilities |

### Python sub-projects (under kits)

- `packages/testing-kit/python/` — `qa-kit`, `pheno-testing-cli`, `pheno-quality-tools`, `pheno-quality-cli`, `pheno-analysis-cli`, `mcp-qa`
- `packages/resilience-kit/python/` — `deploy-kit`, `ci-cd-kit`, `pheno-deploy`

See each package’s `README.md` and `pyproject.toml` for install and usage.

## Development

Root `pyproject.toml` documents the workspace layout. Per-package tooling may use Poetry, setuptools, or Hatch — follow the kit you are changing.

```bash
cd packages/<kit>/python   # when applicable
# use that package's documented install (poetry install, pip install -e ., etc.)
```

## License

MIT — see [LICENSE](LICENSE).
# phenotype-go-sdk

Phenotype-org Go SDK — consolidates Go Kit/SDK packages from the KooshaPari org.

## Packages

| Path | Source | Description |
|------|--------|-------------|
| \packages/devhex\ | [DevHex](https://github.com/KooshaPari/DevHex) | Hexagonal Go library for dev environment abstractions (module `github.com/KooshaPari/devenv-abstraction`). The single canonical Go module in the workspace. |
| \packages/platformkit\ | [PlatformKit](https://github.com/KooshaPari/PlatformKit) | Docs/specs only. Its Go code (`go/devenv`, `go/devhex`) was a broken duplicate of `devhex` and was removed (see Workspace notes). |
| \packages/mcpkit\ | [McpKit](https://github.com/KooshaPari/McpKit) | MCP framework SDK (Go workspace) — deferred (see notes). |

Use `go work sync` from the repo root to build across packages.

## Workspace notes

- `go.work` includes only `packages/devhex` — it builds and tests clean and is
  the single source of the devenv/devhex modules.
- The two duplicate copies under `packages/platformkit/go/` were **removed**
  (2026-06-02, ADR-011 Go convergence): `platformkit/go/devhex` was a
  byte-divergent dup of `packages/devhex` claiming the same module path, and
  `platformkit/go/devenv` was an older lowercase-path copy that did not compile.
- `packages/mcpkit/go/go.work` references missing `pheno-mcp-*` modules — Go MCP
  packages deferred until restored.
> **Pinned references (Phenotype-org)**
> - MSRV: see rust-toolchain.toml
> - cargo-deny config: see deny.toml
> - cargo-audit: rustsec/audit-check@v2 weekly
> - Branch protection: 1 reviewer required, no force-push
> - Authority: phenotype-org-governance/SUPERSEDED.md

# PhenoUtils

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![FR Coverage](https://github.com/KooshaPari/phenoUtils/actions/workflows/fr-coverage.yml/badge.svg)](https://github.com/KooshaPari/phenoUtils/actions/workflows/fr-coverage.yml)
[![Rust](https://img.shields.io/badge/rust-1.75%2B-orange.svg)](https://www.rust-lang.org)

Essential utilities and foundational crates for the Phenotype ecosystem. Provides CLI shells, filesystem abstractions, cryptographic operations, network utilities, and testing helpers used across all Phenotype services and tools.

## Overview

**PhenoUtils** is the foundational utilities library for the Phenotype platform, providing battle-tested implementations of common patterns: interactive shells, filesystem abstractions with async support, cryptographic operations, network utilities, and comprehensive testing helpers. All crates are zero-dependency where possible, thoroughly tested, and designed for high-performance, production use.

**Core Mission**: Eliminate utility boilerplate across Phenotype services by providing reusable, well-tested foundational crates that handle complexity transparently.

## Technology Stack

- **Language**: Rust (edition 2021)
- **Async Runtime**: Tokio for async filesystem and network operations
- **Cryptography**: ring for cryptographic primitives, argon2 for password hashing
- **Testing**: criterion for benchmarking, proptest for property testing
- **Build**: Cargo workspace with shared dependency versions

## Key Features

- **CLI Shell Framework**: Interactive shell builder with command parsing, completions, history
- **Filesystem Utilities**: Async file I/O, recursive operations, atomic writes, path utilities
- **Cryptographic Operations**: Hashing, encryption, signing, HMAC, key derivation
- **Network Utilities**: TCP/UDP helpers, connection pooling, DNS resolution, TLS support
- **Testing Helpers**: Fixtures, temporary files/directories, mock implementations, property generators
- **Error Handling**: Rich error types with context, automatic `?` operator support
- **Performance**: Zero-copy where possible, memory pooling, efficient string handling

## Quick Start

```bash
# Clone and explore
git clone <repo-url>
cd phenoUtils

# Review governance and architecture
cat CLAUDE.md          # Project governance
cat AGENTS.md          # Agent operating contract

# Build all crates
cargo build --workspace

# Run comprehensive test suite
cargo test --workspace

# Run benchmarks
cargo bench --workspace

# Lint and format
cargo clippy --workspace -- -D warnings
cargo fmt --check

# Explore crate examples
ls -la crates/
```

## Project Structure

```
phenoUtils/
├── crates/
│   ├── pheno-shell/            # Interactive CLI shell framework
│   │   ├── src/
│   │   │   ├── shell.rs        # Shell builder and REPL
│   │   │   ├── parser.rs       # Command parsing
│   │   │   ├── completions.rs  # Tab completion engine
│   │   │   └── history.rs      # Command history management
│   │   └── examples/
│   ├── pheno-fs/               # Async filesystem abstractions
│   │   ├── src/
│   │   │   ├── file.rs         # Async file operations
│   │   │   ├── dir.rs          # Directory traversal
│   │   │   ├── atomic.rs       # Atomic write semantics
│   │   │   └── permissions.rs  # Fine-grained access control
│   │   └── tests/
│   ├── pheno-crypto/           # Cryptographic operations
│   │   ├── src/
│   │   │   ├── hash.rs         # Hashing (SHA-256, BLAKE3)
│   │   │   ├── encrypt.rs      # Symmetric encryption (AES-256)
│   │   │   ├── sign.rs         # Digital signatures (Ed25519)
│   │   │   ├── kdf.rs          # Key derivation (Argon2)
│   │   │   └── hmac.rs         # Message authentication
│   │   └── benches/
│   ├── pheno-net/              # Network utilities
│   │   ├── src/
│   │   │   ├── tcp.rs          # TCP connection helpers
│   │   │   ├── udp.rs          # UDP utilities
│   │   │   ├── pool.rs         # Connection pooling
│   │   │   ├── dns.rs          # DNS resolution
│   │   │   └── tls.rs          # TLS configuration
│   │   └── tests/
│   ├── pheno-testing/          # Testing utilities
│   │   ├── src/
│   │   │   ├── fixtures.rs     # Test fixture builders
│   │   │   ├── tempdir.rs      # Temporary directories
│   │   │   ├── mocks.rs        # Mock implementations
│   │   │   └── generators.rs   # Property test generators
│   │   └── tests/
│   └── Cargo.toml              # Workspace manifest
├── docs/
│   ├── ARCHITECTURE.md         # Design and patterns
│   ├── CRATE_GUIDE.md          # Per-crate usage guide
│   └── BENCHMARKS.md           # Performance characteristics
├── benches/
│   ├── crypto_perf.rs
│   ├── fs_perf.rs
│   └── network_perf.rs
└── Cargo.toml                  # Root workspace config
```

## Crate Reference

| Crate | Purpose | Stability |
|-------|---------|-----------|
| **pheno-shell** | Interactive CLI shell builder | Stable |
| **pheno-fs** | Async filesystem abstractions | Stable |
| **pheno-crypto** | Cryptographic operations | Stable |
| **pheno-net** | Network utilities and pooling | Stable |
| **pheno-testing** | Testing helpers and mocks | Stable |

## Related Phenotype Projects

- **PhenoLibs**: Shared data structures and algorithms
- **phenotype-tooling**: CLI tools built on pheno-shell
- **Tracera**: Observability (uses pheno-net for metrics export)
- **phenotype-ops-mcp**: MCP server (uses pheno-crypto for token management)

## License

MIT — see [LICENSE](./LICENSE).
# phenotype-infra

[![Build](https://img.shields.io/github/actions/workflow/status/KooshaPari/phenotype-infra/quality-gate.yml?branch=main&label=build)](https://github.com/KooshaPari/phenotype-infra/actions)
[![Release](https://img.shields.io/github/v/release/KooshaPari/phenotype-infra?include_prereleases&sort=semver)](https://github.com/KooshaPari/phenotype-infra/releases)
[![License](https://img.shields.io/github/license/KooshaPari/phenotype-infra)](LICENSE)
[![Phenotype](https://img.shields.io/badge/Phenotype-org-blueviolet)](https://github.com/KooshaPari)
[![AI Slop Inside](https://sladge.net/badge.svg)](https://sladge.net)


Canonical home for Phenotype-org infrastructure-as-code, architectural decision records (ADRs), specifications, and operational runbooks. Supports the **7-node hybrid compute mesh** spanning Oracle Cloud, GCP, AWS, Cloudflare, and a Tailscale-attached home desktop.

## Overview

`phenotype-infra` is the single source of truth for:

- **Network topology** — Tailscale-based control plane across 7 nodes (OCI primary/secondary, GCP e2-micro, AWS Lambda webhooks, Cloudflare Workers/Tunnel, home Mac runner, and a Hetzner spillover reserved for Phase 2).
- **Runner routing** — Forgejo + Woodpecker CI with label-based dispatch (`[self-hosted, heavy, home]` vs `[self-hosted, oci]`).
- **Credential management** — Vaultwarden as canonical credential store, rotation policy documented in `docs/governance/security-policy.md`.
- **Rollback kill-switch** — Every node has a documented path back to GitHub Actions / disable procedure.

## Quick-start

```bash
# 1. Clone + read the topology
git clone git@github.com:KooshaPari/phenotype-infra.git
cd phenotype-infra
cat docs/specs/compute-mesh-spec.md

# 2. Read the top ADRs in order
ls docs/adr/

# 3. Bring up OCI primary (Day-1)
cat docs/runbooks/day1-oci-first-light.md

# 4. Register home-desktop runner (Day-1)
cat docs/runbooks/day1-home-runner-setup.md
```

## Operational status (2026-04-24)

- **Windows desktop heavy runner** — operational. Service `actions.runner.KooshaPari-phenotype-tooling.desktop-kooshapari-desk` registered and idle on the home Mac. Install procedure (with the gotchas that surfaced live: em-dash → ASCII, alphanumeric password, 48-char Description cap, unquoted `-OrgUrl`) is captured in `docs/runbooks/windows-desktop-runner.md`. Parsec coexistence verified: runner service stays in `Manual` start, only triggered on dispatch.
- Credential for the local `runneruser` account is stored in Vaultwarden under `windows-runner/desktop-kooshapari-desk/runneruser`.
- See `docs/runbooks/windows-desktop-runner.md` for verification, tear-down, and replacement steps.

## Top ADRs

| ADR | Title |
|-----|-------|
| [0001](docs/adr/0001-hybrid-compute-mesh.md) | Hybrid Compute Mesh (7 nodes) |
| [0002](docs/adr/0002-oci-primary-backbone.md) | OCI Ampere as primary backbone |
| [0003](docs/adr/0003-home-desktop-as-heavy-runner.md) | Home desktop as heavy runner |
| [0004](docs/adr/0004-tailscale-as-control-plane.md) | Tailscale as control plane |
| [0005](docs/adr/0005-forgejo-woodpecker-vs-gitea-vs-gh-actions.md) | Forgejo + Woodpecker vs alternatives |
| [0006](docs/adr/0006-vaultwarden-as-canonical-cred-store.md) | Vaultwarden canonical credential store |
| [0007](docs/adr/0007-runner-label-routing.md) | Runner label routing taxonomy |
| [0008](docs/adr/0008-parsec-gaming-mode-pause.md) | Parsec gaming mode pause |
| [0009](docs/adr/0009-hw-mesh-agent-bus.md) | HW mesh agent bus (Phase 2) |

See also: the parent compute-mesh playbook lives at `../docs/governance/compute_mesh.md` (sibling `repos/docs/governance/` directory).

## Contribution rules

- **No secrets.** Every credential is a placeholder (`<OCI_TENANCY_OCID>`, `<TAILSCALE_AUTHKEY>`, etc.). Real values live in Vaultwarden and are injected at runtime.
- **Terraform apply is human-only.** Agents may `terraform plan` and open PRs; `apply` requires explicit user approval.
- **ADR-first.** Any topology change needs an ADR before the IaC change.
- **Runbook-first.** Any node addition needs a runbook before the IaC scaffold.
- **Scripting hierarchy** (per `~/.claude/CLAUDE.md`): Rust default; Zig/Mojo/Go with one-line justification; Bash only as ≤5-line glue with justification comment. Terraform/Ansible/YAML are exempt as domain tools.

## Repository layout

```
docs/adr/             Architectural decisions (immutable once accepted)
docs/specs/           Topology, routing, credential inventory, rollback specs
docs/runbooks/        Step-by-step operational procedures
docs/governance/      Security, cost, incident-response policies
iac/                  Operational crates index — see iac/README.md
iac/oci-lottery/      A1.Flex capacity-lottery daemon (Rust)
iac/oci-post-acquire/ Post-acquire hook orchestrator
iac/tailscale/        Tailscale ACL + ephemeral keygen (Rust)
iac/landing-bootstrap/ Per-node landing-page generator (Rust)
iac/terraform/        Per-provider Terraform modules (stubs)
iac/ansible/          Configuration management playbooks
iac/scripts/          Bootstrap helpers (bash ≤5-line or Rust)
configs/              Per-service .example config files
.github/workflows/    CI (terraform plan, ansible-lint, docs check)
```

For the operational-crates entry index (oci-lottery, oci-post-acquire,
tailscale-keygen, landing-bootstrap), see [`iac/README.md`](iac/README.md).

## License

Dual-licensed under MIT **OR** Apache-2.0 at your option. See `LICENSE-MIT` and `LICENSE-APACHE`.
# Agent DevOps Setups

**STATUS: DEPRECATED — see DEPRECATION.md**

[![AI Slop Inside](https://sladge.net/badge.svg)](https://sladge.net)

This repo is the shared configuration fabric for multi-model agent tooling in the Phenotype
organization: policy federation, harness-specific overlays, task-domain scopes, and extension
runtime hooks for `Codex`, `Cursor-agent`, `Claude`, and `Factory-Droid`.

This repository is superseded by **phenoShared** and is maintained as read-only reference. No new development.

## Problem this solves

Current agent-level toolchains each support their own local override surfaces (`AGENTS.md`,
`CLAUDE.md`, `Cursor` rules, harness flags, etc.), which leads to drift.
This repository unifies those concerns by:

- Defining precedence-aware policy layers,
- Normalizing extension configuration across harnesses,
- Recording all decisions and merges in auditable artifacts.

## Directory layout

```text
agent-devops-setups/
├── policies/
│   ├── system/         # platform / org-wide defaults
│   ├── user/           # user/operator-level overrides
│   ├── harness/        # Codex / Cursor / Claude / Factory-Droid
│   ├── repo/           # per-repo behavior
│   ├── task-domain/    # per-domain behavior (agentops/ci/devops/...)
│   └── extensions/     # optional capability layers
├── extensions/
│   ├── manifests/      # cataloged extension packages
│   └── hooks/          # helper hook templates and docs
├── schemas/            # JSON schemas for policy and extensions
├── tools/
│   ├── federate_policy.py # resolves merged effective policy
│   └── sync_policy.sh     # write generated payload into repos
├── docs/               # audit notes and architecture docs
└── .github/workflows/  # optional validation/refresh automation
```

## Policy resolution model

Default layer order (low → high precedence):

1. `system` (org-wide defaults)
2. `user` (operator role overrides)
3. `harness` (tooling-specific behavior)
4. `repo` (repository-specific controls)
5. `task-domain` (domain-specific contracts)
6. `extensions` (explicitly selected extension packs)

Higher layers override keys from lower layers.

## Usage

```bash
# Build effective policy for a specific context
python tools/federate_policy.py \
  --repo agent-devops-setups \
  --harness codex \
  --user core-operator \
  --task-domain agentops \
  --extensions codex-gate,agentops-ci \
  --out /tmp/effective-policy.json

# Apply a policy payload into the repository path for local tooling
bash tools/sync_policy.sh \
  --repo-root /Users/kooshapari/CodeProjects/Phenotype/repos/thegent \
  --payload /tmp/effective-policy.json \
  --mode write

# Batch onboarding
bash tools/onboard_repos.sh \
  --harness codex \
  --task-domain agentops \
  --extensions codex-gate,agentops-ci \
  --user core-operator \
  --repo-list thegent,template-commons,portage,heliosCLI,cliproxyapi++,agentapi-plusplus

# Matrix onboarding (harness + task-domain)
bash tools/matrix_onboard.sh \
  --harnesses "codex,cursor-agent,claude,factory-droid" \
  --task-domains "agentops,devops" \
  --repo-list thegent,template-commons,portage,heliosCLI,cliproxyapi++,agentapi-plusplus

# Make targets
make help
make policy-sync        # codex + agentops full list
make policy-matrix      # matrix across harnesses and domains
make policy-matrix-dry  # same matrix in dry-run mode
```

## Expected outputs

- `effective_policy`: merged JSON object with all active policy keys.
- `applied_layers`: exact list of layer files used.
- `audit`: deterministic trace for forensics and review.

## Governance goals

- No silent precedence changes.
- No hidden defaults for critical controls.
- Full traceability from base policy to final resolved policy.
- Additive extension system that can be disabled by removing an extension manifest.

## Related tooling

- `AGENTS.md` and `CLAUDE.md` generation for repo surfaces.
- Harness hook policy (`extensions/hooks`).
- CI policy validation and PR gate gating via `.github/workflows`.

## Shared DevOps Helpers

Repository-level automation scripts live in `scripts/` and are consumed by
Phenotype repos that need consistent publish/checker behavior.

- `scripts/repo-push-fallback.sh`:
  publish helper with a primary remote first and local/remote fallback.
- `scripts/repo-devops-checker.sh`:
  lightweight DevOps gate checks for git health and optional `task ci` execution.

Recommended invocation pattern from a repo checkout:

```bash
# Optional override if repo layout differs from ../agent-devops-setups
export PHENOTYPE_DEVOPS_REPO_ROOT=/absolute/path/to/agent-devops-setups

# Optional per-command overrides
export PHENOTYPE_DEVOPS_PUSH_HELPER=$PHENOTYPE_DEVOPS_REPO_ROOT/scripts/repo-push-fallback.sh
export PHENOTYPE_DEVOPS_CHECKER_HELPER=$PHENOTYPE_DEVOPS_REPO_ROOT/scripts/repo-devops-checker.sh

bash /absolute/path/to/your/repo/scripts/push-heliosapp-with-fallback.sh
bash /absolute/path/to/your/repo/scripts/devops-checker.sh --check-ci --emit-summary
```

Because each repo may wire flags and defaults differently, keep a small local
wrapper script that forwards into these shared scripts with repo-local defaults.

## Validation commands

```bash
# Validate generated policy payload against schemas
python tools/validate_policy_payload.py \
  --payload /tmp/effective-policy.json \
  --policy-schema schemas/policy-resolution.schema.json \
  --manifest-schema schemas/extension-manifest.schema.json \
  --manifest-dir extensions/manifests \
  --strict
```

## Signing and rotation audit

```bash
# Emit signed policy payload
python tools/federate_policy.py \
  --repo thegent \
  --harness codex \
  --user core-operator \
  --task-domain agentops \
  --extensions codex-gate \
  --sign-key "$AGENT_POLICY_HMAC_KEY" \
  --out /tmp/effective-policy.json

# Verify signed payload
python tools/validate_policy_payload.py \
  --payload /tmp/effective-policy.json \
  --sign-key "$AGENT_POLICY_HMAC_KEY" \
  --strict

# Track rotation across repos
python tools/audit_policy_rotation.py \
  --repo-list thegent,template-commons,heliosCLI \
  --repo-root /Users/kooshapari/CodeProjects/Phenotype/repos \
  --state /tmp/policy-rotation-state.json \
  --out /tmp/policy-rotation-report.json

# Build PR package
python tools/build_pr_package.py
```
# phenotype-dep-guard

Malicious dependency analysis and supply chain security guard.

## Layer Contract

- layer_type: security_ops
- layer_name: phenotype-dep-guard
- versioning: semver

## Mission

Analyze direct and transitive dependencies for malicious code, vulnerabilities, and anomalous behavior.

1. High-velocity multi-source dependency resolution.
2. Heuristic and static triage (AST parsing, .pth/setup.py scanning).
3. Agentic LLM deep analysis (minimax-m2.7-highspeed, gpt-5-mini).
4. Reporting and alerting.

## Spec Kitty Workflow

```bash
spec-kitty research --feature layered-template-platform --force
```

Primary feature workspace:

- `kitty-specs/layered-template-platform/`

## Operational Workflow

1. Run `task check` before release.
2. Keep manifest/reconcile files aligned for any contract-affecting change.
3. Run `task release:prep` as final pre-release gate.

## Outputs

- Layer contract specs
- WP DAG and execution lanes
- Reconcile contract and acceptance criteria
