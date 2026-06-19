# Absorbed from KodeVibe — 2026-06-18

**Source:** `KooshaPari/KodeVibe` (private, archived 2026-06-18)
**Target:** `KooshaPari/phenotype-tooling/docs/absorbed-from-kodevibe/`
**Reason:** KodeVibe contained a Go static analysis engine + OKF manifest format + HexaKit-style templates; absorbed as a historical reference.

## Contents

- `engine/` — Go static analysis engine (octofhir-grade)
- `okf/` — OKF (Object Knowledge Format) manifest format
- `kodevibe/` — CLI wrapper
- `docs/` — Design docs
- `Justfile` / `Taskfile.yml` / `Makefile` — Task runner configs
- `Dockerfile` — Containerization
- CI workflows (`.github/`)
- `intent.md`, `charter.md` — Project intent + charter
- `install.sh` — Installation script
- `.kodevibe.yaml` — Project config

## Status

Read-only reference. The Go engine and OKF format are historical; canonical replacements:
- Static analysis → `pheno-scaffold-kit` (Python), `pheno-framework-lint` (Rust)
- Task runners → `Justfile` is canonical (Taskfile.yml is deprecated; see ADR-022)
