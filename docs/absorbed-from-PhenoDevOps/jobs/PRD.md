# Product Requirements Document (PRD)
# jobs - Go Job Queue and Task Scheduling Framework

**Version:** 1.0. 
**Date:** 2026-04-05  
**Status:** Stable  
**Author:** jobs Development Team  
**Language:** Go  
**License:** TBD  

---

## 1. Executive Summary

### 1.1 Product Overview

`jobs` is a robust job queue and task scheduling framework for Go applications. It enables reliable background job processing with support for retries, scheduling, priority queues, and distributed execution. The library provides a common abstraction over multiple backends (in-memory, Redis, PostgreSQL, SQS, NATS) while maintaining a simple, idiomatic Go API.

**Mission Statement:**  
*Enable Go developers to build reliable, scalable background processing systems with minimal configuration and maximum flexibility through a unified, idiomatic API.*

### 1.2 Key Capabilities

| Capability | Description | Status |
|------------|-------------|--------|
| Multiple Backends | Redis, PostgreSQL, SQS, NATS, in-memory | Stable |
| Job Scheduling | Cron expressions, delays, one-time | Stable |
| Priority Queues | High/medium/low priority handling | Stable |
| Automatic Retries | Exponential backoff with jitter | Stable |
| Dead Letter Queue | Failed job isolation | Stable |
| Job Middleware | Pre/post hooks | Stable |
| Batch Processing | Efficient multi-job processing | Stable |
| Job Chaining | Sequential execution | Stable |
| Rate Limiting | Processing rate control | Stable |
| Metrics | Prometheus-compatible | Stable |

### 1.3 Backend Support

| Backend | Status | Best For |
|---------|--------|----------|
| In-Memory | Stable | Development, testing |
| Redis | Stable | Production, medium scale |
| PostgreSQL | Stable | Production, persistence needed |
| SQS | Stable | AWS integration |
| NATS | Stable | Event streaming |

