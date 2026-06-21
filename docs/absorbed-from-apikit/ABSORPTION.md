# Absorbed from apikit

**Source:** `KooshaPari/apikit` (archived and deleted from GitHub 2026-06-21)
**Target:** `phenotype-tooling/docs/absorbed-from-apikit/`
**Tracked file count:** 107
**Local clone available:** true

## Justification

| Field | Value |
|---|---|
| Repository description | "HTTP toolkit — REST, GraphQL, and WebSocket adapters (extracted from Apisync, apikit v0.1.0)" |
| Type | Archived "*-kit" library (predecessor namespace) |
| GitHub archive status | Archived prior to this absorption |
| Active successor | See notes below |
| Recommendation | Absorb and delete — content is preserved in this collection |

## Notes

- "HTTP toolkit — REST, GraphQL, and WebSocket adapters (extracted from Apisync, apikit v0.1.0)"
- Active successor `KooshaPari/apikit-httpora-final` was deleted 2026-06-18 (no longer exists)
- 107 tracked files locally — full content preserved
- 9 gitlinks (submodules) preserved as `.GITLINK` placeholders

## Preserved inventory

```text
    .agileplus/specs/001-core-setup/meta.json
    .agileplus/specs/001-core-setup/spec.md
    .agileplus/specs/001-core-setup/tasks.md
    .clippy.toml
    .config/nextest.toml
    .editorconfig
    .env.example
    .gitattributes
    .githooks/pre-commit
    .githooks/pre-push
    .github/CODEOWNERS
    .github/FUNDING.yml
    .github/ISSUE_TEMPLATE/bug.yml
    .github/ISSUE_TEMPLATE/feature.yml
    .github/dependabot.yml
    .github/workflows/audit.yml
    .github/workflows/cargo-deny.yml
    .github/workflows/ci.yml
    .github/workflows/coverage.yml
    .github/workflows/pages-deploy.yml
    .github/workflows/quality-gate.yml
    .github/workflows/release.yml
    .github/workflows/sast.yml
    .github/workflows/scorecard.yml
    .github/workflows/security-deep-scan.yml
    .github/workflows/security-guard.yml
    .github/workflows/trufflehog.yml
    .gitignore
    .health-dashboard.yml
    .pre-commit-config.yaml
    CHANGELOG.md
    CITATION.cff
    CODEOWNERS
    CODE_OF_CONDUCT.md
    CONTRIBUTING.md
    Cargo.toml
    Cargo.toml.apisync-legacy
    FUNDING.yml
    LICENSE
    README.md
    SECURITY.md
    Taskfile.yml
    VERSION
    _typos.toml
    audit_scorecard.json
    benches/api.rs
    benches/graphql_benchmark.rs
    benches/perf.rs
    cliff.toml
    codecov.yml
    deny.toml
    docs/FUNCTIONAL_REQUIREMENTS.md
    docs/SPEC.md
    docs/TEST_COVERAGE_MATRIX.md
    docs/governance/.vitepress/config.mts
    docs/governance/ADR.md
    docs/governance/AGENTS.md
    docs/governance/CHANGELOG.apisync.md
    docs/governance/CLAUDE.md
    docs/governance/FUNCTIONAL_REQUIREMENTS.apisync.md
    docs/governance/PLAN.apisync.md
    docs/governance/PRD.apisync.md
    docs/governance/README.apisync.md
    docs/governance/SPEC.apisync.md
    docs/governance/STATUS.apisync.md
    docs/governance/TEST_COVERAGE_MATRIX.apisync.md
    docs/governance/adr/001-hexagonal-architecture.md
    docs/governance/adr/002-hyper-over-axum.md
    docs/governance/adr/003-async-graphql.md
    docs/governance/adr/004-tokio-tungstenite.md
    docs/governance/adr/005-criterion.md
    docs/index.apisync.md
    docs/research/SOTA.md
    docs/sessions/journeys/index.md
    docs/sessions/journeys/quick-start.md
    docs/sessions/stories/hello-world.md
    docs/sessions/stories/index.md
    docs/sessions/traceability/index.md
    docs/slsa.md
    fuzz/Cargo.toml
    llms.txt
    mise.toml
    nextest.toml
    rust-toolchain.toml
    rustfmt.toml
    sentry_config.rs
    src/adapters/graphql/mod.rs
    src/adapters/graphql/schema.rs
    src/adapters/graphql/server.rs
    src/adapters/mod.rs
    src/adapters/rest/hyper_server.rs
    src/adapters/rest/mod.rs
    src/adapters/websocket/mod.rs
    src/adapters/websocket/server.rs
    src/application/handler.rs
    src/application/mod.rs
    src/application/router.rs
    src/domain/middleware.rs
    src/domain/mod.rs
    src/endpoints.rs
    src/infrastructure/logging.rs
    src/infrastructure/mod.rs
    src/lib.rs
    src/lib.rs.apisync-legacy
    tests/README.md
    tests/property_tests.rs
    tests/rest_integration_tests.rs
```

## Verification note

For local-clone-available absorptions: coverage matches `git ls-files` exactly.
For retroactive stubs: source content is not preserved; GitHub 90-day tombstone recovery is the only path.
