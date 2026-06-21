# Changelog

All notable changes to `fastmcp-asset` will be documented here.
Format follows [Keep a Changelog](https://keepachangelog.com/en/1.1.0/).
This project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] — 2026-06-18

### Changed — **Folded into PhenoFastMCP-rust**

This is the **initial folded release** of `fastmcp-asset` as a
`PhenoFastMCP-rust` workspace crate. Prior to folding, this code lived as a workspace
member of [`KooshaPari/McpKit`](https://github.com/KooshaPari/McpKit)
(`rust/phenotype-mcp-asset`, v0.2.0).

- **Renamed**: crate name folded to `fastmcp-asset` for framework-lane consistency
- **Version reset**: workspace crate starts at 0.1.0 after fold
- **Repository**: `KooshaPari/PhenoFastMCP-rust` (`crates/fastmcp-asset`)
- **License**: dual-licensed `MIT OR Apache-2.0` (was `MIT` only in source)
- **Substrate tier**: reclassified as `pheno-*-lib` per ADR-023
- **Deps**: removed unused `phenotype-mcp-framework = { path = ... }` dep;
  uses workspace dependency inheritance in `PhenoFastMCP-rust`
- **lib.rs**: dropped phantom module declarations for `manifest`,
  `discovery`, `build`, `validation`, `dependencies` — added 5 minimal stub
  modules so the crate compiles standalone. See `BUILD_STATUS.md`.

### Source preserved verbatim

- `src/types.rs` — 575 LoC, 9 unit tests, all public types and their impls
- `src/handler.rs` — 597 LoC, 11 unit tests, `AssetHandler` + `PackInfo`
- `src/lib.rs` — module re-exports + `VERSION` constant (with phantom-module
  declarations removed; see above)

### Why this extraction

`fastmcp-asset` is the McpKit asset crate folded into the
PhenoFastMCP Rust family. Pack handling is intentionally omitted by
`fastmcp_rust` upstream (Phenotype-pack asset handling is fleet-specific
and not part of the upstream MCP model). Per ADR-023 (app-substrate
placement), reusable underlying capabilities belong in `pheno-*-lib` /
`phenotype-*-sdk` / `phenotype-*-framework` / federated service. A pack
handler is a textbook `pheno-*-lib`.

Full provenance: [`ORIGIN.md`](./ORIGIN.md)

## [0.2.0] — (pre-extraction, source: McpKit)

Prior history lived in [`KooshaPari/McpKit`](https://github.com/KooshaPari/McpKit).
See the `CHANGELOG.md` in that repo for the 0.1.x → 0.2.0 evolution.

[0.3.0]: https://github.com/KooshaPari/phenotype-mcp-asset/releases/tag/v0.3.0
[0.2.0]: https://github.com/KooshaPari/McpKit/tree/rust/phenotype-mcp-asset
