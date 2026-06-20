# Absorbed from phenotype-gateway

**Source:** `KooshaPari/phenotype-gateway`
**Target:** `phenotype-tooling/docs/absorbed-from-phenotype-gateway/`
**Tracked file count:** 93

## Purpose

This directory is a historical absorption of the source repository into `phenotype-tooling`.
All tracked source files from `git ls-files` are preserved here, plus this manifest.

## Preserved inventory

```text
    .github/CODEOWNERS
    .github/workflows/cargo.yml
    .github/workflows/deny.yml
    .github/workflows/scaffold.yml
    .gitmodules
    Cargo.toml
    README.md
    Taskfile.yml
    deny.toml
    docs/ABSORPTION.md
    docs/PROMOTION.md
    docs/SPEC.md
    docs/UPSTREAM.md
    docs/adrs/ADR-GW-001-router-lang.md
    docs/governance/CONTRIBUTING.md
    docs/governance/GOVERNANCE.md
    docs/operations/DEPLOY.md
    docs/operations/SUBMODULE_UPDATE.md
    docs/router/COMBO_ROUTING.md
    docs/router/MCP_SUBSET.md
    justfile
    packages/.gitkeep
    packages/agentapi/BOUNDARY.md
    packages/agentapi/PIN.md
    packages/agentapi/README.md
    packages/agentapi/agentapi.go
    packages/agentapi/go.mod
    packages/argis/BOUNDARY.md
    packages/argis/PIN.md
    packages/argis/README.md
    packages/argis/argis.go
    packages/argis/go.mod
    packages/bifrost/BOUNDARY.md
    packages/bifrost/PIN.md
    packages/bifrost/README.md
    packages/bifrost/bifrost.go
    packages/bifrost/go.mod
    packages/cliproxy/BOUNDARY.md
    packages/cliproxy/PIN.md
    packages/cliproxy/README.md
    packages/cliproxy/cliproxy.go
    packages/cliproxy/go.mod
    packages/router/Cargo.lock
    packages/router/Cargo.toml
    packages/router/README.md
    packages/router/src/lib.rs
    scripts/smoke-go.ps1
    scripts/smoke-go.sh
    scripts/smoke-router.ps1
    spikes/go/.gitkeep
    spikes/go/agentapi/README.md
    spikes/go/agentapi/smoke.sh
    spikes/go/argis/README.md
    spikes/go/argis/smoke.sh
    spikes/go/bifrost/README.md
    spikes/go/bifrost/smoke.sh
    spikes/go/cliproxy/README.md
    spikes/go/cliproxy/smoke.sh
    spikes/go/router/README.md
    spikes/mojo/.gitkeep
    spikes/mojo/README.md
    spikes/mojo/router/README.md
    spikes/rust/.gitkeep
    spikes/rust/capacity/AGENTS.md
    spikes/rust/capacity/CHANGELOG.md
    spikes/rust/capacity/Cargo.toml
    spikes/rust/capacity/LICENSE-APACHE
    spikes/rust/capacity/LICENSE-MIT
    spikes/rust/capacity/README.md
    spikes/rust/capacity/SECURITY.md
    spikes/rust/capacity/VERSION.toml
    spikes/rust/capacity/WORKLOG.md
    spikes/rust/capacity/docs/SPEC.md
    spikes/rust/capacity/llms.txt
    spikes/rust/capacity/llvm-cov.toml
    spikes/rust/capacity/src/lib.rs
    spikes/rust/capacity/src/pheno_capacity/attention.rs
    spikes/rust/capacity/src/pheno_capacity/estimate.rs
    spikes/rust/capacity/src/pheno_capacity/math.rs
    spikes/rust/capacity/src/pheno_capacity/mod.rs
    spikes/rust/capacity/src/pheno_capacity/policy.rs
    spikes/rust/router/Cargo.lock
    spikes/rust/router/Cargo.toml
    spikes/rust/router/README.md
    spikes/rust/router/src/delegate.rs
    spikes/rust/router/src/lib.rs
    spikes/zig/.gitkeep
    spikes/zig/router/README.md
    spikes/zig/router/build.zig
    third_party/agentapi-plusplus
    third_party/argis-extensions
    third_party/bifrost
    third_party/cliproxyapi-plusplus
```

## Intentional exclusions

The following generated/runtime artifacts exist in the source working tree but are intentionally not mirrored because they are not tracked source files:

- `__pycache__/`
- `*.egg-info/`
- `target/`
- `.benchmarks/`
- `.pytest_cache/`
- `node_modules/`

## Verification note

Coverage is intended to match the source repository tracked inventory exactly; any extra files in this directory are limited to this manifest and may be used for archival context.
