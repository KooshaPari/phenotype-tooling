# pheno-tracing

Forgecode plugin that spawns the `otel-collector-contrib` binary (OTLP ingest) as a per-machine systemd unit. Routes forgecode + sidecar traces to pheno-tracing (ADR-012/ADR-036B).

See `SKILL.md`, `plugin.toml`, and `systemd/pheno-tracing.service` for details.