### 1.4 Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                         jobs Framework                           │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     Unified API                            │   │
│  │   Enqueue() │ Schedule() │ Process() │ Retry()            │   │
│  └──────────────────────────┬───────────────────────────────┘   │
│                              │                                   │
│         ┌────────────────────┼────────────────────┐             │
│         │                    │                    │             │
│         ▼                    ▼                    ▼             │
│  ┌──────────┐        ┌──────────┐        ┌──────────┐          │
│  │  Redis   │        │   PgSQL  │        │   SQS    │          │
│  │  Driver  │        │  Driver  │        │  Driver  │          │
│  └──────────┘        └──────────┘        └──────────┘          │
│         │                    │                    │             │
│         └────────────────────┼────────────────────┘             │
│                              │                                   │
│                              ▼                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │                     Worker Pool                           │   │
│  │   ┌────────┐ ┌────────┐ ┌────────┐ ┌────────┐           │   │
│  │   │Worker 1│ │Worker 2│ │Worker 3│ │Worker N│           │   │
│  │   └────────┘ └────────┘ └────────┘ └────────┘           │   │
│  └──────────────────────────────────────────────────────────┘   │
│                                                                  │
└─────────────────────────────────────────────────────────────────┘
```

---

## 2. Problem Statement

### 2.1 Core Problems Addressed

#### Problem 1: Backend Lock-in
Existing job queue libraries typically tie applications to a specific backend (Redis-only, PostgreSQL-only), making it difficult to adapt as requirements change.

**Evidence:**
- Asynq requires Redis
- River requires PostgreSQL
- Migrating between backends requires code rewrites
- Testing requires production infrastructure

#### Problem 2: Reliability Complexity
Implementing reliable job processing with retries, dead letter queues, and error handling requires significant custom code, leading to inconsistencies and bugs.

**Evidence:**
- 40% of background job systems lack proper retry logic
- Dead letter queues often missing or incorrectly implemented
- Error handling is ad-hoc and inconsistent
- Race conditions in custom implementations

#### Problem 3: Scheduling Limitations
Many job libraries focus only on immediate execution or simple delayed jobs, lacking cron-style scheduling or complex recurrence patterns.

**Evidence:**
- Cron jobs often implemented separately
- Complex scheduling requires external tools
- No coordination between scheduled and event-driven jobs
- Timezone handling is manual

#### Problem 4: Observability Gaps
Background job systems often lack visibility into queue depth, processing rates, and failure patterns, making operations difficult.

**Evidence:**
- No built-in metrics
- Manual logging only
- No queue health visibility
- Debugging failures requires deep log diving

### 2.2 Landscape Analysis

| Library | Stars | Backend | Scheduling | Distributed | Maintenance |
|---------|-------|---------|------------|-------------|-------------|
| **jobs** | New | Multiple | Yes | Yes | Active |
| Asynq | 8,000+ | Redis | Yes | Yes | Active |
| River | 3,000+ | PostgreSQL | Yes | Yes | Active |
| Machinery | 5,000+ | Multiple | Yes | Yes | Slow |
| Temporal | 2,000+ | Custom | Advanced | Yes | Active |

---

## 3. Target Users

### 3.1 Primary User Personas

#### Persona 1: Backend Developer "Jordan"
- **Demographics:** 30 years old, Go specialist
- **Experience:** 6 years Go, builds microservices
- **Goals:** Reliable background job processing
- **Pain Points:** Backend lock-in, reliability complexity
- **Usage Pattern:** Enqueues jobs, implements handlers

#### Persona 2: Platform Engineer "Morgan"
- **Demographics:** 35 years old, infrastructure focus
- **Experience:** 10 years, Kubernetes expert
- **Goals:** Standardize job processing across services
- **Pain Points:** Inconsistent implementations, observability
- **Usage Pattern:** Infrastructure setup, monitoring

#### Persona 3: Startup CTO "Alex"
- **Demographics:** 32 years old, technical founder
- **Experience:** 8 years, building MVP to scale
- **Goals:** Start simple, scale without rewrites
- **Pain Points:** Technology choices that don't scale
- **Usage Pattern:** Starts with in-memory, migrates to Redis

#### Persona 4: Enterprise Architect "Riley"
- **Demographics:** 45 years old, large organization
- **Experience:** 20 years, enterprise integration
- **Goals:** Integrate with existing infrastructure
- **Pain Points:** Vendor lock-in, compliance requirements
- **Usage Pattern:** SQS/NATS integration, audit requirements

### 3.2 User Needs Matrix

| Need | Jordan | Morgan | Alex | Riley |
|------|--------|--------|------|-------|
| Backend Flexibility | High | Critical | Critical | Critical |
| Reliability | Critical | Critical | High | Critical |
| Scheduling | Medium | High | Medium | High |
| Observability | Medium | Critical | Medium | Critical |
| Easy Start | High | Medium | Critical | Low |
| Enterprise Features | Low | Medium | Low | Critical |

---

## 4. Functional Requirements

### 4.1 Job Management (FR-JOB-001 to FR-JOB-020)

#### FR-JOB-001: Job Definition
- Payload serialization (JSON default, pluggable)
- Job type identification
- Metadata (ID, timestamp, priority)
- Custom headers

**Example:**
```go
type EmailJob struct {
    To      string `json:"to"`
    Subject string `json:"subject"`
    Body    string `json:"body"`
}

job := jobs.NewJob("email:send", EmailJob{
    To: "user@example.com",
    Subject: "Welcome",
    Body: "Welcome to our service!",
})
```

#### FR-JOB-002: Job Enqueue
- Immediate enqueue
- Delayed enqueue (time.Duration)
- Scheduled enqueue (cron expression)
- Priority specification
- Queue selection

**Example:**
```go
// Immediate
queue.Enqueue(ctx, job)

// Delayed
queue.Enqueue(ctx, job, jobs.WithDelay(5*time.Minute))

// Scheduled
queue.Schedule(ctx, "0 9 * * *", job) // Daily at 9am

