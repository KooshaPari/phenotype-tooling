# cheap-llm-mcp absorption

`cheap-llm-mcp` has been absorbed into the canonical `phenotype-ops-mcp` package.
New integrations should import `phenotype_ops_mcp.providers.cheap_llm` directly.

For existing callers, `phenotype-tooling` provides a temporary compatibility
alias at `cheap_llm` that re-exports the canonical provider module.
