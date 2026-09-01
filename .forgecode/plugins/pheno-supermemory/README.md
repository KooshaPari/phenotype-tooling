# pheno-supermemory

Forgecode plugin that spawns the `supermemory` binary as a per-machine systemd unit. Primary adapter for the `Episodic` `MemoryScope` (per `thegent/docs/specs/memory/v2.md`).

See `SKILL.md` for the capability manifest, `plugin.toml` for the forgecode plugin descriptor, and `systemd/pheno-supermemory.service` for the unit definition.

## Install

Installed automatically by the repo-root `scripts/install.sh`.

## Verify

```bash
systemctl status pheno-supermemory.service
curl -fsS http://127.0.0.1:3030/health
```
