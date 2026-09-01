---
name: pheno-cognee
description: Project knowledge graph (code, docs, ADRs) via cognee MCP server. Serves the ProjectKnowledge MemoryScope.
version: 0.1.0
license: Apache-2.0
---

# pheno-cognee

Project knowledge graph. Spawns the `cognee-mcp` server (the MCP wrapper around `topoteretes/cognee`) as a per-machine systemd unit. Implements the 4-op API: `remember`, `recall`, `forget`, `improve`.

## When to use

- You want forgecode to reason over the project's code, docs, and ADRs as a knowledge graph.
- You need cross-reference queries ("which ADRs reference this crate?").
- You want cognitive-science-grounded ontology (cognee uses a tiered ontology: entity → concept → category → theme).

## When NOT

- You need raw episodic recall (use `pheno-supermemory`).
- You need per-agent identity blocks (use `pheno-letta`).

## Endpoints

- MCP (stdio): `cognee-mcp` is launched as a subprocess by the bridge; communication is JSON-RPC over stdio.
- Datasets: `phenotype-code`, `phenotype-docs`, `phenotype-adrs` (configurable via `COGNEE_DATASETS`).

## MemoryScope routing

Primary for `MemoryScope::ProjectKnowledge` (per `thegent/docs/specs/memory/v2.md`).

## Configuration (plugin.env)

| Var | Default | Notes |
|---|---|---|
| `COGNEE_DATASETS` | `phenotype-code,phenotype-docs,phenotype-adrs` | Comma-separated dataset names |
