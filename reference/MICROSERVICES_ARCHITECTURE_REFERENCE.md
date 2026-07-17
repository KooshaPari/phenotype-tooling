# Microservices Architecture Best Practices Reference

## 1. Domain-Driven Design (DDD) for Service Decomposition

### Bounded Contexts

Core concept: Each service owns a single bounded context with:
- Unique business rules and language (ubiquitous language)
- Independent data model
- Clear API boundaries

**Example**: E-commerce → User Service, Product Catalog, Order Service, Payment Service, Shipping Service

### Decomposition Checklist

- [ ] Identify bounded contexts from domain experts
- [ ] Map contexts to service boundaries (1:1 relationship)
- [ ] Define service contracts (input/output schemas)
- [ ] Assess communication frequency (loose coupling preferred)
- [ ] Plan data ownership (database-per-service pattern)

---

## 2. Inter-Service Communication

### Decision Tree

```
Synchronous + Low-latency (<100ms)?
├─ Small payloads (<1MB) → gRPC (binary, fast, typed)
└─ Large payloads → REST API (easier debugging)

Asynchronous / Fire-and-forget?
├─ Event sourced → Kafka/RabbitMQ (audit trail)
└─ Simple notifications → Async REST

Long-running (minutes to hours)?
└─ Saga Pattern (Orchestration or Choreography)
```

---

## 3. Service Mesh (Infrastructure-Level Concerns)

### Linkerd vs Istio

| Criterion | Linkerd | Istio |
|-----------|---------|-------|
| Latency overhead | <10ms p95 | 100-200ms p95 |
| Complexity | Simple, Kubernetes-native | Feature-rich, operational overhead |
| mTLS | Default on install | Requires PeerAuthentication config |
| Use case | Greenfield, high-performance | Complex multi-tenant environments |

**Recommendation**: Linkerd for simplicity, Istio for advanced traffic management

### Key Capabilities (Both)

- Automatic mTLS between services
- Circuit breaking, retry policies
- Traffic splitting (canary deployments)
- Request mirroring for testing
- Observability integration (distributed tracing, metrics)

---

## 4. Resilience Patterns

### Circuit Breaker State Machine

```
Closed (Normal)
├─ Track consecutive failures
└─ After threshold → Open

Open (Failing Fast)
└─ Reject requests immediately
└─ After timeout → Half-Open

Half-Open (Testing Recovery)
└─ Allow single test request
└─ Success → Closed | Failure → Open
```

**Configuration**: Failure threshold 5, timeout 60s, success threshold 2

### Bulkhead Pattern

Isolate resource pools per service boundary:
```
Thread Pool A (Service X): max 20 concurrent
├─ If exhausted, only this caller is affected
Thread Pool B (Service Y): max 30 concurrent
└─ Service Z remains unaffected
```

### Retry + Exponential Backoff

```
Wait: initial * (multiplier ^ attempt) + jitter
Retry 1: 100ms + 0-50ms jitter
Retry 2: 200ms + 0-100ms jitter
Retry 3: 400ms + 0-200ms jitter
```

**Max retries**: 3-5, Max total time: <5 seconds

---

## 5. Distributed Transactions (Saga Pattern)

### Orchestration vs Choreography

| Pattern | Coordinator | Pros | Cons |
|---------|------------|------|------|
| **Orchestration** | Central saga service | Clear flow, easy to debug | Single point of failure |
| **Choreography** | Event-driven (no coordinator) | Decoupled, resilient | Hard to debug, eventual consistency |

### Example: Order Processing Saga (Choreography)

```
Order Service emits:
"order.created"
  ↓
Inventory Service:
  1. Reserve inventory
  2. On success → emit "inventory.reserved"
  On failure → emit "inventory.failed"
  ↓
Payment Service:
  1. Process payment
  2. On success → emit "payment.completed"
  On failure → emit "payment.failed" (trigger compensation)
  ↓
Shipping Service:
  1. Schedule shipment
  2. On success → emit "shipment.scheduled"
  On failure → compensation triggers
```

