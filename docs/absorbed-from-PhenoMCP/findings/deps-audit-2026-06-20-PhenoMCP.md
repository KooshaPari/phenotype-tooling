# Dependency Audit + DRY — PhenoMCP 2026-06-20

## Scope

- **Project**: PhenoMCP at `/Users/kooshapari/CodeProjects/Phenotype/repos/PhenoMCP`
- **Stacks**: Rust (primary), Python (bindings)
- **Tools**: `cargo tree --workspace`, `cargo metadata`, `Cargo.lock` analysis

---

## 1. Duplicate Dependency Versions (Transitive)

These are crates pulled in at multiple versions by the dependency tree (mostly through `surrealdb` and its transitive deps). Not directly controllable from workspace manifests, but worth tracking:

| Crate | Versions Present | Source |
|-------|-----------------|--------|
| `rand` | 0.8.6, 0.9.4 | surrealdb transitive / geo / diskann |
| `hashbrown` | 0.12.3, 0.14.5, 0.15.5, 0.16.1, 0.17.1 | surrealdb / indexmap / quick_cache |
| `syn` | 1.0.109, 2.0.117 | proc-macro eco (1.x legacy, 2.x current) |
| `getrandom` | 0.2.17, 0.3.4, 0.4.2 | different rand versions / tempfile |
| `generic-array` | 0.12.4, 0.13.3, 0.14.7 | digest / crypto legacy |
| `itertools` | 0.11.0, 0.13.0, 0.14.0 | surrealdb / geo / object_store |
| `rand_chacha` | 0.3.1, 0.9.0 | paired with rand versions |
| `rand_core` | 0.6.4, 0.9.5 | paired with rand versions |
| `rstar` | 0.8.4, 0.9.3, 0.10.0, 0.11.0, 0.12.2 | geo / surrealdb |
| `heapless` | 0.6.1, 0.7.17, 0.8.0 | surrealdb / rstar |
| `hash32` | 0.1.1, 0.2.1, 0.3.1 | surrealdb / heapless |
| `phf` / `phf_generator` / `phf_macros` / `phf_shared` | 0.11.3, 0.13.1 | surrealdb (html/css parsing) |
| `windows-*` | multiple minor versions | surrealdb sys deps |
| `wit-bindgen` | 0.51.0, 0.57.1 | wasm deps |
| `foldhash` | 0.1.5, 0.2.0 | hashbrown versions |
| `cpufeatures` | 0.2.17, 0.3.0 | crypto deps |
| `untrusted` | 0.7.1, 0.9.0 | webpki versions |
| `r-efi` | 5.3.0, 6.0.0 | sys deps |
| `heck` | 0.4.1, 0.5.0 | proc-macro eco |

**Impact**: `cargo-deny` (configured in `deny.toml`) warns on multiple versions. Most are unavoidable with surrealdb 3.1.5's current dependency tree. When surrealdb updates its deps, many of these will consolidate.

---

## 2. Unused / Redundant Dependencies

| Dependency | Location | Status |
|-----------|----------|--------|
| `clap-ext` | Root `[workspace.dependencies]` | **Unused** — declared but no crate references it |
| `anyhow` | `phenotype-surrealdb` | Used (legacy helpers) |
| `surrealdb = "=3.1.5"` | `phenotype-surrealdb` | Declared but actual impl delegates to in-memory stub (noted in TODO) |
| Root `pheno-mcp` package has `[[bin]]` with 0 dependencies | Root Cargo.toml | The binary is a stub (`println!("PhenoMCP")`) |
| `pheno-mcp-defs` and `tool-registry` | Separate workspaces | Not in main workspace; have their own `[workspace]` roots |

---

## 3. DRY Opportunities — Dependency Declarations

The following dependencies are declared identically across multiple crates and could be centralized via `[workspace.dependencies]`:

| Dep | Crates | Count |
|-----|--------|-------|
| `serde = { version = "1.0", features = ["derive"] }` | ports, meilisearch, qdrant, surrealdb, defs, tool-registry | **6x** |
| `serde_json = "1.0"` | ports, meilisearch, qdrant, surrealdb, defs, tool-registry | **6x** |
| `thiserror = "2.0"` | ports, meilisearch, qdrant, surrealdb, defs, tool-registry | **6x** |
| `async-trait = "0.1"` | ports, meilisearch, qdrant, surrealdb | **4x** |
| `tokio = { version = "1.44", features = ["full"] }` | meilisearch, qdrant, surrealdb | **3x** |
| `tokio = { version = "1.44", features = ["sync"] }` | ports | **1x** |
| `tracing = "0.1"` | meilisearch, qdrant, surrealdb | **3x** |
| `tokio-test = "0.4"` (dev) | ports, meilisearch, qdrant, surrealdb | **4x** |
| `reqwest = { version = "0.13", ... }` | meilisearch, qdrant | **2x** (identical declaration) |

---

## 4. DRY Opportunities — Code Patterns

### 4a. HTTP Client Construction Pattern
`pheno-meilisearch` and `pheno-qdrant` both create HTTP clients with nearly identical patterns:
- `Client::new()` with default config
- Trim trailing `/` from URL
- Optional API key auth header injection
- Health check endpoints
- `.map_err(|e| ErrorType::Http(e.to_string()))` on every request

**Suggestion**: Extract a shared `HttpClient` helper in `pheno-ports` or a new `pheno-http` crate.

### 4b. Error Mapping Pattern
Both adapters define `to_port_err()` functions mapping private error types to `SearchPortError`:
- `pheno-meilisearch/src/lib.rs:209-215` — `fn to_port_err(e: MeilisearchError) -> SearchPortError`
- `pheno-qdrant/src/lib.rs:344-349` — `fn to_port_err(e: QdrantError) -> SearchPortError`

### 4c. SearchPort Implementation Boilerplate
Both crates implement the same trait (`SearchPort`) with identical method signatures and similar delegation patterns.

### 4d. Edition Inconsistency
- Main workspace uses `edition = "2024"`
- `pheno-mcp-defs` and `tool-registry` use `edition = "2021"`
- Both of those crates are standalone workspaces, not part of the main workspace

### 4e. CI / Config Duplication
- `Taskfile.yml` and `Justfile` both define the same build/test/lint targets (build, test, lint, fmt, audit, grade)
- `grade.sh` is the authoritative CI run script referenced by both task runners
- Clippy config and deny config are centralized (good)

---

## 5. Recommendations

1. **Highest Priority**: Consolidate shared deps (serde, serde_json, thiserror, async-trait, tokio) into `[workspace.dependencies]` — reduces declaration count from 6x to 1x per dep.
2. **Medium**: Investigate bringing `pheno-mcp-defs` and `tool-registry` into the main workspace with edition2024.
3. **Medium**: Remove unused `clap-ext` from workspace deps or wire it into the binary.
4. **Low**: Monitor surrealdb 3.1.x updates for transitive dep consolidation.
5. **Low**: Evaluate shared HTTP client abstraction for `pheno-meilisearch` and `pheno-qdrant`.

---

## 6. Fix Applied

This audit was accompanied by:
- Centralized `serde`, `serde_json`, `thiserror`, `async-trait`, `tracing`, `tokio`, and `tokio-test` into `[workspace.dependencies]`
- Updated all 4 workspace member crates to reference workspace deps
- Reduced redundant declarations from 32+ individual entries to 8 workspace-level entries
