# KlipDot — Substrate Audit DAG Remediation Plan

**Generated**: 2026-07-09
**Audit Score**: 65.3% (C+)
**Total Effort**: ~19.5h across 4 phases
**Pillars Audited**: 184 across 10 domains

---

## Dependency Graph (Phase Ordering)

```
Phase 0 (Quick Wins)
    │
    ├── QW-01 remove continue-on-error ──────────► P1-01 branch protection
    ├── QW-02 migrate deprecated actions ─────────► CICD-12 concurrency
    ├── QW-03 add CodeQL ────────────────────────► P3-02 miri/unsafe audit
    ├── QW-04 add Dependabot ────────────────────► SUP-11 SBOM generation
    ├── QW-05 create llms.txt ───────────────────► (independent)
    └── QW-06 clippy -D warnings ────────────────► P2-02 clippy.toml config
                                                          │
Phase 1 (Critical Infrastructure)                        │
    │                                                     │
    ├── P1-01 branch protection + quality gate ───────────┤
    ├── P1-02 structured observability ───────────────────┤
    │        (JSON logging + metrics + health)             │
    │              │                                       │
    │              └────────────► P3-01 OTel tracing       │
    │                                                      │
    └── P1-03 fuzz + proptest + benchmarks ───────────────┤
                                                          │
Phase 2 (Hardening)                                       │
    │                                                     │
    ├── P2-01 ARCHITECTURE.md + ADR cleanup ──────────────┤
    ├── P2-02 clippy.toml rules + cargo-udeps ◄───────────┘
    ├── P2-03 checksums + cosign signing ◄──────────────── SUP-11 SBOM
    └── P2-04 nextest + coverage gates ◄────────────────── P1-03 fuzz
                                                          │
Phase 3 (Advanced)                                        │
    │                                                     │
    ├── P3-01 OTel tracing ◄────── P1-02 structured logs  │
    ├── P3-02 unsafe audit + miri ◄── QW-03 CodeQL        │
    └── P3-03 features + DI + platform abstraction ───────┘
```

---

## Phase 0 — Quick Wins (~1.5h total)

Low-risk, independent changes with immediate impact. No cross-dependencies.

### QW-01: Harden CI Quality Gates (CICD-05)
- **Effort**: 10m
- **Pillar**: CICD-05 (Continue-on-Error Discipline)
- **Status**: `missing` → `satisfied`
- **Action**: Edit `.github/workflows/ci.yml` — remove `continue-on-error: true` from:
  - `test` jobs (ubuntu, macos, windows)
  - `build` jobs
  - `clippy` job (in tier0-hygiene.yml)
  - Keep `continue-on-error: true` only on `nightly` and `benchmark` jobs
- **Dependencies**: None
- **Unblocks**: P1-01 (branch protection gates only work when CI can actually fail)
- **Risk**: Low. May surface pre-existing failures — fix before merge.

### QW-02: Migrate Deprecated Actions (CICD-06)
- **Effort**: 15m
- **Pillar**: CICD-06 (Deprecated Actions)
- **Status**: `partial` → `satisfied`
- **Action**: Search-and-replace across all `.github/workflows/*.yml`:
  - `actions-rs/toolchain@v1` → `dtolnay/rust-toolchain@master` (or pinned SHA)
  - `actions/create-release@v1` → `softprops/action-gh-release@v2`
- **Dependencies**: None
- **Unblocks**: CICD-12 (concurrency groups)
- **Risk**: Low. Both replacements are drop-in compatible.

### QW-03: Add CodeQL Analysis (SEC-24)
- **Effort**: 15m
- **Pillar**: SEC-24 (CodeQL Analysis)
- **Status**: `missing` → `satisfied`
- **Action**: Create `.github/workflows/codeql.yml`:
  ```yaml
  name: "CodeQL"
  on:
    push: { branches: [main] }
    pull_request: { branches: [main] }
    schedule: [{ cron: '0 6 * * 3' }]
  jobs:
    analyze:
      runs-on: ubuntu-latest
      permissions:
        security-events: write
      steps:
        - uses: actions/checkout@v4
        - uses: github/codeql-action/init@v3
          with:
            languages: rust
            queries: security-extended
        - uses: github/codeql-action/autobuild@v3
        - uses: github/codeql-action/analyze@v3
  ```