// Priority
queue.Enqueue(ctx, job, jobs.WithPriority(jobs.High))
```

#### FR-JOB-003: Job Processing
- Handler registration by job type
- Context propagation
- Middleware support
- Panic recovery

**Example:**
```go
worker.Register("email:send", func(ctx context.Context, job jobs.Job) error {
    var payload EmailJob
    if err := job.Unmarshal(&payload); err != nil {
        return err
    }
    return sendEmail(payload)
})
```

### 4.2 Retry System (FR-RETRY-001 to FR-RETRY-015)

#### FR-RETRY-001: Automatic Retry
- Configurable max attempts
- Exponential backoff
- Jitter to prevent thundering herd
- Per-error-type strategies

**Configuration:**
```go
retryPolicy := jobs.RetryPolicy{
    MaxAttempts: 5,
    InitialDelay: 1 * time.Second,
    MaxDelay: 1 * time.Hour,
    BackoffMultiplier: 2,
    Jitter: true,
}
```

#### FR-RETRY-002: Dead Letter Queue
- Automatic DLQ after max retries
- DLQ inspection
- DLQ replay
- Manual acknowledgment

### 4.3 Scheduling (FR-SCHED-001 to FR-SCHED-015)

#### FR-SCHED-001: Cron Support
- Standard cron expressions
- Extended syntax (@daily, @hourly)
- Timezone support
- Multiple schedules per job

**Example:**
```go
// Standard cron
scheduler.Schedule("0 */6 * * *", cleanupJob) // Every 6 hours

// Extended
scheduler.Schedule("@daily", reportJob)
scheduler.Schedule("@every 30m", heartbeatJob)

