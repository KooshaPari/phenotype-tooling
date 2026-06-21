# SPEC: PhenoSpecs — Unified Specification Registry

## Meta

- **ID**: phenospecs-001
- **Title**: PhenoSpecs — Unified Specification Registry
- **Created**: 2026-04-04
- **State**: specified
- **Version**: 1.0.0
- **Language**: YAML, Markdown, OpenAPI

---

## Charter

### Mission

PhenoSpecs is the **central nervous system** for the Phenotype ecosystem — a unified specification registry that connects requirements, architecture decisions, and implementations across all repositories, languages, and teams.

Our mission is to make specifications **discoverable, traceable, and actionable** — enabling teams to move fast without breaking things, onboard quickly, and maintain quality at scale.

### Tenets (unless you know better ones)

These tenets guide PhenoSpecs' development. They are ordered by priority.

#### 1. Git-Native First

**Specifications live in Git, full stop.**

All specifications are stored as plain text files in version control. This enables:
- Code review workflows for specifications
- Branching and versioning of specs alongside code
- Standard git operations (diff, blame, merge) on documentation
- No separate login or system to access specs

**Implications:**
- No database required for core functionality
- SaaS documentation platforms are secondary mirrors only
- All specs must be readable in a text editor

#### 2. Traceability Is Non-Negotiable

**If it can't be traced, it doesn't exist.**

Every functional requirement must be traceable to code that implements it. This is not documentation overhead — it is engineering rigor.

**Implications:**
- Code annotations are first-class citizens
- CI gates enforce traceability coverage
- Untraced specifications are considered draft

#### 3. Format Diversity With Unified Access

**Let the right format win, then unify access.**

Specifications naturally take different forms (Markdown for features, OpenAPI for HTTP, MADR for decisions). PhenoSpecs unifies access without forcing uniformity.

**Implications:**
- Registry provides the unified interface
- Multiple formats supported natively
- Format-specific tooling preserved
- Common metadata schema across formats

#### 4. Programmer Experience First

**Specs are for builders, not just readers.**

The primary users of PhenoSpecs are engineers building systems. The developer experience must be excellent: fast queries, IDE integration, CLI tooling.

**Implications:**
- CLI speed prioritized (&lt;100ms for common queries)
- IDE extensions for navigation
- GitHub integration for PR workflows
- API for programmatic access

#### 5. Automation Over Manual Curation

**Machines check what humans would forget.**

Manual maintenance of documentation links fails. PhenoSpecs automates validation, coverage reporting, and integrity checks.

**Implications:**
- CI/CD validates all links and references
- Coverage reports generated automatically
- Stale spec detection automated
- Registry updates triggered by code changes

---

## Overview

### What Is PhenoSpecs?

PhenoSpecs is a **specification registry system** consisting of:

1. **A Git repository** (`PhenoSpecs/`) containing specifications
2. **A registry index** (`registry.yaml`) linking all specifications
3. **A CLI tool** (`phenospecs`) for querying and validation
4. **A set of conventions** for annotations and metadata
5. **CI/CD integrations** for validation and enforcement

### The Problem PhenoSpecs Solves

As software ecosystems grow, specifications fragment across:
- Multiple repositories
- Different formats (Markdown, OpenAPI, various ADR formats)
- Various storage systems (GitHub, Notion, Confluence, "that doc someone wrote")

This fragmentation causes:
- **Discovery failure**: Engineers can't find existing specs
- **Duplication**: Teams unknowingly reinvent specifications
- **Drift**: Specs become outdated relative to code
- **Knowledge loss**: Design rationale disappears when people leave
- **Compliance gaps**: No evidence of requirements coverage

### PhenoSpecs Solution

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         PhenoSpecs Architecture                              │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│   ┌────────────────────────────────────────────────────────────────────┐    │
│   │                        Specification Layer                          │    │
│   │                                                                       │    │
│   │   specs/              adrs/              openapi/                   │    │
│   │   ┌──────────┐       ┌──────────┐      ┌──────────┐                 │    │
│   │   │ SPEC-001 │       │ ADR-001  │      │ API-001  │                 │    │
│   │   │ SPEC-002 │       │ ADR-002  │      │ API-002  │                 │    │
│   │   │ ...      │       │ ...      │      │ ...      │                 │    │
│   │   └──────────┘       └──────────┘      └──────────┘                 │    │
│   │   Markdown           MADR              OpenAPI 3.1                  │    │
│   │                                                                       │    │
│   └──────────────────────────┬──────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│   ┌────────────────────────────────────────────────────────────────────┐    │
│   │                         Registry Index                              │    │
│   │                                                                       │    │
│   │   registry.yaml ──► Unified index of all specifications             │    │
│   │                                                                       │    │
│   │   specs:                                                              │    │
│   │     SPEC-001: { title, path, status, implements, ... }             │    │
│   │   adrs:                                                               │    │
│   │     ADR-001: { title, path, status, date, ... }                   │    │
│   │   openapi:                                                            │    │
│   │     API-001: { title, path, version, implements, ... }             │    │
│   │                                                                       │    │
│   └──────────────────────────┬──────────────────────────────────────────┘    │
│                              │                                               │
│                              ▼                                               │
│   ┌────────────────────────────────────────────────────────────────────┐    │
│   │                        Traceability Layer                           │    │
│   │                                                                       │    │
│   │   Code Annotations ◄───► Registry ◄───► Validation                │    │
│   │                                                                       │    │
│   │   #[trace(spec = "SPEC-001")]                                        │    │
│   │   fn implement_feature() { ... }                                     │    │
│   │                                                                       │    │
│   └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
│   ┌────────────────────────────────────────────────────────────────────┐    │
│   │                         Tooling Layer                               │    │
│   │                                                                       │    │
│   │   phenospecs CLI ◄───► GitHub Actions ◄───► IDE Extensions         │    │
│   │                                                                       │    │
│   └────────────────────────────────────────────────────────────────────┘    │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## System Architecture

### 3.1 Component Overview

| Component | Path | Responsibility | Status |
|-----------|------|----------------|--------|
| **Specs** | `specs/` | Feature specifications by domain | Active |
| **ADRs** | `adrs/` | Architecture Decision Records | Active |
| **OpenAPI** | `openapi/` | API contracts and schemas | Active |
| **Integrations** | `integrations/` | Cross-system specifications | Active |
| **Registry** | `registry.yaml` | Central machine-readable index | Active |
| **Catalog** | `catalog-info.yaml` | Backstage integration | Active |

### 3.2 Repository Structure

```
PhenoSpecs/
├── specs/                          # Feature specifications
│   ├── _templates/                 # Spec templates
│   │   ├── spec.md                 # Base spec template
│   │   ├── frd.md                  # FRD template
│   │   └── plan.md                 # Implementation plan template
│   │
│   ├── auth/                       # Authentication domain
│   │   ├── oauth-pkce/
│   │   │   ├── spec.md             # Main specification
│   │   │   ├── frd.md              # Functional requirements
│   │   │   └── plan.md             # Implementation plan
│   │   ├── jwt-management/
│   │   │   ├── spec.md
│   │   │   ├── frd.md
│   │   │   └── plan.md
│   │   └── README.md               # Domain overview
│   │
│   ├── crypto/                     # Cryptography domain
│   │   ├── aes-gcm/
│   │   ├── rsa-ecdh/
│   │   └── README.md
│   │
│   ├── caching/                    # Caching domain
│   │   ├── multi-tier/
│   │   └── README.md
│   │
│   ├── api/                        # API design domain
│   │   ├── versioning/
│   │   ├── pagination/
│   │   └── README.md
│   │
│   ├── agents/                     # Agent framework domain
│   │   ├── orchestration-protocol/
│   │   └── README.md
│   │
│   ├── cli/                        # CLI tools domain
│   │   ├── unified-interface/
│   │   └── README.md
│   │
│   ├── observability/              # Observability domain
│   │   ├── distributed-tracing/
│   │   └── README.md
│   │
│   ├── storage/                    # Data storage domain
│   │   └── README.md
│   │
│   ├── testing/                    # Testing domain
│   │   └── README.md
│   │
│   └── platform/                   # Platform infrastructure
│       └── README.md
│
├── adrs/                           # Architecture Decision Records
│   ├── 001-hexagonal-architecture.md
│   ├── 002-rust-primary-language.md
│   ├── 003-spec-driven-development.md
│   ├── 004-unified-specification-registry.md
│   ├── 005-multi-format-documentation.md
│   ├── 006-traceability-first-development.md
│   └── README.md                   # ADR index and guide
│
├── openapi/                        # API contracts
│   ├── auth-api-v1.yaml
│   ├── cache-api-v1.yaml
│   └── README.md
│
├── integrations/                   # Integration specifications
│   ├── agileplus-github.md
│   └── README.md
│
├── registry.yaml                   # Central registry index
├── catalog-info.yaml               # Backstage catalog entry
├── SPEC.md                         # This specification
├── RESEARCH.md                     # SOTA research
├── README.md                       # Human entry point
└── .github/
    └── workflows/
        └── validate.yml            # CI validation
```