- **Dependencies**: None
- **Unblocks**: P3-02 (unsafe code audit — CodeQL finds issues before miri)
- **Risk**: Low. CodeQL for Rust requires autobuild which may fail for complex builds. Verify on first run.

### QW-04: Add Dependabot Configuration (SUP-15)
- **Effort**: 20m
- **Pillar**: SUP-15 (Renovate/Dependabot)
- **Status**: `missing` → `satisfied`
- **Action**: Create `.github/dependabot.yml`:
  ```yaml
  version: 2
  updates:
    - package-ecosystem: cargo
      directory: "/"
      schedule: { interval: weekly, day: monday }
      open-pull-requests-limit: 10
    - package-ecosystem: github-actions
      directory: "/"
      schedule: { interval: weekly, day: monday }
  ```
- **Dependencies**: None
- **Unblocks**: SUP-11 (SBOM generation can use dependabot output)
- **Risk**: Low. Standard configuration.

### QW-05: Create llms.txt (DOC-11)
- **Effort**: 15m
- **Pillar**: DOC-11 (llms.txt)
- **Status**: `missing` → `satisfied`
- **Action**: Create `llms.txt` with:
  - Project summary and description
  - Key architecture points (module list, async runtime)
  - Build commands (`cargo build`, `cargo test`, `just build`)
  - Test commands (`cargo test`, `cargo nextest` when added)
  - CI/CD info (11 workflows, matrix strategy)
  - Code patterns (tracing, thiserror, clap)
- **Dependencies**: None
- **Unblocks**: None (independent)
- **Risk**: None.

### QW-06: Clippy Warnings as Errors in CI (CQ-14)
- **Effort**: 15m
- **Pillar**: CQ-14 (Lint Enforcement in CI)
- **Status**: `partial` → `satisfied`
- **Action**: Edit `.github/workflows/tier0-hygiene.yml`:
  - Remove `continue-on-error: true` from clippy step
  - Change clippy invocation: `cargo clippy -- -D warnings`
  - Or set `RUSTFLAGS: "-D warnings"` env
- **Dependencies**: None
- **Unblocks**: P2-02 (clippy.toml configuration benefits from enforced lints)
- **Risk**: Low. Fix any pre-existing clippy warnings before enabling.

---

## Phase 1 — Critical Infrastructure (~4h total)

Foundation-level changes that depend on Phase 0 deliverables.

### P1-01: Branch Protection + Quality Gate (CICD-08)
- **Effort**: 1h
- **Pillar**: CICD-08 (PR Quality Gate)
- **Status**: `missing` → `satisfied`
- **Depends on**: QW-01 (CI must be able to fail for gates to matter)
- **Action**:
  1. Create `.github/workflows/quality-gate.yml`:
     ```yaml
     name: Quality Gate
     on:
       pull_request:
         types: [opened, synchronize, reopened]
     jobs:
       gate:
         runs-on: ubuntu-latest
         steps:
           - run: echo "Quality gate passes when all required CI jobs pass"
     ```
  2. Configure GitHub branch protection (via API or UI):
     - Require status checks before merging
     - Required checks: `test (stable)`, `test (beta)`, `lint`, `build`
     - Require pull request reviews
     - Dismiss stale reviews
  3. Add `concurrency` group to all workflows (from CICD-12):
     ```yaml
     concurrency:
       group: ${{ github.workflow }}-${{ github.ref }}
       cancel-in-progress: true
     ```
- **Risks**: Branch protection changes affect all contributors. Coordinate merge flow.
- **Verification**: Create a test PR with a deliberate test failure — verify it cannot merge.

