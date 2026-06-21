# Functional Requirements — phenotype-xdd

**Version:** 1.1.0
**Traces to:** PRD epics E1–E8

---

## Practices Compendium (E1)

### FR-XDD-001 — Practices Unique IDs

**SHALL** assign a unique numeric ID to every documented engineering practice (e.g., `1.`, `2.`,
through `150+`), displayed as a heading number in `README.md`.
**Traces to:** E1.1

### FR-XDD-002 — Machine-Readable Practices Index

**SHALL** maintain a YAML index at `docs/engineering/practices-index.yaml` mapping each
practice to: `id`, `name`, `category`, `anchor` (section link), and `references` list,
enabling agent tooling to look up practices programmatically without parsing prose markdown.
**Traces to:** E1.1, E7.1

### FR-XDD-003 — Practice Entry Structure

**SHALL** document each practice with the following fields:
- Name and one-line definition.
- When to use (3-6 bullet points minimum).
- Anti-patterns or common mistakes.
- Literature references (`_References: author, year_`).

**Traces to:** E1.1

### FR-XDD-004 — Category Table of Contents

**SHALL** provide a table of contents at the top of `README.md` with anchor links to each
category section. Minimum categories: Core Development Disciplines, Architecture Principles,
Design Principles, Testing Methodologies, Documentation, Process and Workflow, Code Quality,
Collaboration, Operational Practices, Advanced Topics, DDD Extensions, Platform-Specific,
Meta-Practices.
**Traces to:** E1.3

### FR-XDD-005 — Minimum Practice Count

**SHALL** document at least 150 engineering practices across all categories.
**Traces to:** E1.1

### FR-XDD-006 — Implementation Complexity Matrix

**SHALL** provide an Implementation Matrix section in `README.md` with at minimum 8 practice
rows. Columns SHALL be: Practice, Complexity (Low/Medium/High/Very High), Team Size, Project
Type, Maturity Level (Foundation/Intermediate/Advanced/Expert).
**Traces to:** E1.4

---

## Wrap-Over-Handroll Governance (E3)

### FR-XDD-007 — Wrap Decision Tree

**SHALL** document a four-node decision tree for wrap-over-handroll choices:

1. Does an OSS library that solves the problem exist?
2. Is it well-maintained (last commit <6 months, active issue responses)?
3. Does it meet the interface contract needed (no significant shim required)?
4. Is the license compatible with the consuming project?

If all four conditions are YES, wrap the library. If any condition is NO, evaluate fork vs
implement from scratch. Documented in `docs/engineering/WRAP_AND_ROLL_GOVERNANCE.md`.
**Traces to:** E3.1

### FR-XDD-008 — Wrap Annotation Requirement

**SHALL** require all wrapped OSS deps to carry a `// wraps: <lib> <version>` annotation in
the consuming source file immediately above the wrapping construct.
**Traces to:** E3.2

### FR-XDD-009 — Wrap Registry

**SHALL** maintain `docs/engineering/wrap-registry.yaml` listing each wrapped OSS dependency
with fields: `library`, `version`, `consuming_module`, `justification`, `last_reviewed`.
**Traces to:** E3.2

### FR-XDD-010 — Fork Policy

**SHALL** document conditions under which forking is acceptable: upstream abandoned, breaking
API change required, security patch needed. Fork obligations SHALL include: upstream credit in
`NOTICE` file, link to original repo in fork README, and declared sync check cadence.
**Traces to:** E3.3

---

## Architecture Reference (E2, E4)

### FR-XDD-011 — Language-Specific Hexagonal References

**SHALL** provide conceptual hexagonal architecture examples for each of the five supported
languages: Go, Python, TypeScript, Rust, Zig. Each example SHALL demonstrate: domain layer
with zero external deps, port definitions (interfaces/traits/Protocols), adapter implementations,
and wiring between layers.
**Traces to:** E2.1, E4.1–E4.5

### FR-XDD-012 — Repo Layout Standard

**SHALL** define the canonical top-level directory structure that every Phenotype repo MUST
follow. SHALL specify required root-level files: `README.md`, `CLAUDE.md`, `AGENTS.md`,
`PRD.md`, `FUNCTIONAL_REQUIREMENTS.md`, `ADR.md`, `PLAN.md`.
**Traces to:** E2.2

### FR-XDD-013 — ADR Lifecycle States

**SHALL** define ADR lifecycle states: `Proposed → Accepted → Deprecated → Superseded`.
Each status transition SHALL record: transition date and rationale.
**Traces to:** E2.3

### FR-XDD-014 — ADR Template

**SHALL** provide an ADR template with sections: Context, Decision, Alternatives Considered,
Consequences, Status (with date).
**Traces to:** E2.3

---

## Testing Methodology Catalogue (E5)

### FR-XDD-015 — Testing Methodology Entries

**SHALL** document at least 25 testing methodologies including: TDD, BDD, ATDD, Property-Based
Testing, Mutation Testing, Fuzz Testing, Snapshot Testing, Golden Master Testing, Conformance
Testing, A/B Testing, Canary Testing, Shadow Testing, Penetration Testing, Performance Testing,
Smoke Testing, Sanity Testing, Regression Testing, Load Testing.
**Traces to:** E5.1

### FR-XDD-016 — Test Selection Matrix

**SHALL** provide a test type selection matrix with rows for: Unit, Integration, E2E,
Property-Based, Contract, Mutation, Security (SAST), Accessibility, Performance,
Snapshot/Golden. Columns SHALL be: New Project, Established, Critical System. Values SHALL be
Optional or Required.
**Traces to:** E5.2

---

## Observability and Security Patterns (E6)

### FR-XDD-017 — Observability Patterns

**SHALL** document at least 15 observability patterns including: Structured Logging, RED Method,
USE Method, Circuit Breaker, Distributed Tracing, DORA Metrics, SLO/SLA/SLI, Health Checks,
Canary Alerting, Error Budgets, Runbook Automation, Synthetic Monitoring.
**Traces to:** E6.1

### FR-XDD-018 — Security Patterns

**SHALL** document at least 12 security engineering patterns including: Zero Trust, OAuth/OIDC,
Secrets Management, Privacy by Design, Threat Modelling, Secure SDLC, OWASP Top 10 mitigations,
Security Review Process.
**Traces to:** E6.2

---

## Cross-References and Agent Tooling (E7)

### FR-XDD-019 — Cross-Reference Links

**SHALL** include a `Related:` or `See also:` list in each methodology entry that references
at least one other methodology ID when a clear relationship exists.
**Traces to:** E7.2

### FR-XDD-020 — Hub Classification Header

**SHALL** maintain a hub classification header in `README.md` indicating: Classification
(Special-purpose hub / governance reference), Prefix policy (phenotype- retained), and
purpose statement (reference asset, not library or tool).
**Traces to:** E1.1

---

## Contribution and Maintenance (E8)

### FR-XDD-021 — Contribution Guide

**SHALL** document the entry format for adding a new methodology in `README.md#contributing`
or a dedicated `CONTRIBUTING.md`, including: required field list (name, category, definition,
when to use, anti-patterns, cross-references, references) and a PR checklist.
**Traces to:** E8.1

### FR-XDD-022 — Deprecation Marker

**SHALL** mark deprecated methodology entries with a visible callout:
`> [!NOTE] Deprecated: superseded by ...` and include a forward link to the replacement
practice or section.
**Traces to:** E8.2