### 3.3 Architecture Diagrams

#### C4 Level 1: System Context

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                           System Context                                     │
│                         (PhenoSpecs in Context)                               │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│     ┌─────────────────┐          ┌─────────────────┐                         │
│     │   Developer     │◄────────►│                 │                         │
│     │   (Engineer)    │  Query   │                 │                         │
│     └─────────────────┘          │                 │                         │
│                                  │   PhenoSpecs    │                         │
│     ┌─────────────────┐          │   (Registry)    │                         │
│     │   CI/CD         │◄────────►│                 │                         │
│     │   (GitHub       │ Validate │                 │                         │
│     │    Actions)     │          │                 │                         │
│     └─────────────────┘          └────────┬────────┘                         │
│                                           │                                  │
│                                           │ Manages                          │
│                                           ▼                                  │
│     ┌─────────────────┐          ┌─────────────────┐                         │
│     │   IDE           │◄────────►│   Codebases     │                         │
│     │   (VS Code)     │  Trace   │   (Git repos)   │                         │
│     └─────────────────┘          └─────────────────┘                         │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### C4 Level 2: Container Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                         Container Diagram                                    │
│                    (Major Structural Building Blocks)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │                        Git Repository                              │   │
│  │  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐             │   │
│  │  │  Specs        │ │  ADRs         │ │  OpenAPI      │             │   │
│  │  │  (Markdown)   │ │  (Markdown)   │ │  (YAML)       │             │   │
│  │  └───────┬───────┘ └───────┬───────┘ └───────┬───────┘             │   │
│  │          │                 │                 │                      │   │
│  │          └─────────────────┼─────────────────┘                      │   │
│  │                            │                                         │   │
│  │                            ▼                                         │   │
│  │                   ┌─────────────────┐                                  │   │
│  │                   │ registry.yaml   │                                  │   │
│  │                   │ (Index)         │                                  │   │
│  │                   └────────┬────────┘                              │   │
│  └──────────────────────────────┼─────────────────────────────────────────┘   │
│                                 │                                            │
│  ┌──────────────────────────────┼─────────────────────────────────────────┐   │
│  │                        CLI Tool (phenospecs)                         │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐ ┌────────────┐        │   │
│  │  │   List     │ │   Trace    │ │  Validate  │ │  Search    │        │   │
│  │  │   Command  │ │  Command   │ │   Command  │ │   Command  │        │   │
│  │  └────────────┘ └────────────┘ └────────────┘ └────────────┘        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                 │                                            │
│  ┌──────────────────────────────┼─────────────────────────────────────────┐   │
│  │                     CI/CD Integration                                   │   │
│  │  ┌────────────┐ ┌────────────┐ ┌────────────┐                        │   │
│  │  │  GitHub    │ │  GitLab    │ │  Custom    │                        │   │
│  │  │  Actions   │ │  CI        │ │  Scripts   │                        │   │
│  │  └────────────┘ └────────────┘ └────────────┘                        │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

#### C4 Level 3: Component Diagram

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Component Diagram                                     │
│                    (Major Components of PhenoSpecs)                        │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────────┐│
│  │                        Registry Component                              ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ ││
│  │  │   Spec       │  │   ADR        │  │   OpenAPI    │  │   Domain     │ ││
│  │  │   Index      │  │   Index      │  │   Index      │  │   Registry   │ ││
│  │  │              │  │              │  │              │  │              │ ││
│  │  │ - ID lookup  │  │ - ID lookup  │  │ - ID lookup  │  │ - Domain     │ ││
│  │  │ - Path map   │  │ - Status     │  │ - Version    │  │   mapping    │ ││
│  │  │ - Status     │  │ - Date       │  │ - Spec links │  │ - Owners     │ ││
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                    │                                        │
│  ┌─────────────────────────────────┼───────────────────────────────────────┐│
│  │                        Parser Components                             ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ ││
│  │  │   Markdown   │  │   OpenAPI    │  │    MADR      │  │   Tracing    │ ││
│  │  │   Parser     │  │   Parser     │  │   Parser     │  │   Parser     │ ││
│  │  │              │  │              │  │              │  │              │ ││
│  │  │ Extracts     │  │ Validates    │  │ Extracts     │  │ Finds code   │ ││
│  │  │ frontmatter  │  │ schema       │  │ ADR fields   │  │ annotations│ ││
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                    │                                        │
│  ┌─────────────────────────────────┼───────────────────────────────────────┐│
│  │                        Query Components                              ││
│  │  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐ ││
│  │  │   Search     │  │   Filter     │  │   Trace      │  │   Report     │ ││
│  │  │   Engine     │  │   Engine     │  │   Engine     │  │   Generator  │ ││
│  │  └──────────────┘  └──────────────┘  └──────────────┘  └──────────────┘ ││
│  └─────────────────────────────────────────────────────────────────────────┘│
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.4 Data Flow

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Data Flow Diagram                                   │
│                    (How Specifications Flow Through)                         │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  CREATE                    VALIDATE                    CONSUME               │
│                                                                              │
│  ┌────────┐               ┌────────┐               ┌────────┐             │
│  │ Author │               │  CI    │               │ Query  │             │
│  │ Creates│               │ Checks │               │ Results│             │
│  │ Spec   │               │ Links  │               │        │             │
│  └───┬────┘               └───┬────┘               └───┬────┘             │
│      │                        │                        │                  │
│      ▼                        ▼                        ▼                  │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                      Git Repository                               │    │
│  │  ┌────────────────────────────────────────────────────────────┐  │    │
│  │  │  PR: New spec.md + registry.yaml update                    │  │    │
│  │  │                                                             │  │    │
│  │  │  1. markdownlint (format)                                   │  │    │
│  │  │  2. phenospecs validate (schema)                            │  │    │
│  │  │  3. phenospecs trace check (if code changes)                │  │    │
│  │  └────────────────────────────────────────────────────────────┘  │    │
│  └──────────────────────────────┬───────────────────────────────────┘    │
│                                 │ Merge                                    │
│                                 ▼                                          │
│  ┌──────────────────────────────────────────────────────────────────┐    │
│  │                      Registry Index                               │    │
│  │                    (registry.yaml updated)                         │    │
│  └──────────────────────────────┬───────────────────────────────────┘    │
│                                 │ Query                                    │
│            ┌────────────────────┼────────────────────┐                     │
│            ▼                    ▼                    ▼                     │
│     ┌────────────┐      ┌────────────┐      ┌────────────┐                │
│     │ Developer  │      │   CI/CD    │      │  Backstage │                │
│     │  (CLI)     │      │  (Gates)   │      │  (Portal)  │                │
│     └────────────┘      └────────────┘      └────────────┘                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Data Models

### 4.1 Registry Schema

The `registry.yaml` is the central data model. It is the **source of truth** for all specification metadata.

