# fastmcp-asset

**Phenotype-pack asset handler for MCP servers.**

Discovers, builds, validates, and resolves dependencies of **phenotype packs**
— the file-based distribution format used by the Phenotype MCP fleet.

```text
version: 0.1.0
tier:    PhenoFastMCP-rust workspace crate
origin:  folded from KooshaPari/phenotype-mcp-asset after McpKit absorption
```

---

## What this crate does

A **phenotype pack** is a directory containing a `phenotype.toml` manifest and
a set of asset files (Python scripts, JS modules, WASM, config, data files).
This crate provides the Rust primitives an MCP server uses to:

| Operation | Method | Purpose |
|---|---|---|
| **Discover** | `AssetHandler::discover(path, recursive)` | Walk a directory and classify each file by extension |
| **Validate** | `AssetHandler::validate(pack_path)` | Parse `phenotype.toml` and check required fields |
| **Build** | `AssetHandler::build(source, output)` | Validate + resolve deps + produce a build artifact |
| **Resolve** | `AssetHandler::resolve_dependencies(pack_path)` | Enumerate declared deps (stub: marks all unresolved) |
| **Info** | `AssetHandler::get_info(pack_path)` | Read manifest, summarize pack metadata + size |

## When to use it

- You are building an **MCP server** that loads phenotype packs at runtime.
- You need to **discover and classify** assets in a directory tree.
- You need to **validate user-supplied `phenotype.toml`** manifests.
- You want a **typed Rust API** (`PackManifest`, `AssetInfo`, `DiscoveryResult`)
  rather than parsing TOML/JSON ad-hoc.

## When NOT to use it

- You don't have phenotype packs (use `fastmcp_rust` or another MCP framework
  for general MCP server development — pack handling is intentionally omitted
  by `fastmcp_rust` upstream).
- You need a remote-registry dependency resolver — the stub resolver marks
  all deps as unresolved until a registry implementation lands.
- You need a full build pipeline (compile/bundle/sign) — the stub builder
  validates the manifest and produces a placeholder artifact; the real
  pipeline is a future-feature backlog item. See `BUILD_STATUS.md`.

## Public API summary

```rust
use fastmcp_asset::{
    AssetHandler, AssetInfo, AssetType, BuildResult, DependencyResolution,
    DiscoveryResult, PackInfo, PackManifest, ValidationResult, VERSION,
};
```

Key types:

- **`AssetHandler`** — high-level façade; construct with `AssetHandler::new(root_dir)`
- **`PackInfo`** — summary of a pack (name, version, asset counts, total size, markdown formatter)
- **`AssetType`** — `PythonScript | JavaScriptModule | WasmModule | ContentPack | Config | Data | Unknown`
- **`AssetInfo`** — single discovered file (path, type, size, optional SHA-256 checksum)
- **`DiscoveryResult`** — aggregated discovery output (assets, total size, errors)
- **`PackManifest`**, **`AssetSpec`**, **`DependencySpec`** — TOML-bound manifest types
- **`ValidationResult`**, **`BuildResult`**, **`DependencyResolution`** — operation result types
- **`VERSION`** — `&str` equal to `CARGO_PKG_VERSION`

## 5-line quickstart

```rust
use fastmcp_asset::AssetHandler;

#[tokio::main]
async fn main() {
    let handler = AssetHandler::new("/path/to/packs");
    let info = handler.get_info("my-pack").await;
    println!("{}", info.map(|i| i.to_markdown()).unwrap_or_default());
}
```

For more, see the unit tests in `src/handler.rs` (they double as usage examples).

## Substrate tier

Per [ADR-023](https://github.com/KooshaPari/phenotype-handbook/blob/main/adr/2026-06-15/ADR-023-agent-effort-governance.md)
this crate is a **`pheno-*-lib`** — pure reusable library; language-specific
(Rust); single concern (file-based pack handling). Promotion to
`fastmcp-asset-sdk` (per ADR-042) requires 2+ polyglot consumers
(currently: 1, Rust only).

## License

MIT OR Apache-2.0 (dual-licensed, matching the Phenotype fleet convention).

## See also

- [`ORIGIN.md`](./ORIGIN.md) — full extraction and fold provenance
- [`BUILD_STATUS.md`](./BUILD_STATUS.md) — stub-module rationale and future-feature backlog
- [`CHANGELOG.md`](./CHANGELOG.md) — version history
