# SPEC: phenotype-gates

## Meta

- **ID**: phenotype-gates-001
- **Title**: phenotype-gates — Policy-as-code gate engine
- **Created**: 2026-06-16
- **State**: scaffold
- **Version**: 0.0.0
- **Language**: Rust

## Overview

`phenotype-gates` is the policy-as-code gate engine for the Phenotype org. It
enforces the shared workflow-hygiene contract (timeouts, pinned action SHAs,
`deny.toml` presence, MSRV baseline) across adopter repos via a single
reusable workflow.

The repo is currently in **scaffold** state; this SPEC records the intended
shape and the registry wiring that makes the project discoverable inside the
Phenotype ecosystem.

## Registry Wiring

This project is registered in the Phenotype registry system. The local
registry entry lives at `projects/phenotype-gates.json` (consumed by the
Phenotype build tooling) and is mirrored upstream in:

- **Registry index:** [KooshaPari/phenotype-registry](https://github.com/KooshaPari/phenotype-registry)
- **Master index file:** `registry.json`
- **Project entry (upstream):** `projects/phenotype-gates.json`

See [`projects/phenotype-gates.json`](./projects/phenotype-gates.json) for
the canonical metadata (`status=scaffold`, `type=tool`, `language=rust`).

## Components

| Component | Path | Responsibility | Status |
|-----------|------|----------------|--------|
| Reusable workflow | `.github/workflows/org-gates.yml` | Shared org-wide gate (timeout, pinned SHAs, deny.toml, MSRV) | active |
| Pilot adopter doc | `docs/adopters/focalpoint.md` | Records FocalPoint as the first adopter | active |
| Registry entry | `projects/phenotype-gates.json` | phenoregistry wiring (this file) | scaffold |

## References

1. [Phenotype Registry (master index)](https://github.com/KooshaPari/phenotype-registry)
2. [PhenoSpecs](https://github.com/KooshaPari/PhenoSpecs) — specifications
3. [PhenoHandbook](https://github.com/KooshaPari/PhenoHandbook) — patterns
4. [HexaKit](https://github.com/KooshaPari/HexaKit) — templates

---

*State: scaffold — see registry entry for upstream status.*
