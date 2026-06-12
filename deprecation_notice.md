# Absorption notice: `cheap-llm-mcp`

`phenotype-tooling` absorbs `cheap-llm-mcp`. The canonical home is
[`KooshaPari/phenotype-ops-mcp/providers/cheap_llm/`](https://github.com/KooshaPari/phenotype-ops-mcp/tree/main/providers/cheap_llm).

New integrations should depend on `phenotype-ops-mcp` and import the
provider from `providers/cheap_llm/`. Existing callers can rely on the
`phenotype-tooling` re-export during the deprecation window; that alias
will be removed in a future major release.

For migration steps, see the upstream guide in
`phenotype-ops-mcp/docs/migrations/cheap_llm.md`.