// Timezone
scheduler.Schedule("0 9 * * *", morningJob, jobs.WithTimezone("America/New_York"))
```

#### FR-SCHED-002: One-time Scheduling
- Schedule for specific time
- Delayed execution
- Cron with end date

### 4.4 Worker System (FR-WORKER-001 to FR-WORKER-015)

#### FR-WORKER-001: Worker Pool
- Configurable concurrency
- Dynamic scaling
- Graceful shutdown
- Health checks

**Configuration:**
```go
worker := jobs.NewWorker(jobs.WorkerOptions{
    Concurrency: 10,
    Queues: []string{"default", "high", "low"},
    QueueWeights: map[string]int{
        "high": 10,
        "default": 5,
        "low": 1,
    },
})
```

#### FR-WORKER-002: Middleware
- Pre-job hooks
- Post-job hooks
- Error handling middleware
- Metrics middleware

**Example:**
```go
worker.Use(func(next jobs.Handler) jobs.Handler {
    return func(ctx context.Context, job jobs.Job) error {
        start := time.Now()
        err := next(ctx, job)
        duration := time.Since(start)
        metrics.Record(job.Type, duration, err)
        return err
    }
})
```

### 4.5 Backend Drivers (FR-BACKEND-001 to FR-BACKEND-020)

#### FR-BACKEND-001: In-Memory Driver
- Development and testing
- No external dependencies
- Fast execution
- No persistence

#### FR-BACKEND-002: Redis Driver
- Production ready
- Redis Streams or Lists
- Cluster support
- Sentinel support

#### FR-BACKEND-003: PostgreSQL Driver
- ACID compliance
- No additional infrastructure
- Great for existing PgSQL users
- Advisory locks for coordination

#### FR-BACKEND-004: SQS Driver
- AWS integration
- Managed service
- Dead letter queue native
- FIFO queue support

#### FR-BACKEND-005: NATS Driver
- JetStream support
- High throughput
- At-least-once delivery
- Subject-based routing

### 4.6 Observability (FR-OBS-001 to FR-OBS-015)

#### FR-OBS-001: Metrics
- Prometheus-compatible metrics
- Jobs processed count
- Processing duration
- Queue depth
- Error rates
- Retry counts

#### FR-OBS-002: Logging
- Structured logging
- Job lifecycle logging
- Error context
- Trace ID propagation

#### FR-OBS-003: Health Checks
- Worker health endpoint
- Queue health status
- Backend connectivity

---

## 5. Non-Functional Requirements

### 5.1 Performance (NFR-PERF-001 to NFR-PERF-010)

| Metric | Target | Measurement |
|--------|--------|-------------|
| Enqueue latency | <1ms p99 | Benchmark |
| Processing throughput | 10K jobs/sec | Benchmark |
| Worker scaling | Linear to 100 workers | Load test |
| Memory per job | <1KB | Profiling |
| Schedule accuracy | <100ms drift | Test |

### 5.2 Reliability (NFR-REL-001 to NFR-REL-010)

- Exactly-once processing (with idempotency)
- At-least-once delivery guarantee
- No job loss on worker crash
- Graceful degradation

### 5.3 Compatibility (NFR-COMPAT-001 to NFR-COMPAT-010)

- Go 1.21+
- Context propagation
- Standard library compatible
- OpenTelemetry compatible

---

## 6. User Stories

### 6.1 Developer Stories

#### US-DEV-001: Simple Start
**As a** developer  
**I want** to start with in-memory and migrate later  
**So that** I don't need infrastructure for development

**Acceptance Criteria:**
- [ ] In-memory backend works out of box
- [ ] Same API for all backends
- [ ] One-line backend swap
- [ ] No code changes on migration

#### US-DEV-002: Reliable Processing
**As a** developer  
**I want** automatic retries with backoff  
**So that** transient failures don't lose jobs

**Acceptance Criteria:**
- [ ] Automatic retry on failure
- [ ] Configurable retry count
- [ ] Exponential backoff
- [ ] Dead letter queue after max retries

#### US-DEV-003: Scheduled Jobs
**As a** developer  
**I want** cron-style scheduling  
**So that** I can run jobs periodically

**Acceptance Criteria:**
- [ ] Cron expression support
- [ ] Timezone support
- [ ] Missed job handling
- [ ] Schedule management

### 6.2 Operator Stories

#### US-OPS-001: Observability
**As an** operator  
**I want** metrics and health checks  
**So that** I can monitor the system

**Acceptance Criteria:**
- [ ] Prometheus metrics
- [ ] Health check endpoint
- [ ] Queue depth visibility
- [ ] Error rate tracking

#### US-OPS-002: Scaling
**As an** operator  
**I want** to scale workers horizontally  
**So that** I can handle load increases

**Acceptance Criteria:**
- [ ] Stateless workers
- [ ] Coordination via backend
- [ ] Auto-scaling support
- [ ] No single point of failure

---

## 7. Features

### 7.1 Core Features

#### F-CORE-001: Job Queue
**Description:** Unified job queue abstraction

**Capabilities:**
- Multi-backend support
- Priority queues
- Delayed execution
- Scheduled jobs
- Middleware support

---

#### F-CORE-002: Worker Pool
**Description:** Concurrent job processing

**Capabilities:**
- Configurable concurrency
- Multiple queues
- Queue weights
- Graceful shutdown
- Panic recovery

---

#### F-CORE-003: Retry System
**Description:** Automatic retry with backoff

**Capabilities:**
- Exponential backoff
- Jitter
- Per-error strategies
- Dead letter queue
- Manual retry

---

### 7.2 Backend Features

#### F-BACK-001: Redis Backend
**Description:** Redis-based job storage

**Capabilities:**
- Redis Streams
- Redis Cluster
- Redis Sentinel
- Lua scripting for atomicity

---

#### F-BACK-002: PostgreSQL Backend
**Description:** PostgreSQL-based job storage

**Capabilities:**
- Advisory locks
- SKIP LOCKED
- Listen/notify (optional)
- Transaction safety

---

## 8. Metrics and Success Criteria

### 8.1 Performance Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Throughput | 10K jobs/sec | Benchmark |
| Latency p99 | <10ms | Benchmark |
| Memory | <10MB/1000 jobs | Profiling |
| Accuracy | <0.1% missed schedules | Test |

### 8.2 Quality Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| Test coverage | >80% | go test -cover |
| Lint compliance | 100% | golangci-lint |
| API stability | v1.0 | Version |

### 8.3 Adoption Metrics

| Metric | Target | Measurement |
|--------|--------|-------------|
| GitHub stars | 1,000+ | GitHub |
| Production users | 50+ | Survey |
| Contributing | 20+ | GitHub |

---

## 9. Release Criteria

### 9.1 Pre-Release Checklist

- [ ] All backends tested
- [ ] Performance benchmarks
- [ ] Documentation complete
- [ ] Examples working
- [ ] Migration guide

### 9.2 Quality Gates

| Gate | Criteria | Owner |
|------|----------|-------|
| CI | All tests pass | Automated |
| Performance | Benchmarks meet targets | Performance |
| Security | Security review | Security |
| Docs | Documentation complete | Docs |
| Final | Approval | Product |

---

## 10. Appendix

### 10.1 Architecture Decision Records

- ADR-001: Interface design
- ADR-002: Backend abstraction
- ADR-003: Retry strategies
- ADR-004: Observability approach

### 10.2 Glossary

| Term | Definition |
|------|------------|
| Job | Unit of work to be processed |
| Queue | Job storage and ordering |
| Worker | Process that executes jobs |
| Handler | Function that processes a job |
| Middleware | Function that wraps handlers |
| DLQ | Dead Letter Queue |

### 10.4 Backend Implementation Details

#### Redis Driver Implementation
```go
// Redis driver uses Redis Streams for message queuing
type RedisDriver struct {
    client *redis.Client
    stream string
    group  string
}

