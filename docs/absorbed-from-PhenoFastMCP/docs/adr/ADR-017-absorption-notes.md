# ADR-017: McpKit absorption notes

**Status:** Accepted
**Date:** 2026-06-17
**Supersedes:** n/a (references historical material from the now-archived McpKit project)

## Context

The McpKit project (KooshaPari/McpKit) was a polyglot MCP framework effort
maintained alongside early PhenoFastMCP work. It shipped an extensive
documentation set — most notably a full MCP specification draft and three
architecture decision records covering transport choice, a YAML tool registry,
and SDK generation strategy. McpKit itself was archived on 2026-06-17 because
every framework capability it offered was either absorbed into the PhenoFastMCP
forks or superseded by them.

This ADR does not introduce a new decision. Its purpose is to record **where
the McpKit material lives now**, what patterns from it carried forward into
PhenoFastMCP, and which ones were intentionally not carried forward.

## Source material (archived)

The original McpKit documentation is preserved at the McpKit repository's
archive pointer. The patterns are referenced, not copied, in this repo.

| Source document | Topic | Carried forward? |
|-----------------|-------|------------------|
| `McpKit/docs/SPEC.md` | Full MCP specification draft (≈105 KB) | No — superseded by the official `modelcontextprotocol` spec and by the PhenoFastMCP API surface. |
| `McpKit/docs/adr/ADR-001-mcp-transport.md` | Dual stdio + HTTP/SSE transport decision | Yes — implemented in `fastmcp_slim/fastmcp/server/` transport layer. |
| `McpKit/docs/adr/ADR-002-tool-registry.md` | YAML-declared tool registry | Partially — the `fastmcp` decorator API was retained as the primary path; YAML discovery was dropped in favor of programmatic registration to match upstream `PrefectHQ/fastmcp`. |
| `McpKit/docs/adr/ADR-003-sdk-generation.md` | Multi-language SDK generation strategy | Yes — codified as the tier model in `PHENO.md` (tier 0 spec → tier 1–2 framework bindings, generated consumers at tier 1). |

## Patterns absorbed

### Transport (from ADR-001)

McpKit's argument for supporting both stdio and HTTP/SSE from a single
`FastMCP`-style server object carried forward unchanged. In PhenoFastMCP this
shows up as the shared `FastMCP` mount surface used by both the stdio entry
point and the HTTP/SSE server in `fastmcp_slim/fastmcp/server/`.

### Tool registration (from ADR-002)

McpKit's registry aimed to let users declare tools in YAML and have the
framework instantiate handlers. PhenoFastMCP kept the **shape** of that
registry (a name + description + JSON-Schema input) but moved the binding from
declarative YAML to the `@tool` / `@resource` / `@prompt` decorator API, which
gives static type checking and matches upstream `fastmcp` expectations.

### SDK generation (from ADR-003)

McpKit's tiered plan — a spec core, framework bindings per language, generated
client SDKs on top — is the model codified in `PHENO.md`'s tier table. The
`PhenoFastMCP-rust` (tier 0) and `PhenoFastMCP-go` (tier 1) forks are the
direct lineage of that ADR's "one binding per language" plan.

## Patterns intentionally not carried forward

- **The full 105 KB `SPEC.md`.** The authoritative spec is now the upstream
  `modelcontextprotocol` repo. Duplicating a spec in this fork would drift.
- **YAML tool declarations as the primary surface.** The decorator API is
  strictly more capable (typed params, async handlers, dependency injection
  via `Depends`) and is what `PrefectHQ/fastmcp` users expect.
- **McpKit's vendored mcp-forge LSP copy.** Dropped per `FORK-NOTES.md` —
  language-server concerns belong in editor tooling, not the framework.

## Cross-references

- `PHENO.md` — tier model and sibling-fork map (direct descendant of McpKit ADR-003).
- `SUPERSET.md` — PhenoFastMCP integration lane; cites this ADR for polyrepo boundaries.
- `FORK-NOTES.md` § "Absorption from deprecated phenotype repos" — McpKit row.
- `PhenoMCPServers` `catalog/registry.yaml` — PhenoFastMCP is registered as the
  `framework.python` entry; the McpKit archive link is recorded alongside it
  for historical lookup.

## Verification

- No duplicate MCP specification copy exists under `docs/`. The closest
  material is `docs/development/` (contributor docs) and `docs/python-sdk/`
  (auto-generated API reference, owned by a long-lived bot PR per
  `CLAUDE.md`); neither overlaps with McpKit's `SPEC.md`.
- The McpKit archive pointer is referenced from `PhenoMCPServers`
  `catalog/registry.yaml`; no second copy needs to live in this repo.
