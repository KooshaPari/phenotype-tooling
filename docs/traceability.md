# Traceability Matrix

Minimal requirement-to-code mapping for the main features in `phenotype-tooling`.

| Requirement | Source file | Test | Status |
|---|---|---|---|
| Agent orchestrator dispatches tasks across multiple lanes | `crates/agent-orchestrator/src/lib.rs` | `crates/agent-orchestrator/tests/integration_multi_lane.rs` | Implemented |
| Commit messages follow conventional format | `crates/commit-msg-check/src/lib.rs` | `crates/commit-msg-check/src/lib.rs` (unit tests) | Implemented |
| Markdown documentation links are valid | `crates/doc-link-check/src/lib.rs` | `crates/doc-link-check/src/lib.rs` (unit tests) | Implemented |
| SBOM is generated for workspace crates | `crates/sbom-gen/src/lib.rs` | — | Planned |
| Quality gate blocks PRs on policy violations | `crates/quality-gate/src/main.rs` | — | Partial |
| Privacy audit scans for PII patterns | `crates/audit-privacy/src/lib.rs` | — | Planned |
| Phenotype config diffing between versions | `crates/phenotype-diff/src/lib.rs` | — | Planned |
| Service registry tracks runtime endpoints | `crates/phenotype-service-registry/src/lib.rs` | — | Planned |
| Automated release cut with changelog | `crates/release-cut/src/lib.rs` | — | Partial |
| Acceptance contract tests for API stability | `crates/acceptance-contract/src/lib.rs` | — | Planned |
