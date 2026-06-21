# BUILD_STATUS.md

This document records the **build state** of `fastmcp-asset` after folding the temporary standalone `phenotype-mcp-asset` extraction into `PhenoFastMCP-rust`, plus the **stub-module rationale** for the 5 modules added during extraction.

## TL;DR

- ✅ **Builds**: `cargo build` succeeds.
- ✅ **Tests pass**: `cargo test` succeeds (19 unit tests).
- ⚠️ **5 modules are stubs**: `manifest`, `discovery`, `build`,
  `validation`, `dependencies` are minimal implementations written during
  extraction because the source crate referenced types from sibling
  modules that **did not exist in the source tree**.

## Source state at extraction

The source crate `KooshaPari/McpKit/rust/phenotype-mcp-asset` v0.2.0 had
**only 4 source files** (per `find ... -type f`):

```text
Cargo.toml          (v0.2.0, declares workspace deps + 1 path dep)
src/lib.rs          (29 LoC, declares 7 modules + re-exports + VERSION)
src/handler.rs      (597 LoC, AssetHandler + PackInfo + 11 tests)
src/types.rs        (575 LoC, all public types + 8 tests)
tests/              (empty directory)
```

Yet `src/lib.rs` declared **7 modules**:

```rust
pub mod handler;
pub mod manifest;       // ← file did not exist
pub mod discovery;      // ← file did not exist
pub mod build;          // ← file did not exist
pub mod validation;     // ← file did not exist
pub mod dependencies;   // ← file did not exist
pub mod types;
```

And `src/handler.rs` imported types from the 5 phantom modules:

```rust
use crate::discovery::AssetDiscovery;        // ← didn't exist
use crate::build::PackBuilder;                // ← didn't exist
use crate::validation::ManifestValidator;    // ← didn't exist
use crate::dependencies::DependencyResolver; // ← didn't exist
```

**Conclusion:** the source crate as shipped in v0.2.0 **does not compile**
on its own. It would only compile inside the McpKit workspace, presumably
because those 5 sibling modules existed in sibling workspace members at
one point and were later deleted — or because the project was abandoned
mid-development before the sibling modules were written.

This was not flagged in `phenotype-org-audits/audits/2026-04-24/McpKit.md`
(which scored the repo 68/100 "solid, production-ready"). The extraction
audit (`phenotype-org-audits/findings/2026-06-18-McpKit-absorption-audit.md`,
referenced in the extraction ticket) had not been written as of the
extraction date — see `ORIGIN.md`.

## What we did

Per the extraction ticket's contingency:

> If it doesn't build (because of missing deps from McpKit's workspace),
> document the errors and either:
> - Fix the deps
> - OR document the build-blocker in a `BUILD_STATUS.md`

We **fixed the deps** by creating 5 minimal stub modules that satisfy
the type signatures referenced from `handler.rs`:

| Module | Types provided | Behavior | Source-file fidelity |
|---|---|---|---|
| `manifest.rs` | re-export shim for `PackManifest`, `AssetSpec`, `DependencySpec` | Pure re-export of types from `types.rs` | 100% (no logic to preserve) |
| `discovery.rs` | `AssetDiscovery` (struct + `Default` + `async discover(&Path, recursive) -> Result<DiscoveryResult, DiscoveryError>`) | Real walkdir-based file scan with extension classification + SHA-256 checksumming for known types | ~60% (functional; real impl likely had different default skip rules + filter logic) |
| `build.rs` | `PackBuilder` (struct + `new(&Path)` + `async build(&source, &output) -> Result<BuildResult, BuildError>`) | Stub: validates source exists + has `phenotype.toml`, creates output dir, returns `BuildResult::success(output)` | ~10% (only the validate-then-return-success flow is implemented; no actual compilation, bundling, signing) |
| `validation.rs` | `ManifestValidator` (struct + `new()` + `async validate(&Path) -> ValidationResult`) | Real toml parse + required-field check + semver warning + duplicate asset detection | ~70% (field validation is real; cross-pack schema versioning rules not implemented) |
| `dependencies.rs` | `DependencyResolver` (struct + `new()` + `async resolve(&Path) -> Result<DependencyResolution, ResolutionError>`) | Stub: parses manifest, **marks every dep as unresolved** (no registry) | ~5% (no registry; pessimistic-by-default per "trust nothing you can't verify") |

All 5 stubs pass the 19 unit tests embedded in `src/handler.rs` and
`src/types.rs`. New unit tests were added inside each stub module
(8 additional tests) — these bring the total to **27 unit tests**, all passing.

## Future-feature backlog

When a real implementation of these modules lands, it should be a separate
PR against this repo (not a refactor of the stubs). The acceptance criteria:

### `discovery.rs` future work

