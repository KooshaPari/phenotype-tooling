---
name: pheno-supermemory
description: Primary memory store via supermemory binary + smfs filesystem. Serves the Episodic MemoryScope per the locked stack in ADR-096.
version: 0.1.0
license: Apache-2.0
---

# pheno-supermemory

Primary memory store for forgecode sessions. Spawns the `supermemory` binary as a per-machine systemd unit (or launchd-managed background process on macOS). SOTA on LongMemEval, LoCoMo, and ConvoMem benchmarks.

## When to use

- You want forgecode sessions to have persistent memory across invocations.
- You need a filesystem-style read/write interface to memory (smfs — `supermemory fs`).
- You want SOTA-quality episodic recall.

## When NOT to use

- You need per-agent identity blocks (use `pheno-letta` for the `Identity` MemoryScope).
- You need project knowledge graph queries (use `pheno-cognee` for `ProjectKnowledge`).
- You want cloud-managed memory (use supermemory cloud or a different plugin).

## Endpoints

- REST: `http://127.0.0.1:3030`
- MCP: `stdio:supermemory-mcp` (auto-spawned by the bridge)
- smfs: `http://127.0.0.1:3030/fs` (filesystem interface; mount via `pheno_memory mount_smfs <path>`)

## MemoryScope routing

This plugin is the **primary** adapter for:

- `MemoryScope::Episodic` — session history, conversation logs, transient state.

It does NOT serve: `Identity` (→ pheno-letta), `ProjectKnowledge` (→ pheno-cognee). The `CompositeAdapter` in `thegent-memory` v2 routes by scope.

## Lifecycle

- **Linux:** managed by `pheno-supermemory.service` (systemd); brought up by `pheno-forge-sidecars.target`.
- **macOS:** launched by `scripts/launch-sidecars.sh start` (launchd fallback).

## Configuration (plugin.env)

| Var | Default | Notes |
|---|---|---|
| `PHENO_BINARY_NAME` | `supermemory` | Binary name (resolved at `fetch-sidecars.sh` time) |
| `PHENO_BINARY_PATH` | `<plugin_dir>/bin/supermemory` | Resolved by `spawn.sh` |
| `PHENO_BINARY_ARGS` | `--port 3030 --store /var/lib/pheno-forge/supermemory` | Resolved by `spawn.sh` |
| `PHENO_STATE_DIR` | `/var/lib/pheno-forge/supermemory` | Persistent store path |
| `PHENO_HEALTH_URL` | `http://127.0.0.1:3030/health` | HTTP healthcheck |
| `PHENO_HEALTH_TIMEOUT` | `5` | Seconds |
| `PHENO_SD_UNIT` | `pheno-supermemory.service` | systemd unit name |

## Install

```bash
# bundled with the rest of the plugin bundle (see repo root README)
./scripts/install.sh
```

## Verify

```bash
systemctl status pheno-supermemory.service
curl -s http://127.0.0.1:3030/health
./scripts/healthcheck.sh pheno-supermemory
```