### P1-02: Structured Observability (OBS-01/OBS-03/OBS-04)
- **Effort**: 1.5h
- **Pillar**: OBS-01 (Structured Logging), OBS-04 (Metrics Collection), OBS-07 (Health Check)
- **Status**: `missing` → `partial` (JSON logging + health done; OTel deferred to P3-01)
- **Depends on**: None
- **Action**:
  1. **JSON Logging** (`src/main.rs` / `src/lib.rs`):
     ```rust
     use tracing_subscriber::{fmt, prelude::*, EnvFilter, Registry};
     use tracing_subscriber::layer::SubscriberExt;

     let log_format = std::env::var("LOG_FORMAT").unwrap_or_default();
     let subscriber = Registry::default()
         .with(EnvFilter::from_default_env());
     if log_format == "json" {
         let json_layer = fmt::layer().json();
         subscriber.with(json_layer).init();
     } else {
         let fmt_layer = fmt::layer();
         subscriber.with(fmt_layer).init();
     }
     ```
  2. **Metrics Counters** (new `src/metrics.rs`):
     ```rust
     use std::sync::atomic::{AtomicU64, Ordering};
     pub static IMAGES_INTERCEPTED: AtomicU64 = AtomicU64::new(0);
     pub static BYTES_PROCESSED: AtomicU64 = AtomicU64::new(0);
     pub static ERRORS_TOTAL: AtomicU64 = AtomicU64::new(0);
     ```
     Wire counters into: interceptor (image detected), service (bytes forwarded), error paths.
  3. **Health Endpoint** (`src/health.rs`):
     ```rust
     use axum::{routing::get, Router};
     async fn liveness() -> &'static str { "ok" }
     async fn readiness() -> &'static str { "ok" }
     ```
     Start HTTP server on `--health-addr 127.0.0.1:9091` via tokio::spawn.
- **Risks**: Adding axum dependency increases binary size. Feature-gate health endpoint.
- **Verification**: `LOG_FORMAT=json cargo run ... | jq` produces valid JSON.

### P1-03: Fuzz + Proptest + Benchmarks (TST-05/TST-06/TST-07)
- **Effort**: 1.5h
- **Pillar**: TST-05 (Property-Based Testing), TST-06 (Fuzz Testing), TST-07 (Benchmark Suite)
- **Status**: `missing` → `partial`
- **Depends on**: None
- **Action**:
  1. **Proptest** (`tests/proptest.rs`):
     ```rust
     use proptest::prelude::*;
     proptest! {
         #[test]
         fn image_format_detection_never_panics(data in prop::collection::vec(any::<u8>(), 0..1024)) {
             let _ = klipdot::detect_image_format(&data);
         }
     }
     ```
  2. **Cargo Fuzz** (requires nightly):
     ```bash
     cargo fuzz init
     cargo fuzz add image_parse
     cargo fuzz add clipboard_parse
     cargo fuzz add config_deser
     ```
     Write targets in `fuzz/fuzz_targets/`:
     - `image_parse.rs`: feed random bytes to image format detection
     - `clipboard_parse.rs`: feed random strings to clipboard parser
     - `config_deser.rs`: feed random bytes to config deserializer
  3. **Criterion Benchmarks** (`benches/image_processing.rs`):
     ```rust
     use criterion::{black_box, criterion_group, criterion_main, Criterion};
     fn bench_process_image(c: &mut Criterion) {
         let data = std::fs::read("tests/resources/sample.png").unwrap();
         c.bench_function("process_image", |b| b.iter(|| klipdot::process_image(black_box(&data))));
     }
     ```
  4. **CI Integration**: Add fuzz job (nightly only, 30s per target) and benchmark job to ci.yml.
- **Risks**: Fuzz requires nightly Rust. Criterion requires stable benchmark harness.
- **Verification**: `cargo proptest` passes. `cargo fuzz run image_parse -- -runs=100000` finds no crashes in 100k iterations.

---

## Phase 2 — Quality & Documentation Hardening (~6h total)

Bulk of documentation and tooling improvements. Benefits from Phase 1 foundations.