### Compensating Transactions

Undo operations if saga fails:
- Payment failed → refund previous charge
- Inventory failed → release reservation
- Shipment failed → cancel order

---

## 6. Observability (OpenTelemetry Stack)

### Architecture

```
App SDKs (OTEL)
    ↓
OTEL Collector (batching, sampling, transformation)
    ↓
Backends:
├─ Jaeger (distributed tracing)
├─ Prometheus (metrics)
└─ Loki (logs)
```

### Instrumentation Minimum

- **Tracing**: W3C Trace Context headers propagated across services
- **Metrics**: Request latency (p50, p95, p99), error rate, throughput
- **Logs**: Structured with correlation IDs

### Trace Sampling Strategy

- **Head sampling**: Decide at trace start (% of requests)
- **Tail sampling**: Keep interesting traces (errors, high latency)
- **Default**: 1-5% of normal requests, 100% of errors

---

## 7. Deployment Strategies

### Blue-Green Deployment

1. Maintain 2 identical production environments (Blue=current, Green=new)
2. Deploy to Green
3. Test thoroughly
4. Switch load balancer to Green
5. Rollback: flip back to Blue

**Pros**: Instant rollback | **Cons**: 2× infrastructure cost

### Canary Deployment

1. 10% traffic → new version
2. Monitor metrics (error rate, latency)
3. Gradual shift: 10% → 20% → 50% → 100%
4. Auto-rollback on SLO violation

**Pros**: Low blast radius | **Cons**: Slower rollout

### Rolling Deployment (Kubernetes default)

1. Replace old instances with new (configurable rate)
2. No downtime but mixed-version period
3. Slower rollback

---

## 8. Failure Modes & Analysis (FMEA Template)

| Service | Failure Mode | Severity | Occurrence | Detection | RPN | Mitigation |
|---------|---|---|---|---|---|---|
| Order Service | Timeout calling Payment | 5 | 3 | 2 | 30 | Circuit breaker + bulkhead |
| Payment Service | DB connection pool exhausted | 5 | 2 | 1 | 10 | Bulkhead per caller |
| Event Bus | Message loss | 5 | 1 | 4 | 20 | Persistence + replication |

**RPN = Severity × Occurrence × Detection**

---

## 9. API Contracts & Versioning

### Contract Patterns

- **URL path versioning**: `/api/v1/users` (explicit)
- **Header versioning**: `Accept: application/json;version=2` (flexible)
- **Content negotiation**: Clients request specific version (modern)

### Breaking Change Detection

- Use OpenAPI/AsyncAPI specs
- Validate consumer contracts with Pact framework
- Automated breaking change detection in CI

---

## 10. Service Decomposition Decision Tree

**Questions to ask**:
1. What's the communication frequency between services?
2. Can they have independent deployments?
3. Can each service own its own database?
4. How different are their scaling requirements?

**High cohesion + low coupling** = good service boundary

---

## 11. Production Readiness Checklist

- [ ] Observability: Tracing, metrics, logs with correlation IDs
- [ ] Resilience: Circuit breaker, bulkhead, timeouts, retries
- [ ] Security: mTLS, AuthZ, secret rotation
- [ ] Disaster recovery: Backup, replication, failover
- [ ] Deployment automation: Blue-green or canary ready
- [ ] Incident response: Runbooks, war room process, postmortems
- [ ] Testing: Unit, integration, E2E, chaos experiments
- [ ] Monitoring: SLO dashboards, alert thresholds

---

## References

- Domain-Driven Design: https://www.domainlanguage.com/ddd/
- Microservices.io Patterns: https://microservices.io/patterns/
- OpenTelemetry: https://opentelemetry.io/
- Linkerd vs Istio: https://www.buoyant.io/linkerd-vs-istio
- FMEA Methodology: https://www.quality-one.com/fmea/
