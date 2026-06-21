# Architecture Decision Record: Audit Logging

**Status**: Accepted  
**Date**: 2026-04-04  
**Author**: Flagward Architecture Team  
**Deciders**: Platform Engineering Team, Security Team, Compliance  

---

## Context

Feature flags control critical application behavior. Changes to flags can impact millions of users, revenue, and compliance status. Audit logging is essential for:

1. **Security**: Detect unauthorized flag changes
2. **Compliance**: SOX, HIPAA, SOC 2 require audit trails
3. **Debugging**: Understand what changed when issues arise
4. **Accountability**: Know who made changes and why
5. **Forensics**: Reconstruct timeline during incidents

Requirements:
- Tamper-evident (can't alter history without detection)
- Complete (all flag operations logged)
- Queryable (search by flag, user, time, action)
- Performant (don't slow down flag operations)
- Retained (configurable retention periods)

---

## Decision

We will implement a **hash-chained audit log** with the following characteristics:

1. **Sequential integrity**: Each entry references the hash of the previous entry
2. **Cryptographic hashing**: SHA-256 for all entries
3. **Immutable storage**: Append-only, no updates or deletes
4. **Async logging**: Don't block operations on audit writes
5. **Verification API**: Endpoint to verify chain integrity

### Audit Entry Schema

```typescript
interface AuditEntry {
  // Identity
  id: string;                    // UUID v4
  timestamp: string;             // ISO 8601 UTC
  
  // Actor
  actor: string;                 // User ID or API key ID
  actorType: 'user' | 'api_key' | 'system';
  
  // Action
  action: AuditAction;
  resource: 'flag' | 'segment' | 'api_key' | 'environment';
  resourceKey: string;
  
  // Change details
  changeType: 'create' | 'update' | 'delete' | 'toggle' | 'evaluate';
  changes?: ChangeSet;           // Before/after for updates
  metadata?: Record<string, unknown>;
  
  // Chain integrity
  previousHash: string | null;   // null for first entry
  hash: string;                  // SHA-256 of this entry
  
  // Request context
  ipAddress?: string;
  userAgent?: string;
  requestId?: string;
  sessionId?: string;
}

type AuditAction =
  | 'flag.created'
  | 'flag.updated'
  | 'flag.deleted'
  | 'flag.toggled'        // Enable/disable toggle
  | 'flag.evaluated'      // Server-side evaluation
  | 'segment.created'
  | 'segment.updated'
  | 'segment.deleted'
  | 'api_key.created'
  | 'api_key.revoked'
  | 'environment.created'
  | 'export.requested'
  | 'import.completed';

interface ChangeSet {
  [field: string]: {
    from: unknown;
    to: unknown;
  };
}
```

### Rationale

**Why hash chain:**
- Tamper detection: Any modification breaks the chain
- Order verification: Entries must be in sequence
- No trusted third party: Cryptographic proof, not administrative
- Industry standard: Same approach as blockchain, git, certificate transparency

**Why SHA-256:**
- Industry standard, widely supported
- Fast enough for our use case
- Not vulnerable to length extension attacks
- Future-proof (quantum-resistant alternatives available if needed)

**Why async logging:**
- Don't slow down flag operations
- Audit system failure shouldn't break flags
- Can batch writes for efficiency

**Why not external audit service:**
- Additional cost and dependency
- Network latency
- Vendor lock-in
- Self-hosted requirement for some customers

---

## Consequences

### Positive

1. **Tamper evidence**: Any alteration detectable via chain verification
2. **Compliance ready**: Meets SOX, HIPAA, SOC 2 requirements
3. **Forensic capability**: Complete history reconstructible
4. **Trust**: Users can verify system integrity
5. **Debugging**: Full history of flag changes

### Negative

1. **Storage growth**: Audit log grows indefinitely
2. **Performance overhead**: Hash computation adds ~1ms per operation
3. **Complexity**: More code to maintain
4. **No deletion**: Can't purge old entries without breaking chain
5. **Verification cost**: Full chain verification is O(n)

### Mitigations

1. **Retention policies**: Archive old entries to cold storage (keep chain intact)
2. **Sampling**: Don't log every evaluation (sample 1% or log only changes)
3. **Batching**: Async queue with batch inserts
4. **Incremental verification**: Verify recent entries more frequently than full chain
5. **Compression**: Archive compressed, deduplicated entries

---

## Implementation Details

### Hash Computation

```typescript
import { createHash } from 'crypto';

function computeAuditHash(entry: Omit<AuditEntry, 'id' | 'hash'>): string {
  // Canonical JSON serialization (sorted keys)
  const canonical = JSON.stringify({
    timestamp: entry.timestamp,
    actor: entry.actor,
    actorType: entry.actorType,
    action: entry.action,
    resource: entry.resource,
    resourceKey: entry.resourceKey,
    changeType: entry.changeType,
    changes: entry.changes,
    metadata: entry.metadata,
    previousHash: entry.previousHash,
    ipAddress: entry.ipAddress,
    userAgent: entry.userAgent,
    requestId: entry.requestId
  }, Object.keys({...entry, id: undefined, hash: undefined}).sort());
  
  return createHash('sha256')
    .update(canonical)
    .digest('hex');
}

// Entry creation
async function createAuditEntry(
  data: Omit<AuditEntry, 'id' | 'hash' | 'previousHash'>
): Promise<AuditEntry> {
  // Get previous entry
  const lastEntry = await storage.getLastAuditEntry();
  const previousHash = lastEntry?.hash ?? null;
  
  // Compute hash
  const hash = computeAuditHash({ ...data, previousHash });
  
  // Create entry
  const entry: AuditEntry = {
    id: crypto.randomUUID(),
    ...data,
    previousHash,
    hash
  };
  
  // Store
  await storage.createAuditEntry(entry);
  
  return entry;
}
```

### Chain Verification

```typescript
interface VerificationResult {
  valid: boolean;
  entriesVerified: number;
  brokenAt?: {
    index: number;
    expectedHash: string;
    actualHash: string;
  };
  tamperedEntries?: number[];
}

async function verifyAuditChain(
  fromTimestamp?: Date,
  toTimestamp?: Date
): Promise<VerificationResult> {
  // Get entries in chronological order
  const entries = await storage.getAuditLog({
    from: fromTimestamp,
    to: toTimestamp,
    order: 'asc'
  });
  
  let entriesVerified = 0;
  
  for (let i = 0; i < entries.length; i++) {
    const entry = entries[i];
    
    // Verify chain link
    if (i > 0) {
      const previousEntry = entries[i - 1];
      if (entry.previousHash !== previousEntry.hash) {
        return {
          valid: false,
          entriesVerified,
          brokenAt: {
            index: i,
            expectedHash: previousEntry.hash,
            actualHash: entry.previousHash ?? 'null'
          }
        };
      }
    } else {
      // First entry should have null previousHash
      if (entry.previousHash !== null) {
        return {
          valid: false,
          entriesVerified: 0,
          brokenAt: {
            index: 0,
            expectedHash: 'null',
            actualHash: entry.previousHash
          }
        };
      }
    }
    
    // Verify entry integrity
    const { hash, id, ...entryWithoutHash } = entry;
    const expectedHash = computeAuditHash(entryWithoutHash);
    
    if (hash !== expectedHash) {
      return {
        valid: false,
        entriesVerified,
        tamperedEntries: [i]
      };
    }
    
    entriesVerified++;
  }
  
  return { valid: true, entriesVerified };
}
```

### Async Logging

```typescript
class AsyncAuditLogger {
  private queue: AuditEntryInput[] = [];
  private flushInterval: NodeJS.Timeout;
  private maxQueueSize: number = 100;
  private flushPromise: Promise<void> | null = null;
  
  constructor(private storage: StorageAdapter) {
    // Flush every 5 seconds
    this.flushInterval = setInterval(() => this.flush(), 5000);
  }
  
  async log(entry: AuditEntryInput): Promise<void> {
    this.queue.push(entry);
    
    // Flush immediately if queue is full
    if (this.queue.length >= this.maxQueueSize) {
      await this.flush();
    }
  }
  
  private async flush(): Promise<void> {
    // Prevent concurrent flushes
    if (this.flushPromise) {
      await this.flushPromise;
      return;
    }
    
    if (this.queue.length === 0) return;
    
    this.flushPromise = this.performFlush();
    await this.flushPromise;
    this.flushPromise = null;
  }
  
  private async performFlush(): Promise<void> {
    const entries = this.queue.splice(0, this.maxQueueSize);
    
    // Create entries with proper hash chain
    for (const input of entries) {
      try {
        await createAuditEntry(input);
      } catch (error) {
        // Log to stderr but don't throw (audit shouldn't break operations)
        console.error('Failed to create audit entry:', error);
      }
    }
  }
  
  async shutdown(): Promise<void> {
    clearInterval(this.flushInterval);
    await this.flush();
  }
}
```

### API Endpoints

```typescript
// GET /api/v1/audit
// Query audit log with filters
interface AuditQueryParams {
  flagKey?: string;
  actor?: string;
  action?: string;
  from?: string;  // ISO 8601
  to?: string;    // ISO 8601
  limit?: number; // Default: 100, Max: 1000
  offset?: number;
}

// GET /api/v1/audit/verify
// Verify chain integrity
interface VerifyResponse {
  valid: boolean;
  totalEntries: number;
  lastVerifiedAt: string;
  brokenAt?: {
    entryId: string;
    timestamp: string;
  };
}

// POST /api/v1/audit/export
// Export audit log (admin only)
// Returns: CSV or JSON
```

---

## Storage Considerations

### Database Schema

```sql
-- Audit log table
CREATE TABLE audit_log (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    timestamp TIMESTAMP WITH TIME ZONE NOT NULL,
    actor VARCHAR(255) NOT NULL,
    actor_type VARCHAR(50) NOT NULL,
    action VARCHAR(100) NOT NULL,
    resource VARCHAR(50) NOT NULL,
    resource_key VARCHAR(255) NOT NULL,
    change_type VARCHAR(50) NOT NULL,
    changes JSONB,
    metadata JSONB,
    previous_hash VARCHAR(64),
    hash VARCHAR(64) NOT NULL,
    ip_address INET,
    user_agent TEXT,
    request_id VARCHAR(255),
    session_id VARCHAR(255)
);

-- Indexes for common queries
CREATE INDEX idx_audit_timestamp ON audit_log(timestamp DESC);
CREATE INDEX idx_audit_resource ON audit_log(resource, resource_key);
CREATE INDEX idx_audit_actor ON audit_log(actor);
CREATE INDEX idx_audit_action ON audit_log(action);
CREATE INDEX idx_audit_request ON audit_log(request_id);

-- Composite index for flag history queries
CREATE INDEX idx_audit_flag_history ON audit_log(resource_key, timestamp DESC)
WHERE resource = 'flag';

-- Partial index for recent entries (hot data)
CREATE INDEX idx_audit_recent ON audit_log(timestamp DESC)
WHERE timestamp > NOW() - INTERVAL '30 days';
```

### Retention Strategy

```typescript
interface RetentionPolicy {
  hotStorage: {
    duration: number;     // Days to keep in primary DB
    sampling: number;     // 1 = all, 0.1 = 10% sample
  };
  coldStorage: {
    duration: number;     // Days to keep in archive
    compress: boolean;    // Gzip compression
  };
  deletion: {
    after: number;        // Days after which entries can be deleted
    keepChain: boolean;   // Keep chain intact even if data deleted
  };
}

const DEFAULT_RETENTION: RetentionPolicy = {
  hotStorage: {
    duration: 90,    // 90 days in primary DB
    sampling: 1      // Keep all for 90 days
  },
  coldStorage: {
    duration: 365,   // 1 year in archive
    compress: true
  },
  deletion: {
    after: 1095,     // 3 years total retention
    keepChain: true  // Keep hash chain even if purging data
  }
};
```

---

## Compliance Mapping

| Requirement | Implementation |
|-------------|----------------|
| SOX | Immutable audit trail with hash chain |
| HIPAA | Access logging, user attribution |
| SOC 2 | Change tracking, timestamp integrity |
| GDPR | PII handling in audit logs (hashing) |
| PCI DSS | Access control logging |

---

## Performance Targets

| Metric | Target |
|--------|--------|
| Audit write latency | <5ms (async) |
| Audit query latency (p95) | <100ms |
| Chain verification (10k entries) | <1s |
| Storage growth | <1GB/month per 1M flag operations |

---

## Related Decisions

- ADR-001: Storage Engine (determines audit storage backend)
- ADR-002: Evaluation Strategy (evaluation actions are audited)

---

## References

- Certificate Transparency: https://certificate.transparency.dev/
- Git internals: https://git-scm.com/book/en/v2/Git-Internals-Git-Objects
- SHA-256: https://nvlpubs.nist.gov/nistpubs/FIPS/NIST.FIPS.180-4.pdf
- SOX compliance: https://www.sec.gov/rules/final/33-8238.htm

---

## Notes

- Consider Merkle tree for more efficient verification in future
- Evaluate batch hashing for high-volume scenarios
- Implement alerting for verification failures
- Document audit log format for external analysis tools

**Status**: Accepted  
**Last Updated**: 2026-04-04