### P2-01: Architecture Documentation + ADR Cleanup (DOC-01/DOC-06)
- **Effort**: 2h
- **Pillar**: DOC-01 (Architecture Overview), DOC-06 (ADR Documentation)
- **Status**: `missing` → `satisfied`
- **Depends on**: None
- **Action**:
  1. **Create `ARCHITECTURE.md`** (Mermaid diagrams):
     - Module directory with dependency arrows
     - Interception pipeline flow:
       ```
       ┌──────────┐    SIGSTOP    ┌────────────┐    pipe    ┌──────────┐
       │ Child    │──────────────►│ Interceptor │──────────►│ Service  │
       │ Process  │               │ (stdout)    │           │ (filter) │
       └──────────┘               └────────────┘           └──────────┘
                                                                    │
                                                          ┌─────────▼──────┐
                                                          │ ImageProcessor │
                                                          │ Clipboard      │
                                                          └────────────────┘
       ```
     - Shell hook lifecycle (bash hook → exec → interception)
     - Config resolution order (CLI → config file → env → default)
  2. **ADR cleanup**:
     - Create `docs/adr/` directory
     - Split `ADR.md` into individual `docs/adr/0001-*.md` through `docs/adr/0010-*.md`
     - Review and accept/reject each pending ADR
     - Update `ADR.md` to be an index only, linking to `docs/adr/` files
     - Fix any broken cross-references
- **Risks**: Low. Time-consuming but straightforward.
- **Verification**: `ARCHITECTURE.md` covers all 14 modules. All 10 ADRs have a decision (accepted/rejected).

### P2-02: Clippy Guardrails + Dependency Hygiene (CQ-02/CQ-10/SUP-07)
- **Effort**: 1.5h
- **Pillar**: CQ-02 (Clippy Configuration), CQ-10 (Complexity Budgeting), SUP-07 (Dependency Tree Cleanliness)
- **Status**: `missing` → `satisfied`
- **Depends on**: QW-06 (clippy enforcement must be active first)
- **Action**:
  1. **Configure `clippy.toml`**:
     ```toml
     cognitive-complexity-threshold = 25
     cyclomatic-complexity-threshold = 35
     doc-valid-idents = ["KlipDot", "SIGSTOP", "SIGCONT"]
     allow-unwrap-in-tests = true
     ```
  2. **Add cargo-udeps to CI** (`tier0-hygiene.yml`):
     ```yaml
     - name: Check unused deps (nightly)
       run: cargo +nightly udeps
       continue-on-error: true  # advisory only for now
     ```
  3. **Add loc-per-function lint** via clippy restriction:
     ```toml
     # clippy.toml
     too-many-lines-threshold = 100
     ```
  4. **Add `cargo-deny` check for unused dependencies** (update `deny.toml`):
     ```toml
     [unused]
     ignore-build-dependencies = true
     ignore-dev-dependencies = true
     ```
- **Risks**: Setting cycles too low may cause initial failures. Start with advisory thresholds, ratchet down over 2 weeks.
- **Verification**: `cargo clippy` passes with new restrictions. `cargo udeps` shows 0 (or documented) unused deps.

### P2-03: Release Integrity — Checksums + Container Signing (SUP-14/SUP-16)
- **Effort**: 1h
- **Pillar**: SUP-14 (Binary Integrity Check), SUP-16 (Container Image Signing)
- **Status**: `missing` → `satisfied`
- **Depends on**: None
- **Action**:
  1. **SHA-256 checksums in release.yml** (after build step):
     ```yaml
     - name: Generate checksums
       run: |
         cd dist/
         sha256sum klipdot-* > SHA256SUMS
     - name: Upload checksums
       uses: actions/upload-artifact@v4
       with:
         name: checksums
         path: dist/SHA256SUMS
     ```
  2. **Cosign container signing** (in Docker build step):
     ```yaml
     - name: Sign container image
       uses: sigstore/cosign-installer@v3
     - name: Sign with OIDC
       run: |
         cosign sign --yes ghcr.io/${{ github.repository_owner }}/klipdot:${{ github.ref_name }}
       env:
         COSIGN_EXPERIMENTAL: 1
     ```
  3. Add a release check step: verify checksums match before publishing.
- **Risks**: Cosign requires OIDC token permissions in GitHub Actions. May need permission adjustments.
- **Verification**: `sha256sum -c SHA256SUMS` passes on downloaded artifacts. `cosign verify` succeeds on published image.

