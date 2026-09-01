# pheno-config

Forgecode plugin that spawns the `configra` daemon (canonical config substrate per ADR-031) as a per-machine systemd unit. Provides 12-factor cascade, hot-reload (L37), and a unified REST API.

See `SKILL.md`, `plugin.toml`, and `systemd/pheno-config.service` for details.