```yaml
# Registry Schema Definition
# Version: 1.0.0

# Required: Registry metadata
registry_version: string  # Semantic version of registry schema
last_updated: string    # ISO 8601 date (YYYY-MM-DD)

# Optional: Domain classifications
domains:
  <domain-key>:           # Machine-readable domain identifier
    name: string         # Human-readable domain name
    description: string  # Domain overview
    owner: string        # Team responsible (e.g., "team-security")
    repos: [string]      # Associated repositories
    tags: [string]       # Classification tags

# Required: Specifications index
specs:
  <spec-id>:             # Unique identifier (e.g., "SPEC-AUTH-001")
    title: string        # Human-readable title
    path: string         # Relative path to spec file
    domain: string       # Domain key (must exist in domains)
    status: enum         # draft | specified | implementing | implemented | deprecated
    
    # Optional
    description: string  # Brief description
    created: string      # ISO 8601 date
    updated: string      # ISO 8601 date
    author: string       # GitHub handle (@username)
    tags: [string]       # Classification tags
    
    # Relationships
    implements: [string] # IDs of specs/ADRs this implements
    depends_on: [string] # IDs this spec depends on
    supersedes: [string] # IDs this spec replaces
    
    # Implementation links
    repos: [string]      # Repository names implementing this spec
    
    # Associated documents
    frd: string         # Path to Functional Requirements Doc
    plan: string        # Path to Implementation Plan
    openapi: string     # Path to OpenAPI spec (if applicable)
    adr: string         # Path to related ADR
    
    # Traceability
    coverage:
      status: enum      # complete | partial | none
      percentage: int   # 0-100
      missing_frs: [string]  # FRs without implementations

# Required: ADRs index
adrs:
  <adr-id>:             # Unique identifier (e.g., "ADR-001")
    title: string       # Human-readable title
    path: string        # Relative path to ADR file
    status: enum        # proposed | accepted | deprecated | superseded
    date: string        # Decision date (YYYY-MM-DD)
    
    # Optional
    author: string      # GitHub handle
    tags: [string]      # Classification tags
    
    # Relationships
    relates_to: [string]  # Related ADRs
    supersedes: string      # ADR this replaces (if any)
    superseded_by: string   # ADR that replaces this (if deprecated)
    
    # Impact
    affected_specs: [string]  # Specs affected by this decision
    affected_repos: [string]  # Repos affected

# Required: OpenAPI index
openapi:
  <api-id>:             # Unique identifier (e.g., "auth-api-v1")
    title: string       # API title
    path: string        # Relative path to OpenAPI file
    version: string     # API version (semantic versioning)
    status: enum        # draft | stable | deprecated
    
    # Optional
    description: string
    domain: string      # Domain classification
    
    # Relationships
    implements: [string]  # Spec IDs this API implements
    
    # Implementation
    repos: [string]         # Repositories implementing this API
    
    # Endpoints summary (auto-generated)
    endpoints:
      - path: string
        method: string
        summary: string
        spec_ref: string    # SPEC ID implemented

# Optional: Integration specs
integrations:
  <int-id>:             # Unique identifier (e.g., "INT-001")
    title: string       # Integration name
    path: string        # Path to integration spec
    systems: [string]   # System names involved
    protocol: string    # Integration protocol (REST, gRPC, event, etc.)
    status: enum        # draft | specified | implementing | implemented
    
    # Optional
    description: string
    created: string
    updated: string

# Optional: Cross-cutting concerns
cross_cutting:
  security:
    refs: [string]      # Spec IDs related to security
  performance:
    refs: [string]      # Spec IDs related to performance
  observability:
    refs: [string]      # Spec IDs related to observability
  reliability:
    refs: [string]      # Spec IDs related to reliability
```

### 4.2 Specification Document Model

```yaml
# Specification Frontmatter Schema
---
# Required fields
id: string              # Unique spec ID (e.g., "SPEC-AUTH-001")
title: string           # Human-readable title

# Required - Status
domain: string          # Domain key (auth, crypto, api, etc.)
status: enum            # draft | specified | implementing | implemented

# Optional - Metadata
created: string         # ISO 8601 date (YYYY-MM-DD)
updated: string         # ISO 8601 date (YYYY-MM-DD)
author: string          # Primary author (@username)
contributors: [string]  # Additional contributors
version: string         # Document version (semver)

# Optional - Classification
tags: [string]          # E.g., ["oauth", "security", "web"]
priority: enum          # P0 | P1 | P2 | P3

# Optional - Relationships (must match registry)
implements: [string]    # IDs this implements
depends_on: [string]    # IDs this depends on
supersedes: [string]    # IDs this replaces

# Optional - Implementation
repositories:           # Where this is implemented
  - name: string
    path: string        # Path within repo
    status: enum        # complete | partial | planned
    language: string    # Primary language
---

# Document Body (Markdown)
```

### 4.3 ADR Document Model

```yaml
# ADR Frontmatter Schema (MADR + extensions)
---
# Required
id: string              # ADR ID (e.g., "ADR-001")
title: string           # Decision title
status: enum            # proposed | accepted | deprecated | superseded
date: string            # Decision date (YYYY-MM-DD)

# Optional
author: string          # Decision author
tags: [string]          # Classification tags

# Relationships
supersedes: string      # ADR this replaces
superseded_by: string   # ADR that replaces this
relates_to: [string]    # Related ADRs
affected_specs: [string]  # Specs affected
---

# Document Body (MADR format)
```

### 4.4 OpenAPI Extension Schema

```yaml
# OpenAPI with PhenoSpecs extensions
openapi: '3.1.0'
info:
  title: API Title
  version: '1.0.0'
  
  # PhenoSpecs extensions (x-phenotype-*)
  x-phenotype-spec-id: string        # Primary spec implemented
  x-phenotype-domain: string         # Domain classification
  x-phenotype-status: enum          # draft | stable | deprecated
  x-phenotype-implements: [string]  # Additional specs implemented

paths:
  /endpoint:
    get:
      summary: Endpoint description
      # Traceability extensions
      x-phenotype-fr: string          # FR ID implemented
      x-phenotype-spec-ref: string    # Spec reference
```

### 4.5 Traceability Annotation Models

#### Rust Procedural Macro

```rust
// Attribute syntax
#[trace(spec = "SPEC-XXX-NNN")]
#[trace(spec = "SPEC-XXX-NNN", fr = "FR-NNN")]
#[trace(spec = "SPEC-XXX-NNN", fr = "FR-NNN", repo = "org/repo")]

// Model
struct TraceAnnotation {
    spec: String,        // Required: Spec ID
    fr: Option<String>,   // Optional: FR ID(s), comma-separated
    repo: Option<String>, // Optional: Repository override
    path: Option<String>, // Optional: File path override
}
```

#### Go Comment Convention

```go
// Single line
// FR: <spec-id> <fr-id> [description]

// Multi-line
// FR: <spec-id> <fr-id>,<fr-id>
// <extended description>
// See: <spec-path>

// Model
type TraceComment struct {
    Spec string   // Required
    FRs []string  // Optional
    Description string  // Optional
}
```

#### TypeScript JSDoc

```typescript
/**
 * @spec SPEC-XXX-NNN
 * @fr FR-NNN
 * @repo org/repo
 */

// Model
interface TraceJSDoc {
    spec: string;     // Required
    fr?: string;      // Optional
    repo?: string;    // Optional
}
```

---

## Domain Model

### 5.1 Domain Classifications

| Domain | Description | Typical Specs | Owner |
|--------|-------------|---------------|-------|
| **auth** | Authentication & authorization | OAuth, JWT, MFA, SSO | team-security |
| **crypto** | Cryptographic operations | Encryption, hashing, keys | team-security |
| **caching** | Caching strategies | Multi-tier, invalidation | team-platform |
| **database** | Data storage & access | Schema design, migrations | team-platform |
| **api** | API design & implementation | REST, GraphQL, versioning | team-platform |
| **integration** | System integrations | Webhooks, events, protocols | team-platform |
| **frontend** | UI/UX patterns | Components, state management | team-frontend |
| **deployment** | CI/CD & infrastructure | Pipelines, environments | team-devops |
| **observability** | Monitoring & logging | Tracing, metrics, alerts | team-platform |
| **agents** | Agent framework | Orchestration, protocols | team-agents |
| **cli** | CLI tools | Command design, UX | team-devtools |
| **testing** | Testing strategies | TDD, BDD, integration | team-quality |
| **storage** | Data persistence | Files, objects, streams | team-platform |

### 5.2 Domain Relationships

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                          Domain Dependencies                                 │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────┐                                                               │
│  │  auth   │◄────────────────────────────────────┐                        │
│  └────┬────┘                                      │                        │
│       │                                           │                        │
│       │ uses                                      │ secures                │
│       ▼                                           ▼                        │
│  ┌─────────┐      ┌─────────┐      ┌─────────┐  ┌─────────┐               │
│  │  crypto │      │  api    │      │  agents │  │  cli    │               │
│  └─────────┘      └────┬────┘      └─────────┘  └─────────┘               │
│                        │                                                   │
│           ┌────────────┼────────────┐                                      │
│           │            │            │                                       │
│           ▼            ▼            ▼                                       │
│      ┌─────────┐  ┌─────────┐  ┌─────────┐                                │
│      │ caching │  │database │  │observability                             │
│      └─────────┘  └─────────┘  └─────────┘                                │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## API Specification

### 6.1 CLI Interface

#### Command: `phenospecs list`

```bash
# List all specifications
phenospecs list

# List by domain
phenospecs list --domain auth

# List by status
phenospecs list --status implemented

# List by tag
phenospecs list --tag security

# Combined filters
phenospecs list --domain auth --status implementing --format json

# Output formats
phenospecs list --format table    # Default
phenospecs list --format json     # Machine-readable
phenospecs list --format yaml     # Registry-compatible
phenospecs list --format csv      # Spreadsheet import
```

**Output (table):**
```
ID              DOMAIN    STATUS         TITLE
───────────────────────────────────────────────────────────
SPEC-AUTH-001   auth      implemented    OAuth 2.0 + PKCE
SPEC-AUTH-002   auth      implementing   JWT Management
SPEC-CRYPTO-001 crypto    implemented    AES-GCM Encryption
```

#### Command: `phenospecs trace`

