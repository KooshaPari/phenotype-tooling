# Traceability Matrix

| Requirement | Source | Test | Status |
|-------------|--------|------|--------|
| Markdown linting and broken-link detection | `docs-health` crate | `cargo test -p docs-health` | ✅ Implemented |
| FR-NNN requirement-to-test traceability scan | `fr-trace` crate | `cargo test -p fr-trace` | ✅ Implemented |
| Aggregate `cargo fmt` / `clippy` / `test` pass-fail gate | `quality-gate` crate | `cargo test -p quality-gate` | ✅ Implemented |
| Detect shell/Python anti-patterns per scripting policy | `legacy-scan` crate | `cargo test -p legacy-scan` | ✅ Implemented |
| Reusable-workflow federation (cargo-deny / trufflehog / journey-gate) | `.github/workflows/` | `cargo test -p bench-guard` | 🔄 In Progress |