### P2-04: Nextest + Coverage Gates (TST-11/TST-12/TST-22)
- **Effort**: 1.5h
- **Pillar**: TST-11 (Coverage Reporting), TST-12 (CI Test Matrix), TST-22 (Nextest Runner)
- **Status**: `missing` → `satisfied`
- **Depends on**: None
- **Action**:
  1. **Configure cargo-nextest**:
     ```bash
     mkdir -p .config
     cat > .config/nextest.toml << 'EOF'
     [profile.default]
     test-threads = 4
     retries = 2
     per-test-timeout = "60s"
     [profile.ci]
     test-threads = "num-cpu"
     retries = 0
     per-test-timeout = "30s"
     ```
  2. **Update CI** (`ci.yml`):
     ```yaml
     - name: Install nextest
       uses: taiki-e/install-action@nextest
     - name: Run tests with nextest
       run: cargo nextest run --profile ci
     - name: JUnit report
       run: cargo nextest run --profile ci --message-format junit > test-results.xml
     - name: Upload test results
       uses: actions/upload-artifact@v4
       with:
         name: test-results
         path: test-results.xml
     ```
  3. **Coverage threshold** (update ci.yml coverage section):
     ```yaml
     - name: Upload coverage to Codecov
       uses: codecov/codecov-action@v4
       with:
         fail_ci_if_error: true
         verbose: true
     ```
  4. **Add coverage config** (create `codecov.yml`):
     ```yaml
     coverage:
       status:
         project:
           default:
             target: 60%
             threshold: 2%
         patch:
           default:
             target: 80%
     ```
- **Risks**: Codecov status checks require token setup. Nextest may surface pre-existing flaky tests.
- **Verification**: `cargo nextest run` completes. Coverage report shows >=60% line coverage.

---

## Phase 3 — Advanced & Production Polish (~8h total)

Deep architectural improvements with dependencies on earlier phases.

### P3-01: OpenTelemetry Tracing (OBS-03/OBS-11/OBS-12)
- **Effort**: 3h
- **Pillar**: OBS-03 (Distributed Tracing), OBS-11 (Context Propagation), OBS-12 (Log Enrichment)
- **Status**: `missing` → `satisfied`
- **Depends on**: P1-02 (JSON logging provides foundation)
- **Action**:
  1. **Add OTel dependencies** (`Cargo.toml`):
     ```toml
     opentelemetry = { version = "0.25", features = ["trace", "metrics"] }
     opentelemetry-otlp = { version = "0.25", features = ["trace", "metrics", "grpc-tonic"] }
     opentelemetry-semantic-conventions = "0.25"
     tracing-opentelemetry = "0.28"
     ```
  2. **Create `src/telemetry.rs`**:
     ```rust
     use opentelemetry::{global, KeyValue};
     use opentelemetry_otlp::WithExportConfig;
     use tracing_subscriber::{prelude::*, Registry, EnvFilter};
     use tracing_opentelemetry::OpenTelemetryLayer;

     pub fn init_otel() -> Result<(), Box<dyn std::error::Error>> {
         let tracer = opentelemetry_otlp::new_pipeline()
             .tracing()
             .with_exporter(opentelemetry_otlp::new_exporter().tonic()
                 .with_endpoint(std::env::var("OTEL_EXPORTER_OTLP_ENDPOINT")
                     .unwrap_or_else(|_| "http://localhost:4317".to_string())))
             .install_batch(opentelemetry_sdk::runtime::Tokio)?;
         let otel_layer = OpenTelemetryLayer::new(tracer);
         let subscriber = Registry::default()
             .with(EnvFilter::from_default_env())
             .with(otel_layer);
         subscriber.init();
         Ok(())
     }
     ```
  3. **Instrument key operations**:
     ```rust
     // In interceptor.rs
     async fn intercept_stream(stream: &mut impl AsyncRead) -> Result<()> {
         let span = info_span!("intercept_stream", operation.id = %Uuid::new_v4(), child.pid = %pid);
         async { /* existing logic */ }.instrument(span).await
     }
     ```
  4. **Span enrichment**: Add fields systematically to all spans:
     - `service.name`, `operation.id`, `image.format`, `image.size_bytes`
     - `child.pid`, `duration_ms`, `error.type`
  5. **Trace context propagation**: Add `traceparent` header propagation for child processes via env.