```bash
# Trace a specification to implementations
phenospecs trace SPEC-AUTH-001

# Trace with format options
phenospecs trace SPEC-AUTH-001 --format tree
phenospecs trace SPEC-AUTH-001 --format list
phenospecs trace SPEC-AUTH-001 --format json

# Trace specific FR
phenospecs trace SPEC-AUTH-001 FR-002

# Update traceability index
phenospecs trace scan [--repo <path>]

# Validate traceability
phenospecs trace validate
```

**Output (tree):**
```
SPEC-AUTH-001: OAuth 2.0 Implementation
├── FR-001: Authorization code flow [3 implementations]
│   ├── phenotype-auth-ts/src/oauth/flow.rs:42
│   ├── phenotype-auth-go/oauth/flow.go:38
│   └── Authvault/src/flow.ts:45
├── FR-002: PKCE support [2 implementations]
│   ├── phenotype-auth-ts/src/oauth/pkce.rs:15
│   └── Authvault/src/pkce.ts:22
└── FR-003: Refresh token rotation [0 implementations] ⚠️
```

#### Command: `phenospecs coverage`

```bash
# Overall coverage report
phenospecs coverage

# Coverage for specific spec
phenospecs coverage SPEC-AUTH-001

# Coverage by domain
phenospecs coverage --domain auth

# Output formats
phenospecs coverage --format html --output ./report
phenospecs coverage --format json
phenospecs coverage --format markdown
```

**Output (summary):**
```yaml
summary:
  total_specs: 50
  traced_specs: 48
  coverage: 96%
  
by_domain:
  auth:
    specs: 10
    traced: 10
    coverage: 100%
  crypto:
    specs: 5
    traced: 4
    coverage: 80%
    
untraced:
  - SPEC-CRYPTO-002 (Asymmetric Encryption)
  - SPEC-AGENT-001 (Agent Orchestration)
```

#### Command: `phenospecs validate`

```bash
# Validate registry integrity
phenospecs validate

# Strict validation (fail on warnings)
phenospecs validate --strict

# Validate specific spec
phenospecs validate SPEC-AUTH-001

# Fix auto-fixable issues
phenospecs validate --fix
```

**Checks performed:**
- [x] All paths in registry exist
- [x] All IDs are unique
- [x] All domain references are valid
- [x] All relationships resolve
- [x] Frontmatter matches registry
- [x] OpenAPI files are valid (if Spectral available)

#### Command: `phenospecs search`

```bash
# Search specifications
phenospecs search "oauth pkce"

# Search with filters
phenospecs search "encryption" --domain crypto

# Fuzzy search
phenospecs search "auth" --fuzzy

# Search in content (not just titles)
phenospecs search "refresh token" --content
```

#### Command: `phenospecs init`

```bash
# Initialize phenospecs in current repo
phenospecs init

# Create new specification
phenospecs init spec specs/auth/new-feature

# Create new ADR
phenospecs init adr "Decision Title"

# Create OpenAPI stub
phenospecs init openapi new-api
```

### 6.2 Library Interface (Rust)

```rust
use phenospecs::{Registry, Spec, Query};

// Load registry
let registry = Registry::load("registry.yaml")?;

// Query specifications
let specs = registry.specs()
    .filter(|s| s.domain == "auth")
    .filter(|s| s.status == Status::Implemented)
    .collect::<Vec<_>>();

// Get traceability
let traces = registry.trace("SPEC-AUTH-001")?;
for trace in traces {
    println!("{} in {}:{}", 
        trace.function, 
        trace.repo, 
        trace.path
    );
}

// Validate
let report = registry.validate()?;
if !report.is_valid() {
    for error in report.errors() {
        eprintln!("Error: {}", error);
    }
}
```

### 6.3 HTTP API (Future)

```yaml
openapi: '3.1.0'
info:
  title: PhenoSpecs API
  version: '1.0.0'

paths:
  /specs:
    get:
      summary: List specifications
      parameters:
        - name: domain
          in: query
          schema:
            type: string
        - name: status
          in: query
          schema:
            type: string
            enum: [draft, specified, implementing, implemented]
      responses:
        '200':
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/Spec'

  /specs/{id}:
    get:
      summary: Get specification details
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/SpecDetail'

  /trace/{specId}:
    get:
      summary: Get traceability for spec
      responses:
        '200':
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Traceability'
```

---

## Integration Patterns

### 7.1 GitHub Integration

#### Pull Request Template

```markdown
<!-- .github/pull_request_template.md -->

## Description
Brief description of changes.

## Specification Reference
<!-- Link to relevant specification -->
- [ ] No spec changes required
- [ ] Implements: <!-- SPEC-XXX-NNN -->
- [ ] Updates: <!-- SPEC-XXX-NNN -->
- [ ] New spec created: <!-- Link to spec -->

## Traceability
<!-- For implementation PRs -->
- [ ] Code includes trace annotations
- [ ] FR coverage complete
- [ ] `phenospecs trace validate` passes

## Checklist
- [ ] Tests added/updated
- [ ] Documentation updated
- [ ] Registry updated (if needed)
```

#### GitHub Actions Workflow

```yaml
# .github/workflows/specs.yml
name: Specification Checks

on:
  pull_request:
    paths:
      - '**/*.md'
      - '**/registry.yaml'
      - '**/openapi/**'

jobs:
  validate:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      
      - name: Setup PhenoSpecs
        uses: phenotype/setup-phenospecs@v1
        
      - name: Validate Registry
        run: phenospecs validate --strict
        
      - name: Check Traceability
        run: |
          phenospecs trace scan
          phenospecs trace validate
          
      - name: Coverage Report
        run: |
          phenospecs coverage --format markdown >> $GITHUB_STEP_SUMMARY
        
      - name: Comment PR
        uses: phenotype/spec-pr-comment@v1
        with:
          github-token: ${{ secrets.GITHUB_TOKEN }}
```

### 7.2 Backstage Integration

```yaml
# catalog-info.yaml
apiVersion: backstage.io/v1alpha1
kind: Component
metadata:
  name: phenospecs
  annotations:
    phenotype.dev/specs: "specs/"
    phenotype.dev/registry: "registry.yaml"
    phenotype.dev/coverage: "85%"
spec:
  type: documentation
  owner: team-platform
  lifecycle: production
  dependsOn:
    - component:agileplus
```

### 7.3 IDE Integration

#### VS Code Extension

```json
// Features
{
  "spec-links.hover": {
    "description": "Show spec details on hover",
    "enabled": true
  },
  "spec-links.navigation": {
    "description": "Go to spec from code annotation",
    "keybinding": "Ctrl+Shift+S"
  },
  "spec-links.validation": {
    "description": "Real-time annotation validation",
    "severity": "warning"
  },
  "spec-links.completion": {
    "description": "Autocomplete spec IDs",
    "trigger": "@"
  },
  "spec-links.coverage": {
    "description": "Show coverage in gutter",
    "colors": {
      "complete": "#4CAF50",
      "partial": "#FFC107",
      "none": "#F44336"
    }
  }
}
```

### 7.4 AgilePlus Integration

```bash
# Link work package to spec
agileplus plan --feature kitty-spec-001 --link-spec SPEC-AUTH-001

# Check spec coverage for feature
agileplus validate --feature kitty-spec-001 --check-specs

# Generate implementation plan from spec
agileplus plan generate --spec SPEC-AUTH-001
```

---

## Governance Model

### 8.1 Specification Lifecycle

```
┌─────────┐      ┌──────────┐      ┌─────────────┐      ┌─────────────┐
│  DRAFT  │ ──►  │ SPECIFIED │ ──► │ IMPLEMENTING │ ──► │ IMPLEMENTED │
└─────────┘      └──────────┘      └─────────────┘      └─────────────┘
      │                              │
      │                              │
      ▼                              ▼
┌─────────┐                   ┌─────────────┐
│REJECTED │                   │ DEPRECATED  │
└─────────┘                   └─────────────┘
```

**Status Definitions:**

| Status | Definition | Exit Criteria |
|--------|-----------|---------------|
| **Draft** | Initial creation, not yet reviewed | Complete FRD, technical approach |
| **Specified** | Reviewed and approved | Peer review, registry update |
| **Implementing** | Code development in progress | First trace annotation committed |
| **Implemented** | Fully implemented and traced | Coverage > 90%, tests pass |
| **Deprecated** | No longer recommended | Superseding spec exists |
| **Rejected** | Not accepted | ADR documenting rejection |

### 8.2 Approval Process

#### For Specifications

| Change | Approver | Process |
|--------|----------|---------|
| Draft → Specified | Domain Owner | PR review + approval |
| Specified → Implementing | Tech Lead | Implementation plan approved |
| Implementing → Implemented | Domain Owner + QA | Coverage check + tests |
| Specified → Deprecated | Architecture Team | ADR required |

#### For ADRs

