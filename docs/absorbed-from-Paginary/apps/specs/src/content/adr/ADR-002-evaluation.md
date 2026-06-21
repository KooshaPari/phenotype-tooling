# Architecture Decision Record: Evaluation Strategy

**Status**: Accepted  
**Date**: 2026-04-04  
**Author**: Flagward Architecture Team  
**Deciders**: Platform Engineering Team, Performance Team  

---

## Context

Flagward must support multiple evaluation patterns to accommodate different use cases:
1. **UI feature toggles**: Need sub-millisecond evaluation in browsers
2. **Backend authorization**: Need secure server-side evaluation
3. **Mobile apps**: Need offline-capable evaluation
4. **Edge deployment**: Need evaluation at CDN edge

Key requirements:
- Sub-10ms evaluation latency for UI use cases
- Secure evaluation for sensitive operations (billing, admin access)
- Offline capability for mobile and edge
- Consistent behavior across all evaluation modes

---

## Decision

We will implement a **hybrid evaluation strategy** with three modes:

1. **Local Evaluation (Primary)**: SDK evaluates flags locally using cached rules
2. **Server Evaluation**: API calls to Flagward server for sensitive evaluations
3. **Edge Evaluation**: WebAssembly-based evaluation at CDN edge

The default mode is **local evaluation with server fallback** for sensitive flags.

### Evaluation Mode Selection Matrix

| Use Case | Mode | Latency | Security |
|----------|------|---------|----------|
| UI feature toggle | Local | <1ms | Medium |
| API authorization | Server | 10-20ms | High |
| Pricing/billing | Server | 10-20ms | High |
| Experiment assignment | Local | <1ms | Low |
| Mobile offline | Local | <1ms | Medium |
| Edge routing | Edge | <5ms | Medium |

### Rationale

**Why local evaluation as primary:**
- Sub-millisecond latency essential for UI responsiveness
- No network dependency after initial sync
- Scales with client count (no server load from evaluations)
- Works offline (mobile apps, poor connectivity)

**Why server evaluation for sensitive operations:**
- Rules not exposed to client
- Can use sensitive context (PII, internal data)
- Audit trail for compliance
- Central point of control

**Why edge evaluation:**
- Global low latency without origin round-trip
- Geolocation-based targeting
- Reduced origin load
- Modern CDN capabilities (Cloudflare Workers, Fastly Compute)

**Why not single evaluation mode:**
- No single mode satisfies all use cases
- Trade-offs between latency, security, and complexity
- Users need choice based on context

---

## Consequences

### Positive

1. **Optimal latency**: Local evaluation for UI (<1ms), server for security
2. **Security flexibility**: Choose appropriate mode per flag
3. **Scalability**: No server bottleneck from high-volume evaluations
4. **Resilience**: Local evaluation works during network outages
5. **Developer choice**: Per-flag configuration of evaluation mode

### Negative

1. **Complexity**: Three evaluation paths to maintain
2. **Consistency risk**: SDK logic must match server logic exactly
3. **Debugging complexity**: Harder to trace evaluation issues
4. **Testing overhead**: Must test all three modes
5. **Documentation burden**: Must explain when to use each mode

### Mitigations

1. **Shared evaluation engine**: Core logic shared between server and SDK (via WASM or shared library)
2. **Deterministic hashing**: MurmurHash3 for consistent bucketing across platforms
3. **Comprehensive testing**: Automated tests verify identical results across modes
4. **Evaluation tracing**: OpenTelemetry spans for debugging
5. **Clear defaults**: Sensible defaults reduce decision fatigue

---

## Implementation Details

### SDK Architecture

