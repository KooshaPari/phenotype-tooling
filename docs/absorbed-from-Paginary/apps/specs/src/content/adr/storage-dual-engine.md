# Architecture Decision Record: Storage Engine

**Status**: Accepted  
**Date**: 2026-04-04  
**Author**: Flagward Architecture Team  
**Deciders**: Platform Engineering Team, CTO  

---

## Context

Flagward needs a storage solution that balances simplicity for small deployments with scalability for production use. The system must support both single-node deployments (for development and small teams) and distributed deployments (for enterprise use).

Key requirements:
1. **Zero-config option**: Should work out of the box without external dependencies
2. **Production scalability**: Must handle high-throughput read workloads
3. **ACID compliance**: Flag changes must be atomic and durable
4. **JSON support**: Flexible schema for flag rules and metadata
5. **Operational simplicity**: Easy backups, monitoring, and maintenance

---

## Decision

We will support a **dual-mode storage architecture**:

1. **SQLite** for development, single-node deployments, and edge use cases
2. **PostgreSQL** for production, multi-node deployments, and high-availability requirements

Both storage engines will use an identical schema and be abstracted behind a common interface.

### Rationale

**Why SQLite for simple deployments:**
- Zero configuration (single file)
- No separate process required
- Excellent read performance (in-memory page cache)
- ACID compliant
- Built-in JSON support (JSON1 extension)
- Cross-platform (works everywhere Bun runs)
- Easy backup (copy file)

**Why PostgreSQL for production:**
- Industry standard for production workloads
- Excellent horizontal scaling (read replicas)
- Row-level security for multi-tenant isolation
- Advanced JSON operations (JSONB indexing)
- Mature ecosystem (backups, monitoring, connection pooling)
- Battle-tested at scale

**Why not other options:**
- **MySQL**: Similar to PostgreSQL but less robust JSON support
- **MongoDB**: No ACID transactions across documents, adds operational complexity
- **Redis**: Not durable by default, data loss risk
- **DynamoDB**: Vendor lock-in, complex for simple use cases
- **Single storage option**: Would compromise either simplicity or scalability

---

## Consequences

### Positive

1. **Progressive complexity**: Start with SQLite, migrate to PostgreSQL when needed
2. **No external dependencies for development**: Single `bun install` and run
3. **Production-ready path**: Clear migration path to PostgreSQL
4. **Operational flexibility**: Choose appropriate storage for deployment context
5. **Reduced vendor lock-in**: Both are open-source with broad support

### Negative

1. **Dual maintenance**: Must test and maintain two storage implementations
2. **Migration complexity**: Need to support SQLite → PostgreSQL migration
3. **Feature parity**: Must ensure both engines support same features
4. **Documentation overhead**: Must document both deployment modes

### Mitigations

1. **Shared abstraction layer**: Single interface (`StorageAdapter`) with two implementations
2. **Automated testing**: CI runs full test suite against both SQLite and PostgreSQL
3. **Migration tooling**: Built-in export/import commands
4. **Feature detection**: Runtime checks for storage capabilities

---

## Implementation Details

### Storage Interface

```typescript
interface StorageAdapter {
  // Connection lifecycle
  connect(): Promise<void>;
  disconnect(): Promise<void>;
  
  // Flags
  getFlag(key: string, environment: string): Promise<Flag | null>;
  getFlags(environment: string): Promise<Flag[]>;
  createFlag(flag: CreateFlagInput): Promise<Flag>;
  updateFlag(key: string, updates: UpdateFlagInput): Promise<Flag>;
  deleteFlag(key: string, environment: string): Promise<void>;
  
  // Segments
  getSegment(key: string, environment: string): Promise<Segment | null>;
  getSegments(environment: string): Promise<Segment[]>;
  createSegment(segment: CreateSegmentInput): Promise<Segment>;
  updateSegment(key: string, updates: UpdateSegmentInput): Promise<Segment>;
  deleteSegment(key: string, environment: string): Promise<void>;
  
  // Audit
  createAuditEntry(entry: AuditEntryInput): Promise<AuditEntry>;
  getAuditLog(filter: AuditFilter): Promise<AuditEntry[]>;
  verifyAuditChain(): Promise<boolean>;
  
  // Migration support
  export(): Promise<ExportData>;
  import(data: ExportData): Promise<void>;
}
```

### Configuration

```typescript
interface StorageConfig {
  type: 'sqlite' | 'postgresql';
  
  // SQLite options
  sqlite?: {
    path: string;           // Default: './flagward.db'
  };
  
  // PostgreSQL options
  postgresql?: {
    host: string;
    port: number;           // Default: 5432
    database: string;
    user: string;
    password: string;
    ssl?: boolean | object;
    poolSize?: number;      // Default: 10
  };
}
```

### Migration Path

```bash
# Development (SQLite)
FLAGWARD_STORAGE_TYPE=sqlite FLAGWARD_SQLITE_PATH=./dev.db bun run start

# Production (PostgreSQL)
FLAGWARD_STORAGE_TYPE=postgresql \
  FLAGWARD_PG_HOST=postgres.internal \
  FLAGWARD_PG_DATABASE=flagward \
  bun run start

# Export from SQLite, import to PostgreSQL
bun run flagward migrate \
  --from sqlite --from-path ./dev.db \
  --to postgresql --to-host postgres.internal --to-database flagward
```

---

## Related Decisions

- ADR-002: Evaluation Strategy (determines read patterns)
- ADR-003: Audit Logging (determines write patterns)

---

## References

- SQLite: https://sqlite.org
- PostgreSQL: https://postgresql.org
- Bun SQLite driver: https://bun.sh/docs/api/sqlite
- node-postgres: https://node-postgres.com/

---

## Notes

- SQLite write performance degrades with high concurrency; use WAL mode
- PostgreSQL connection pooling essential for high-throughput
- Consider Redis as caching layer for PostgreSQL in future (ADR-XXX)

**Status**: Accepted  
**Last Updated**: 2026-04-04
