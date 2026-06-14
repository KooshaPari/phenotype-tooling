# Traceability Matrix

| Requirement | Source | Test | Status |
|-------------|--------|------|--------|
| Acceptance contract engine with hard/soft probes | `crates/acceptance-contract/` | `cargo test -p acceptance-contract` | Implemented |
| Lane-based agent orchestration & dispatch | `crates/agent-orchestrator/` | `cargo test -p agent-orchestrator` | Implemented |
| Agent workload forecasting | `crates/agent-forecast/` | `cargo test -p agent-forecast` | Implemented |
| Anthropic API usage polling | `crates/anthropic-usage-poll/` | `cargo test -p anthropic-usage-poll` | Implemented |
| Privacy audit scanning | `crates/audit-privacy/` | `cargo test -p audit-privacy` | Implemented |
| Benchmark regression guarding | `crates/bench-guard/` | `cargo test -p bench-guard` | Implemented |
| Reusable CI quality gate federation | `.github/workflows/ci.yml`, `.github/workflows/quality-gate.yml` | `cargo test --workspace` via phenoShared reusable workflow | Active |
| Dependency vulnerability scanning (cargo-deny) | `.github/workflows/cargo-deny.yml` | `cargo deny check` in CI | Active |
| Documentation link health | `.github/workflows/doc-links.yml` | `cargo doc` + link checker in CI | Active |
| Release automation & SBOM generation | `crates/sbom-gen/`, `.github/workflows/release.yml` | `cargo test -p sbom-gen` | Implemented |
