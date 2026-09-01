---
name: pheno-mem0
description: Fallback memory via mem0 server. Activated only when the primary adapter for a MemoryScope fails.
version: 0.1.0
license: Apache-2.0
---

# pheno-mem0

Fallback memory layer. Spawns the `mem0` server (59.2k stars; the largest by adoption) as a per-machine systemd unit. The `CompositeAdapter` in `thegent-memory` v2 only routes to this plugin when the primary adapter for a `MemoryScope` returns a `Transport` or `Backend` error.

## When to use

- You want a high-availability safety net for the memory stack.
- The primary adapter (supermemory/letta/cognee) is temporarily down.
- You want a known-good, widely-deployed fallback with low maintenance burden.

## When NOT

- You want a primary memory backend (use `pheno-supermemory` for `Episodic`, `pheno-letta` for `Identity`, `pheno-cognee` for `ProjectKnowledge`).
- You want to debug memory issues — mem0-as-fallback hides root cause. Use the structured logs from `pheno-tracing` to see fallback activation events.

## Endpoints

- REST: `http://127.0.0.1:8000`

## MemoryScope routing

**Fallback** for all scopes (per `thegent/docs/specs/memory/v2.md` § 3.5 `CompositeAdapter::with_fallback`).

## Configuration (plugin.env)

| Var | Default | Notes |
|---|---|---|
| `MEM0_VECTOR_STORE` | `qdrant` | Vector store backend (qdrant, chroma, pgvector) |
| `MEM0_LLM_PROVIDER` | `openai` | LLM provider for memory extraction |