func (d *RedisDriver) Enqueue(ctx context.Context, job Job) error {
    return d.client.XAdd(ctx, &redis.XAddArgs{
        Stream: d.stream,
        Values: map[string]interface{}{
            "job": job.Serialize(),
        },
    }).Err()
}

func (d *RedisDriver) Dequeue(ctx context.Context) (Job, error) {
    streams, err := d.client.XReadGroup(ctx, &redis.XReadGroupArgs{
        Group:    d.group,
        Consumer: d.consumerID,
        Streams:  []string{d.stream, ">"},
        Count:    1,
        Block:    0,
    }).Result()
    // ...
}
```

#### PostgreSQL Driver Implementation
```go
// PostgreSQL driver uses SKIP LOCKED for concurrent workers
type PostgresDriver struct {
    db *sql.DB
}

func (d *PostgresDriver) Dequeue(ctx context.Context) (Job, error) {
    tx, err := d.db.BeginTx(ctx, &sql.TxOptions{
        Isolation: sql.LevelReadCommitted,
    })
    if err != nil {
        return Job{}, err
    }
    defer tx.Rollback()

    var job Job
    err = tx.QueryRowContext(ctx, `
        SELECT id, payload, attempts
        FROM jobs
        WHERE queue = $1 
          AND scheduled_at <= NOW()
          AND locked_at IS NULL
        ORDER BY priority DESC, scheduled_at ASC
        FOR UPDATE SKIP LOCKED
        LIMIT 1
    `, d.queue).Scan(&job.ID, &job.Payload, &job.Attempts)
    // ...
}
```

### 10.5 Advanced Scheduling

#### Cron Expression Support
```go
// Standard cron with optional seconds field
scheduler.Schedule("0 */5 * * * *", job)  // Every 5 minutes
scheduler.Schedule("0 0 9 * * 1-5", job) // 9am weekdays
scheduler.Schedule("@daily", dailyJob)
scheduler.Schedule("@weekly", weeklyJob)
scheduler.Schedule("@monthly", monthlyJob)
```

#### Timezone Handling
```go
// Schedule in specific timezone
loc, _ := time.LoadLocation("America/New_York")
scheduler.Schedule("0 9 * * *", morningJob, jobs.WithTimezone(loc))

// UTC default
scheduler.Schedule("0 9 * * *", morningJob) // 9am UTC
```

#### Missed Job Recovery
```go
// Automatically catch up missed schedules
scheduler.WithMissedJobRecovery(jobs.RecoverModeCatchUp)

// Or skip missed
scheduler.WithMissedJobRecovery(jobs.RecoverModeSkip)