| Status Change | Approver | Process |
|--------------|----------|---------|
| Proposed → Accepted | Architecture Team | Discussion + consensus |
| Accepted → Deprecated | Original Author | ADR documenting reason |

### 8.3 Roles and Responsibilities

| Role | Responsibilities |
|------|------------------|
| **Spec Author** | Create specifications, maintain accuracy, ensure traceability |
| **Domain Owner** | Review domain specs, approve status changes, ensure consistency |
| **Tech Lead** | Ensure implementation follows specs, maintain code annotations |
| **Architecture Team** | Review ADRs, cross-domain impacts, deprecation decisions |
| **Platform Team** | Maintain tooling, CI/CD integration, registry health |
| **QA** | Validate spec coverage, test against FRs |

### 8.4 Quality Gates

#### Specification Quality Checklist

- [ ] Clear, testable requirements (FRs)
- [ ] Technical requirements defined (TRs)
- [ ] Data models documented
- [ ] Interface contracts specified
- [ ] Error cases enumerated
- [ ] Performance requirements stated
- [ ] Security considerations documented
- [ ] Dependencies identified
- [ ] Registry entry complete

#### Implementation Quality Checklist

- [ ] Trace annotations present
- [ ] All P0 FRs implemented
- [ ] Tests verify FRs
- [ ] Coverage report generated
- [ ] Documentation updated
- [ ] Registry status updated

---

## Tooling Ecosystem

### 9.1 Core Tools

| Tool | Purpose | Language | Status |
|------|---------|----------|--------|
| **phenospecs** | CLI for registry operations | Rust | Building |
| **spec-links** | Traceability scanner | Rust | Building |
| **spec-trace** | Code annotation macros | Rust/Go/TS | Building |
| **phenospecs-vscode** | VS Code extension | TypeScript | Planned |

### 9.2 Integration Tools

| Tool | Purpose | Integration |
|------|---------|-------------|
| **markdownlint** | Markdown linting | CI |
| **yamllint** | YAML validation | CI |
| **Spectral** | OpenAPI validation | CI |
| **Vale** | Prose linting | CI/Editor |
| **Swagger UI** | API doc rendering | Portal |
| **ReDoc** | API doc rendering | Portal |

### 9.3 Tool Architecture

```
┌─────────────────────────────────────────────────────────────────────────────┐
│                        Tooling Ecosystem                                     │
├─────────────────────────────────────────────────────────────────────────────┤
│                                                                              │
│  ┌─────────────────────────────────────────────────────────────────────┐  │
│  │                        Core Platform                                 │  │
│  │  ┌────────────┐  ┌────────────┐  ┌────────────┐  ┌────────────┐     │  │
│  │  │phenospecs  │  │spec-links  │  │  Registry  │  │   Parser   │     │  │
│  │  │  CLI       │  │  Scanner   │  │   Engine   │  │   Engine   │     │  │
│  │  └────────────┘  └────────────┘  └────────────┘  └────────────┘     │  │
│  └─────────────────────────────────────────────────────────────────────┘  │
│                                    │                                        │
│           ┌────────────────────────┼────────────────────────┐               │
│           │                        │                        │               │
│           ▼                        ▼                        ▼               │
│  ┌─────────────────┐      ┌─────────────────┐      ┌─────────────────┐    │
│  │  IDE Extensions  │      │   CI/CD Tools   │      │  Portal/Server  │    │
│  │                  │      │                  │      │                  │    │
│  │  • VS Code       │      │  • GitHub       │      │  • Backstage    │    │
│  │  • IntelliJ      │      │    Actions       │      │  • Custom UI    │    │
│  │  • Vim           │      │  • GitLab CI     │      │  • Static Site  │    │
│  └─────────────────┘      │  • pre-commit    │      └─────────────────┘    │
│                           └─────────────────┘                               │
│                                                                              │
└─────────────────────────────────────────────────────────────────────────────┘
```

---

## Implementation Guide

### 10.1 Getting Started

#### For Spec Authors

1. **Read the handbook**: Understand spec format and conventions
2. **Use templates**: Start with `phenospecs init spec`
3. **Follow the lifecycle**: Draft → Review → Specified
4. **Maintain traceability**: Link to implementations
5. **Update registry**: Keep registry.yaml current

#### For Developers

1. **Find specs**: Use `phenospecs list` or IDE integration
2. **Read before coding**: Check `specs/<domain>/` for relevant specs
3. **Add annotations**: Use trace macros when implementing FRs
4. **Run validation**: `phenospecs validate` before PR
5. **Update status**: Move spec to "implemented" when done

#### For Leads

1. **Enforce gates**: CI validation must pass
2. **Review ADRs**: Architecture decisions need review
3. **Monitor coverage**: Regular coverage reports
4. **Update domains**: Keep domain ownership current
5. **Evolve process**: Suggest improvements via ADRs

### 10.2 Migration Strategy

#### Phase 1: Bootstrap (Week 1-2)
- [ ] Create PhenoSpecs repository
- [ ] Define initial domains
- [ ] Migrate existing specs from AgilePlus
- [ ] Set up CI validation

#### Phase 2: Adoption (Week 3-4)
- [ ] Team training sessions
- [ ] Document first new specs
- [ ] Create initial ADRs
- [ ] Set up IDE extensions

#### Phase 3: Enforcement (Week 5-8)
- [ ] Enable CI gates
- [ ] Require traceability for new code
- [ ] Backfill critical specs
- [ ] Measure coverage

#### Phase 4: Optimization (Ongoing)
- [ ] Automate registry updates
- [ ] Build custom tooling
- [ ] Integrate with other systems
- [ ] Measure impact

### 10.3 Best Practices

#### Specification Writing

1. **Start with the user**: What problem does this solve?
2. **Be specific**: Quantify requirements where possible
3. **Include examples**: Data models, API calls, error cases
4. **Keep it current**: Specs should reflect reality
5. **Link liberally**: Connect to related specs, ADRs, code

#### Traceability

1. **Annotate at the right level**: Function/method, not module
2. **Be specific**: Link to specific FRs, not just specs
3. **Update with refactoring**: Annotations must survive changes
4. **Validate locally**: Run `phenospecs trace validate` before commit
5. **Don't over-trace**: Infrastructure code may not need annotations

#### Registry Maintenance

1. **Update atomically**: Spec + registry in same PR
2. **Validate frequently**: CI catches errors early
3. **Archive carefully**: Deprecate, don't delete
4. **Document relationships**: Use implements/depends_on
5. **Keep it clean**: Remove stale entries promptly

---

## Appendix A: Specification Templates

### A.1 Feature Specification Template

```markdown
---
id: SPEC-XXX-NNN
title: Feature Title
domain: auth|crypto|api|...
status: draft
created: YYYY-MM-DD
author: @username
---

# Feature Title

## Overview

Brief description of the feature (2-3 sentences).

### Goals
- Goal 1
- Goal 2

### Non-Goals
- Out of scope item 1
- Out of scope item 2

---

## Functional Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|-------------------|
| FR-001 | Requirement description | P0 | How to verify |
| FR-002 | Another requirement | P1 | How to verify |

---

## Technical Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| TR-001 | Performance target | &lt;100ms | Benchmark |
| TR-002 | Availability target | 99.9% | Monitoring |

---

## Data Model

```typescript
interface ModelName {
  id: string;
  // ...
}
```

---

## Interface Design

### API Endpoints (if applicable)

| Method | Path | Description | Spec Ref |
|--------|------|-------------|----------|
| POST | /endpoint | Description | FR-001 |

### Events (if applicable)

| Event | Schema | Description |
|-------|--------|-------------|
| event.name | { ... } | Description |

---

## Error Handling

| Error | Code | Description | Handling |
|-------|------|-------------|----------|
| ERROR_NAME | 400 | Description | What to do |

---

## Security Considerations

- Consideration 1
- Consideration 2

---

## Dependencies

- Depends on: SPEC-XXX-NNN
- Enables: SPEC-XXX-NNN

---

## Implementation Links

- repo-name: `src/path/to/implementation/`

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| YYYY-MM-DD | 0.1.0 | Initial draft | @username |
```

### A.2 ADR Template

```markdown
---
id: ADR-NNN
title: Decision Title
status: proposed
date: YYYY-MM-DD
author: @username
tags: [architecture, category]
---

# ADR-NNN: Decision Title

## Status

Proposed / Accepted / Deprecated / Superseded

## Context

What is the issue that we're seeing that is motivating this decision or change?

## Decision

What is the change that we're proposing or have agreed to implement?

## Consequences

What becomes easier or more difficult to do because of this change?

### Positive
- Benefit 1
- Benefit 2

### Negative
- Cost 1
- Cost 2

## Mitigations

How will we address the negative consequences?

## Related

- Related ADRs: ADR-NNN
- Affected specs: SPEC-XXX-NNN
- Supersedes: ADR-NNN (if applicable)
```