```typescript
interface EvaluationMode {
  type: 'local' | 'server' | 'edge';
  fallback?: EvaluationMode;  // Fallback if primary fails
}

interface FlagConfig {
  key: string;
  defaultValue: unknown;
  evaluationMode: EvaluationMode;
  sensitive?: boolean;  // Forces server evaluation
}

class FlagwardClient {
  private localEvaluator: LocalEvaluator;
  private serverClient: ServerClient;
  private cache: FlagCache;
  
  async evaluate<T>(
    flagKey: string,
    context: EvaluationContext,
    defaultValue: T
  ): Promise<T> {
    const flag = await this.getFlagConfig(flagKey);
    
    // Sensitive flags always use server evaluation
    if (flag.sensitive) {
      return this.serverClient.evaluate(flagKey, context, defaultValue);
    }
    
    switch (flag.evaluationMode.type) {
      case 'local':
        return this.evaluateLocal(flag, context, defaultValue);
        
      case 'server':
        return this.serverClient.evaluate(flagKey, context, defaultValue);
        
      case 'edge':
        throw new Error('Edge evaluation requires edge SDK');
    }
  }
  
  private evaluateLocal<T>(
    flag: Flag,
    context: EvaluationContext,
    defaultValue: T
  ): T {
    // Get cached rules
    const rules = this.cache.getRules(flag.key);
    
    // Evaluate locally
    const result = this.localEvaluator.evaluate(flag, rules, context);
    
    // Log async (don't block evaluation)
    this.logEvaluation(flag.key, context, result).catch(console.error);
    
    return (result ?? defaultValue) as T;
  }
}
```

### Server Evaluation API

```typescript
// POST /api/v1/flags/:key/evaluate
interface EvaluateRequest {
  context: EvaluationContext;
  defaultValue?: unknown;
}

interface EvaluateResponse {
  key: string;
  value: unknown;
  source: 'server' | 'cache';
  evaluationId: string;  // For audit trail
  timestamp: string;
}

// Example
POST /api/v1/flags/premium-feature/evaluate
{
  "context": {
    "userId": "user-123",
    "plan": "enterprise",
    "sessionId": "sess-456"
  },
  "defaultValue": false
}

Response:
{
  "key": "premium-feature",
  "value": true,
  "source": "server",
  "evaluationId": "eval-789",
  "timestamp": "2026-04-04T12:00:00Z"
}
```

### Consistent Hashing

```typescript
import { murmur3 } from 'murmurhash-js';

function getConsistentBucket(
  flagKey: string,
  context: EvaluationContext,
  salt?: string
): number {
  // Build consistent input string
  const inputs = [flagKey];
  
  if (context.userId) inputs.push(context.userId);
  else if (context.sessionId) inputs.push(context.sessionId);
  else inputs.push('anonymous');
  
  if (salt) inputs.push(salt);
  
  const input = inputs.join(':');
  const hash = murmur3(input);
  
  return Math.abs(hash) % 100;  // 0-99
}

// Same user, same flag = always same bucket
getConsistentBucket('new-feature', { userId: 'alice' });  // Always 42
getConsistentBucket('new-feature', { userId: 'bob' });     // Always 73
```

### Edge Evaluation (Future)

```typescript
// WebAssembly module for edge evaluation
interface EdgeEvaluator {
  evaluate(flagKey: string, context: EvaluationContext): unknown;
}

// Cloudflare Worker example
export default {
  async fetch(request: Request, env: Env) {
    const url = new URL(request.url);
    
    // Load WASM evaluator
    const evaluator = await WebAssembly.instantiate(env.FLAG_EVALUATOR);
    
    // Get user context from request
    const context = {
      country: request.cf?.country,
      userAgent: request.headers.get('user-agent')
    };
    
    // Evaluate at edge (no origin call)
    const variant = evaluator.evaluate('landing-page', context);
    
    // Serve appropriate variant
    url.pathname = `/variants/${variant}${url.pathname}`;
    return fetch(new Request(url, request));
  }
};
```

---

## Performance Targets

| Mode | Target Latency (p99) | Throughput |
|------|---------------------|------------|
| Local | <1ms | 500,000+ evals/sec |
| Server | <20ms | 50,000+ evals/sec |
| Edge | <5ms | 100,000+ evals/sec |

---

## Related Decisions

- ADR-001: Storage Engine (determines rule storage)
- ADR-003: Audit Logging (determines evaluation logging)

---

## References

- MurmurHash3: https://github.com/aappleby/smhasher
- LaunchDarkly evaluation: https://docs.launchdarkly.com/sdk/concepts/evaluation
- Cloudflare Workers: https://workers.cloudflare.com/
- Fastly Compute@Edge: https://www.fastly.com/products/edge-compute

---

## Notes

- All evaluation modes must produce identical results for same inputs
- SDK versions must maintain backward compatibility with rule format
- Consider WebAssembly for universal evaluation engine in v2
- Edge evaluation deferred to v1.5 (complex deployment requirements)

**Status**: Accepted  
**Last Updated**: 2026-04-04
