# Absorbed from phenotype-teamcomm

**Source:** `KooshaPari/phenotype-teamcomm`
**Target:** `phenotype-tooling/docs/absorbed-from-phenotype-teamcomm/`
**Tracked file count:** 76

## Purpose

This directory is a historical absorption of the source repository into `phenotype-tooling`.
All tracked source files from `git ls-files` are preserved here, plus this manifest.

## Preserved inventory

```text
    .editorconfig
    .github/CODEOWNERS
    .github/ISSUE_TEMPLATE/bug_report.md
    .github/ISSUE_TEMPLATE/config.yml
    .github/ISSUE_TEMPLATE/feature_request.md
    .github/ISSUE_TEMPLATE/question.md
    .github/ISSUE_TEMPLATE/security_report.md
    .github/PULL_REQUEST_TEMPLATE.md
    .github/workflows/ci.yml
    .github/workflows/release-attestation.yml
    .gitignore
    AGENTS.md
    ARCHITECTURE.md
    CHANGELOG.md
    CODE_OF_CONDUCT.md
    CONTRIBUTING.md
    Cargo.toml
    LICENSE
    README.md
    SECURITY.md
    SPEC.md
    WORKLOG.md
    configs/.gitkeep
    configs/README.md
    crates/teamcomm-cli/Cargo.toml
    crates/teamcomm-cli/src/cmd_daemon.rs
    crates/teamcomm-cli/src/cmd_discover.rs
    crates/teamcomm-cli/src/cmd_inbox.rs
    crates/teamcomm-cli/src/cmd_reservations.rs
    crates/teamcomm-cli/src/cmd_sessions.rs
    crates/teamcomm-cli/src/cmd_state.rs
    crates/teamcomm-cli/src/connect.rs
    crates/teamcomm-cli/src/main.rs
    crates/teamcomm-cli/src/output.rs
    crates/teamcomm-cli/src/rpc.rs
    crates/teamcomm-client/Cargo.toml
    crates/teamcomm-client/src/lib.rs
    crates/teamcomm-daemon/Cargo.toml
    crates/teamcomm-daemon/src/config.rs
    crates/teamcomm-daemon/src/db.rs
    crates/teamcomm-daemon/src/error.rs
    crates/teamcomm-daemon/src/handlers.rs
    crates/teamcomm-daemon/src/lib.rs
    crates/teamcomm-daemon/src/listener.rs
    crates/teamcomm-daemon/src/main.rs
    crates/teamcomm-daemon/src/pid.rs
    crates/teamcomm-daemon/src/state.rs
    crates/teamcomm-daemon/tests/integration.rs
    crates/teamcomm-mcp/Cargo.toml
    crates/teamcomm-mcp/mcp/manifest.json
    crates/teamcomm-mcp/src/dispatch.rs
    crates/teamcomm-mcp/src/handlers.rs
    crates/teamcomm-mcp/src/lib.rs
    crates/teamcomm-mcp/src/main.rs
    crates/teamcomm-mcp/src/manifest.rs
    crates/teamcomm-mcp/tests/dispatch.rs
    crates/teamcomm-mcp/tests/manifest.rs
    crates/teamcomm-protocol/Cargo.toml
    crates/teamcomm-protocol/src/discovery.rs
    crates/teamcomm-protocol/src/error.rs
    crates/teamcomm-protocol/src/hook_event.rs
    crates/teamcomm-protocol/src/inbox.rs
    crates/teamcomm-protocol/src/lib.rs
    crates/teamcomm-protocol/src/reservation.rs
    crates/teamcomm-protocol/src/rpc.rs
    crates/teamcomm-protocol/src/session.rs
    crates/teamcomm-protocol/src/state.rs
    crates/teamcomm-protocol/src/thread.rs
    docs/.gitkeep
    docs/SDD.md
    docs/index.md
    docs/slsa.md
    dprint.json
    justfile
    schemas/.gitkeep
    tests/.gitkeep
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
