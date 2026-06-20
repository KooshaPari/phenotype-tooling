# Architecture Decision Records — phenotype-dep-guard

## ADR-001 — Python as Primary Implementation Language

**Status:** Accepted  
**Date:** 2026-03-27

### Context
Dependency resolution tooling for Python, Node, Rust, and Go ecosystems must parse a variety of lock-file formats. Python has mature libraries for each (pip, `tomllib`, `json`, `yaml`).

### Decision
Implement phenotype-dep-guard in Python 3.11+ using `typer` for the CLI, `pydantic` for data models, and `ast` for static analysis.

### Consequences
- Native `ast` module enables zero-dependency AST parsing for Python packages.
- For JS/TS triage, `esprima` or `tree-sitter-javascript` via subprocess.
- Distribution as a PyPI package and a standalone binary via `pyinstaller`.

---

## ADR-002 — SARIF as Primary Report Format

**Status:** Accepted  
**Date:** 2026-03-27

### Context
GitHub Advanced Security and most SAST integrations consume SARIF. Producing SARIF natively avoids conversion steps.

### Decision
All findings are serialized to SARIF 2.1.0. A text renderer is provided for human-readable terminal output.

### Consequences
- SARIF schema must be kept current with the 2.1.0 spec.
- JSON and plain-text output are secondary projections of the SARIF model.

---

## ADR-003 — Policy Rules in YAML Contract Files

**Status:** Accepted  
**Date:** 2026-03-27

### Context
Policy rules must be auditable, version-controlled, and editable by non-engineers. YAML is preferred over embedded Python config.

### Decision
Policy rules live in `contracts/reconcile.rules.yaml`. The rule schema is validated with `jsonschema` on load.

### Consequences
- Schema changes require a migration guide.
- Rules are hot-reloadable without recompiling.

---

## ADR-004 — Hexagonal Architecture for Triage Engine

**Status:** Accepted  
**Date:** 2026-03-27

### Context
The triage engine must support multiple analysis back-ends (OSV API, local DB, custom heuristics) without coupling the domain logic to any single back-end.

### Decision
Apply hexagonal architecture: domain triage logic depends only on port interfaces (`VulnerabilitySource`, `AnalysisBackend`). Adapters implement these ports for each back-end.

### Consequences
- New vulnerability sources (e.g., GitHub Advisory) are added as adapters without touching domain code.
- Testability: domain logic is tested with in-memory stub adapters.