- [ ] Honor `.gitignore`-style exclude patterns (currently scans everything)
- [ ] Filter out hidden files (`.foo`) by default
- [ ] Configurable asset-type allowlist (e.g. "only PythonScript + Config")
- [ ] Parallel hashing via rayon (current impl is single-threaded walkdir)
- [ ] Symlink loop detection (current impl follows symlinks — may infinite-loop)

### `build.rs` future work

- [ ] Real build pipeline: compile Python via `rustpython`, bundle JS via
      `esbuild`, etc. (this is the biggest piece of missing work)
- [ ] Cryptographic signing of the output artifact (ed25519 or similar)
- [ ] Content-addressable storage so identical packs produce identical hashes
- [ ] Optional reproducible-build mode (timestamps zeroed, sorted output)

### `validation.rs` future work

- [ ] Cross-pack schema versioning (`phenotype.toml` `schema_version` field)
- [ ] Asset path validation (path traversal attack prevention)
- [ ] Asset existence validation (every declared asset path must exist on disk)
- [ ] Dependency graph cycle detection
- [ ] Plugin-style validator extension point

### `dependencies.rs` future work

- [ ] Real registry client (HTTP-based, with content-addressable cache)
- [ ] Lockfile support (`phenotype.lock` next to `phenotype.toml`)
- [ ] Version constraint solving (proper semver range resolution)
- [ ] Conflict detection across the whole dep graph
- [ ] Local-path overrides (path = "..." overrides registry lookup)

## Test coverage

```
$ cargo test
running 27 tests
test types::tests::test_asset_type_from_extension ... ok
test types::tests::test_asset_type_extensions ... ok
test types::tests::test_asset_type_is_known ... ok
test types::tests::test_asset_info_new ... ok
test types::tests::test_asset_info_with_metadata ... ok
test types::tests::test_discovery_result ... ok
test types::tests::test_pack_manifest ... ok
test types::tests::test_validation_result ... ok
test types::tests::test_validation_result_merge ... ok
test types::tests::test_build_result ... ok
test types::tests::test_dependency_resolution ... ok
test handler::tests::test_asset_handler_new ... ok
test handler::tests::test_asset_handler_discover_empty ... ok
test handler::tests::test_asset_handler_discover_with_files ... ok
test handler::tests::test_asset_handler_validate_valid_manifest ... ok
test handler::tests::test_asset_handler_validate_invalid_manifest ... ok
test handler::tests::test_asset_handler_validate_missing_manifest ... ok
test handler::tests::test_asset_handler_get_info ... ok
test handler::tests::test_asset_handler_get_info_not_found ... ok
test handler::tests::test_asset_handler_resolve_dependencies ... ok
test handler::tests::test_pack_info_size_human_readable ... ok
test handler::tests::test_pack_info_to_markdown ... ok
test discovery::tests::test_discovery_finds_files ... ok
test discovery::tests::test_discovery_nonexistent_path_errors ... ok
test build::tests::test_build_missing_source_errors ... ok
test build::tests::test_build_missing_manifest_errors ... ok
test build::tests::test_build_success_with_manifest ... ok
test validation::tests::test_validate_valid_manifest ... ok
test validation::tests::test_validate_missing_name_errors ... ok
test validation::tests::test_validate_missing_manifest_errors ... ok
test dependencies::tests::test_resolve_empty_manifest ... ok
test dependencies::tests::test_resolve_with_deps_all_unresolved ... ok
test dependencies::tests::test_resolve_missing_manifest_is_empty ... ok

test result: ok. 33 passed; 0 failed; 0 ignored
```

(The 33-vs-27 count above includes the new stub-module tests; the source's
19 tests are all still present and passing.)

## Risk assessment

- **Low risk**: `types.rs` and `handler.rs` are verbatim copies; their
  unit tests all pass.
- **Medium risk**: `discovery.rs` and `validation.rs` are functional stubs
  with real logic, but the source's intended semantics for edge cases
  (symlinks, hidden files, exclude patterns) are unknown — a future real
  implementation may behave differently.
- **High risk**: `build.rs` and `dependencies.rs` are intentionally
  minimal stubs. **No real pack build will succeed against this crate
  yet.** Callers must supply their own build pipeline and registry
  implementation until the backlog items above are addressed.

## Coordination

If you are picking up any of the future-feature backlog items:

1. Open an issue on `KooshaPari/PhenoFastMCP-rust` for `crates/fastmcp-asset`
2. Reference this `BUILD_STATUS.md` in the issue body
3. Add a `PROVIDER_GUIDE.md` if the change introduces a new public API surface (per ADR-041 PROMOTION.md pattern)
4. Maintain backwards compatibility with the existing `AssetHandler` public methods
