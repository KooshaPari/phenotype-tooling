# PRD — phenotype-xdd

**Version:** 1.1.0
**Stack:** Documentation / Governance (language-agnostic)
**Repo:** `KooshaPari/phenotype-xdd`
**Classification:** Special-purpose governance reference hub

---

## Overview

`phenotype-xdd` is the eXtreme Domain-Driven Design (xDD) methodologies compendium for the
Phenotype organisation. It is not a runtime library; it is an authoritative reference hub that
codifies the 180+ engineering practices, wrap-over-handroll governance, hexagonal architecture
standards, and polyglot conventions adopted across all Phenotype repos.

The hub serves as the single source of truth for architecture decisions, engineering practices,
and methodology documentation consumed by both human contributors and AI agents.

---

## Epics Summary

| Epic | Title | Status |
|------|-------|--------|
| E1 | Engineering Practices Compendium | Active |
| E2 | Architecture Reference | Active |
| E3 | Wrap-Over-Handroll Governance | Active |
| E4 | Hexagonal Architecture Patterns Per Language | Active |
| E5 | Testing Methodology Catalogue | Active |
| E6 | Observability and Security Patterns | Active |
| E7 | Machine-Readable Indexes and Agent Tooling | Active |
| E8 | Contribution and Maintenance Lifecycle | Active |

---

## E1 — Engineering Practices Compendium

**Goal:** Document all numbered xDD practices so any agent or engineer can look up the canonical
guidance for a pattern.

### E1.1 Practices Registry

- As a contributing engineer, I want a machine-readable registry of practices so agents can
  cross-reference them in code reviews and PR descriptions.
- **Acceptance:**
  - All practices are reachable at `README.md` with unique numeric IDs (e.g., `1.`, `2.`).
  - Each practice entry includes: name, one-line definition, when to use, anti-patterns,
    referenced literature.
  - At least 150 practices documented across all categories.

### E1.2 Wrap-and-Roll Governance

- As an agent author, I want explicit wrap-over-handroll rules so I know when to use an OSS
  library versus implement custom code.
- **Acceptance:**
  - `docs/engineering/WRAP_AND_ROLL_GOVERNANCE.md` covers decision tree, exemptions,
    and documentation requirements.
  - Decision tree has at minimum 4 decision nodes: exists? maintained? contract-compatible?
    license-compatible?

### E1.3 Category Organisation

- As a reader, I want practices grouped into coherent categories with clear headings so I can
  navigate the compendium without reading it linearly.
- **Acceptance:**
  - Categories include: Core Development Disciplines, Architecture Principles, Design Principles,
    Testing Methodologies, Documentation, Process and Workflow, Code Quality, Collaboration,
    Operational Practices, Advanced Topics, DDD Extensions, Platform-Specific, Meta-Practices.
  - Table of contents at the top of `README.md` with anchor links to each section.

### E1.4 Implementation Complexity Matrix

- As a team lead, I want a matrix mapping each practice to complexity level, recommended team
  size, project type, and maturity level so I can choose practices appropriate to the context.
- **Acceptance:**
  - `## Implementation Matrix` section in `README.md` with at minimum 8 practices.
  - Columns: Practice, Complexity (Low/Medium/High/Very High), Team Size, Project Type,
    Maturity Level (Foundation/Intermediate/Advanced/Expert).

---

## E2 — Architecture Reference

**Goal:** Provide canonical architecture decision records and hexagonal architecture patterns for
the entire Phenotype platform.

### E2.1 Hexagonal Architecture Reference

- As a service author, I want a worked example of hexagonal architecture in each supported
  language so I can implement ports and adapters correctly.
- **Acceptance:**
  - Reference architectures and conceptual examples exist for Go, Python, TypeScript, Rust, Zig.
  - Each example shows: domain layer, ports (interfaces), adapters, and wiring.
  - Documented in `docs/hexagonal-spec.md` or equivalent.

### E2.2 Top-Level Repo Layout Standard

- As a repository author, I want a canonical directory structure standard so every Phenotype
  repo has a consistent, discoverable layout.
- **Acceptance:**
  - `docs/engineering/TOP_LEVEL_REPO_LAYOUT.md` defines the canonical directory structure.
  - Defines required files: `README.md`, `CLAUDE.md`, `AGENTS.md`, `PLAN.md`, `PRD.md`,
    `FUNCTIONAL_REQUIREMENTS.md`, `ADR.md`.
  - Defines required top-level directories and their purpose.

### E2.3 ADR Lifecycle

- As an architecture author, I want a defined ADR lifecycle with states and transitions so ADRs
  are maintained rather than abandoned.
- **Acceptance:**
  - Lifecycle states defined: `Proposed → Accepted → Deprecated → Superseded`.
  - Each status transition records date and rationale.
  - Template ADR format provided.

---

## E3 — Wrap-Over-Handroll Governance

**Goal:** Codify the decision process for choosing between wrapping an OSS library, forking it,
or implementing from scratch.

### E3.1 Wrap Decision Tree

- As an engineer, I want an explicit decision tree for wrap-vs-handroll choices so I spend
  engineering effort consistently and avoid reinventing maintained OSS work.
- **Acceptance:**
  - Decision tree documented in `docs/engineering/WRAP_AND_ROLL_GOVERNANCE.md`.
  - Steps: (1) Does an OSS library exist? (2) Is it well-maintained (last commit <6 months)?
    (3) Does it meet the interface contract? (4) Is the license compatible?
    If all yes → wrap; else → evaluate fork vs implement.
  - Exemptions documented (security-critical code, legal restrictions, performance requirements).

### E3.2 Wrap Documentation Requirements

