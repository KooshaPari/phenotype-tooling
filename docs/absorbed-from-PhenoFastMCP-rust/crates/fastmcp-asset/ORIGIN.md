# ORIGIN — extraction provenance

This crate was extracted from McpKit into a temporary standalone repo, then folded into `PhenoFastMCP-rust/crates/fastmcp-asset`. This document records the full chain of custody.

## Source

| Field | Value |
|---|---|
| **Source repo** | [`KooshaPari/McpKit`](https://github.com/KooshaPari/McpKit) |
| **Source status (as of extraction)** | **ARCHIVED** (read-only on GitHub) |
| **Source path** | `rust/phenotype-mcp-asset/` |
| **Source version** | **v0.2.0** |
| **Source commit** | (McpKit HEAD at extraction time — not separately recorded; the source repo is read-only) |
| **License** | MIT (source) → MIT OR Apache-2.0 (this crate) |
| **Extraction date** | 2026-06-18 |
| **Extracted by** | forge subagent (per McpKit absorption audit, L5-109) |

## Destination

| Field | Value |
|---|---|
| **Temporary destination repo** | `KooshaPari/phenotype-mcp-asset` |
| **Final folded home** | `KooshaPari/PhenoFastMCP-rust` `crates/fastmcp-asset` |
| **Folded version** | `fastmcp-asset` v0.1.0 inside the Rust FastMCP workspace |
| **Substrate tier** | `pheno-*-lib` per ADR-023 |

## GitHub repo creation — ✅ **CREATED**

The `gh repo create` command **succeeded** despite an earlier `gh auth status`
warning about the token being "invalid" — the token evidently has sufficient
scope for `repo` create + push operations even if it can't authenticate for
status checks.

```text
$ gh repo create KooshaPari/phenotype-mcp-asset --public \
    --description "Phenotype-pack asset handler for MCP servers (extracted from McpKit)" \
    --source . --remote origin --push

https://github.com/KooshaPari/phenotype-mcp-asset
To github.com:KooshaPari/phenotype-mcp-asset.git
 * [new branch]      HEAD -> main
branch 'main' set up to track 'origin/main'.
```

**Temporary repository:** <https://github.com/KooshaPari/phenotype-mcp-asset> — superseded by `PhenoFastMCP-rust/crates/fastmcp-asset`.

Created 2026-06-18 12:17:01 UTC, public, commit `d47bdb2` on `main`.
Full source tree, docs (README, CHANGELOG, ORIGIN, BUILD_STATUS), and all
33 unit tests are on the remote.

## Why this extraction

Per the McpKit absorption audit (ADR-017 retire pattern, ADR-023 substrate
placement):

1. **`phenotype-mcp-asset` is the ONLY McpKit Rust crate with no equivalent
   in the PhenoFastMCP family.** The other 4 McpKit members
   (`phenotype-mcp-core`, `phenotype-mcp-framework`, `phenotype-mcp-fast`,
   `phenotype-mcp-fast-macros`) are absorbed into `pheno-mcp-router` (per
   ADR-013) and `phenotype-mcp-sdk-{cs,go,py,ts}`. Pack handling is
   intentionally omitted by `fastmcp_rust` upstream.
2. **Per ADR-023 Rule 3**, reusable underlying capabilities go to
   `pheno-*-lib`, `phenotype-*-sdk`, `phenotype-*-framework`, or federated
   service. A pack handler is a textbook `pheno-*-lib`.
3. **Per ADR-042 (substrate graduation path)**, this crate can be promoted
   to `phenotype-mcp-asset-sdk` once it has 2+ polyglot consumers.

## Audit reference

The original McpKit absorption audit is the L5-109 (4-repo retirement)
batch. The audit doc referenced in the extraction ticket —
`phenotype-org-audits/findings/2026-06-18-McpKit-absorption-audit.md` —
**does not exist at the expected path** as of 2026-06-18 extraction time.
The closest existing artifacts are:

- `phenotype-org-audits/audits/2026-04-24/McpKit.md` — older fleet-wide
  audit (April 2026), scored McpKit 68/100 (solid, production-ready).
  **Note: this audit was overly optimistic** — it scored 7/10 on test
  coverage (claimed 35 test files) and 7/10 on code maturity, but the
  actual state at extraction was 19 unit tests across only 2 source files
  (`handler.rs`, `types.rs`) with **5 phantom module declarations**
  (manifest, discovery, build, validation, dependencies) referencing
  types that didn't exist in the source tree. The audit's "~110 LoC,
  0 tests, file-based pack handler" line-item claim is closer to the
  ground truth but still off (actual: ~1,172 LoC, 19 tests).
- `findings/2026-06-18-L5-109-4-repo-retirement.md` — the L5-109 batch
  audit, of which McpKit absorption is the first track.

If the specific `2026-06-18-McpKit-absorption-audit.md` is later written
to `phenotype-org-audits/findings/`, this ORIGIN.md should be amended to
point at it.

## Chain of custody

```text
KooshaPari/McpKit                    (source repo, ARCHIVED 2026-06-17)
└── rust/
    └── phenotype-mcp-asset/         (source path, v0.2.0)
        ├── Cargo.toml               ─┐
        ├── src/lib.rs                │ copied verbatim (with phantom
        ├── src/handler.rs            │ modules removed in lib.rs)
        ├── src/types.rs              │
        └── tests/                    │ (empty in source)
                                     ─┘
                                     ↓
KooshaPari/PhenoFastMCP-rust/crates/fastmcp-asset (folded destination, v0.1.0)
├── Cargo.toml                       (deps: workspace → explicit versions;
│                                     removed unused phenotype-mcp-framework)
├── README.md                        (new)
├── CHANGELOG.md                     (new, includes 0.3.0 extraction entry)
├── ORIGIN.md                        (new — this file)
├── BUILD_STATUS.md                  (new — stub-module rationale)
└── src/
    ├── lib.rs                       (FIXED: phantom modules removed;
    │                                 5 stub modules added + re-exported)
    ├── types.rs                     (verbatim from source)
    ├── handler.rs                   (verbatim from source)
    ├── manifest.rs                  (NEW stub: re-export shim)
    ├── discovery.rs                 (NEW stub: walkdir + sha256)
    ├── build.rs                     (NEW stub: validate + placeholder artifact)
    ├── validation.rs                (NEW stub: toml parse + field checks)
    └── dependencies.rs              (NEW stub: marks all deps as unresolved)
```

## Authorship & license

- **Source copyright**: Phenotype Developers (per source `Cargo.toml`)
- **Source license**: MIT
- **Destination license**: MIT OR Apache-2.0 (dual; matches Phenotype fleet
  convention per ADR-023 substrate placement)
- **Authorship attribution**: preserved — `authors = ["Phenotype Developers <dev@phenotype.dev>"]`
