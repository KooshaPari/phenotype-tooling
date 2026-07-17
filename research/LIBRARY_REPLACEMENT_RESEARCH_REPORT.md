# Research Report: Library Replacement & Consolidation

> **WORK_STREAM IDs**:
> - research-library-diskcache ✅ Research Complete
> - research-library-psutil ✅ Research Complete
> - research-library-md5-sha256 ✅ Research Complete
> - research-library-tomlkit ✅ Research Complete
> - research-library-env-settings ✅ Research Complete
> - research-library-http ✅ Research Complete
> - research-library-watchdog ✅ Research Complete
> **Date**: 2026-02-19

## Executive Summary

The audit of custom implementations versus standard libraries is complete. We have identified several key areas where custom code can be replaced with robust, well-maintained libraries to improve reliability, performance, and maintainability.

## Key Findings

1. **Caching (`diskcache`)**: Custom file-based caching and TTL logic in `execution.py` and `governance/` will be replaced with `diskcache`, providing atomic operations and SQLite-backed persistence.
2. **Monitoring (`psutil`)**: Subprocess calls to `ps` and manual `/proc` parsing will be replaced with `psutil` for cross-platform resource monitoring (CPU, MEM, FD).
3. **Hashing (SHA256)**: Fragmented usage of MD5 and SHA1 will be unified to SHA256 across all audit logs, MAIF artifacts, and cache keys for security and consistency.
4. **Configuration (`tomlkit`)**: Custom TOML/YAML parsing will be migrated to `tomlkit` (for comment-preserving TOML) or `ruamel.yaml` to ensure round-trip integrity of user configs.
5. **Settings (Pydantic)**: Scattered `os.environ.get` calls (15+ files) will be consolidated into the `ThegentSettings` class using `pydantic-settings` for type-safe, validated configuration.

## Implementation Status

- **Audit**: Deep file-level audit complete (47 sections).
- **Selection**: Primary and fallback libraries identified for all categories.
- **Plan**: Consolidated migration plan exists in `LIBRARY_REPLACEMENT_CONSOLIDATED.md`.

## Next Steps

1. Install `diskcache`, `psutil`, and `pydantic-settings` dependencies.
2. Begin Phase 1 migration: HTTP (`httpx`) and Retry (`tenacity`).
3. Refactor `ThegentSettings` to absorb all environmental variables.

## Reference

Detailed research available in [LIBRARY_REPLACEMENT_AUDIT_DEEP.md](./LIBRARY_REPLACEMENT_AUDIT_DEEP.md) and [LIBRARY_REPLACEMENT_CONSOLIDATED.md](./LIBRARY_REPLACEMENT_CONSOLIDATED.md).