- **Risks**: OTLP gRPC dependency increases binary size significantly. Feature-gate behind `otel` feature.
- **Verification**: Run with `OTEL_EXPORTER_OTLP_ENDPOINT` set — traces appear in Jaeger/OTEL collector.

### P3-02: Unsafe Code Audit + Miri + Binary Signing (SEC-06/SEC-08/SEC-25)
- **Effort**: 2.5h
- **Pillar**: SEC-06 (Code Signing), SEC-08 (Unsafe Code Audit), SEC-25 (Memory Safety via Miri)
- **Status**: `missing` → `satisfied`
- **Depends on**: QW-03 (CodeQL first pass to identify issues)
- **Action**:
  1. **Create `UNSAFE.md`** tracking all 4 unsafe blocks:
     ```markdown
     # Unsafe Code Inventory
     | # | File | Line | Purpose | Reviewed | SAFETY comment |
     |---|------|------|---------|----------|----------------|
     | 1 | interceptor.rs | 42 | sigaction setup | ☐ | Yes |
     | 2 | interceptor.rs | 78 | signal mask | ☐ | Yes |
     | 3 | main.rs | 120 | raw fd | ☐ | Yes |
     | 4 | main.rs | 145 | signal handler fn ptr | ☐ | Yes |
     ```
  2. **Miri in CI** (weekly, separate workflow):
     ```yaml
     name: Miri
     on:
       schedule: [{ cron: '0 5 * * 1' }]
     jobs:
       miri:
         runs-on: ubuntu-latest
         steps:
           - uses: actions/checkout@v4
           - uses: dtolnay/rust-toolchain@nightly
             with: { components: miri }
           - run: cargo miri test --tests interceptor
     ```
  3. **Binary signing** (add to release.yml):
     ```yaml
     - name: Import GPG key
       uses: crazy-max/ghaction-import-gpg@v6
       with:
         gpg_private_key: ${{ secrets.GPG_PRIVATE_KEY }}
         passphrase: ${{ secrets.GPG_PASSPHRASE }}
     - name: Sign release artifacts
       run: |
         for f in dist/klipdot-*; do
           gpg --detach-sign --armor "$f"
         done
     ```
  4. **Review and fix unsafe blocks**: For each unsafe block, verify:
     - SAFETY comment references an ADR or tracking issue
     - Pre/post conditions are documented
     - Alternative safe approaches were considered and documented
- **Risks**: Miri on nightly may find UB in transitive dependencies (false positives common). GPG key management requires operational procedure.
- **Verification**: `cargo miri test` passes on interceptor tests. All unsafe blocks have reviewed SAFETY comments.

### P3-03: Feature Gating + Platform Abstraction (ARC-04/ARC-07/ARC-16)
- **Effort**: 2.5h
- **Pillar**: ARC-04 (Dependency Injection), ARC-07 (Platform Abstraction), ARC-16 (Feature Gating)
- **Status**: `missing` → `satisfied`
- **Depends on**: None
- **Action**:
  1. **Cargo features** (`Cargo.toml`):
     ```toml
     [features]
     default = ["clipboard-all", "image-processing", "signal-hooks"]
     clipboard-x11 = ["arboard"]
     clipboard-wayland = ["arboard"]
     clipboard-all = ["clipboard-x11", "clipboard-wayland"]
     image-processing = ["image", "base64"]
     signal-hooks = ["signal-hook"]
     otel = ["opentelemetry", "opentelemetry-otlp", "tracing-opentelemetry"]
     ```
     Gate platform-specific code:
     ```rust
     #[cfg(target_os = "linux")]
     mod linux_clipboard;
     #[cfg(target_os = "macos")]
     mod macos_clipboard;
     ```
  2. **Platform trait** (`src/interceptor/signal.rs`):
     ```rust
     pub trait SignalHandler: Send + Sync {
         fn register_signal(signal: libc::c_int, handler: unsafe extern "C" fn(libc::c_int)) -> Result<()>;
         fn block_signal(signal: libc::c_int) -> Result<()>;
     }
     #[cfg(unix)]
     pub struct UnixSignalHandler;
     #[cfg(unix)]
     impl SignalHandler for UnixSignalHandler {
         fn register_signal(signal: libc::c_int, handler: unsafe extern "C" fn(libc::c_int)) -> Result<()> {
             unsafe { /* existing sigaction logic */ }
         }
     }
     ```
  3. **Trait-based DI** (for testability):
     ```rust
     pub trait Clipboard: Send + Sync {
         fn get_contents(&self) -> Result<String>;
         fn set_contents(&self, text: &str) -> Result<()>;
     }
     pub struct Service {
         clipboard: Box<dyn Clipboard>,
         image_processor: Box<dyn ImageProcessor>,
     }
     impl Service {
         pub fn new(clipboard: Box<dyn Clipboard>, image_processor: Box<dyn ImageProcessor>) -> Self { ... }
     }
     ```
  4. **Update tests**: Use mock implementations:
     ```rust
     struct MockClipboard;
     impl Clipboard for MockClipboard {
         fn get_contents(&self) -> Result<String> { Ok("test data".into()) }
         fn set_contents(&self, _text: &str) -> Result<()> { Ok(()) }
     }
     ```
