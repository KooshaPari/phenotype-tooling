# phenotype-dep-guard — Archived

This repository has been productized as a security operations tool.

## Migration

**Source**: `phenotype-dep-guard/`
**Target**: `tools/dep-guard/`
**Package name**: `dep-guard` (neutral)

## Changes

- Package renamed from `phenotype-dep-guard` to `dep-guard`
- Moved to `tools/` directory for CLI/tool repos
- Module name: `dep_guard` (from `phenotype_dep_guard`)
- Updated repository URL to `github.com/phenotype-dev/dep-guard`

## Usage

After migration, use:

```bash
pip install tools/dep-guard
dep-guard analyze <package>
```

## Documentation

See `tools/dep-guard/CLAUDE.md` for architecture and API details.

---

*Archived: 2026-03-26*
*Phase 6 Batch 4*
