# Absorbed from phenotype-config

**Source:** `KooshaPari/phenotype-config`
**Target:** `phenotype-tooling/docs/absorbed-from-phenotype-config/`
**Tracked file count:** 118

## Purpose

This directory is a historical absorption of the source repository into `phenotype-tooling`.
All tracked source files from `git ls-files` are preserved here, plus this manifest.

## Preserved inventory

```text
    CANONICAL_REDIRECT.md
    Cargo.lock
    Cargo.toml
    MIGRATE_TO_CONFIGRA.md
    README.md
    SOTA.md
    charter.md
    crates/phenotype-config-loader/Cargo.toml
    crates/phenotype-config-loader/src/lib.rs
    crates/settly/.agileplus/worklog.md
    crates/settly/.config/nextest.toml
    crates/settly/.editorconfig
    crates/settly/.env.example
    crates/settly/.githooks/pre-commit
    crates/settly/.githooks/pre-push
    crates/settly/.github/CODEOWNERS
    crates/settly/.github/FUNDING.yml
    crates/settly/.github/ISSUE_TEMPLATE/bug.yml
    crates/settly/.github/ISSUE_TEMPLATE/feature.yml
    crates/settly/.github/dependabot.yml
    crates/settly/.github/pull_request_template.md
    crates/settly/.github/workflows/auto-merge.yml
    crates/settly/.github/workflows/benchmarks.yml
    crates/settly/.github/workflows/cargo-deny.yml
    crates/settly/.github/workflows/ci.yml
    crates/settly/.github/workflows/coverage.yml
    crates/settly/.github/workflows/legacy-tooling-gate.yml
    crates/settly/.github/workflows/pages-deploy.yml
    crates/settly/.github/workflows/pre-commit.yml
    crates/settly/.github/workflows/quality-gate.yml
    crates/settly/.github/workflows/release-drafter.yml
    crates/settly/.github/workflows/release.yml
    crates/settly/.github/workflows/sast.yml
    crates/settly/.github/workflows/security-deep-scan.yml
    crates/settly/.github/workflows/security-guard.yml
    crates/settly/.github/workflows/security.yml
    crates/settly/.github/workflows/trufflehog.yml
    crates/settly/.gitignore
    crates/settly/ADR.md
    crates/settly/AGENTS.md
    crates/settly/CANONICAL.md
    crates/settly/CANONICAL_FROM_PHENO_SHARED_CONFIG.md
    crates/settly/CHANGELOG.md
    crates/settly/CLAUDE.md
    crates/settly/CODEOWNERS
    crates/settly/CONTRIBUTING.md
    crates/settly/Cargo.lock
    crates/settly/Cargo.toml
    crates/settly/FUNCTIONAL_REQUIREMENTS.md
    crates/settly/FUNDING.yml
    crates/settly/LICENSE
    crates/settly/PLAN.md
    crates/settly/PRD.md
    crates/settly/QA_MATRIX.md
    crates/settly/README.md
    crates/settly/SECURITY.md
    crates/settly/SPEC.md
    crates/settly/STANDARDS.md
    crates/settly/TEST_COVERAGE_MATRIX.md
    crates/settly/Taskfile.yml
    crates/settly/VERIFICATION_POLICY.md
    crates/settly/VERSION
    crates/settly/_typos.toml
    crates/settly/benches/perf.rs
    crates/settly/cliff.toml
    crates/settly/clippy.toml
    crates/settly/codecov.yml
    crates/settly/deny.toml
    crates/settly/docs/journeys/index.md
    crates/settly/docs/journeys/quick-start.md
    crates/settly/docs/research/SOTA.md
    crates/settly/docs/stories/hello-world.md
    crates/settly/docs/stories/index.md
    crates/settly/docs/traceability/index.md
    crates/settly/fuzz/Cargo.toml
    crates/settly/mise.toml
    crates/settly/nextest.toml
    crates/settly/rust-toolchain.toml
    crates/settly/rustfmt.toml
    crates/settly/src/adapters/formats.rs
    crates/settly/src/adapters/idempotency.rs
    crates/settly/src/adapters/mod.rs
    crates/settly/src/adapters/sources.rs
    crates/settly/src/application/builder.rs
    crates/settly/src/application/mod.rs
    crates/settly/src/application/submission.rs
    crates/settly/src/application/submission_tests.rs
    crates/settly/src/domain/config.rs
    crates/settly/src/domain/errors.rs
    crates/settly/src/domain/idempotency.rs
    crates/settly/src/domain/layers.rs
    crates/settly/src/domain/mod.rs
    crates/settly/src/domain/ports.rs
    crates/settly/src/domain/sources.rs
    crates/settly/src/domain/validation.rs
    crates/settly/src/infrastructure/error.rs
    crates/settly/src/infrastructure/mod.rs
    crates/settly/src/lib.rs
    docs/intent/README.md
    docs/intent/assumptions.md
    docs/intent/prompts/.gitkeep
    docs/intent/prompts/README.md
    docs/intent/synthesis.md
    docs/slsa.md
    docs/sota/README.md
    docs/sota/alternatives.md
    docs/sota/ax.md
    docs/sota/cost.md
    docs/sota/dx.md
    docs/sota/fork-rationale.md
    docs/sota/ops.md
    docs/sota/security.md
    docs/sota/technical.md
    docs/sota/ux.md
    intent.md
    okf/manifest.okf.yaml
    okf/wiki/README.md
    review.md
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
