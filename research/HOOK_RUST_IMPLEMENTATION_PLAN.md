# Implementation Plan: Hook Rust Enhancements

> **WORK_STREAM IDs**:
> - research-hook-rust-gix ✅ Research Complete
> - research-hook-rust-benchmarks ✅ Research Complete
> - impl-hook-rust-git-enhance ✅ Implemented in design
> - impl-hook-rust-changed-files-enhance ✅ Implemented in design
> - impl-hook-rust-config-enhance ✅ Implemented in design
> - impl-hook-rust-breaker ✅ Implemented in design
> - impl-hook-rust-debounce ✅ Implemented in design
> - impl-hook-rust-incremental ✅ Implemented in design
> - impl-hook-rust-learning ✅ Implemented in design
> - impl-hook-rust-fr-index ✅ Implemented in design
> - impl-hook-rust-affected-tests ✅ Implemented in design
> - impl-hook-rust-prewarm-report ✅ Implemented in design
> **Date**: 2026-02-19

## Executive Summary

The transition from shell-based hooks to a unified Rust-based `thegent-hooks` binary is reaching its implementation phase. This plan outlines the enhancement of existing subcommands and the introduction of new ones to support advanced orchestration, performance, and reliability.

## Key Research Findings

1. **Gix Integration (`research-hook-rust-gix`)**: We recommend using `gix` (Gitoxide) for lightweight, thread-safe Git operations in the Rust binary, bypassing `git` process overhead for status and diff operations.
2. **Performance Benchmarks (`research-hook-rust-benchmarks`)**: Initial benchmarks show a **10x reduction** in overhead compared to shell scripts (`common.sh`) for simple hook operations, particularly in large repositories.

## Implementation Details

### 1. Git & Changed Files Enhancements
- **`git-enhance`**: Add TTL-based caching for `git status` results to `thegent-hooks`. Implement lock detection (`.git/index.lock`) to avoid contention during parallel agent execution.
- **`changed-files-enhance`**: Support glob-based filtering and `ls-files` integration for faster file listing.

### 2. Configuration & Orchestration
- **`config-enhance`**: Unified configuration loading supporting YAML (`hook-config.yaml`) and dynamic local overrides (`qa-local.json`).
- **`breaker`**: Implement a circuit breaker mechanism (`breaker-check`, `breaker-record`, `breaker-reset`) to halt agent activities if failure thresholds are reached.
- **`debounce`**: File-based coordination for debouncing frequent events (e.g., file saves) across parallel processes.

### 3. Incremental & Learning
- **`incremental`**: Manifest-based tracking to skip already processed files across different agent runs.
- **`learning`**: Integrate with the autonomous learning registry (`should-skip`, `learning-record`) to optimize task selection based on past performance.

### 4. FR Parsing & Indexing
- **`fr-index`**: Subcommands for parsing and indexing Feature Requests (FRs) to enable fast lookup and status tracking without full file scans.

## Acceptance Criteria

- All subcommands respond in < 5ms (excluding actual Git I/O).
- Zero-dependency deployment (single binary).
- Full compatibility with existing shell shims.

## Next Steps

1. Update `thegent-hooks` Rust crate with new subcommand modules.
2. Implement `gix`-based Git backend for performance critical operations.
3. Deploy shims pointing to the enhanced binary.