- As a code reviewer, I want all wrapped OSS dependencies to be annotated so I know what is
  wrapping what without reading the full dependency tree.
- **Acceptance:**
  - Comment convention: `// wraps: <lib-name> <version>` in the consuming source file.
  - `docs/engineering/wrap-registry.yaml` lists all wrapped dependencies with: library name,
    version, wrapping module, justification, and last-reviewed date.

### E3.3 Fork Policy

- As an engineer, I want a documented fork policy so I know when forking is acceptable and what
  obligations follow from forking.
- **Acceptance:**
  - Fork conditions: upstream abandoned, breaking API change required, security patch needed.
  - Fork obligations: upstream credit in `NOTICE`, link to original repo, sync check cadence.

---

## E4 — Hexagonal Architecture Patterns Per Language

**Goal:** Provide language-specific hexagonal architecture skeleton references for Go, Python,
TypeScript, Rust, and Zig.

### E4.1 Go Hexagonal Reference

- **Acceptance:** Package layout `domain/`, `ports/`, `adapters/`, `application/`, `cmd/`;
  domain package has zero external deps; adapters inject via interface parameters.

### E4.2 Python Hexagonal Reference

- **Acceptance:** Module layout `domain/`, `ports/`, `adapters/`, `application/`; ports use
  `typing.Protocol`; adapters registered via dependency injection or factory pattern.

### E4.3 TypeScript Hexagonal Reference

- **Acceptance:** Directory layout `domain/`, `ports/`, `adapters/`, `application/`; ports are
  TypeScript `interface` definitions; adapters implement interfaces with concrete classes.

### E4.4 Rust Hexagonal Reference

- **Acceptance:** Module layout `domain/`, `application/`, `adapters/`; ports are Rust `trait`
  definitions in `domain/ports/`; adapters depend only on port traits; domain crate has zero
  external infrastructure deps.

### E4.5 Zig Hexagonal Reference

- **Acceptance:** Documented approach for Zig's comptime-based polymorphism as port mechanism;
  example showing domain struct, comptime interface, adapter struct.

---

## E5 — Testing Methodology Catalogue

**Goal:** Provide a complete, cross-referenced catalogue of testing methodologies with guidance
on when to apply each.

### E5.1 Test Method Entries

- As a test engineer, I want each testing methodology documented with: definition, forces that
  motivate it, when to use, when NOT to use, tooling examples, and anti-patterns.
- **Acceptance:**
  - At least 25 testing methodologies documented (TDD, BDD, ATDD, Property-Based, Mutation,
    Fuzz, Snapshot, Golden Master, Conformance, A/B, Canary, Shadow, Penetration, etc.).
  - Each entry is 3-6 bullet points minimum.

### E5.2 Test Selection Matrix

- As a team lead, I want a matrix mapping test types to project maturity so I know which tests
  to mandate at each level.
- **Acceptance:**
  - Matrix covers: Maturity levels L1–L5.
  - Rows: test types (Unit, Integration, E2E, Property-Based, Contract, Mutation, Security,
    Accessibility, Performance, Snapshot/Golden).
  - Columns: New Project, Established, Critical System.
  - Values: Optional / Required.

---

## E6 — Observability and Security Patterns

**Goal:** Document observability and security patterns as part of the xDD compendium.

### E6.1 Observability Patterns

- **Acceptance:**
  - At least 15 observability patterns documented.
  - Patterns include: Structured Logging, RED Method, USE Method, Circuit Breaker,
    Distributed Tracing, DORA Metrics, SLO/SLA/SLI, Health Check, Canary Alerting.

### E6.2 Security Patterns

- **Acceptance:**
  - At least 12 security patterns documented.
  - Patterns include: Zero Trust, OAuth/OIDC, Secrets Management, OWASP Top 10 mitigations,
    Privacy by Design, Threat Modelling, Secure SDLC.

---

## E7 — Machine-Readable Indexes and Agent Tooling

**Goal:** Provide structured, machine-readable indexes so AI agents can look up practices
programmatically without parsing prose markdown.

### E7.1 Practices Index

- As an AI agent, I want a YAML or JSON index mapping practice IDs to section anchors so I can
  look up a practice ID and retrieve the canonical definition with a single fetch.
- **Acceptance:**
  - `docs/engineering/practices-index.yaml` contains at minimum: `id`, `name`, `category`,
    `anchor`, `references` for each documented practice.
  - Index is in sync with `README.md`.

### E7.2 Cross-Reference Links

- **Acceptance:**
  - Each methodology entry includes a `Related:` or `See also:` list of other methodology IDs.
  - Cross-references are navigable as Markdown anchor links.

---

## E8 — Contribution and Maintenance Lifecycle

**Goal:** Define a clear process for adding, updating, and deprecating methodology entries.

### E8.1 New Methodology Contribution Process

- **Acceptance:**
  - `CONTRIBUTING.md` or `README.md` section documents the entry format.
  - Entry template provided: name, category, definition, when to use, anti-patterns,
    cross-references, literature references.

### E8.2 Methodology Deprecation

- **Acceptance:**
  - Deprecated entries marked with a `> [!NOTE] Deprecated: superseded by PRAC-NNN` callout.
  - Superseded entries include a forward link to the replacement.

---

## Constraints and Non-Goals

- `phenotype-xdd` is documentation-only. It MUST NOT contain Go modules, Python packages,
  TypeScript packages, Rust crates, or any published runtime artefacts.
- The hub is consumed via URL reference or git submodule; consumers do not add it as a package
  dependency.
- Content is in CommonMark Markdown with embedded Mermaid diagrams.
- AI agents access content via `gh api` raw file fetch; no special API is required.
