# Absorbed from phenotype-dep-guard

**Source:** `KooshaPari/phenotype-dep-guard`
**Target:** `phenotype-tooling/docs/absorbed-from-phenotype-dep-guard/`
**Tracked file count:** 158

## Purpose

This directory is a historical absorption of the source repository into `phenotype-tooling`.
All tracked source files from `git ls-files` are preserved here, plus this manifest.

## Preserved inventory

```text
    .agileplus/agileplus.db
    .agileplus/agileplus.db-shm
    .agileplus/agileplus.db-wal
    .claudeignore
    .editorconfig
    .gitattributes
    .github/CODEOWNERS
    .github/FUNDING.yml
    .github/ISSUE_TEMPLATE/bug_report.md
    .github/ISSUE_TEMPLATE/config.yml
    .github/ISSUE_TEMPLATE/config_issue.md
    .github/ISSUE_TEMPLATE/feature_request.md
    .github/PULL_REQUEST_TEMPLATE.md
    .github/dependabot.yml
    .github/workflows/branch-protection-audit.yml
    .github/workflows/ci.yml
    .github/workflows/doc-links.yml
    .github/workflows/fr-coverage.yml
    .github/workflows/policy-gate.yml
    .github/workflows/python-ci.yml
    .github/workflows/quality-gate.yml
    .github/workflows/reusable-dep-guard.yml
    .github/workflows/trufflehog.yml
    .gitignore
    .kittify/AGENTS.md
    .kittify/config.yaml
    .kittify/memory/constitution.md
    .kittify/metadata.yaml
    .kittify/missions/documentation/command-templates/implement.md
    .kittify/missions/documentation/command-templates/plan.md
    .kittify/missions/documentation/command-templates/review.md
    .kittify/missions/documentation/command-templates/specify.md
    .kittify/missions/documentation/command-templates/tasks.md
    .kittify/missions/documentation/mission.yaml
    .kittify/missions/documentation/templates/divio/explanation-template.md
    .kittify/missions/documentation/templates/divio/howto-template.md
    .kittify/missions/documentation/templates/divio/reference-template.md
    .kittify/missions/documentation/templates/divio/tutorial-template.md
    .kittify/missions/documentation/templates/generators/jsdoc.json.template
    .kittify/missions/documentation/templates/generators/sphinx-conf.py.template
    .kittify/missions/documentation/templates/plan-template.md
    .kittify/missions/documentation/templates/release-template.md
    .kittify/missions/documentation/templates/spec-template.md
    .kittify/missions/documentation/templates/task-prompt-template.md
    .kittify/missions/documentation/templates/tasks-template.md
    .kittify/missions/research/command-templates/implement.md
    .kittify/missions/research/command-templates/merge.md
    .kittify/missions/research/command-templates/plan.md
    .kittify/missions/research/command-templates/review.md
    .kittify/missions/research/command-templates/specify.md
    .kittify/missions/research/command-templates/tasks.md
    .kittify/missions/research/mission.yaml
    .kittify/missions/research/templates/data-model-template.md
    .kittify/missions/research/templates/plan-template.md
    .kittify/missions/research/templates/research-template.md
    .kittify/missions/research/templates/research/evidence-log.csv
    .kittify/missions/research/templates/research/source-register.csv
    .kittify/missions/research/templates/spec-template.md
    .kittify/missions/research/templates/task-prompt-template.md
    .kittify/missions/research/templates/tasks-template.md
    .kittify/missions/software-dev/command-templates/accept.md
    .kittify/missions/software-dev/command-templates/analyze.md
    .kittify/missions/software-dev/command-templates/checklist.md
    .kittify/missions/software-dev/command-templates/clarify.md
    .kittify/missions/software-dev/command-templates/constitution.md
    .kittify/missions/software-dev/command-templates/dashboard.md
    .kittify/missions/software-dev/command-templates/implement.md
    .kittify/missions/software-dev/command-templates/merge.md
    .kittify/missions/software-dev/command-templates/plan.md
    .kittify/missions/software-dev/command-templates/review.md
    .kittify/missions/software-dev/command-templates/specify.md
    .kittify/missions/software-dev/command-templates/tasks.md
    .kittify/missions/software-dev/mission.yaml
    .kittify/missions/software-dev/templates/plan-template.md
    .kittify/missions/software-dev/templates/spec-template.md
    .kittify/missions/software-dev/templates/task-prompt-template.md
    .kittify/missions/software-dev/templates/tasks-template.md
    .kittify/scripts/debug-dashboard-scan.py
    .kittify/scripts/tasks/acceptance_core.py
    .kittify/scripts/tasks/acceptance_support.py
    .kittify/scripts/tasks/task_helpers.py
    .kittify/scripts/tasks/task_helpers_shared.py
    .kittify/scripts/tasks/tasks_cli.py
    .kittify/scripts/validate_encoding.py
    ADR.md
    AGENTS.md
    ARCHIVED.md
    CHANGELOG.md
    CLAUDE.md
    CODEOWNERS
    CODE_OF_CONDUCT.md
    CONTRIBUTING.md
    FUNCTIONAL_REQUIREMENTS.md
    FUNDING.yml
    LICENSE
    LICENSE-APACHE
    LICENSE-MIT
    PRD.md
    README.md
    SECURITY.md
    Taskfile.yml
    audit_scorecard.json
    contracts/reconcile.rules.yaml
    contracts/template.manifest.json
    deny.toml
    docs/BRANCH_PROTECTION.md
    docs/boundary/phenotype-dep-guard.md
    docs/index.md
    docs/intent/phenotype-dep-guard.md
    docs/security/THREAT_MODEL.md
    docs/sessions/2026-03-01-template-workflow-hardening/00_SESSION_OVERVIEW.md
    docs/sessions/2026-03-01-template-workflow-hardening/01_RESEARCH.md
    docs/sessions/2026-03-01-template-workflow-hardening/02_SPECIFICATIONS.md
    docs/sessions/2026-03-01-template-workflow-hardening/03_DAG_WBS.md
    dprint.json
    justfile
    kitty-specs/layered-template-platform/ADR.md
    kitty-specs/layered-template-platform/DOMAIN_WAVE.md
    kitty-specs/layered-template-platform/FR.md
    kitty-specs/layered-template-platform/IMPLEMENTATION_STRATEGY.md
    kitty-specs/layered-template-platform/POLYGLOT_HEX_STRATEGY.md
    kitty-specs/layered-template-platform/PRD.md
    kitty-specs/layered-template-platform/TESTING_STRATEGY.md
    kitty-specs/layered-template-platform/WBS_DAG.md
    kitty-specs/layered-template-platform/data-model.md
    kitty-specs/layered-template-platform/research.md
    kitty-specs/layered-template-platform/research/evidence-log.csv
    kitty-specs/layered-template-platform/research/source-register.csv
    kitty-specs/phenotype-dep-guard/contracts/governance-v1.json
    kitty-specs/phenotype-dep-guard/plan.md
    kitty-specs/phenotype-dep-guard/spec.md
    kitty-specs/phenotype-dep-guard/tasks/WP01-initial-implementation.md
    ports/Cargo.toml
    ports/release_spec.md
    ports/src/adapters/cargo.rs
    ports/src/adapters/mod.rs
    ports/src/adapters/npm.rs
    ports/src/lib.rs
    ports/src/supply_chain.rs
    ports/tests/supply_chain.rs
    pyproject.toml
    pyrightconfig.json
    requirements-audit.txt
    requirements.txt
    schemas/README.md
    scripts/scaffold-smoke.sh
    scripts/validate-domains.sh
    scripts/validate-foundation.sh
    src/phenotype_dep_guard/agent.py
    src/phenotype_dep_guard/cli.py
    src/phenotype_dep_guard/console.py
    src/phenotype_dep_guard/resolver.py
    src/phenotype_dep_guard/triage.py
    tests/create_sample.py
    tests/samples/malicious_pkg/site-packages-malicious.pth
    tests/test_triage.py
    tests/verify_triage.py
    worklog.md
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
