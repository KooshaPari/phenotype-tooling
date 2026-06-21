# Claude AI Agent Guide

This repository is designed to work seamlessly with Claude (and other advanced AI agents) as an autonomous software engineer.

**Authority and Scope**
- This file is the canonical contract for all agent behavior in this repository.
- Act autonomously; only pause when blocked by missing secrets, external access, or truly destructive actions.

---

## Table of Contents

1. [Core Expectations for Agents](#1-core-expectations-for-agents)
2. [Repository Mental Model](#2-repository-mental-model)
3. [File Size & Modularity Mandate](#3-file-size--modularity-mandate)
4. [Standard Operating Loop (SWE Autopilot)](#4-standard-operating-loop-swe-autopilot)
5. [CLI Usage](#5-cli-usage)
6. [Test File Naming & Organization](#6-test-file-naming--organization)
7. [File Naming & Organization](#7-file-naming--organization)
8. [Session Documentation Management](#8-session-documentation-management)
9. [Architecture Mandates](#9-architecture-mandates)
10. [Project-Specific Patterns](#10-project-specific-patterns)
11. [Security & Secrets](#11-security--secrets)
12. [Common Workflows](#12-common-workflows)
13. [Troubleshooting](#13-troubleshooting)
14. [Performance Metrics](#14-performance-metrics)
15. [MCP Integration Patterns](#15-mcp-integration-patterns)
16. [Multi-Model Orchestration](#16-multi-model-orchestration)

---

## 1. Core Expectations for Agents

### Autonomous Operation (Critical - Minimal Human Intervention)

Agents MUST operate with **maximum autonomy**:

**When to proceed without asking:**
- Implementation details and technical approach decisions
- Library/framework choices aligned with existing patterns
- Code structure and organization
- Test strategies and coverage approaches
- Refactoring and optimization decisions
- Bug fixes and performance improvements
- Documentation updates
- Decomposition of large files
- Consolidation of duplicate code
- Removing dead code and legacy patterns

**Only ask when truly blocked by:**
- Missing credentials/secrets (cannot be inferred from environment)
- External service access permissions
- Genuine product ambiguity (behavior not determinable from specs/code/tests)
- Destructive operations (production data deletion, forced pushes)

**Default behavior: Research → Decide → Implement → Validate → Continue**

### Research-First Development (CRITICAL)

Before implementing ANY feature or fix, agents MUST conduct comprehensive research:

**1. Codebase Research (Always Required):**
```bash
# Find similar implementations
rg "pattern_name" --type py -A 5 -B 5

# Trace call chains
rg "function_name\(" --type py

# Find test patterns
rg "def test_.*pattern" tests/ -A 10

# Check architecture patterns
rg "class.*Adapter\|class.*Factory\|class.*Service" --type py

# Find all usages of a module
rg "from.*module_name import" --type py

# Check for existing abstractions
rg "class.*Base\|class.*Abstract\|class.*Interface" --type py

# Find configuration patterns
rg "Settings\|Config\|Environment" --type py -A 3

# Locate error handling patterns
rg "raise.*Error\|except.*:" --type py -A 2
```

**2. Web Research (When Needed):**
- External API documentation
- Library usage patterns (when introducing new dependencies)
- Best practices for performance/security patterns
- Debugging rare errors or edge cases
- Framework-specific patterns (FastAPI, FastMCP, Pydantic)
- Cloud service integration patterns (Supabase, Vercel, etc.)

**3. Research Documentation:**
- Document findings in `docs/sessions/<session-id>/01_RESEARCH.md`
- Include URLs, code examples, and decision rationale
- Update continuously as new information discovered
- Reference findings in implementation decisions

### Autonomous SWE Loop

Follow continuous loop: **research → plan → execute → validate → polish → repeat**

- Do not ask for step-by-step guidance unless blocked
- Make decisions based on:
  - Existing codebase patterns
  - This contract file
  - Research findings
  - Test results and validation

### Environment & Tooling

```bash
# Always activate project environment first
source .venv/bin/activate

# Prefer uv for Python execution
uv run <command>
uv pip install <package>

# Use project CLI when available (CRITICAL)
# See CLI Reference section below
```

### Aggressive Change Policy (CRITICAL)

**NO backwards compatibility. NO gentle migrations. NO MVP-grade implementations.**

- **Avoid ANY backwards compatibility shims or legacy fallbacks**
- **Always perform FULL, COMPLETE changes** when refactoring
- **Do NOT preserve deprecated patterns** for transition periods
- **Remove old code paths entirely** when replacing them
- **Update ALL callers simultaneously** when changing signatures

**Forward-Only Progression:**
- NO `git revert` or `git reset` (fix forward instead)
- NO haphazard delete-and-rewrite cycles
- Push forward to clean, working states via incremental fixes
- Document issues in `05_KNOWN_ISSUES.md`, resolve systematically

**Full Production-Grade Implementation:**
- NO minimal implementations or MVPs
- NO "we'll add this later" placeholder code
- Every feature: production-ready, fully tested, documented
- Complete error handling, edge cases, logging
- Full test coverage (unit + integration where applicable)

---

## 2. Repository Mental Model

Understand these as first-class constraints before editing:

### Runtime & Framework
- **Python**: 3.10+ (async-first)
- **Framework**: FastAPI/FastMCP
- **Package Manager**: uv preferred
- **Type System**: Pydantic models, strict typing

### Key Modules
```
src/<package>/
  main.py              # Application entrypoint
  app.py               # ASGI entrypoint for Vercel/stateless HTTP
  server.py            # Core MCP server wiring, auth, rate limiting
  api/                 # API routes/endpoints
    routes/            # Route handlers by domain
  services/            # Business logic layer
    embedding/         # Embedding factory and services
    auth/              # Authentication helpers
  infrastructure/      # External adapters (DB, auth, storage)
    supabase_adapter.py    # Database operations
    auth_adapter.py        # Auth integration
    storage_adapter.py     # File storage
    rate_limiter.py        # Rate limiting
  models/              # Data models (Pydantic, ORM)
  tools/               # MCP tools (workspace, entity, relationship, workflow, query)
  auth/                # Session, middleware, hybrid auth provider
  utils/               # Shared utilities
  cli/                 # CLI commands (Typer)
tests/
  unit/                # Unit tests
  integration/         # Integration tests
  e2e/                 # End-to-end tests
  performance/         # Performance tests
  conftest.py          # Shared fixtures
config/                # Configuration files
  settings.yml         # Application settings
  secrets.yml          # Secrets (gitignored)
docs/
  sessions/            # Session-based work docs
  architecture/        # Architecture documentation
```

### Style Constraints
- **Line length**: 100 characters
- **Formatter**: Ruff/Black
- **Type checker**: mypy/pyright
- **Linter**: Ruff
- **File size**: ≤500 lines hard limit, ≤350 target
- **Typing**: typed where practical, explicit error handling
- **Logging**: clear, structured logging

See `pyproject.toml` and `Brewfile`.

## Phenotype Org Cross-Project Reuse Protocol <!-- PHENOTYPE_SHARED_REUSE_PROTOCOL -->

- Treat this repository as part of the broader Phenotype organization project collection, not an isolated codebase.
- During research and implementation, actively identify code that is sharable, modularizable, splittable, or decomposable for reuse across repositories.
- When reusable logic is found, prefer extraction into existing shared modules/projects first; if none fit, propose creating a new shared module/project.
- Include a `Cross-Project Reuse Opportunities` section in plans with candidate code, target shared location, impacted repos, and migration order.
- For cross-repo moves or ownership-impacting extractions, ask the user for confirmation on destination and rollout, then bake that into the execution plan.
- Execute forward-only migrations: extract shared code, update all callers, and remove duplicated local implementations.
## Phenotype Git and Delivery Workflow Protocol <!-- PHENOTYPE_GIT_DELIVERY_PROTOCOL -->

- Use branch-based delivery with pull requests; do not rely on direct default-branch writes where rulesets apply.
- Prefer stacked PRs for multi-part changes so each PR is small, reviewable, and independently mergeable.
- Keep PRs linear and scoped: one concern per PR, explicit dependency order for stacks, and clear migration steps.
- Enforce CI and required checks strictly: do not merge until all required checks and policy gates are green.
- Resolve all review threads and substantive PR comments before merge; do not leave unresolved reviewer feedback.
- Follow repository coding standards and best practices (typing, tests, lint, docs, security) before requesting merge.
- Rebase or restack to keep branches current with target branch and to avoid stale/conflicting stacks.
- When a ruleset or merge policy blocks progress, surface the blocker explicitly and adapt the plan (for example: open PR path, restack, or split changes).
## Phenotype Long-Term Stability and Non-Destructive Change Protocol <!-- PHENOTYPE_LONGTERM_STABILITY_PROTOCOL -->

- Optimize for long-term platform value over short-term convenience; choose durable solutions even when implementation complexity is higher.
- Classify proposed changes as `quick_fix` or `stable_solution`; prefer `stable_solution` unless an incident response explicitly requires a temporary fix.
- Do not use deletions/reversions as the default strategy; prefer targeted edits, forward fixes, and incremental hardening.
- Prefer moving obsolete or superseded material into `.archive/` over destructive removal when retention is operationally useful.
- Prefer clean manual merges, explicit conflict resolution, and auditable history over forceful rewrites, force merges, or history-destructive workflows.
- Prefer completing unused stubs into production-quality implementations when they represent intended product direction; avoid leaving stubs ignored indefinitely.
- Do not merge any PR while any check is failing, including non-required checks, unless the user gives explicit exception approval.
- When proposing a quick fix, include a scheduled follow-up path to a stable solution in the same plan.
## Child-Agent and Delegation Policy
- Use child agents liberally for scoped discovery, audits, multi-repo scans, and implementation planning before direct parent-agent edits.
- Prefer delegating high-context or high-churn tasks to subagents, and keep parent-agent changes focused on integration and finalization.
- Reserve parent-agent direct writes for the narrowest, final decision layer.

## Child Agent Usage
- Use child agents liberally for discovery-heavy, migration-heavy, and high-context work.
- Delegate broad scans, decomposition, and implementation waves to subagents before final parent-agent integration.
- Keep the parent lane focused on deterministic integration and finalization.
- Preserve explicit handoffs and cross-agent context in session notes and audits.


## CI Completeness Policy

- Always evaluate and fix ALL CI check failures on a PR, including pre-existing failures inherited from main.
- Never dismiss a CI failure as "pre-existing" or "unrelated to our changes" — if it fails on the PR, fix it in the PR.
- This includes: build, lint, test, docs build, security scanning (CodeQL), code review gates (CodeRabbit), workflow guard checks, and any other CI jobs.
- When a failure is caused by infrastructure outside the branch (e.g., rate limits, external service outages), implement or improve automated retry/bypass mechanisms in CI workflows.
- After fixing CI failures, verify locally where possible (build, vet, tests) before pushing.

## Phenotype Git and Delivery Workflow Protocol <!-- PHENOTYPE_GIT_DELIVERY_PROTOCOL -->

- Use branch-based delivery with pull requests; do not rely on direct default-branch writes where rulesets apply.
- Prefer stacked PRs for multi-part changes so each PR is small, reviewable, and independently mergeable.
- Keep PRs linear and scoped: one concern per PR, explicit dependency order for stacks, and clear migration steps.
- Enforce CI and required checks strictly: do not merge until all required checks and policy gates are green.
- Resolve all review threads and substantive PR comments before merge; do not leave unresolved reviewer feedback.
- Follow repository coding standards and best practices (typing, tests, lint, docs, security) before requesting merge.
- Rebase or restack to keep branches current with target branch and to avoid stale/conflicting stacks.
- When a ruleset or merge policy blocks progress, surface the blocker explicitly and adapt the plan (for example: open PR path, restack, or split changes).

## CI Completeness Policy

- Always evaluate and fix ALL CI check failures on a PR, including pre-existing failures inherited from main.
- Never dismiss a CI failure as "pre-existing" or "unrelated to our changes" — if it fails on the PR, fix it in the PR.
- This includes: build, lint, test, docs build, security scanning (CodeQL), code review gates (CodeRabbit), workflow guard checks, and any other CI jobs.
- When a failure is caused by infrastructure outside the branch (e.g., rate limits, external service outages), implement or improve automated retry/bypass mechanisms in CI workflows.
- After fixing CI failures, verify locally where possible (build, vet, tests) before pushing.

## Phenotype Git and Delivery Workflow Protocol <!-- PHENOTYPE_GIT_DELIVERY_PROTOCOL -->

- Use branch-based delivery with pull requests; do not rely on direct default-branch writes where rulesets apply.
- Prefer stacked PRs for multi-part changes so each PR is small, reviewable, and independently mergeable.
- Keep PRs linear and scoped: one concern per PR, explicit dependency order for stacks, and clear migration steps.
- Enforce CI and required checks strictly: do not merge until all required checks and policy gates are green.
- Resolve all review threads and substantive PR comments before merge; do not leave unresolved reviewer feedback.
- Follow repository coding standards and best practices (typing, tests, lint, docs, security) before requesting merge.
- Rebase or restack to keep branches current with target branch and to avoid stale/conflicting stacks.
- When a ruleset or merge policy blocks progress, surface the blocker explicitly and adapt the plan (for example: open PR path, restack, or split changes).

## Phenotype Org Cross-Project Reuse Protocol <!-- PHENOTYPE_SHARED_REUSE_PROTOCOL -->

- Treat this repository as part of the broader Phenotype organization project collection, not an isolated codebase.
- During research and implementation, actively identify code that is sharable, modularizable, splittable, or decomposable for reuse across repositories.
- When reusable logic is found, prefer extraction into existing shared modules/projects first; if none fit, propose creating a new shared module/project.
- Include a `Cross-Project Reuse Opportunities` section in plans with candidate code, target shared location, impacted repos, and migration order.
- For cross-repo moves or ownership-impacting extractions, ask the user for confirmation on destination and rollout, then bake that into the execution plan.
- Execute forward-only migrations: extract shared code, update all callers, and remove duplicated local implementations.

## Phenotype Long-Term Stability and Non-Destructive Change Protocol <!-- PHENOTYPE_LONGTERM_STABILITY_PROTOCOL -->

- Optimize for long-term platform value over short-term convenience; choose durable solutions even when implementation complexity is higher.
- Classify proposed changes as `quick_fix` or `stable_solution`; prefer `stable_solution` unless an incident response explicitly requires a temporary fix.
- Do not use deletions/reversions as the default strategy; prefer targeted edits, forward fixes, and incremental hardening.
- Prefer moving obsolete or superseded material into `.archive/` over destructive removal when retention is operationally useful.
- Prefer clean manual merges, explicit conflict resolution, and auditable history over forceful rewrites, force merges, or history-destructive workflows.
- Prefer completing unused stubs into production-quality implementations when they represent intended product direction; avoid leaving stubs ignored indefinitely.
- Do not merge any PR while any check is failing, including non-required checks, unless the user gives explicit exception approval.
- When proposing a quick fix, include a scheduled follow-up path to a stable solution in the same plan.

## Worktree Discipline

- Feature work goes in `.worktrees/<topic>/`
- Legacy `PROJECT-wtrees/` and `repo-wtrees/` roots are for migration only and must not receive new work.
- Canonical repository remains on `main` for final integration and verification.