### A.3 OpenAPI Template

```yaml
openapi: '3.1.0'
info:
  title: API Title
  version: '1.0.0'
  description: API description
  
  x-phenotype-spec-id: SPEC-XXX-NNN
  x-phenotype-domain: domain
  x-phenotype-status: draft

servers:
  - url: https://api.example.com/v1

paths:
  /resource:
    get:
      summary: Get resources
      operationId: getResources
      x-phenotype-fr: FR-001
      
      responses:
        '200':
          description: Success
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/Resource'

components:
  schemas:
    Resource:
      type: object
      properties:
        id:
          type: string
```

---

## Appendix B: Traceability Examples

### B.1 Rust Example

```rust
//! OAuth 2.0 implementation
//! 
//! Implements: SPEC-AUTH-001

use phenotype_trace::trace;

/// Authenticate user with OAuth 2.0
/// 
/// Implements authorization code flow as specified in
/// [SPEC-AUTH-001](specs/auth/oauth-pkce/spec.md)
#[trace(spec = "SPEC-AUTH-001", fr = "FR-001")]
pub async fn authenticate(
    request: AuthRequest
) -> Result<AuthResponse, AuthError> {
    // Implementation
}

/// Generate PKCE pair for secure authorization
/// 
/// Implements PKCE extension per RFC 7636
#[trace(spec = "SPEC-AUTH-001", fr = "FR-002")]
pub fn generate_pkce() -> PKCEPair {
    // Implementation
}

/// Refresh access token
/// 
/// Implements refresh token rotation
#[trace(spec = "SPEC-AUTH-001", fr = "FR-003")]
pub async fn refresh_token(
    refresh_token: &str
) -> Result<TokenPair, AuthError> {
    // Implementation
}
```

### B.2 Go Example

```go
// Package oauth implements OAuth 2.0 authentication
//
// Implements: SPEC-AUTH-001
package oauth

// Authenticate handles OAuth 2.0 authorization code flow
//
// FR: SPEC-AUTH-001 FR-001 - Authorization code flow
func Authenticate(ctx context.Context, req *AuthRequest) (*AuthResponse, error) {
    // Implementation
}

// GeneratePKCE creates a PKCE code verifier and challenge
//
// FR: SPEC-AUTH-001 FR-002 - PKCE support
// See: https://tools.ietf.org/html/rfc7636
func GeneratePKCE() (*PKCEPair, error) {
    // Implementation
}

// RefreshToken rotates refresh tokens for security
//
// FR: SPEC-AUTH-001 FR-003 - Token rotation
// Related: SPEC-CRYPTO-001 (token encryption)
func RefreshToken(refreshToken string) (*TokenPair, error) {
    // Implementation
}
```

### B.3 TypeScript Example

```typescript
/**
 * OAuth 2.0 authentication module
 * 
 * @module oauth
 * @spec SPEC-AUTH-001
 */

/**
 * Authenticate user with OAuth 2.0 authorization code flow
 * 
 * @spec SPEC-AUTH-001
 * @fr FR-001
 * @param request - Authentication request
 * @returns Authentication response with tokens
 * @throws AuthError if authentication fails
 */
export async function authenticate(
  request: AuthRequest
): Promise<AuthResponse> {
  // Implementation
}

/**
 * Generate PKCE parameters for secure OAuth flow
 * 
 * @spec SPEC-AUTH-001
 * @fr FR-002
 * @see {@link https://tools.ietf.org/html/rfc7636}
 */
export function generatePKCE(): PKCEPair {
  // Implementation
}

/**
 * Refresh access token with rotation
 * 
 * @spec SPEC-AUTH-001
 * @fr FR-003
 * @param refreshToken - Current refresh token
 * @returns New token pair, previous refresh token invalidated
 */
export async function refreshToken(
  refreshToken: string
): Promise<TokenPair> {
  // Implementation
}
```

---

## Appendix C: Glossary

| Term | Definition |
|------|------------|
| **ADR** | Architecture Decision Record |
| **API** | Application Programming Interface |
| **C4 Model** | Context, Containers, Components, Code architecture visualization |
| **Domain** | Logical grouping of related specifications |
| **FR** | Functional Requirement |
| **FRD** | Functional Requirements Document |
| **MADR** | Markdown ADR format |
| **OpenAPI** | Standard for HTTP API specifications |
| **P0/P1/P2/P3** | Priority levels (P0 = critical, P3 = nice-to-have) |
| **PKCE** | Proof Key for Code Exchange (OAuth 2.0 extension) |
| **Registry** | Central index of all specifications |
| **SDD** | Specification-Driven Development |
| **Spec** | Specification document |
| **Traceability** | Linking specifications to code implementations |
| **TR** | Technical Requirement |

---

## Appendix D: References

### Standards

