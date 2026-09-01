---
name: pheno-letta
description: Subconscious memory blocks (per-agent identity) via letta server. Serves the Identity MemoryScope.
version: 0.1.0
license: Apache-2.0
---

# pheno-letta

Subconscious memory substrate. Spawns the `letta` server (ex-MemGPT) as a per-machine systemd unit. Manages the per-agent `core_memory` (in-context) + `archival_memory` (vector, out-of-context) + `recall_memory` (conversation history) blocks — Letta's "conscious/subconscious" mental model.

## When to use

- You want per-agent persistent identity that survives across sessions.
- You need the "subconscious" pattern: memory blocks auto-managed (auto-archival + auto-recall).
- You want Letta's `core_memory` blocks (persona + human) editable in-flight.

## When NOT

- You need raw episodic recall (use `pheno-supermemory`).
- You need project knowledge graph (use `pheno-cognee`).
- You want a stateless memory layer (Letta is intentionally stateful).

## Endpoints

- REST: `http://127.0.0.1:8283`
- Web UI: `http://127.0.0.1:8283/`

## MemoryScope routing

Primary for `MemoryScope::Identity` (per `thegent/docs/specs/memory/v2.md`).

## Configuration (plugin.env)

| Var | Default | Notes |
|---|---|---|
| `LETTA_AGENT_ID` | `default-agent` | The agent identity whose blocks this plugin manages |
| `PHENO_HEALTH_URL` | `http://127.0.0.1:8283/v1/health` | HTTP healthcheck |
