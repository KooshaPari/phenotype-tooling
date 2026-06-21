# SPEC: Database Migration System

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Data Models](#data-models)
4. [API Specification](#api-specification)
5. [Implementation Details](#implementation-details)
6. [Testing Strategy](#testing-strategy)
7. [Deployment Guide](#deployment-guide)
8. [Security Considerations](#security-considerations)
9. [Performance Characteristics](#performance-characteristics)
10. [Operational Guide](#operational-guide)
11. [Migration Examples](#migration-examples)
12. [Troubleshooting](#troubleshooting)
13. [Appendices](#appendices)

## Overview

### Purpose

This specification defines the Phenotype Database Migration System, a Go-based framework for managing database schema evolution with support for:

- Versioned schema migrations
- Transactional safety
- Programmatic and SQL-based migrations
- Seeding capabilities
- Rollback operations
- Multi-database support

### Scope

**In Scope**:
- Migration definition and execution
- Schema versioning and tracking
- Up/Down migration support
- Seeding infrastructure
- Transaction management
- Observability and monitoring

**Out of Scope**:
- Database administration
- Data replication
- Backup/restore operations
- Query optimization

### Goals

1. **Reliability**: Migrations execute atomically with proper error handling
2. **Observability**: Comprehensive logging and metrics for all operations
3. **Flexibility**: Support for both SQL and programmatic migrations
4. **Safety**: Transactional safety, rollback capabilities, and dry-run support
5. **Integration**: Seamless integration with Phenotype ecosystem

### Non-Goals

1. Database-agnostic ORM functionality
2. Automatic schema generation from models
3. Real-time schema synchronization
4. Multi-master replication support

## Architecture

### System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                    Migration System                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────┐          │
│  │   Migration  │  │   Migration  │  │    Seeder    │          │
│  │   Runner     │  │   Registry   │  │              │          │
│  └──────┬───────┘  └──────┬───────┘  └──────┬───────┘          │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│                    ┌──────┴──────┐                             │
│                    │   State     │                             │
│                    │   Manager   │                             │
│                    └──────┬──────┘                             │
│                           │                                     │
│         ┌─────────────────┼─────────────────┐                   │
│         │                 │                 │                   │
│    ┌────┴────┐      ┌────┴────┐      ┌────┴────┐              │
│    │   Up    │      │  Down   │      │ Status  │              │
│    │Executor │      │Executor │      │  Query  │              │
│    └────┬────┘      └────┬────┘      └────┬────┘              │
│         │                 │                 │                   │
│         └─────────────────┼─────────────────┘                   │
│                           │                                     │
│                    ┌──────┴──────┐                             │
│                    │   Database  │                             │
│                    │   (PostgreSQL)│                           │
│                    └─────────────┘                             │
└─────────────────────────────────────────────────────────────────┘
```

### Component Description

**Migration Runner**: Orchestrates migration execution, manages transactions, and coordinates between components.

**Migration Registry**: Maintains the list of available migrations and their ordering.

**State Manager**: Tracks applied migrations in the database via schema_migrations table.

**Up Executor**: Executes forward migrations with transaction management.

**Down Executor**: Executes rollback migrations with transaction management.

**Seeder**: Handles database seeding with initial/test data.

## Data Models

### Migration Structure

```go
// Migration represents a database migration
type Migration struct {
    // Version is the unique migration identifier
    // Format: Sequential number (001, 002) or timestamp (20240115120000)
    Version string
    
    // Name is the human-readable migration description
    // Example: "create_users_table", "add_email_index"
    Name string
    
    // Up executes the forward migration
    // Must be idempotent and transactional where possible
    Up func(*sql.Tx) error
    
    // Down executes the rollback migration
    // Should reverse all changes made by Up
    Down func(*sql.Tx) error
}
```

### Migration Record

```go
// MigrationRecord tracks an applied migration in the database
type MigrationRecord struct {
    // Version matches the Migration.Version
    Version string `db:"version"`
    
    // Name stores the migration name for reference
    Name string `db:"name"`
    
    // AppliedAt is the timestamp when migration was applied
    AppliedAt time.Time `db:"applied_at"`
    
    // Checksum is the SHA-256 hash of the migration content
    // Used for integrity verification
    Checksum string `db:"checksum"`
    
    // ExecutionTimeMs is the duration of migration execution
    ExecutionTimeMs int `db:"execution_time_ms"`
    
    // AppliedBy identifies who/what applied the migration
    AppliedBy string `db:"applied_by"`
}
```

### Migration Status

```go
// MigrationStatus represents the current state of a migration
type MigrationStatus struct {
    Version string
    Name    string
    Applied bool
    
    // LastError is populated if the migration failed
    LastError *string
    
    // AppliedAt is nil if not applied
    AppliedAt *time.Time
}
```

### Seed Data Structure

```go
// SeedData contains all seed information
type SeedData struct {
    // Users to seed
    Users []UserSeed
    
    // Webhooks to seed
    Webhooks []WebhookSeed
    
    // Jobs to seed
    Jobs []JobSeed
    
    // Custom seed functions for complex scenarios
    CustomSeeds []func(*sql.DB) error
}

type UserSeed struct {
    Email    string
    Name     string
    Password string // Will be hashed
    Role     string
}

type WebhookSeed struct {
    UserID string
    URL    string
    Events []string
}

type JobSeed struct {
    Type    string
    Payload string
    Status  string
}
```

## API Specification

### MigrationRunner Interface

```go
// MigrationRunner manages database migrations
type MigrationRunner interface {
    // Init creates the migrations tracking table
    Init(ctx context.Context) error
    
    // Up executes all pending migrations
    Up(ctx context.Context) error
    
    // UpTo executes migrations up to a specific version
    UpTo(ctx context.Context, version string) error
    
    // Down rolls back the last migration
    Down(ctx context.Context) error
    
    // DownTo rolls back migrations to a specific version
    DownTo(ctx context.Context, version string) error
    
    // Status returns the current migration status for all migrations
    Status(ctx context.Context) ([]MigrationStatus, error)
    
    // Verify checks migration integrity
    Verify(ctx context.Context) error
    
    // DryRun simulates migration execution without applying changes
    DryRun(ctx context.Context, direction Direction) ([]string, error)
}
```

### Runner Configuration

```go
// RunnerConfig contains configuration for MigrationRunner
type RunnerConfig struct {
    // TableName for migration tracking (default: schema_migrations)
    TableName string
    
    // LockTimeout for advisory locks (default: 30s)
    LockTimeout time.Duration
    
    // BatchSize for data migrations (default: 1000)
    BatchSize int
    
    // Logger for structured logging
    Logger *slog.Logger
    
    // Metrics for observability
    Metrics MetricsCollector
    
    // DryRun mode - simulate without executing
    DryRun bool
    
    // AllowOutOfOrder allows migrations to be applied non-sequentially
    AllowOutOfOrder bool
    
    // ValidateChecksums enables checksum verification
    ValidateChecksums bool
}
```

### Seeder Interface

```go
// Seeder handles database seeding
type Seeder interface {
    // Seed applies seed data to the database
    Seed(ctx context.Context, data SeedData) error
    
    // SeedFromFile loads and applies seed data from a file
    SeedFromFile(ctx context.Context, path string) error
    
    // Clear removes all seeded data
    Clear(ctx context.Context) error
    
    // Truncate removes all data from seedable tables
    Truncate(ctx context.Context) error
}
```

## Implementation Details

### Transaction Management

PostgreSQL supports transactional DDL, allowing migrations to be atomic:

```go
func (r *MigrationRunner) executeMigration(ctx context.Context, m Migration, direction Direction) error {
    // Begin transaction
    tx, err := r.db.BeginTx(ctx, nil)
    if err != nil {
        return fmt.Errorf("begin transaction: %w", err)
    }
    defer tx.Rollback()
    
    // Execute migration function
    var execErr error
    if direction == Up {
        execErr = m.Up(tx)
    } else {
        execErr = m.Down(tx)
    }
    
    if execErr != nil {
        return fmt.Errorf("migration %s failed: %w", m.Version, execErr)
    }
    
    // Update migration record
    if err := r.updateMigrationRecord(ctx, tx, m, direction); err != nil {
        return fmt.Errorf("update record: %w", err)
    }
    
    // Commit transaction
    if err := tx.Commit(); err != nil {
        return fmt.Errorf("commit transaction: %w", err)
    }
    
    return nil
}
```

### Migration Ordering

Migrations are sorted by version using natural string comparison:

```go
func sortMigrations(migrations []Migration) {
    sort.Slice(migrations, func(i, j int) bool {
        return migrations[i].Version < migrations[j].Version
    })
}
```

### Checksum Calculation

Checksums verify migration integrity:

```go
func calculateChecksum(m Migration) string {
    // Create deterministic representation
    data := fmt.Sprintf("%s:%s", m.Version, m.Name)
    
    hash := sha256.Sum256([]byte(data))
    return hex.EncodeToString(hash[:])
}
```

### Advisory Locking

PostgreSQL advisory locks prevent concurrent migrations:

```go
func (r *MigrationRunner) acquireLock(ctx context.Context) (func(), error) {
    // Generate lock ID from table name hash
    lockID := generateLockID(r.table)
    
    // Try to acquire lock
    _, err := r.db.ExecContext(ctx, 
        "SELECT pg_advisory_lock($1)", lockID)
    if err != nil {
        return nil, fmt.Errorf("acquire lock: %w", err)
    }
    
    // Return release function
    return func() {
        r.db.Exec("SELECT pg_advisory_unlock($1)", lockID)
    }, nil
}
```

## Testing Strategy

### Unit Testing

```go
func TestMigrationRunner_Up(t *testing.T) {
    // Setup test database
    db := setupTestDB(t)
    defer db.Close()
    
    // Create migrations
    migrations := []Migration{
        {
            Version: "001",
            Name:    "create_test_table",
            Up: func(tx *sql.Tx) error {
                _, err := tx.Exec(`CREATE TABLE test (id INT PRIMARY KEY)`)
                return err
            },
            Down: func(tx *sql.Tx) error {
                _, err := tx.Exec(`DROP TABLE test`)
                return err
            },
        },
    }
    
    // Create runner
    runner := NewMigrationRunner(db, migrations, slog.Default())
    
    // Execute
    ctx := context.Background()
    err := runner.Init(ctx)
    require.NoError(t, err)
    
    err = runner.Up(ctx)
    require.NoError(t, err)
    
    // Verify
    var count int
    err = db.QueryRow("SELECT COUNT(*) FROM schema_migrations").Scan(&count)
    require.NoError(t, err)
    assert.Equal(t, 1, count)
}
```

### Integration Testing

```go
func TestMigrationRunner_Integration(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping integration test")
    }
    
    // Start PostgreSQL container
    ctx := context.Background()
    container, db := startPostgresContainer(t, ctx)
    defer container.Terminate(ctx)
    
    // Run migrations
    migrations := LoadMigrations("../migrations")
    runner := NewMigrationRunner(db, migrations, slog.Default())
    
    err := runner.Init(ctx)
    require.NoError(t, err)
    
    err = runner.Up(ctx)
    require.NoError(t, err)
    
    // Verify schema
    verifySchema(t, db)
}
```

### Migration Testing Checklist

- [ ] Migration applies cleanly
- [ ] Migration is idempotent
- [ ] Rollback works correctly
- [ ] Data is preserved during migrations
- [ ] Checksums match
- [ ] Concurrent execution is safe
- [ ] Error cases are handled
- [ ] Performance is acceptable

## Deployment Guide

### Prerequisites

1. PostgreSQL 14+ database
2. Go 1.21+ runtime
3. Database credentials with DDL privileges
4. Network connectivity to database

### Installation

```bash
# Add to go.mod
go get github.com/KooshaPari/phenotype-go-kit/migrations

# Import in your application
import "github.com/KooshaPari/phenotype-go-kit/migrations"
```

### Configuration

```go
// Initialize migration runner
db, err := sql.Open("postgres", dsn)
if err != nil {
    log.Fatal(err)
}

migrations := []migrations.Migration{
    // Define your migrations here
}

runner := migrations.NewMigrationRunner(
    db, 
    migrations,
    slog.Default(),
)
```

### Execution

```go
func main() {
    ctx := context.Background()
    
    // Initialize (create tracking table)
    if err := runner.Init(ctx); err != nil {
        log.Fatal(err)
    }
    
    // Run pending migrations
    if err := runner.Up(ctx); err != nil {
        log.Fatal(err)
    }
    
    log.Println("Migrations complete")
}
```

### CI/CD Integration

```yaml
migrations:
  stage: deploy
  script:
    - go run ./cmd/migrate up
  environment:
    name: production
  only:
    - main
```

## Security Considerations

### Access Control

1. **Migration Execution**: Restrict to deployment service accounts
2. **Database Permissions**: DDL privileges required
3. **Audit Logging**: Log all migration operations
4. **Change Approval**: Require approval for production migrations

### Data Protection

1. **PII Handling**: Never log or expose PII in migrations
2. **Secrets**: Use parameterized queries, never hardcode secrets
3. **Encryption**: Use encrypted connections (TLS)

### Injection Prevention

```go
// Good: Parameterized query
_, err := tx.Exec("UPDATE users SET status = $1 WHERE id = $2", status, id)

// Bad: String concatenation (vulnerable to injection)
query := fmt.Sprintf("UPDATE users SET status = '%s' WHERE id = %s", status, id)
```

## Performance Characteristics

### Benchmarks

| Operation | Time | Notes |
|-----------|------|-------|
| Small DDL (<1MB) | 10-100ms | CREATE TABLE, ADD COLUMN |
| Index Creation | 1s - 10min | Depends on table size |
| Data Migration | 1s - 1hr | Depends on row count |
| Batch Update (1000) | 100-500ms | With proper batching |

### Optimization Guidelines

1. **Batch Size**: Default 1000, tune based on row size
2. **Index Creation**: Use CREATE INDEX CONCURRENTLY
3. **Vacuum**: Run after large changes
4. **Timing**: Schedule during low-traffic periods

## Operational Guide

### Health Checks

```sql
-- Check migration status
SELECT version, name, applied_at 
FROM schema_migrations 
ORDER BY version DESC;

-- Check for failed migrations
SELECT version, name, applied_at
FROM schema_migrations
WHERE execution_time_ms > 60000;  -- Slow migrations
```

### Monitoring

**Metrics to Track**:
- Migration duration
- Migration error rate
- Database connection pool status
- Lock wait times

**Alerting**:
- Migration duration > threshold
- Migration failures
- Checksum mismatches

### Troubleshooting

**Migration Stuck**:
```sql
-- Check for locks
SELECT * FROM pg_locks WHERE locktype = 'advisory';

-- Release if necessary (CAREFUL!)
SELECT pg_advisory_unlock_all();
```

**Checksum Mismatch**:
1. Investigate cause
2. Manual verification required
3. Consider migration as failed
4. Manual intervention may be needed

## Migration Examples

### Basic Table Creation

```go
{
    Version: "001",
    Name:    "create_users_table",
    Up: func(tx *sql.Tx) error {
        _, err := tx.Exec(`
            CREATE TABLE users (
                id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                email VARCHAR(255) UNIQUE NOT NULL,
                name VARCHAR(255),
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        `)
        return err
    },
    Down: func(tx *sql.Tx) error {
        _, err := tx.Exec(`DROP TABLE users`)
        return err
    },
}
```

### Adding Index

```go
{
    Version: "002",
    Name:    "add_user_email_index",
    Up: func(tx *sql.Tx) error {
        _, err := tx.Exec(`
            CREATE INDEX CONCURRENTLY idx_users_email 
            ON users(email)
        `)
        return err
    },
    Down: func(tx *sql.Tx) error {
        _, err := tx.Exec(`DROP INDEX idx_users_email`)
        return err
    },
}
```

### Data Migration

```go
{
    Version: "003",
    Name:    "migrate_user_data",
    Up: func(tx *sql.Tx) error {
        // Batch update
        _, err := tx.Exec(`
            UPDATE users 
            SET status = 'active' 
            WHERE status IS NULL
        `)
        return err
    },
    Down: func(tx *sql.Tx) error {
        // Revert if possible
        _, err := tx.Exec(`
            UPDATE users 
            SET status = NULL 
            WHERE status = 'active'
        `)
        return err
    },
}
```

## Appendices

### Appendix A: SQL Reference

**Create Migration Table**:
```sql
CREATE TABLE schema_migrations (
    version VARCHAR(255) PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    applied_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    checksum VARCHAR(64),
    execution_time_ms INTEGER,
    applied_by VARCHAR(255)
);
```

**Check Applied Migrations**:
```sql
SELECT * FROM schema_migrations ORDER BY version;
```

**Manual Rollback (Emergency)**:
```sql
-- WARNING: Only in emergencies
DELETE FROM schema_migrations WHERE version = 'xxx';
```

### Appendix B: Environment Variables

| Variable | Description | Default |
|----------|-------------|---------|
| `DATABASE_URL` | PostgreSQL connection string | required |
| `MIGRATIONS_TABLE` | Migration tracking table | `schema_migrations` |
| `MIGRATIONS_DRY_RUN` | Simulate without executing | `false` |
| `MIGRATIONS_BATCH_SIZE` | Batch size for data migrations | `1000` |

### Appendix C: CLI Reference

```bash
# Run all pending migrations
go run ./cmd/migrate up

# Rollback last migration
go run ./cmd/migrate down

# Check status
go run ./cmd/migrate status

# Dry run
go run ./cmd/migrate up --dry-run

# Specific version
go run ./cmd/migrate up-to 005
```

---

*Specification Version: 1.0*
*Last Updated: 2026-04-05*
*Status: Active*
