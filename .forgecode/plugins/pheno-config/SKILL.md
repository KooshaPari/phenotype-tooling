---
name: pheno-config
description: Config substrate via Configra daemon. Per ADR-022/031, Configra is the canonical config repo for the fleet.
version: 0.1.0
license: Apache-2.0
---

# pheno-config

Config substrate. Spawns the `configra` daemon (per ADR-031, the canonical config repo for the fleet after `phenotype-config` was absorbed) as a per-machine systemd unit. Provides 12-factor cascade, hot-reload (L37), and a unified REST API for config reads.

## When to use

- You want forgecode sessions to read fleet-wide config from a single source.
- You need hot-reload of config values without restarting forgecode sessions (L37).
- You want the 12-factor cascade (env → TOML → remote) per `Configra` semantics.

## When NOT

- You don't use the `Configra` config format.
- You want a per-plugin config (use forgecode's own plugin-level config).

## Endpoints

- REST: `http://127.0.0.1:9100`
- Config schema: `http://127.0.0.1:9100/schema`

## Refs

- ADR-022 (config consolidation — two-crate canonical split)
- ADR-031 (Configra absorb — `phenotype-config` → `Configra`)
- ADR-035 (Configra migration gates)
