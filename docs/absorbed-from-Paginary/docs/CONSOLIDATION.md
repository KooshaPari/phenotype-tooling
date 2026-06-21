# Paginary Content Consolidation Map

This document tracks the consolidation of source repositories into Paginary apps.

## Overview

Paginary is a federated documentation hub that brings together content from multiple Phenotype repositories. Content is **copied, not moved** — originals remain in source repos for continued evolution.

## Source Repository Mapping

### 1. PhenoHandbook → apps/handbook/

**Source**: `/Users/kooshapari/CodeProjects/Phenotype/repos/PhenoHandbook`

**Content Scope**:
- Organizational playbooks and operational guides
- Governance procedures and decision frameworks
- Team workflows and communication standards
- Onboarding and training materials

**Status**: ⧖ Pending initial content pull

**Notes**:
- Directory structure preserved during copy
- `.vitepress/` config managed at Paginary root
- Sidebar nav updated in root `vitepress.config.ts`

---

### 2. PhenoSpecs → apps/specs/

**Source**: `/Users/kooshapari/CodeProjects/Phenotype/repos/PhenoSpecs`

**Content Scope**:
- Feature specifications (PRDs, FRs)
- Architecture Decision Records (ADRs)
- System design documents and diagrams
- Project plans and work breakdowns

**Status**: ⧖ Pending initial content pull

**Notes**:
- Specs organized by project and feature area
- Mermaid diagrams embedded
- Maintains version history links to source

---

### 3. phenoXdd → apps/xdd/

**Source**: `/Users/kooshapari/CodeProjects/Phenotype/repos/phenoXdd` (or similar)

**Content Scope**:
- Test-Driven Development (TDD) patterns
- Behavior-Driven Development (BDD) practices
- QA governance and quality gates
- Smart contract verification patterns

**Status**: ⧖ Pending initial content pull

**Notes**:
- Advanced workflows remain in source repo
- Paginary contains synthesis and guides
- Links to full QA governance spec included

---

### 4. phenotype-journeys → apps/journeys/

**Source**: `/Users/kooshapari/CodeProjects/Phenotype/repos/phenotype-journeys`

**Content Scope**:
- User journey flows (feature, onboarding, integration, operational)
- Persona definitions and user research
- Acceptance criteria and journey completion definitions
- Alternative paths and edge case documentation

**Status**: ⧖ Pending initial content pull

**Notes**:
- Journey analytics and metrics remain in source
- Paginary contains journey maps and workflow diagrams
- Links to detailed analytics and tracking

---

## Merger Candidates (Flagged for Evaluation)

### phenotype-auth-ts

**Status**: ⧖ HOLD for evaluation

**Rationale**: Could become a docs-subject (auth design, patterns, implementation guides). Requires review to determine if:
1. Content should be extracted into Specs
2. Implementation guide should go to Handbook
3. OR remain a standalone project repo

**Decision Deferred**: Awaiting user direction

---

## Content Pull Workflow

For each source repo consolidation:

1. **Source Audit** — Map structure and file count
2. **Copy Phase** — `cp -r source-repo/docs/* apps/<name>/`
3. **VitePress Config** — Update sidebar nav, fix relative links
4. **Verification** — `bun run build` confirms rendering
5. **Documentation** — Update this CONSOLIDATION.md with status

---

## Content Update Policy

- Source repos remain canonical
- Paginary content is **read-only federation**
- Updates flow source → Paginary (manual pull, periodic automated sync)
- No content modifications in Paginary apps (they reflect source exactly)

---

## Known Gaps

| Item | Status | Notes |
|------|--------|-------|
| Handbook initial pull | ⧖ Pending | Awaiting source repo structure scan |
| Specs initial pull | ⧖ Pending | Awaiting source repo structure scan |
| XDD initial pull | ⧖ Pending | Source repo location TBD |
| Journeys initial pull | ⧖ Pending | Awaiting source repo structure scan |
| phenotype-auth-ts eval | ⧖ Held | User decision pending |

---

## Next Steps

1. Scan each source repo for `/docs` or content directory
2. Run initial copy phase for all four main apps
3. Verify `bun run build` succeeds across all sites
4. Update status to ✅ Complete
5. Schedule periodic content sync (monthly or on-demand)