1. [IEEE 830-1998] Recommended Practice for Software Requirements Specifications
2. [ISO/IEC/IEEE 42010:2022] Software and systems engineering — Architecture description
3. [OpenAPI Specification 3.1.0](https://spec.openapis.org/oas/v3.1.0)
4. [MADR](https://adr.github.io/madr/) - Markdown ADR format

### Phenotype References

1. [AgilePlus](https://github.com/KooshaPari/AgilePlus) - Spec-driven development CLI
2. [HexaKit](https://github.com/KooshaPari/HexaKit) - Project templates
3. [PhenoHandbook](https://github.com/KooshaPari/PhenoHandbook) - Patterns and guidelines
4. [RESEARCH.md](RESEARCH.md) - State of the art analysis

### External Resources

1. [C4 Model](https://c4model.com/) - Architecture visualization
2. [Diátaxis](https://diataxis.fr/) - Documentation framework
3. [Backstage](https://backstage.io/) - Developer portal platform
4. [Write the Docs](https://www.writethedocs.org/) - Documentation community

---

## Appendix E: Migration Checklist

### Pre-Migration
- [ ] Identify existing specifications
- [ ] Audit current documentation locations
- [ ] Define domain boundaries
- [ ] Assign domain owners
- [ ] Set up PhenoSpecs repository

### Migration
- [ ] Create registry.yaml structure
- [ ] Migrate specifications to specs/
- [ ] Create initial ADRs
- [ ] Set up CI/CD validation
- [ ] Train teams on new workflow

### Post-Migration
- [ ] Monitor adoption metrics
- [ ] Collect feedback
- [ ] Refine processes
- [ ] Build additional tooling
- [ ] Measure impact

---

## Appendix F: Detailed Implementation Examples

### F.1 Complete Spec Example: Authentication Service

```markdown
---
id: SPEC-AUTH-001
title: OAuth 2.0 + PKCE Authentication Flow
domain: auth
status: implemented
created: 2024-01-15
updated: 2024-06-20
author: @kooshapari
contributors: [@alice, @bob]
tags: [oauth, pkce, security, web]
priority: P0
---

# OAuth 2.0 + PKCE Authentication Flow

## Overview

This specification defines the OAuth 2.0 authentication flow with PKCE (Proof Key for Code Exchange) extension for the Phenotype ecosystem. PKCE prevents authorization code interception attacks, making this flow suitable for public clients including mobile and desktop applications.

### Goals
- Implement secure OAuth 2.0 authorization code flow
- Add PKCE extension for public client security
- Support refresh token rotation for enhanced security
- Provide clear integration patterns for all Phenotype services

### Non-Goals
- Resource Owner Password Credentials flow (deprecated, insecure)
- Client Credentials flow (covered in SPEC-AUTH-002)
- Device Authorization flow (future specification)
- Third-party identity provider integration (covered in SPEC-AUTH-003)

---

## Functional Requirements

| ID | Requirement | Priority | Acceptance Criteria |
|----|-------------|----------|-------------------|
| FR-001 | Support authorization code flow | P0 | RFC 6749 compliant, tested with standard OAuth clients |
| FR-002 | Support PKCE extension | P0 | RFC 7636 compliant, S256 method mandatory, plain method rejected |
| FR-003 | Support refresh token rotation | P1 | New refresh token issued with each access token refresh |
| FR-004 | Support state parameter validation | P0 | State parameter required, validated on callback |
| FR-005 | Support multiple redirect URIs per client | P1 | Exact match validation, no wildcards |
| FR-006 | Support scope validation | P0 | Scopes validated against client registration |
| FR-007 | Provide clear error responses | P0 | RFC 6749 error format, descriptive messages |
| FR-008 | Support token introspection | P2 | RFC 7662 compliant introspection endpoint |

---

## Technical Requirements

| ID | Requirement | Target | Measurement |
|----|-------------|--------|-------------|
| TR-001 | Authorization endpoint response time | &lt;50ms p99 | Load test 10k req/s |
| TR-002 | Token endpoint response time | &lt;30ms p99 | Load test 10k req/s |
| TR-003 | Access token lifetime | 15 minutes | Configurable, default 900s |
| TR-004 | Refresh token lifetime | 7 days | Configurable, default 604800s |
| TR-005 | Authorization code lifetime | 10 minutes | Non-configurable for security |
| TR-006 | System availability | 99.95% | Measured over 30 days |
| TR-007 | PKCE code challenge minimum length | 43 characters | RFC 7636 requirement |
| TR-008 | PKCE code challenge maximum length | 128 characters | Implementation limit |

---

## Data Model

### Authorization Request

```typescript
interface AuthorizationRequest {
  response_type: "code";           // Required, must be "code"
  client_id: string;               // Required, registered client ID
  redirect_uri: string;            // Required, must match registration
  scope: string;                   // Optional, space-delimited scopes
  state: string;                   // Required, CSRF protection
  code_challenge: string;          // Required (PKCE)
  code_challenge_method: "S256";   // Required, must be "S256"
}
```

### Token Request

```typescript
interface TokenRequest {
  grant_type: "authorization_code" | "refresh_token";
  code?: string;                   // Required for authorization_code
  refresh_token?: string;          // Required for refresh_token
  redirect_uri?: string;           // Required for authorization_code
  code_verifier?: string;          // Required for authorization_code (PKCE)
  client_id: string;               // Required
  client_secret?: string;          // Optional, for confidential clients
}
```

### Token Response

```typescript
interface TokenResponse {
  access_token: string;            // JWT access token
  token_type: "Bearer";           // Fixed value
  expires_in: number;              // Seconds until expiration
  refresh_token: string;           // Opaque refresh token
  scope: string;                   // Granted scopes
}
```

### Token Claims

```typescript
interface AccessTokenClaims {
  sub: string;                     // User ID
  iss: string;                     // Issuer (auth service URL)
  aud: string;                     // Audience (client ID)
  exp: number;                     // Expiration timestamp
  iat: number;                     // Issued at timestamp
  jti: string;                     // Unique token ID
  scope: string;                   // Granted scopes
  client_id: string;               // Client ID
}
```

---

## Interface Design

### Endpoints

| Method | Path | Description | FR Ref |
|--------|------|-------------|--------|
| GET | /oauth/authorize | Authorization endpoint | FR-001, FR-002 |
| POST | /oauth/token | Token endpoint | FR-001, FR-002 |
| POST | /oauth/token | Token refresh | FR-003 |
| POST | /oauth/introspect | Token introspection | FR-008 |
| POST | /oauth/revoke | Token revocation | - |

### Authorization Endpoint

**Request:**
```
GET /oauth/authorize?
  response_type=code&
  client_id=my-client&
  redirect_uri=https://app.example.com/callback&
  scope=read write&
  state=xyz123&
  code_challenge=E9Melhoa2OwvFrEMT...&
  code_challenge_method=S256
```

**Success Response:**
```
HTTP/1.1 302 Found
Location: https://app.example.com/callback?
  code=SplxlOBeZQQYbYS6WxSbIA&
  state=xyz123
```

**Error Response:**
```
HTTP/1.1 302 Found
Location: https://app.example.com/callback?
  error=invalid_request&
  error_description=Missing+required+parameter:+code_challenge&
  state=xyz123
```

### Token Endpoint

**Request:**
```
POST /oauth/token
Content-Type: application/x-www-form-urlencoded

grant_type=authorization_code&
code=SplxlOBeZQQYbYS6WxSbIA&
redirect_uri=https://app.example.com/callback&
code_verifier=dBjftJeZ4CVP-mB92K27uhbUJU1p1r_wW1gFWFOEjXk&
client_id=my-client
```

**Response:**
```json
{
  "access_token": "eyJhbGciOiJSUzI1NiIs...",
  "token_type": "Bearer",
  "expires_in": 900,
  "refresh_token": "tGzv3JOkF0XG5Qx2TlKWIA",
  "scope": "read write"
}
```

---

## Error Handling

| Error | Code | HTTP Status | Description | Handling |
|-------|------|-------------|-------------|----------|
| invalid_request | 400 | 400 | Malformed request | Log, return error |
| invalid_client | 401 | 401 | Client authentication failed | Log security event |
| invalid_grant | 400 | 400 | Invalid/expired code or refresh token | Log, clear client state |
| unauthorized_client | 400 | 400 | Client not authorized for grant type | Log security event |
| unsupported_grant_type | 400 | 400 | Grant type not supported | Return error |
| invalid_scope | 400 | 400 | Requested scope invalid | Return error, log |
| server_error | 500 | 500 | Unexpected server error | Log, alert on-call |
| temporarily_unavailable | 503 | 503 | Service temporarily down | Return error, retry |

---

## Security Considerations

1. **PKCE is mandatory**: All clients must use PKCE. Requests without `code_challenge` are rejected.

2. **State parameter**: Required for all authorization requests to prevent CSRF attacks.

3. **Short-lived codes**: Authorization codes expire after 10 minutes and can only be used once.

4. **Token rotation**: Refresh tokens are single-use. Using a consumed refresh token revokes all tokens.

5. **HTTPS only**: All OAuth endpoints require TLS 1.3 or higher.

6. **Rate limiting**: Token endpoint has aggressive rate limiting (100 req/min per client).

7. **Audit logging**: All authentication events logged with client ID, IP, and outcome.

8. **Secret rotation**: Client secrets must be rotated every 90 days.

---

## Dependencies

- **Implements**: ADR-001 (Hexagonal Architecture)
- **Depends on**: SPEC-CRYPTO-001 (Token encryption)
- **Enables**: SPEC-API-001 (API authentication middleware)

---

## Implementation Links

- phenotype-auth-ts: `src/oauth/`
- phenotype-auth-go: `oauth/`

---

## Change Log

| Date | Version | Changes | Author |
|------|---------|---------|--------|
| 2024-01-15 | 0.1.0 | Initial draft | @kooshapari |
| 2024-02-01 | 0.2.0 | Add PKCE requirements | @alice |
| 2024-03-15 | 0.3.0 | Add refresh token rotation | @bob |
| 2024-06-20 | 1.0.0 | Implemented, all tests pass | @kooshapari |
```

### F.2 Complete ADR Example: Database Selection

```markdown
---
id: ADR-042
title: PostgreSQL as Primary Database
status: accepted
date: 2024-03-15
author: @alice
tags: [database, storage, infrastructure]
affected_specs: [SPEC-DB-001, SPEC-DB-002]
affected_repos: [phenotype-api, phenotype-worker]
---

# ADR-042: PostgreSQL as Primary Database

## Status

Accepted - 2024-03-15

## Context

The Phenotype platform requires a primary relational database for:
- User data and authentication records
- Application state and configuration
- Audit logs and compliance data
- Time-series data (short-term retention)

We evaluated options based on:
- Operational complexity
- Team expertise
- Performance characteristics
- Cloud compatibility
- Cost

## Decision

We will use **PostgreSQL 15+** as our primary relational database.

### Rationale

PostgreSQL was selected over alternatives for these reasons:

1. **Rich feature set**: JSONB, full-text search, window functions, CTEs
2. **Proven reliability**: 25+ year track record, ACID compliance
3. **Team expertise**: 80% of engineers have PostgreSQL experience
4. **Cloud-native**: Excellent managed service options (RDS, Cloud SQL, AlloyDB)
5. **Extensibility**: PostGIS, TimescaleDB extensions available
6. **Cost**: Open source, no licensing fees

### Configuration

```yaml
# Standard configuration
database:
  type: postgresql
  version: "15.4"
  instance_class: db.r6g.xlarge
  storage: 500GB
  encryption: AES-256
  backup_retention: 30 days
  multi_az: true
  
  parameters:
    max_connections: 500
    shared_buffers: 8GB
    effective_cache_size: 24GB
    work_mem: 16MB
    maintenance_work_mem: 2GB
```

## Alternatives Considered

### MySQL 8.0

**Pros:**
- Wide adoption
- Good performance for simple queries
- Familiar syntax

**Cons:**
- Inferior JSON support (before 8.0)
- Less advanced query optimizer
- Replication limitations

**Verdict**: Rejected - PostgreSQL has superior feature set for our needs.

### Amazon Aurora

**Pros:**
- Managed service
- Excellent performance
- Aurora Serverless option

**Cons:**
- AWS lock-in
- Higher cost than RDS PostgreSQL
- Some PostgreSQL features not supported

**Verdict**: Rejected - Prefer cloud-agnostic solution. May use Aurora PostgreSQL compatibility mode.

### CockroachDB

**Pros:**
- Distributed by design
- PostgreSQL wire compatible
- Horizontal scaling

**Cons:**
- Higher operational complexity
- Smaller community
- Some PostgreSQL features missing

**Verdict**: Rejected - Overkill for current scale (100k users). Revisit at 10M+ users.

### MongoDB

**Pros:**
- Flexible schema
- Good document model for some use cases
- Strong horizontal scaling

**Cons:**
- Not ACID compliant (by default)
- Different query language
- Team less experienced

**Verdict**: Rejected - Need ACID guarantees for financial data.

## Consequences

### Positive

1. **Rich SQL feature set** enables complex queries without application-level processing
2. **JSONB support** allows hybrid relational/document patterns where needed
3. **Managed service options** reduce operational burden
4. **Active community** provides extensive tooling and documentation
5. **Strong consistency model** simplifies application logic

### Negative

1. **Vertical scaling limits** may require sharding at very high scale
2. **Write throughput** limited by single-primary replication
3. **Operational expertise** needed for self-hosted scenarios
4. **Migration complexity** from existing MySQL databases

### Mitigations

1. **Sharding strategy**: Design for future horizontal partition by tenant_id
2. **Read replicas**: Offload read traffic, plan for 5x read scaling
3. **Managed services**: Use RDS/Cloud SQL to minimize operational load
4. **Migration tooling**: Build and test migration scripts before cutover

## Related

- Supersedes: ADR-015 (MySQL for prototype phase)
- Related to: ADR-043 (Read replica strategy)
- Affected specs: SPEC-DB-001 (Database schema), SPEC-DB-002 (Connection pooling)

## Notes

PostgreSQL selection was approved by Architecture Team on 2024-03-10. All new services must use PostgreSQL unless explicitly exempted via ADR.

Migration of existing MySQL databases scheduled for Q3 2024.
```

### F.3 OpenAPI Example: Complete API Spec

```yaml
openapi: '3.1.0'
info:
  title: Phenotype User API
  version: '2.0.0'
  description: |
    User management API for the Phenotype platform.
    
    Implements: SPEC-USER-001, SPEC-AUTH-001
  
  x-phenotype-spec-id: SPEC-USER-001
  x-phenotype-domain: user
  x-phenotype-status: stable

servers:
  - url: https://api.phenotype.dev/v2
    description: Production
  - url: https://api.staging.phenotype.dev/v2
    description: Staging

security:
  - bearerAuth: []

paths:
  /users:
    get:
      operationId: listUsers
      summary: List users
      description: |
        Retrieves a paginated list of users.
        Supports filtering by status, role, and creation date.
      x-phenotype-fr: FR-001
      
      parameters:
        - name: status
          in: query
          schema:
            type: string
            enum: [active, inactive, pending]
        - name: role
          in: query
          schema:
            type: string
            enum: [admin, user, guest]
        - name: limit
          in: query
          schema:
            type: integer
            minimum: 1
            maximum: 100
            default: 20
        - name: offset
          in: query
          schema:
            type: integer
            minimum: 0
            default: 0
      
      responses:
        '200':
          description: Successful response
          content:
            application/json:
              schema:
                type: object
                properties:
                  data:
                    type: array
                    items:
                      $ref: '#/components/schemas/User'
                  pagination:
                    $ref: '#/components/schemas/Pagination'
        
        '401':
          $ref: '#/components/responses/Unauthorized'
        
        '403':
          $ref: '#/components/responses/Forbidden'
    
    post:
      operationId: createUser
      summary: Create user
      description: Creates a new user account.
      x-phenotype-fr: FR-002
      
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserCreate'
      
      responses:
        '201':
          description: User created
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        
        '400':
          $ref: '#/components/responses/BadRequest'
        
        '409':
          description: Email already exists

  /users/{id}:
    get:
      operationId: getUser
      summary: Get user
      description: Retrieves a specific user by ID.
      x-phenotype-fr: FR-003
      
      parameters:
        - name: id
          in: path
          required: true
          schema:
            type: string
            format: uuid
      
      responses:
        '200':
          description: User found
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
        
        '404':
          $ref: '#/components/responses/NotFound'
    
    patch:
      operationId: updateUser
      summary: Update user
      description: Partially updates user information.
      x-phenotype-fr: FR-004
      
      requestBody:
        required: true
        content:
          application/json:
            schema:
              $ref: '#/components/schemas/UserUpdate'
      
      responses:
        '200':
          description: User updated
          content:
            application/json:
              schema:
                $ref: '#/components/schemas/User'
    
    delete:
      operationId: deleteUser
      summary: Delete user
      description: Soft-deletes a user account.
      x-phenotype-fr: FR-005
      
      responses:
        '204':
          description: User deleted
        
        '404':
          $ref: '#/components/responses/NotFound'

components:
  schemas:
    User:
      type: object
      required:
        - id
        - email
        - status
        - created_at
      properties:
        id:
          type: string
          format: uuid
          example: "550e8400-e29b-41d4-a716-446655440000"
        email:
          type: string
          format: email
          example: "user@example.com"
        name:
          type: string
          example: "Jane Smith"
        status:
          type: string
          enum: [active, inactive, pending]
          example: "active"
        role:
          type: string
          enum: [admin, user, guest]
          example: "user"
        created_at:
          type: string
          format: date-time
        updated_at:
          type: string
          format: date-time
    
    UserCreate:
      type: object
      required:
        - email
        - name
      properties:
        email:
          type: string
          format: email
        name:
          type: string
        role:
          type: string
          enum: [admin, user, guest]
          default: user
    
    UserUpdate:
      type: object
      properties:
        name:
          type: string
        status:
          type: string
          enum: [active, inactive]
        role:
          type: string
          enum: [admin, user, guest]
    
    Pagination:
      type: object
      properties:
        limit:
          type: integer
        offset:
          type: integer
        total:
          type: integer
        has_more:
          type: boolean
  
  securitySchemes:
    bearerAuth:
      type: http
      scheme: bearer
      bearerFormat: JWT
  
  responses:
    Unauthorized:
      description: Authentication required
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    
    Forbidden:
      description: Insufficient permissions
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    
    BadRequest:
      description: Invalid request
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    
    NotFound:
      description: Resource not found
      content:
        application/json:
          schema:
            $ref: '#/components/schemas/Error'
    
    Error:
      type: object
      properties:
        error:
          type: string
        message:
          type: string
        code:
          type: string
```

---

## Appendix G: Performance Benchmarks

### G.1 Registry Query Performance

| Operation | Target | Notes |
|-----------|--------|-------|
| List all specs | &lt;50ms | 1000 specs |
| Filter by domain | &lt;30ms | Indexed |
| Search by keyword | &lt;100ms | Full-text |
| Trace query | &lt;200ms | Multi-repo |
| Coverage report | &lt;500ms | Full analysis |

### G.2 CI Validation Performance

| Check | Target | Command |
|-------|--------|---------|
| Registry validation | &lt;5s | `phenospecs validate` |
| Traceability scan | &lt;30s | `phenospecs trace scan` |
| Full coverage | &lt;60s | `phenospecs coverage` |
| Link checking | &lt;30s | `lychee` |

---

## Appendix H: Troubleshooting Guide

### H.1 Common Issues

#### Registry Validation Fails

**Symptom:** `phenospecs validate` reports errors

**Common causes:**
1. Missing required frontmatter fields
2. Duplicate spec IDs
3. Invalid domain references
4. Broken cross-references

**Solution:**
```bash
# See detailed errors
phenospecs validate --verbose

# Auto-fix where possible
phenospecs validate --fix
```

#### Traceability Gap

**Symptom:** Coverage report shows missing implementations

**Solution:**
```bash
# Find untraced specs
phenospecs trace untraced

# Check specific spec
phenospecs trace SPEC-XXX-NNN

# Add missing annotations in code, then re-scan
phenospecs trace scan
```

#### Spec Not Found

**Symptom:** `phenospecs list` doesn't show expected spec

**Common causes:**
1. Registry not updated after adding spec
2. File path incorrect in registry
3. YAML syntax error

**Solution:**
```bash
# Validate registry YAML
yamllint registry.yaml

# Check specific entry
phenospecs list --format yaml | grep SPEC-XXX-NNN
```

---

## Appendix I: Changelog

| Date | Version | Changes |
|------|---------|---------|
| 2026-04-04 | 1.0.0 | Initial comprehensive specification |

---

## Document Metadata

- **Version**: 1.0.0
- **Last Updated**: 2026-04-04
- **Authors**: Phenotype Platform Team
- **Reviewers**: Engineering Leads
- **Approval**: Accepted 2026-04-04
- **Review Cycle**: Quarterly
- **Next Review**: 2026-07-04

---

*This document is the authoritative specification for PhenoSpecs. For questions or clarifications, please open an issue or contact the Platform Team.*
