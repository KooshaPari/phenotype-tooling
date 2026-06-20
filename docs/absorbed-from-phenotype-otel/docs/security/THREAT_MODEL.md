---
title: "Threat Model"
version: 0.1.0
lastUpdated: 2026-06-16
---

# Threat Model

> **Source of truth:** phenotype-otel (Phenotype OpenTelemetry bridge — single-call OTLP + tracing-subscriber init)
> **Scope:** OpenTelemetry exporters, OTLP endpoint config, telemetry data, init flow, distribution

## Assets

1. **Telemetry data (spans, metrics, logs)** — PII-adjacent data emitted by every instrumented service. If mutable in transit, an attacker can observe fleet behavior, user actions, or internal endpoints.
2. **OTLP endpoint config (`OTEL_EXPORTER_OTLP_ENDPOINT`)** — Read from env. If mutable (e.g., by a rogue env-var injector), the attacker can redirect telemetry to a malicious collector.
3. **OpenTelemetry SDK (`opentelemetry`, `opentelemetry-otlp`, `tracing-subscriber`)** — Rust + Python deps. If mutable, can ship a backdoor that exfiltrates telemetry or modifies the in-process trace.
4. **CI pipeline** — Builds and publishes the bridge crate. If mutable, can inject backdoors.
5. **Init function (`init()` or `init_otel()`)** — Called once at service start. If mutable, can ship a side-effect that runs on every service start (e.g., reading env vars not in scope, or opening a side channel).

## Threats (STRIDE)

| Category | Threat | Likelihood | Impact | Mitigation |
|---|---|---|---|---|
| **Spoofing** | An adversary publishes a `phenotype-otel` fork under a similar name and downstream consumers fetch the wrong crate. | Low | Critical | Releases are signed (cosign, keyless). README documents the canonical install path. |
| **Tampering** | A `tracing` layer is modified to redact or falsify spans (e.g., hiding the attacker's actions). | Low | High | All commits are signed. CI runs `cargo audit` on every PR. The `tracing-subscriber` registry is configured to fail-closed if a custom layer panics. |
| **Repudiation** | A contributor pushes a layer change and later denies it. | Low | Medium | All commits are signed (gitsign, keyless). Releases are tagged. |
| **Information Disclosure** | The OTLP exporter sends PII (user IDs, request bodies) to a third-party collector. | High | High | The bridge enforces a `redact-paths` allowlist for span attributes. Common PII keys (`email`, `phone`, `address`, `ssn`, etc.) are auto-redacted. The default OTLP endpoint is the org's collector; if `OTEL_EXPORTER_OTLP_ENDPOINT` is set to a non-org URL, the bridge logs a warning. |
| **Denial of Service** | A maliciously-large span (100MB) causes the OTLP exporter to OOM. | Medium | Medium | The exporter enforces `max-span-size=64KB` and a `flush-timeout=5s`. Spans over the limit are dropped with a counter increment. |
| **Elevation of Privilege** | A malicious `tracing-subscriber` layer executes arbitrary code on init. | Low | Critical | The init function uses a static allowlist of layer types; reflection-based layer discovery is disabled. All layers are versioned and signed. |

## Residual Risk and Revision Cadence

The most material residual risk is **PII leakage via telemetry** — even with redaction, novel PII keys (e.g., a new `x-user-ssn` header) may not be on the allowlist. The strongest available mitigation is the path-based allowlist, but it requires ongoing maintenance. The next highest residual is **OTLP endpoint hijack** — if an attacker can set the `OTEL_EXPORTER_OTLP_ENDPOINT` env var (e.g., via a compromised CI step), they can redirect all telemetry to a malicious collector. This threat model should be revised quarterly (February, May, August, November) or whenever a new OpenTelemetry SDK version is integrated, a new exporter is added, or the redaction allowlist grows beyond 50 entries. The revision trigger is any PR that adds a new exporter, a new redaction rule, or a new layer type.
