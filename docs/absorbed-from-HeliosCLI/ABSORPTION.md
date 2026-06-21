# Absorbed from HeliosCLI

**Source:** `KooshaPari/HeliosCLI` (archived and deleted from GitHub 2026-06-21)
**Target:** `phenotype-tooling/docs/absorbed-from-HeliosCLI/`
**Tracked file count:** 241

## Purpose

This directory is a historical absorption of the source repository into `phenotype-tooling`.
All tracked source files from `git ls-files` are preserved here, plus this manifest.

## Preserved inventory

```text
    .agileplus/specs/001-codex-tui-renderer-optimization/meta.json
    .agileplus/specs/001-codex-tui-renderer-optimization/spec.md
    .agileplus/specs/001-codex-tui-renderer-optimization/tasks.md
    .airlock/workflows/main.yml
    .archive/absorb-readiness-2026-03-03/helios-cli.post-normalize.status.txt
    .archive/absorb-readiness-2026-03-03/helios-cli.recent-commits.txt
    .archive/absorb-readiness-2026-03-03/helios-cli.tracked-delta.manifest.txt
    .archive/absorb-readiness-2026-03-03/heliosCLI.post-normalize.status.txt
    .archive/absorb-readiness-2026-03-03/heliosCLI.recent-commits.txt
    .archive/absorb-readiness-2026-03-03/heliosCLI.tracked-delta.manifest.txt
    .archive/absorb-readiness-2026-03-03/repo-heads.env
    .archive/kitty-specs/001-codex-tui-renderer-optimization/checklists/requirements.md
    .archive/kitty-specs/001-codex-tui-renderer-optimization/data-model.md
    .archive/kitty-specs/001-codex-tui-renderer-optimization/meta.json
    .archive/kitty-specs/001-codex-tui-renderer-optimization/pr-layered-strategy.md
    .archive/kitty-specs/001-codex-tui-renderer-optimization/research.md
    .archive/kitty-specs/001-codex-tui-renderer-optimization/research/evidence-log.csv
    .archive/kitty-specs/001-codex-tui-renderer-optimization/research/source-register.csv
    .archive/kitty-specs/001-codex-tui-renderer-optimization/spec.md
    .archive/kitty-specs/kitty-specs/001-codex-tui-renderer-optimization/checklists/requirements.md
    .archive/kitty-specs/kitty-specs/001-codex-tui-renderer-optimization/data-model.md
    .archive/kitty-specs/kitty-specs/001-codex-tui-renderer-optimization/meta.json
    .archive/kitty-specs/kitty-specs/001-codex-tui-renderer-optimization/pr-layered-strategy.md
    .archive/kitty-specs/kitty-specs/001-codex-tui-renderer-optimization/research.md
    .archive/kitty-specs/kitty-specs/001-codex-tui-renderer-optimization/research/evidence-log.csv
    .archive/kitty-specs/kitty-specs/001-codex-tui-renderer-optimization/research/source-register.csv
    .archive/kitty-specs/kitty-specs/001-codex-tui-renderer-optimization/spec.md
    .archive/kitty-specs/kitty-specs/002-chat-composer-decomposition/meta.json
    .archive/kitty-specs/kitty-specs/002-chat-composer-decomposition/spec.md
    .bazelignore
    .bazelrc
    .bazelversion
    .cargo/config.toml
    .claude/commands/spec-kitty.accept.md
    .claude/commands/spec-kitty.analyze.md
    .claude/commands/spec-kitty.checklist.md
    .claude/commands/spec-kitty.clarify.md
    .claude/commands/spec-kitty.constitution.md
    .claude/commands/spec-kitty.dashboard.md
    .claude/commands/spec-kitty.implement.md
    .claude/commands/spec-kitty.merge.md
    .claude/commands/spec-kitty.plan.md
    .claude/commands/spec-kitty.research.md
    .claude/commands/spec-kitty.review.md
    .claude/commands/spec-kitty.specify.md
    .claude/commands/spec-kitty.status.md
    .claude/commands/spec-kitty.tasks.md
    .claudeignore
    .coderabbit.yaml
    .codespellignore
    .codespellrc
    .codex/skills/babysit-pr/SKILL.md
    .codex/skills/babysit-pr/agents/openai.yaml
    .codex/skills/babysit-pr/references/github-api-notes.md
    .codex/skills/babysit-pr/references/heuristics.md
    .codex/skills/babysit-pr/scripts/gh_pr_watch.py
    .codex/skills/test-tui/SKILL.md
    .config/nextest.toml
    .coverage
    .devcontainer/Dockerfile
    .devcontainer/README.md
    .devcontainer/devcontainer.json
    .editorconfig
    .env.example
    .gemini/config.yaml
    .gitattributes
    .github/CODEOWNERS
    .github/FUNDING.yml
    .github/ISSUE_TEMPLATE/1-codex-app.yml
    .github/ISSUE_TEMPLATE/2-extension.yml
    .github/ISSUE_TEMPLATE/3-cli.yml
    .github/ISSUE_TEMPLATE/4-bug-report.yml
    .github/ISSUE_TEMPLATE/5-feature-request.yml
    .github/ISSUE_TEMPLATE/6-docs-issue.yml
    .github/ISSUE_TEMPLATE/bug_report.md
    .github/ISSUE_TEMPLATE/bug_report.yml
    .github/ISSUE_TEMPLATE/config.yml
    .github/ISSUE_TEMPLATE/epic_teammate_system.md
    .github/ISSUE_TEMPLATE/feature_multi_level_cache.md
    .github/ISSUE_TEMPLATE/feature_request.md
    .github/ISSUE_TEMPLATE/feature_request.yml
    .github/ISSUE_TEMPLATE/teammate_subagent_system.md
    .github/PULL_REQUEST_TEMPLATE.md
    .github/RULESET_BASELINE.md
    .github/SECURITY.md
    .github/actions/linux-code-sign/action.yml
    .github/actions/macos-code-sign/action.yml
    .github/actions/macos-code-sign/notary_helpers.sh
    .github/actions/policy-gate/action.yml
    .github/actions/windows-code-sign/action.yml
    .github/codex-cli-splash.png
    .github/codex/home/config.toml
    .github/codex/labels/codex-attempt.md
    .github/codex/labels/codex-review.md
    .github/codex/labels/codex-rust-review.md
    .github/codex/labels/codex-triage.md
    .github/dependabot.yaml
    .github/dependabot.yml
    .github/dotslash-config.json
    .github/hooks/pre-commit
    .github/hooks/security-guard.sh
    .github/scripts/install-musl-build-tools.sh
    .github/scripts/security-guard.sh
    .github/workflows/Dockerfile.bazel
    .github/workflows/alert-sync-issues.yml
    .github/workflows/audit.yml
    .github/workflows/bazel.yml
    .github/workflows/cargo-audit.yml
    .github/workflows/cargo-deny.yml
    .github/workflows/cargo-machete.yml
    .github/workflows/cargo-semver-checks.yml
    .github/workflows/ci.bazelrc
    .github/workflows/ci.yml
    .github/workflows/cla.yml
    .github/workflows/close-stale-contributor-prs.yml
    .github/workflows/codeql-rust.yml
    .github/workflows/codeql.yml
    .github/workflows/codespell.yml
    .github/workflows/cpu-profiling.yml
    .github/workflows/deny.yml
    .github/workflows/docs-site.yml
    .github/workflows/e2e.yml
    .github/workflows/fuzzing.yml
    .github/workflows/helios-cli-release.yml
    .github/workflows/helios-cli.yml
    .github/workflows/iac-scan.yml
    .github/workflows/issue-deduplicator.yml
    .github/workflows/issue-labeler.yml
    .github/workflows/journey-gate.yml
    .github/workflows/leak-detection.yml
    .github/workflows/license-compliance.yml
    .github/workflows/network-optimization.yml
    .github/workflows/pages.yml
    .github/workflows/policy-gate.yml
    .github/workflows/pr-babysit-watch.yml
    .github/workflows/pr-governance-gate.yml
    .github/workflows/python-ci.yml
    .github/workflows/quality.yml
    .github/workflows/release-attestation.yml
    .github/workflows/release.yml
    .github/workflows/review-wave-orchestrator.yml
    .github/workflows/rust-ci.yml
    .github/workflows/rust-release-prepare.yml
    .github/workflows/rust-release-windows.yml
    .github/workflows/rust-release.yml
    .github/workflows/sast-full.yml
    .github/workflows/sast-quick.yml
    .github/workflows/scorecard.yml
    .github/workflows/sdk.yml
    .github/workflows/security-guard-hook-audit.yml
    .github/workflows/security-guard.yml
    .github/workflows/sentry-error-tracking.yml
    .github/workflows/shell-tool-mcp-ci.yml
    .github/workflows/shell-tool-mcp.yml
    .github/workflows/snyk-scan.yml
    .github/workflows/sonarcloud.yml
    .github/workflows/stage-gates.yml
    .github/workflows/trivy-scan.yml
    .github/workflows/trufflehog.yml
    .github/workflows/workflow-maintenance.yml
    .github/workflows/workflow-sync.yml
    .github/workflows/zap-dast.yml
    .github/workflows/zstd
    .gitignore
    .gitmodules
    .kittify/.dashboard
    .kittify/AGENTS.md
    .kittify/config.yaml
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
    .markdownlint-cli2.yaml
    .mise.toml
    .npmrc
    .pre-commit-config.yaml
    .prettierignore
    .prettierrc.toml
    .process-compose/dev-fast.yaml
    .process-compose/dev-full.yaml
    .serena/.gitignore
    .serena/memories/memory_maintenance.md
    .serena/project.local.yml
    .serena/project.yml
    .vscode/extensions.json
    .vscode/launch.json
    .vscode/settings.json
    .worktrees/chore-govern-pi
```

## Intentional exclusions

The following generated/runtime artifacts exist in the source working tree but are intentionally not mirrored because they are not tracked source files:

- `__pycache__/`
- `*.egg-info/`
- `target/`
- `.benchmarks/`
- `.pytest_cache/`
- `node_modules/`
- `build/`
- `dist/`

## Verification note

Coverage is intended to match the source repository tracked inventory exactly; any extra files in this directory are limited to this manifest and may be used for archival context.