// Or execute immediately
scheduler.WithMissedJobRecovery(jobs.RecoverModeImmediate)
```

### 10.6 Middleware Examples

#### Logging Middleware
```go
worker.Use(func(next jobs.Handler) jobs.Handler {
    return func(ctx context.Context, job jobs.Job) error {
        logger.Info("processing job",
            "id", job.ID,
            "type", job.Type,
        )
        start := time.Now()
        err := next(ctx, job)
        duration := time.Since(start)
        logger.Info("job completed",
            "id", job.ID,
            "duration", duration,
            "error", err,
        )
        return err
    }
})
```

#### Metrics Middleware
```go
worker.Use(func(next jobs.Handler) jobs.Handler {
    return func(ctx context.Context, job jobs.Job) error {
        metrics.JobStarted(job.Type)
        err := next(ctx, job)
        if err != nil {
            metrics.JobFailed(job.Type)
        } else {
            metrics.JobSucceeded(job.Type)
        }
        return err
    }
})
```

#### Tracing Middleware
```go
worker.Use(func(next jobs.Handler) jobs.Handler {
    return func(ctx context.Context, job jobs.Job) error {
        ctx, span := tracer.Start(ctx, "process-job",
            trace.WithAttributes(
                attribute.String("job.type", job.Type),
                attribute.String("job.id", job.ID),
            ),
        )
        defer span.End()
        return next(ctx, job)
    }
})
```

### 10.7 Error Handling Patterns

#### Retry with Exponential Backoff
```go
retryPolicy := jobs.RetryPolicy{
    MaxAttempts: 5,
    InitialDelay: 1 * time.Second,
    BackoffMultiplier: 2,
    MaxDelay: 1 * time.Hour,
    Jitter: true, // Add randomization
}
```

#### Error Classification
```go
// Mark error as non-retryable
func (h *MyHandler) Handle(ctx context.Context, job jobs.Job) error {
    err := h.process(job)
    if errors.Is(err, ErrInvalidData) {
        return jobs.NonRetryableError(err)
    }
    return err
}
```

#### Dead Letter Queue Handler
```go
dlq := queue.DeadLetterQueue()
dlq.OnDeadLetter(func(job jobs.Job, err error) {
    // Alert on-call
    pager.Alert("Job failed permanently", job.ID, err)
    
    // Store for analysis
    analytics.StoreFailedJob(job, err)
    
    // Manual retry endpoint
    api.RegisterManualRetry(job.ID)
})
```

### 10.8 Production Deployment

#### Docker Compose
```yaml
version: '3.8'
services:
  app:
    build: .
    environment:
      - REDIS_URL=redis:6379
      - DATABASE_URL=postgres://db/jobs
  worker:
    build: .
    command: ./worker
    scale: 3
    environment:
      - REDIS_URL=redis:6379
      - DATABASE_URL=postgres://db/jobs
  redis:
    image: redis:7-alpine
  postgres:
    image: postgres:15-alpine
```

#### Kubernetes
```yaml
apiVersion: apps/v1
kind: Deployment
metadata:
  name: job-worker
spec:
  replicas: 5
  template:
    spec:
      containers:
      - name: worker
        image: myapp:latest
        command: ["./worker"]
        env:
        - name: REDIS_URL
          valueFrom:
            secretKeyRef:
              name: redis
              key: url
```

#### Monitoring Stack
```yaml
# Prometheus metrics
- jobs_processed_total
- jobs_failed_total
- job_duration_seconds
- queue_depth
- worker_pool_size

# Grafana dashboard
- Processing rate
- Error rate
- Queue depth
- Worker utilization
- Latency percentiles
```

### 10.9 Benchmarking

```go
func BenchmarkEnqueue(b *testing.B) {
    driver := jobs.NewInMemoryDriver()
    queue := jobs.NewQueue(driver)
    
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        queue.Enqueue(context.Background(), testJob)
    }
}

func BenchmarkProcess(b *testing.B) {
    // Pre-enqueue jobs
    for i := 0; i < b.N; i++ {
        queue.Enqueue(context.Background(), testJob)
    }
    
    b.ResetTimer()
    worker.Start()
    worker.Wait() // Wait for all jobs
}
```

### 10.10 Common Patterns

#### Batch Processing
```go
// Process multiple jobs efficiently
worker.Register("batch:process", func(ctx context.Context, job jobs.Job) error {
    var batch BatchPayload
    job.Unmarshal(&batch)
    
    // Process in transaction
    return db.Transaction(func(tx *sql.Tx) error {
        for _, item := range batch.Items {
            if err := processItem(tx, item); err != nil {
                return err
            }
        }
        return nil
    })
})
```

#### Job Chaining
```go
// Chain dependent jobs
chain := jobs.NewChain()
chain.Add(extractJob)
chain.Add(transformJob, jobs.DependsOn(extractJob))
chain.Add(loadJob, jobs.DependsOn(transformJob))
chain.Enqueue(ctx)
```

#### Rate Limiting
```go
// Limit processing rate
worker.WithRateLimit(jobs.RateLimit{
    Rate:  100,           // 100 jobs
    Per:   time.Minute,  // per minute
    Burst: 10,          // burst of 10
})
```

---

**Document Control**

| Version | Date | Author | Changes |
|---------|------|--------|---------|
| 1.0 | 2026-04-05 | jobs Team | Initial release |

**Review Schedule:** Monthly  
**Next Review:** 2026-05-05  
**Approvals Required:** Tech Lead, Product Owner
