---
name: pheno-tracing
description: OTLP trace ingest via otel-collector-contrib. Routes forgecode + sidecar traces to pheno-tracing (ADR-012/ADR-036B).
version: 0.1.0
license: Apache-2.0
---

# pheno-tracing

OTLP trace ingest. Spawns the `otel-collector-contrib` binary as a per-machine systemd unit. Receives OTLP gRPC (`:4317`) and HTTP (`:4318`) from forgecode + the 4 memory sidecars + the config sidecar, and forwards to pheno-tracing (the canonical tracing substrate per ADR-012/ADR-036B).

## When to use

- You want unified observability across the forgecode + sidecar fleet.
- You need OTel-compatible traces (Jaeger, Tempo, or pheno-tracing as backend).
- You want to debug fallback activation events from `pheno-mem0` (visible in traces).

## When NOT

- You don't need observability (forgecode has its own logs).
- You want a different trace backend (you can override the otel-collector-contrib config).

## Endpoints

- OTLP gRPC: `grpc://127.0.0.1:4317`
- OTLP HTTP: `http://127.0.0.1:4318`
- Health: `http://127.0.0.1:13133/health`

## Refs

- ADR-012 (pheno-tracing canonical across pheno-* repos)
- ADR-036B (pheno-tracing substrate canonical — re-affirmed)
- ADR-042 (security audit cadence — tracing is in scope)
