# Absorbed from authkit

**Source:** `KooshaPari/authkit` (archived and deleted from GitHub 2026-06-21)
**Target:** `phenotype-tooling/docs/absorbed-from-authkit/`
**Tracked file count:** 200
**Local clone available:** true

## Justification

| Field | Value |
|---|---|
| Repository description | "Auth/AuthZ framework with OAuth2, JWT, and RBAC/ABAC support" |
| Type | Archived "*-kit" library (predecessor namespace) |
| GitHub archive status | Archived prior to this absorption |
| Active successor | See notes below |
| Recommendation | Absorb and delete — content is preserved in this collection |

## Notes

- "Auth/AuthZ framework with OAuth2, JWT, and RBAC/ABAC support"
- Active successor `KooshaPari/AuthKit` does not exist (only lowercase `authkit` exists, now archived)
- Note: `KooshaPari/phenotype-auth-ts` was absorbed into `KooshaPari/AuthKit` per L5-109 retirement — but `AuthKit` itself was never created on GitHub
- 200 tracked files locally — full content preserved (the most substantial of the 9)
- 10 gitlinks (submodules) preserved as `.GITLINK` placeholders

## Preserved inventory

```text
    .config/nextest.toml
    .editorconfig
    .gitattributes
    .github/CODEOWNERS
    .github/FUNDING.yml
    .github/ISSUE_TEMPLATE/bug_report.md
    .github/ISSUE_TEMPLATE/feature_request.md
    .github/PULL_REQUEST_TEMPLATE.md
    .github/codeql/codeql-config.yml
    .github/dependabot.yml
    .github/workflows/cargo-deny.yml
    .github/workflows/ci.yml
    .github/workflows/codeql.yml
    .github/workflows/doc-links.yml
    .github/workflows/fr-coverage.yml
    .github/workflows/quality-gate.yml
    .github/workflows/release-attestation.yml
    .github/workflows/release-drafter.yml
    .github/workflows/release.yml
    .github/workflows/scorecard.yml
    .github/workflows/trufflehog.yml
    .gitignore
    .pre-commit-config.yaml
    .trufflehog.yml
    ADR.md
    AGENTS.md
    CHANGELOG.md
    CHARTER.md
    CITATION.cff
    CLAUDE.md
    CODEOWNERS
    CODE_OF_CONDUCT.md
    CONTRIBUTING.md
    Cargo.toml
    FRs/FR-AUTH-001.md
    FRs/FR-AUTH-002.md
    FRs/FR-AUTH-003.md
    FRs/FR-AUTH-004.md
    FRs/FR-AUTH-005.md
    FRs/FR-AUTH-006.md
    FRs/FR-AUTH-007.md
    FRs/FR-AUTH-008.md
    FRs/FR-AUTH-009.md
    FRs/FR-AUTH-010.md
    FUNCTIONAL_REQUIREMENTS.md
    FUNDING.yml
    LICENSE
    PLAN.md
    PRD.md
    README.md
    SECURITY.md
    Taskfile.yml
    audit_scorecard.json
    benches/auth.rs
    benches/benchmarks.rs
    benches/perf.rs
    cargo-machete.yml
    crates/authkit-core/Cargo.toml
    crates/authkit-core/src/adapters/audit.rs
    crates/authkit-core/src/adapters/hashers.rs
    crates/authkit-core/src/adapters/kms.rs
    crates/authkit-core/src/adapters/mod.rs
    crates/authkit-core/src/adapters/refresh_token.rs
    crates/authkit-core/src/adapters/revocation.rs
    crates/authkit-core/src/adapters/storage.rs
    crates/authkit-core/src/adapters/vault_store.rs
    crates/authkit-core/src/application/mod.rs
    crates/authkit-core/src/application/services.rs
    crates/authkit-core/src/domain/auth.rs
    crates/authkit-core/src/domain/errors.rs
    crates/authkit-core/src/domain/identity.rs
    crates/authkit-core/src/domain/mod.rs
    crates/authkit-core/src/domain/pkce.rs
    crates/authkit-core/src/domain/policy.rs
    crates/authkit-core/src/domain/ports.rs
    crates/authkit-core/src/domain/session.rs
    crates/authkit-core/src/domain/session_store.rs
    crates/authkit-core/src/domain/signing.rs
    crates/authkit-core/src/domain/vault.rs
    crates/authkit-core/src/infrastructure/error.rs
    crates/authkit-core/src/infrastructure/mod.rs
    crates/authkit-core/src/lib.rs
    crates/authkit-core/src/middleware/adapter.rs
    crates/authkit-core/src/middleware/mod.rs
    crates/authkit-core/src/middleware/pkce_state_session.rs
    crates/phenotype-auth-contracts/Cargo.toml
    crates/phenotype-auth-contracts/src/auth.rs
    crates/phenotype-auth-contracts/src/lib.rs
    crates/phenotype-auth-contracts/src/policy.rs
    crates/phenotype-casbin-wrapper/Cargo.toml
    crates/phenotype-casbin-wrapper/src/adapter.rs
    crates/phenotype-casbin-wrapper/src/error.rs
    crates/phenotype-casbin-wrapper/src/lib.rs
    crates/phenotype-casbin-wrapper/src/models.rs
    crates/phenotype-cipher/Cargo.toml
    crates/phenotype-cipher/src/core/encryption.rs
    crates/phenotype-cipher/src/core/hashing.rs
    crates/phenotype-cipher/src/core/mod.rs
    crates/phenotype-cipher/src/core/signatures.rs
    crates/phenotype-cipher/src/lib.rs
    crates/phenotype-crypto/Cargo.toml
    crates/phenotype-crypto/src/hash.rs
    crates/phenotype-crypto/src/kdf.rs
    crates/phenotype-crypto/src/key.rs
    crates/phenotype-crypto/src/lib.rs
    crates/phenotype-crypto/src/random.rs
    crates/phenotype-crypto/src/signing.rs
    deny.toml
    docs/FUNCTIONAL_REQUIREMENTS.md
    docs/PLAN.md
    docs/PRD.md
    docs/SPEC.md
    docs/adr/ADR-001-auth-flow.md
    docs/adr/ADR-002-session-management.md
    docs/adr/ADR-003-multi-provider.md
    docs/adr/ADRS.md
    docs/audit/BLOCK-C-AUDIT.md
    docs/boundary/AuthKit.md
    docs/index.md
    docs/intent/AuthKit.md
    docs/journeys/manifests/README.md
    docs/operations/iconography/SPEC.md
    docs/operations/journey-traceability.md
    docs/reference/fr_coverage_matrix.md
    docs/research/AUTH_TOOLKITS_SOTA.md
    docs/slsa.md
    docs/sota/SOTA.md
    docs/worklogs/README.md
    go
    justfile
    pyproject.toml
    pyrightconfig.json
    python/authkit/README.md
    python/authkit/__init__.py
    python/authkit/pyproject.toml
    python/pheno-auth
    python/pheno-security
    registry.yaml
    rust-toolchain.toml
    rust/Cargo.toml
    rust/deny.toml
    rust/phenotype-bid/Cargo.toml
    rust/phenotype-bid/src/lib.rs
    rust/phenotype-content-hash/Cargo.toml
    rust/phenotype-content-hash/src/lib.rs
    rust/phenotype-contracts/Cargo.toml
    rust/phenotype-contracts/src/lib.rs
    rust/phenotype-security-aggregator/Cargo.toml
    rust/phenotype-security-aggregator/src/health_integration.rs
    rust/phenotype-security-aggregator/src/lib.rs
    rust/phenotype-security-aggregator/src/sources.rs
    tests/__init__.py
    tests/integration_tests.rs
    tests/pkce_constants.rs
    tests/session_is_valid.rs
    tests/test_smoke.py
    tests/unit_tests.rs
    typescript/package.json
    typescript/packages/auth-ts/.editorconfig
    typescript/packages/auth-ts/.gitignore
    typescript/packages/auth-ts/.nvmrc
    typescript/packages/auth-ts/.pre-commit-config.yaml
    typescript/packages/auth-ts/ADR.md
    typescript/packages/auth-ts/CHANGELOG.md
    typescript/packages/auth-ts/CITATION.cff
    typescript/packages/auth-ts/CODEOWNERS
    typescript/packages/auth-ts/FUNCTIONAL_REQUIREMENTS.md
    typescript/packages/auth-ts/FUNDING.yml
    typescript/packages/auth-ts/LICENSE
    typescript/packages/auth-ts/PRD.md
    typescript/packages/auth-ts/README.md
    typescript/packages/auth-ts/adr/ADR-001-architecture.md
    typescript/packages/auth-ts/docs/.vitepress/config.mts
    typescript/packages/auth-ts/docs/.vitepress/theme/custom.css
    typescript/packages/auth-ts/docs/.vitepress/theme/index.ts
    typescript/packages/auth-ts/docs/.vitepress/theme/style.css
    typescript/packages/auth-ts/docs/FUNCTIONAL_REQUIREMENTS.md
    typescript/packages/auth-ts/docs/getting-started.md
    typescript/packages/auth-ts/docs/index.md
    typescript/packages/auth-ts/docs/journeys/manifests/README.md
    typescript/packages/auth-ts/docs/operations/iconography/SPEC.md
    typescript/packages/auth-ts/docs/operations/journey-traceability.md
    typescript/packages/auth-ts/docs/reference/fr_coverage_matrix.md
    typescript/packages/auth-ts/package.json
    typescript/packages/auth-ts/renovate.json5
    typescript/packages/auth-ts/sonar-project.properties
    typescript/packages/auth-ts/src/adapters/jwt-provider.ts
    typescript/packages/auth-ts/src/adapters/memory-token-store.ts
    typescript/packages/auth-ts/src/domain/claims.ts
    typescript/packages/auth-ts/src/domain/errors.ts
    typescript/packages/auth-ts/src/domain/token.ts
    typescript/packages/auth-ts/src/index.ts
    typescript/packages/auth-ts/src/ports/index.ts
    typescript/packages/auth-ts/tests/core.test.ts
    typescript/packages/auth-ts/tests/phenotype-ts-utils.test.ts
    typescript/packages/auth-ts/tests/token.contract.test.ts
    typescript/packages/auth-ts/tools/Export-Brand.ps1
    typescript/packages/auth-ts/tsconfig.json
    typescript/packages/auth-ts/worklog.md
    worklog.md
```

## Verification note

For local-clone-available absorptions: coverage matches `git ls-files` exactly.
For retroactive stubs: source content is not preserved; GitHub 90-day tombstone recovery is the only path.
