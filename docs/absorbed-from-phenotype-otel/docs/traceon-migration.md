# Traceon migration

`KooshaPari/Traceon` (`tracingkit`, archived) proposed a hexagonal distributed tracing framework.

## Absorption status

| Traceon capability | pheno-otel coverage |
|--------------------|---------------------|
| OTLP export | ✅ `init()` + OTLP HTTP bridge |
| tracing-subscriber wiring | ✅ |
| Hexagonal adapters/domain | ❌ not ported |
| Jaeger/Zipkin feature flags | ❌ stubs only in Traceon |
| Trace context domain model | ❌ |

**Coverage: ~35%** — pheno-otel is the production OTLP init crate; Traceon remains archived as design reference.

## Traceon layout (reference)

```
src/adapters, application, domain, infrastructure
```

For new work, use `pheno_otel::init()` and standard `tracing` spans rather than reviving Traceon.