- **Risks**: Feature gating can cause compilation surprises on untested platforms. CI should test `--no-default-features`.
- **Verification**: `cargo build --no-default-features` compiles. `cargo test` uses mock implementations. Linux/macOS CI covers both platform backends.

---

## Summary

| Phase | Title | Items | Effort | Score Impact | Domain Impact |
|-------|-------|-------|--------|-------------|--------------|
| 0 | Quick Wins | 6 | ~1.5h | +5% | CI/CD, Security, DX |
| 1 | Critical Infrastructure | 3 | ~4h | +8% | CI/CD, Observability, Testing |
| 2 | Quality & Documentation | 4 | ~6h | +7% | Documentation, Code Quality, Supply Chain |
| 3 | Advanced & Production Polish | 3 | ~8h | +5% | Architecture, Security, Observability |
| **Total** | **16** | **~19.5h** | **+25%** | **→ ~90% (A-)** |

### Effort Breakdown by Domain

| Domain | Current % | Phase 0 | Phase 1 | Phase 2 | Phase 3 | Target % |
|--------|-----------|---------|---------|---------|---------|----------|
| Code Quality | 73.2% | +1.8% | -- | +12.5% | -- | **87.5%** |
| Architecture | 64.7% | -- | -- | -- | +17.6% | **82.3%** |
| Testing | 44.2% | -- | +11.5% | +11.5% | -- | **67.2%** |
| Observability | 40.3% | -- | +16.7% | -- | +16.7% | **73.7%** |
| Security | 68.8% | +3.1% | -- | -- | +6.2% | **78.1%** |
| Documentation | 57.4% | +5.9% | -- | +17.6% | -- | **80.9%** |
| CI/CD | 58.9% | +14.3% | +14.3% | -- | -- | **87.5%** |
| Supply Chain | 55.0% | +5.0% | -- | +10.0% | -- | **70.0%** |
| Release Engineering | 65.4% | -- | -- | -- | -- | **65.4%** |
| Developer Experience | 61.5% | -- | -- | +7.7% | -- | **69.2%** |
| **Overall** | **65.3%** | **+3.1%** | **+4.3%** | **+4.9%** | **+2.7%** | **~80.3% (B)** |

### Recommended Sprint Allocation

| Sprint | Phase | Focus | Hours |
|--------|-------|-------|-------|
| Sprint 1 | Phase 0 | Quick infrastructure wins | 1.5h |
| Sprint 1 | Phase 1 | CI hardening + observability | 4h |
| Sprint 2 | Phase 2 | Documentation + tooling | 6h |
| Sprint 3 | Phase 3 | Advanced architecture | 8h |

Parallelism note: Phases 0 and 1 items have no blocking dependencies between each other within each phase. All Phase 0 items can be executed in any order. Phase 1 items can be done in parallel if multiple contributors are available.
