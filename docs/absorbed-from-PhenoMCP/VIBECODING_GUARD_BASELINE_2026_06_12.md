# VIBECODING_GUARD_BASELINE_2026_06_12.md

Protected paths for PhenoMCP-cheap (vibecoding-guard do-not-touch zones).

1. `Cargo.lock` — Rust dependency lockfile; regenerating it silently changes the transitive dependency graph
2. `deny.toml` — Dependency audit and license policy; changes here affect supply-chain security
3. `go.mod` — Go module manifest; controls the Go binding dependency graph
4. `package-lock.json` — Node dependency lockfile; changes silently alter the TS binding dependency graph
5. `pyproject.toml` — Python project manifest and tool configuration; changes affect the Python binding build
