# pheno-mem0

Forgecode plugin that spawns the `mem0` server (fallback memory) as a per-machine systemd unit. Activated by the `CompositeAdapter` only when the primary adapter for a `MemoryScope` fails.

See `SKILL.md`, `plugin.toml`, and `systemd/pheno-mem0.service` for details.
