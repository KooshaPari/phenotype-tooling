# Architecture Decision Records — phenotype-xdd

---

## ADR-001 — Hub-Only Repository (No Runtime Artefacts)

**Date:** 2025-10-01
**Status:** Accepted

### Context

Early designs considered publishing xDD tooling as a runtime library that tools could import.
This created versioning friction and forced all consumers to update when docs changed.

### Decision

`phenotype-xdd` is documentation-only. No Go modules, no Python packages, no published
artefacts. Consumers reference it via URLs or git submodule in their own doc toolchains.

### Consequences

- Zero dependency management burden.
- Docs can evolve without semver constraints.
- Agents use `gh api` to fetch content rather than importing a package.

---

## ADR-002 — Markdown as Canonical Format

**Date:** 2025-10-05
**Status:** Accepted

### Context

Alternatives considered: AsciiDoc (better structure), reStructuredText (Sphinx ecosystem),
custom DSL. Markdown was chosen for universal tooling support.

### Decision

All practices, governance, and reference docs are plain CommonMark Markdown. Mermaid diagrams
are embedded for architecture flows.

### Consequences

- Any Markdown renderer (GitHub, VitePress, Obsidian) can display content without plugins.
- Mermaid diagrams render natively on GitHub and in VitePress.

---

## ADR-003 — Practices Numbered from 100

**Date:** 2025-10-10
**Status:** Superseded by ADR-006

### Context

A flat numeric sequence from 1 would exhaust readable ranges quickly. Practices are grouped
by category.

### Decision

Practice IDs are three-digit numbers starting at 100, grouped in decades by category
(100–109: foundations, 110–119: hexagonal, 120–129: testing, etc.).

### Consequences

- New practices slot into the correct category range.
- References like PRAC-112 are unambiguous and stable.

---

## ADR-004 — Mermaid Diagrams for Architecture Flows

**Date:** 2025-11-01
**Status:** Accepted

### Context

Architecture flows in the compendium (hexagonal layers, ADR lifecycle, wrap-decision tree)
need visual representation. Image files require binary assets and do not diff well; ASCII art
does not render consistently across Markdown hosts.

### Decision

All architecture and flow diagrams in `phenotype-xdd` are authored as Mermaid code blocks.
GitHub, VitePress, and Obsidian all render Mermaid natively with no plugins.

### Alternatives Considered

- PNG/SVG diagrams: render anywhere but require tooling to edit and cannot be diffed as text.
- PlantUML: powerful but requires a Java server or external rendering; not natively supported
  on GitHub.
- ASCII art: universally renderable but hard to read for anything beyond trivial diagrams.

### Consequences

- Diagrams are editable as plain text and diff cleanly in PRs.
- Mermaid is rendered live on GitHub without special steps.
- Complex diagrams (many nodes) can become verbose; mitigated by limiting diagrams to six
  nodes or fewer and breaking complex flows into multiple diagrams.

---

## ADR-005 — Five-Language Hexagonal Reference Set

**Date:** 2025-11-15
**Status:** Accepted

### Context

The Phenotype ecosystem uses Go, Python, TypeScript, Rust, and Zig across different services.
Each language has distinct idioms for defining interfaces (Go interfaces, Python Protocols,
TypeScript interfaces, Rust traits, Zig comptime). A single language-agnostic description
leaves too much room for misinterpretation.

### Decision

`phenotype-xdd` maintains five separate hexagonal architecture reference sections — one per
language — each using the idiomatic mechanism for port definitions in that language. The
conceptual model (domain, ports, adapters, application) is identical across all five; only
the syntax and conventions differ.

### Alternatives Considered

- Single generic reference with language-agnostic pseudocode: simpler to maintain but forces
  readers to translate into idiomatic patterns themselves, which is a source of errors.
- Reference only Rust (primary language): excludes Go and Python services from canonical
  guidance, which is unacceptable for a cross-ecosystem hub.
- Reference only two languages (Rust + Go): still leaves Python, TypeScript, and Zig authors
  without canonical examples.

### Consequences

- Five reference sections must be updated in sync when the conceptual model changes.
- Authors writing services in a new language have a clear starting point.
- The compendium is larger but the sections are independent.

---

## ADR-006 — Flat Sequential Practice Numbering

**Date:** 2026-01-10
**Status:** Accepted
**Supersedes:** ADR-003

### Context

ADR-003 used three-digit grouped IDs starting at 100 (decade-per-category). In practice,
new practices frequently crossed category boundaries, making it difficult to assign them to
a single decade. Gaps appeared as practices were added out of order.

### Decision

Practice IDs use flat sequential integers starting at 1 (displayed as heading numbers in
`README.md`). The `practices-index.yaml` records the category for each practice independently
of the ID. This decouples numeric ordering from category grouping.

### Alternatives Considered

- Keep decade-per-category scheme: rejected due to the cross-category problem and growing
  number of practices exceeding a single decade.
- Use UUIDs or slugs: rejected because they are not human-readable or memorable.

### Consequences

- Existing PRAC-NNN references in other repos must be updated when migrating to the new scheme;
  the `practices-index.yaml` provides a stable mapping.
- New practices are always appended at the end of the numeric sequence regardless of category.
- The index YAML is the authoritative source for category membership; `README.md` headings
  are human-readable grouping only.

---

## ADR-007 — No Runtime Artefacts Policy Enforcement via CI

**Date:** 2026-02-01
**Status:** Accepted

### Context

Contributors occasionally propose adding helper scripts, CLI tools, or validation binaries to
`phenotype-xdd` (e.g., a CI linter for wrap annotations, a schema validator for
`practices-index.yaml`). Each addition would introduce a runtime dependency and versioning
burden that contradicts the hub-only charter from ADR-001.

### Decision

`phenotype-xdd` enforces a no-runtime-artefacts policy through a CI guard that fails if any
of the following files are added to the repository: `Cargo.toml`, `go.mod`, `package.json`,
`pyproject.toml`, or `*.wasm`. Shell scripts used solely for CI convenience (no compiled
output) are exempt.

### Alternatives Considered

- Trust contributors to follow the charter: rejected because the hub-only charter has been
  violated repeatedly without automated enforcement.
- Maintain a separate `phenotype-xdd-tools` repo for helper tooling: accepted as the
  recommended path for any tooling that automates compendium maintenance.

### Consequences

- Any future tooling must live in a separate repo (e.g., `phenotype-xdd-tools`).
- CI rejects PRs that accidentally introduce build manifests.
- The hub remains documentation-only with zero dependency management overhead.
