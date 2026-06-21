# jobs Specification

**Version:** 1.0.0  
**Status:** Stable  
**Date:** 2026-04-05  
**Lines:** 2,500+

---

## Table of Contents

1. [Executive Summary](#executive-summary)
2. [State of the Art Research](#state-of-the-art-research)
3. [System Architecture](#system-architecture)
4. [Component Specifications](#component-specifications)
5. [Data Models](#data-models)
6. [API Reference](#api-reference)
7. [Configuration](#configuration)
8. [Performance Targets](#performance-targets)
9. [Security Model](#security-model)
10. [Testing Strategy](#testing-strategy)
11. [Deployment Guide](#deployment-guide)
12. [Monitoring & Observability](#monitoring--observability)
13. [Scaling Strategies](#scaling-strategies)
14. [Troubleshooting](#troubleshooting)
15. [Appendices](#appendices)

---

## Executive Summary

The `jobs` library provides a robust job queue and task scheduling framework for Go applications. It enables reliable background job processing with support for retries, scheduling, priority queues, and distributed execution.

### Purpose and Scope

The jobs library addresses the need for:

- **Background Job Processing**: Asynchronous task execution
- **Scheduled Jobs**: Cron-like job scheduling
- **Retry Logic**: Automatic failure recovery
- **Job Prioritization**: Priority-based queue ordering
- **Distributed Processing**: Multi-worker job distribution
- **Dead Letter Queues**: Failed job isolation

### Target Use Cases

| Use Case | Description | Features Used |
|----------|-------------|---------------|
| Email Sending | Async email delivery | Queue + Retry |
| Data Import | Large dataset processing | Scheduled + Priority |
| Report Generation | Background report creation | Queue + Timeout |
| Webhook Delivery | Reliable webhook calls | Retry + DLQ |
| Data Sync | Cross-system synchronization | Scheduled + Distributed |
| Image Processing | Async image transformations | Queue + Priority |
| Database Cleanup | Maintenance tasks | Scheduled + Cron |
| Notification Dispatch | Push notifications | Queue + Retry |
| Analytics Aggregation | Background stats computation | Scheduled + Distributed |
| Cache Warming | Pre-populating cache | Queue + Priority |

### Key Features

- **Multiple Backends**: In-memory, Redis, PostgreSQL, SQS, NATS
- **Job Scheduling**: Cron expressions, delays, and one-time jobs
- **Priority Queues**: High/medium/low priority handling
- **Automatic Retries**: Exponential backoff with jitter
- **Dead Letter Queue**: Failed job isolation and analysis
- **Job Middleware**: Pre/post job hooks
- **Metrics & Monitoring**: Prometheus-compatible metrics
- **Distributed Workers**: Multi-instance job processing
- **Batch Processing**: Process multiple jobs efficiently
- **Job Chaining**: Sequential job execution
- **Rate Limiting**: Control job processing rates

### Success Metrics

- Job enqueue latency: < 1ms p99
- Job processing throughput: 10,000 jobs/sec
- Retry success rate: > 95%
- Worker scaling: Linear up to 100 workers
- Memory per job: < 1KB
- Schedule accuracy: < 100ms drift

---

## State of the Art Research

### Go Job Queue Library Landscape

| Library | Stars | Features | Backends | Distributed | Maintenance |
|---------|-------|----------|----------|-------------|-------------|
| **this library (jobs)** | New | Full | Multiple | Yes | Active |
| **Asynq** | 8,000+ | Good | Redis | Yes | Active |
| **River** | 3,000+ | Good | PostgreSQL | Yes | Active |
| **Machinery** | 5,000+ | Full | Multiple | Yes | Slow |
| **Temporal Go** | 2,000+ | Enterprise | Custom | Yes | Active |
| **gocelery** | 1,500+ | Basic | Redis | No | Stale |
| **NATS JetStream** | 4,000+ | Streaming | NATS | Yes | Active |
| **Faktory** | 5,000+ | Full | Redis | Yes | Active |

### Detailed Library Comparison

#### Asynq Analysis

```go
// Asynq example - Redis-based task queue
package asynq_example

import (
    "context"
    "encoding/json"
    "log"
    "time"
    
    "github.com/hibiken/asynq"
)

// Task payload type
type EmailTaskPayload struct {
    UserID     int    `json:"user_id"`
    TemplateID string `json:"template_id"`
    Subject    string `json:"subject"`
}

func NewEmailTask(userID int, templateID, subject string) (*asynq.Task, error) {
    payload, err := json.Marshal(EmailTaskPayload{
        UserID:     userID,
        TemplateID: templateID,
        Subject:    subject,
    })
    if err != nil {
        return nil, err
    }
    return asynq.NewTask("email:send", payload), nil
}

// Client setup with advanced options
func createAsynqClient() *asynq.Client {
    redisOpt := asynq.RedisClientOpt{
        Addr:     "localhost:6379",
        Password: "",
        DB:       0,
        PoolSize: 20,
    }
    
    client := asynq.NewClient(redisOpt)
    return client
}

// Enqueue with options
func enqueueWithOptions(client *asynq.Client) error {
    task, _ := NewEmailTask(42, "welcome", "Welcome to our service!")
    
    info, err := client.Enqueue(task,
        // Process immediately
        asynq.Queue("default"),
        // Max retry attempts
        asynq.MaxRetry(5),
        // Timeout per attempt
        asynq.Timeout(30*time.Second),
        // Unique task within 1 hour
        asynq.Unique(1*time.Hour),
        // Task priority (lower = higher priority)
        asynq.Priority(10),
    )
    if err != nil {
        return err
    }
    
    log.Printf("Enqueued task: id=%s queue=%s", info.ID, info.Queue)
    return nil
}

// Periodic task configuration
func setupPeriodicTasks(mux *asynq.ServeMux) *asynq.PeriodicTaskManager {
    mgr, _ := asynq.NewPeriodicTaskManager(
        asynq.PeriodicTaskManagerOpts{
            RedisConnOpt: asynq.RedisClientOpt{Addr: "localhost:6379"},
            PeriodicTaskConfigProvider: &StaticConfigProvider{
                configs: []*asynq.PeriodicTaskConfig{
                    {
                        Cronspec: "0 * * * *", // Every hour
                        Task:     asynq.NewTask("reports:hourly", nil),
                        Options: []asynq.Option{
                            asynq.Queue("reports"),
                        },
                    },
                    {
                        Cronspec: "0 0 * * 0", // Weekly on Sunday
                        Task:     asynq.NewTask("cleanup:weekly", nil),
                        Options: []asynq.Option{
                            asynq.Queue("maintenance"),
                        },
                    },
                },
            },
        },
    )
    return mgr
}

// Worker server configuration
func createAsynqServer() *asynq.Server {
    srv := asynq.NewServer(
        asynq.RedisClientOpt{Addr: "localhost:6379"},
        asynq.Config{
            // Number of concurrent workers
            Concurrency: 10,
            // Multiple queues with different priorities
            Queues: map[string]int{
                "critical": 6,
                "default":  3,
                "low":      1,
            },
            // Strict priority (process critical before default)
            StrictPriority: true,
            // Error handler
            ErrorHandler: asynq.ErrorHandlerFunc(func(ctx context.Context, task *asynq.Task, err error) {
                log.Printf("Task failed: %s, error: %v", task.Type(), err)
            }),
        },
    )
    return srv
}
```

**Asynq Pros:**
- Excellent Redis-based implementation
- Built-in monitoring UI
- Strong type safety
- Active maintenance

**Asynq Cons:**
- Redis-only backend
- Limited to Go
- No transactions across job enqueue

#### River Analysis

```go
// River example - PostgreSQL-based job processing
package river_example

import (
    "context"
    "log/slog"
    "time"
    
    "github.com/riverqueue/river"
    "github.com/riverqueue/river/rivertype"
)

// Define a job type
type SendEmailArgs struct {
    UserID    int64  `json:"user_id"`
    Subject   string `json:"subject"`
    Body      string `json:"body"`
}

func (SendEmailArgs) Kind() string { return "send_email" }

// Worker implementation
type SendEmailWorker struct {
    river.WorkerDefaults[SendEmailArgs]
    emailService *EmailService
}

func (w *SendEmailWorker) Work(ctx context.Context, job *river.Job[SendEmailArgs]) error {
    // Job is automatically inserted with transaction
    return w.emailService.Send(ctx, job.Args.UserID, job.Args.Subject, job.Args.Body)
}

// Client with transaction support
func createRiverClient(db pool) (*river.Client, error) {
    workers := river.NewWorkers()
    river.AddWorker(workers, &SendEmailWorker{emailService: newEmailService()})
    
    client, err := river.NewClient(riverpgxv5.New(db), &river.Config{
        Queues: map[string]river.QueueConfig{
            "default": {MaxWorkers: 100},
            "urgent":  {MaxWorkers: 50},
        },
        Workers: workers,
        // Job rescue after 1 hour stuck
        RescueStuckJobsAfter: 1 * time.Hour,
        // Retry policy
        RetryPolicy: &river.RetryPolicy{
            MaxAttempts: 5,
            // Exponential backoff: 1s, 2s, 4s, 8s, 16s
            Backoff: func(attempt int) time.Duration {
                return time.Duration(attempt*attempt) * time.Second
            },
        },
        // Scheduled job executor
        ScheduledJobExecutor: &river.PeriodicJobExecutor{
            // Jobs scheduled with INSERT ... ON CONFLICT DO NOTHING
            // Ensures exactly-once semantics
        },
    })
    if err != nil {
        return nil, err
    }
    
    return client, nil
}

// Insert job within transaction
func insertJobWithTransaction(ctx context.Context, db pool, client *river.Client) error {
    tx, err := db.Begin(ctx)
    if err != nil {
        return err
    }
    defer tx.Rollback(ctx)
    
    // Insert user record
    var userID int64
    err = tx.QueryRow(ctx, 
        "INSERT INTO users (email) VALUES ($1) RETURNING id",
        "user@example.com",
    ).Scan(&userID)
    if err != nil {
        return err
    }
    
    // Insert job within same transaction - atomic!
    _, err = client.InsertTx(ctx, tx, SendEmailArgs{
        UserID:  userID,
        Subject: "Welcome!",
        Body:    "Thanks for signing up!",
    }, &river.InsertOpts{
        Queue:    "urgent",
        Priority: 1, // Higher priority = processed sooner
    })
    if err != nil {
        return err
    }
    
    return tx.Commit(ctx)
}

// Subscribe to job events
func subscribeToJobEvents(client *river.Client) {
    client.Subscribe(river.EventKindJobCompleted, func(event *river.Event) {
        slog.Info("Job completed",
            "job_id", event.Job.ID,
            "duration", event.Job.AttemptedAt.Sub(event.Job.ScheduledAt),
        )
    })
    
    client.Subscribe(river.EventKindJobFailed, func(event *river.Event) {
        slog.Error("Job failed",
            "job_id", event.Job.ID,
            "error", event.Job.Error,
            "attempt", event.Job.Attempt,
        )
    })
}

// Unique job by args
func insertUniqueJob(client *river.Client) error {
    _, err := client.Insert(context.Background(), SendEmailArgs{
        UserID:  123,
        Subject: "Weekly Digest",
    }, &river.InsertOpts{
        UniqueOpts: &river.UniqueOpts{
            // Unique by job kind + serialized args
            ByArgs: true,
            // Unique within 1 hour window
            ByPeriod: 1 * time.Hour,
        },
    })
    return err
}
```

**River Pros:**
- PostgreSQL-based with ACID transactions
- Transactional job enqueue
- Excellent unique job support
- Built-in scheduling
- Very active development

**River Cons:**
- PostgreSQL-only
- Newer library (breaking changes possible)
- Limited ecosystem compared to Asynq

#### Machinery Analysis

```go
// Machinery example - Multi-backend task queue
package machinery_example

import (
    "context"
    "encoding/json"
    "time"
    
    "github.com/RichardKnop/machinery/v2"
    "github.com/RichardKnop/machinery/v2/config"
    "github.com/RichardKnop/machinery/v2/tasks"
)

// Task signatures
type TaskSignatures struct{}

func (t *TaskSignatures) SendEmailTask(userEmail, subject string) *tasks.Signature {
    return &tasks.Signature{
        Name: "send_email",
        Args: []tasks.Arg{
            {Type: "string", Value: userEmail},
            {Type: "string", Value: subject},
        },
        RoutingKey: "email_queue",
        RetryTimeout: 10,
        RetryTimes: 3,
    }
}

// Redis broker + result backend
func createRedisMachinery() (*machinery.Server, error) {
    cnf := &config.Config{
        DefaultQueue:    "machinery_tasks",
        ResultsExpireIn: 3600,
        Redis: &config.RedisConfig{
            Broker:        "redis://localhost:6379",
            DefaultQueue:  "machinery_tasks",
            ResultBackend: "redis://localhost:6379",
            DB:            0,
        },
    }
    
    server, err := machinery.NewServer(cnf)
    if err != nil {
        return nil, err
    }
    
    return server, nil
}

// AMQP broker (RabbitMQ)
func createAMQPMachinery() (*machinery.Server, error) {
    cnf := &config.Config{
        Broker:          "amqp://guest:guest@localhost:5672/",
        DefaultQueue:    "machinery_tasks",
        ResultBackend:   "redis://localhost:6379",
        ResultsExpireIn: 3600,
        AMQP: &config.AMQPConfig{
            Exchange:      "machinery_exchange",
            ExchangeType:  "direct",
            BindingKey:    "machinery_task",
            PrefetchCount: 3,
        },
    }
    
    return machinery.NewServer(cnf)
}

// AWS SQS broker
func createSQSMachinery() (*machinery.Server, error) {
    cnf := &config.Config{
        Broker:          "sqs://ACCESS_KEY_ID:SECRET_ACCESS_KEY@us-east-1",
        DefaultQueue:    "machinery_tasks",
        ResultBackend:   "redis://localhost:6379",
        ResultsExpireIn: 3600,
        SQS: &config.SQSConfig{
            Client: nil, // Will use default AWS credentials chain
            // OR:
            AccessKeyID:     "ACCESS_KEY",
            SecretAccessKey: "SECRET_KEY",
            Region:          "us-east-1",
        },
    }
    
    return machinery.NewServer(cnf)
}

// MongoDB result backend
func createMongoMachinery() (*machinery.Server, error) {
    cnf := &config.Config{
        Broker:        "redis://localhost:6379",
        DefaultQueue:  "machinery_tasks",
        ResultBackend: "mongodb://localhost:27017/machinery",
        MongoDB: &config.MongoDBConfig{
            Client: nil, // Will create new client
        },
    }
    
    return machinery.NewServer(cnf)
}

// Task registration and worker
func setupMachineryWorker(server *machinery.Server) error {
    // Register tasks
    tasks := map[string]interface{}{
        "send_email":      SendEmail,
        "process_image":   ProcessImage,
        "generate_report": GenerateReport,
    }
    
    return server.RegisterTasks(tasks)
}

// Worker with multiple queues
func startMachineryWorker(server *machinery.Server) error {
    worker := server.NewWorker("worker_1", 10)
    
    // Process specific queues
    worker.SetPreTaskHandler(func(signature *tasks.Signature) {
        // Pre-task hook
    })
    
    return worker.Launch()
}

// Chain and group tasks
func createTaskWorkflow(server *machinery.Server) error {
    // Create task signatures
    task1 := &tasks.Signature{
        Name: "download_image",
        Args: []tasks.Arg{
            {Type: "string", Value: "https://example.com/image.jpg"},
        },
    }
    
    task2 := &tasks.Signature{
        Name: "process_image",
    }
    
    task3 := &tasks.Signature{
        Name: "upload_image",
    }
    
    // Chain: task1 -> task2 -> task3
    chain, _ := tasks.NewChain(task1, task2, task3)
    chainID, err := server.SendChain(chain)
    if err != nil {
        return err
    }
    
    // Group: task1, task2, task3 in parallel
    group, _ := tasks.NewGroup(task1, task2, task3)
    groupID, err := server.SendGroup(group, 0)
    if err != nil {
        return err
    }
    
    // Chord: group then callback
    callback := &tasks.Signature{Name: "notify_completion"}
    chord, _ := tasks.NewChord(group, callback)
    chordID, err := server.SendChord(chord, 0)
    if err != nil {
        return err
    }
    
    return nil
}

// Task implementations
func SendEmail(email, subject string) error {
    // Send email implementation
    return nil
}

func ProcessImage(imageData []byte) ([]byte, error) {
    // Process image
    return imageData, nil
}

func GenerateReport(startDate, endDate time.Time) ([]byte, error) {
    // Generate report
    return nil, nil
}
```

**Machinery Pros:**
- Multiple broker backends (Redis, AMQP, SQS)
- Multiple result backends (Redis, MongoDB, Memcache)
- Chains, groups, and chords (complex workflows)
- Mature and stable

**Machinery Cons:**
- Slower maintenance
- Complex configuration
- No built-in scheduling
- JSON-based task args (less type safe)

### Job Queue Patterns

**1. FIFO Queue**
```
┌─────────┐    ┌─────────┐    ┌─────────┐
│ Job A   │ →  │ Job B   │ →  │ Job C   │
└─────────┘    └─────────┘    └─────────┘
   ↑                              ↓
Enqueue                      Dequeue/Process
```

**2. Priority Queue**
```
┌─────────────┐
│ HIGH: Job A │ ← Executed first
├─────────────┤
│ HIGH: Job D │
├─────────────┤
│ MED: Job B  │
├─────────────┤
│ MED: Job E  │
├─────────────┤
│ LOW: Job C  │
└─────────────┘
```

**3. Scheduled Execution**
```
Time →
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
Now:      Job A scheduled for T+1h
T+30min:  Job B scheduled for T+2h
T+1h:     Job A executed
T+1h:     Job C (cron @hourly) executed
T+2h:     Job B executed
T+24h:    Job D (cron @daily) executed
```

**4. Distributed Processing**
```
┌──────────┐     ┌──────────┐     ┌──────────┐
│ Worker 1 │ ←→ │  Queue   │ ←→ │ Worker 2 │
│ (Poll)   │     │ (Redis)  │     │ (Poll)   │
└────┬─────┘     └──────────┘     └────┬─────┘
     │                                │
     └──────────┐    ┌───────────────┘
                ↓    ↓
             ┌──────────┐
             │ Worker 3 │
             │ (Poll)   │
             └──────────┘
```

**5. Job Retry Flow**
```
Job Processing:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Process Job] → Success → [Mark Complete]
       ↓
   Failure
       ↓
[Check Retry Count] → Exceeded → [Move to DLQ]
       ↓
   Below Limit
       ↓
[Calculate Backoff] → [Schedule Retry]
       ↓
[Wait Backoff Period] → [Re-queue Job]
```

**6. Dead Letter Queue**
```
Main Queue Processing:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

Job A (retry 3/3) → FAIL → [DLQ: Job A]
                           ├─ error: timeout
                           ├─ original_queue: default
                           ├─ failed_at: 2026-01-15T10:30:00Z
                           └─ retry_count: 3

Job B (retry 1/3) → FAIL → [Requeue with delay]
       ↓
   After delay → [Retry Job B]
```

### Backend Comparison

| Backend | Persistence | Performance | Scalability | Best For | Complexity |
|---------|-------------|-------------|-------------|----------|------------|
| In-Memory | No | Fastest | Single node | Development | Low |
| Redis | Yes | Fast | Medium | Production | Low |
| PostgreSQL | Yes | Moderate | High | Transactional | Medium |
| SQS | Yes | Moderate | Very High | AWS native | Low |
| NATS | Yes | Fast | High | Real-time | Medium |
| AMQP/RabbitMQ | Yes | Fast | High | Complex routing | High |
| Kafka | Yes | Fast | Very High | Event streaming | High |

### Backend Deep Dive

#### Redis Backend

```go
// Redis backend implementation details
package redis_backend

import (
    "context"
    "encoding/json"
    "fmt"
    "time"
    
    "github.com/redis/go-redis/v9"
)

// Redis queue structure
type RedisBackend struct {
    client     *redis.Client
    queuePrefix string
    scriptSHA   map[string]string
}

// Redis key patterns
const (
    KeyQueueList     = "jobs:queues"           // Set of all queues
    KeyQueue         = "jobs:queue:%s"          // List - pending jobs
    KeyQueuePriority = "jobs:queue:%s:prio"    // Sorted set - priority queue
    KeyQueueScheduled = "jobs:queue:%s:scheduled" // Sorted set - scheduled jobs
    KeyJob           = "jobs:job:%s"           // Hash - job data
    KeyJobProcessing = "jobs:processing:%s"   // Hash - in-progress jobs
    KeyDeadLetter    = "jobs:dlq:%s"           // List - dead letter queue
    KeyStats         = "jobs:stats:%s"          // Hash - queue statistics
    KeyWorkerHeartbeat = "jobs:workers:%s"     // String - worker liveness
)

// Lua scripts for atomic operations
const (
    // Atomic dequeue with job status update
    scriptDequeue = `
        local queue_key = KEYS[1]
        local processing_key = KEYS[2]
        local worker_id = ARGV[1]
        local now = ARGV[2]
        
        -- Get job from queue
        local job_id = redis.call('LPOP', queue_key)
        if not job_id then
            return nil
        end
        
        -- Mark as processing
        redis.call('HSET', processing_key, job_id, worker_id)
        redis.call('HSET', 'jobs:job:' .. job_id, 'status', 'processing')
        redis.call('HSET', 'jobs:job:' .. job_id, 'started_at', now)
        
        return job_id
    `
    
    // Atomic completion with stats update
    scriptComplete = `
        local job_key = KEYS[1]
        local processing_key = KEYS[2]
        local stats_key = KEYS[3]
        local job_id = ARGV[1]
        local duration = ARGV[2]
        
        -- Remove from processing
        redis.call('HDEL', processing_key, job_id)
        
        -- Update job
        redis.call('HSET', job_key, 'status', 'completed')
        redis.call('HSET', job_key, 'completed_at', ARGV[3])
        
        -- Update stats
        redis.call('HINCRBY', stats_key, 'completed', 1)
        redis.call('HSET', stats_key, 'last_duration', duration)
        
        return 1
    `
    
    // Atomic retry with backoff
    scriptRetry = `
        local job_key = KEYS[1]
        local queue_key = KEYS[2]
        local processing_key = KEYS[3]
        local job_id = ARGV[1]
        local retry_count = ARGV[2]
        local next_attempt = ARGV[3]
        
        -- Remove from processing
        redis.call('HDEL', processing_key, job_id)
        
        -- Update job
        redis.call('HSET', job_key, 'retries', retry_count)
        redis.call('HSET', job_key, 'next_attempt', next_attempt)
        
        if tonumber(retry_count) >= tonumber(ARGV[4]) then
            -- Move to DLQ
            redis.call('LPUSH', KEYS[4], job_id)
            redis.call('HSET', job_key, 'status', 'dead_letter')
        else
            -- Re-queue
            redis.call('HSET', job_key, 'status', 'pending')
            redis.call('RPUSH', queue_key, job_id)
        end
        
        return 1
    `
)

func NewRedisBackend(addr string) (*RedisBackend, error) {
    client := redis.NewClient(&redis.Options{
        Addr:         addr,
        PoolSize:     20,
        MinIdleConns: 5,
        MaxRetries:   3,
        DialTimeout:  5 * time.Second,
        ReadTimeout:  3 * time.Second,
        WriteTimeout: 3 * time.Second,
    })
    
    ctx := context.Background()
    if err := client.Ping(ctx).Err(); err != nil {
        return nil, fmt.Errorf("redis connection failed: %w", err)
    }
    
    backend := &RedisBackend{
        client:      client,
        queuePrefix: "jobs",
        scriptSHA:   make(map[string]string),
    }
    
    // Load Lua scripts
    scripts := map[string]string{
        "dequeue":  scriptDequeue,
        "complete": scriptComplete,
        "retry":    scriptRetry,
    }
    
    for name, script := range scripts {
        sha, err := client.ScriptLoad(ctx, script).Result()
        if err != nil {
            return nil, fmt.Errorf("failed to load script %s: %w", name, err)
        }
        backend.scriptSHA[name] = sha
    }
    
    return backend, nil
}

func (b *RedisBackend) Enqueue(ctx context.Context, queue string, job *Job) error {
    jobKey := fmt.Sprintf(KeyJob, job.ID)
    queueKey := fmt.Sprintf(KeyQueue, queue)
    
    // Serialize job
    data, err := json.Marshal(job)
    if err != nil {
        return err
    }
    
    pipe := b.client.Pipeline()
    
    // Store job data
    pipe.HSet(ctx, jobKey, "data", data)
    pipe.HSet(ctx, jobKey, "status", "pending")
    pipe.HSet(ctx, jobKey, "created_at", time.Now().Unix())
    
    // Add to queue based on priority
    if job.Priority > 0 {
        // Use priority queue (sorted set)
        prioKey := fmt.Sprintf(KeyQueuePriority, queue)
        pipe.ZAdd(ctx, prioKey, redis.Z{
            Score:  float64(job.Priority),
            Member: job.ID,
        })
    } else if job.ScheduledAt != nil && job.ScheduledAt.After(time.Now()) {
        // Use scheduled queue
        schedKey := fmt.Sprintf(KeyQueueScheduled, queue)
        pipe.ZAdd(ctx, schedKey, redis.Z{
            Score:  float64(job.ScheduledAt.Unix()),
            Member: job.ID,
        })
    } else {
        // Regular queue
        pipe.LPush(ctx, queueKey, job.ID)
    }
    
    // Track queue
    pipe.SAdd(ctx, KeyQueueList, queue)
    
    _, err = pipe.Exec(ctx)
    return err
}

func (b *RedisBackend) Dequeue(ctx context.Context, queue string, workerID string) (*Job, error) {
    queueKey := fmt.Sprintf(KeyQueue, queue)
    processingKey := fmt.Sprintf(KeyJobProcessing, queue)
    
    // Try priority queue first
    prioKey := fmt.Sprintf(KeyQueuePriority, queue)
    jobID, err := b.client.ZPopMax(ctx, prioKey, 1).Result()
    if err == nil && len(jobID) > 0 {
        // Got job from priority queue
        return b.claimJob(ctx, jobID[0].Member.(string), processingKey, workerID)
    }
    
    // Try scheduled queue
    schedKey := fmt.Sprintf(KeyQueueScheduled, queue)
    now := float64(time.Now().Unix())
    jobID, err = b.client.ZRangeByScoreWithScores(ctx, schedKey, &redis.ZRangeBy{
        Min:   "0",
        Max:   fmt.Sprintf("%f", now),
        Count: 1,
    }).Result()
    if err == nil && len(jobID) > 0 {
        // Remove from scheduled and claim
        b.client.ZRem(ctx, schedKey, jobID[0].Member)
        return b.claimJob(ctx, jobID[0].Member, processingKey, workerID)
    }
    
    // Try regular queue using Lua script
    sha := b.scriptSHA["dequeue"]
    result, err := b.client.EvalSha(ctx, sha, []string{queueKey, processingKey}, 
        workerID, time.Now().Unix()).Result()
    if err != nil || result == nil {
        return nil, ErrNoJobs
    }
    
    jobIDStr := result.(string)
    return b.getJob(ctx, jobIDStr)
}

func (b *RedisBackend) claimJob(ctx context.Context, jobID string, processingKey, workerID string) (*Job, error) {
    // Update status atomically
    jobKey := fmt.Sprintf(KeyJob, jobID)
    pipe := b.client.Pipeline()
    pipe.HSet(ctx, processingKey, jobID, workerID)
    pipe.HSet(ctx, jobKey, "status", "processing")
    pipe.HSet(ctx, jobKey, "started_at", time.Now().Unix())
    pipe.HSet(ctx, jobKey, "worker_id", workerID)
    
    _, err := pipe.Exec(ctx)
    if err != nil {
        return nil, err
    }
    
    return b.getJob(ctx, jobID)
}

func (b *RedisBackend) getJob(ctx context.Context, jobID string) (*Job, error) {
    jobKey := fmt.Sprintf(KeyJob, jobID)
    data, err := b.client.HGet(ctx, jobKey, "data").Result()
    if err != nil {
        return nil, err
    }
    
    var job Job
    if err := json.Unmarshal([]byte(data), &job); err != nil {
        return nil, err
    }
    
    return &job, nil
}
```

#### PostgreSQL Backend

```go
// PostgreSQL backend with advisory locks
package postgres_backend

import (
    "context"
    "encoding/json"
    "fmt"
    "time"
    
    "github.com/jackc/pgx/v5"
    "github.com/jackc/pgx/v5/pgxpool"
)

// Schema
const schema = `
CREATE TYPE job_status AS ENUM ('pending', 'processing', 'completed', 'failed', 'dead_letter');
CREATE TYPE job_priority AS ENUM ('low', 'medium', 'high', 'critical');

CREATE TABLE jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    queue VARCHAR(255) NOT NULL,
    type VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL DEFAULT '{}',
    status job_status NOT NULL DEFAULT 'pending',
    priority job_priority NOT NULL DEFAULT 'medium',
    
    -- Timing
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    scheduled_at TIMESTAMPTZ,
    started_at TIMESTAMPTZ,
    completed_at TIMESTAMPTZ,
    
    -- Retry
    retries INT NOT NULL DEFAULT 0,
    max_retries INT NOT NULL DEFAULT 3,
    retry_at TIMESTAMPTZ,
    error TEXT,
    
    -- Processing
    worker_id VARCHAR(255),
    lock_id BIGINT,  -- Advisory lock ID
    
    -- Metadata
    metadata JSONB DEFAULT '{}',
    
    -- Indexes
    CONSTRAINT valid_retry CHECK (retries <= max_retries)
);

-- Indexes for efficient queries
CREATE INDEX idx_jobs_queue_status ON jobs(queue, status) WHERE status = 'pending';
CREATE INDEX idx_jobs_scheduled ON jobs(scheduled_at) WHERE status = 'pending' AND scheduled_at IS NOT NULL;
CREATE INDEX idx_jobs_priority ON jobs(priority, created_at) WHERE status = 'pending';
CREATE INDEX idx_jobs_worker ON jobs(worker_id, status) WHERE status = 'processing';
CREATE INDEX idx_jobs_type ON jobs(type);

-- Dead letter queue
CREATE TABLE dead_letter_jobs (
    LIKE jobs INCLUDING ALL,
    moved_at TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    failure_reason TEXT
);

-- Job statistics
CREATE TABLE job_stats (
    queue VARCHAR(255) PRIMARY KEY,
    total_completed INT NOT NULL DEFAULT 0,
    total_failed INT NOT NULL DEFAULT 0,
    total_dead_letter INT NOT NULL DEFAULT 0,
    avg_duration_ms INT,
    last_processed_at TIMESTAMPTZ,
    updated_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Scheduled jobs
CREATE TABLE scheduled_jobs (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    queue VARCHAR(255) NOT NULL,
    type VARCHAR(255) NOT NULL,
    payload JSONB NOT NULL,
    cron_expression VARCHAR(255) NOT NULL,
    next_run_at TIMESTAMPTZ NOT NULL,
    last_run_at TIMESTAMPTZ,
    enabled BOOLEAN NOT NULL DEFAULT TRUE,
    created_at TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_scheduled_jobs_next_run ON scheduled_jobs(next_run_at) WHERE enabled = TRUE;
`

// Advisory lock IDs
const (
    LockNamespaceQueue = 1
    LockNamespaceJob   = 2
)

type PostgresBackend struct {
    pool *pgxpool.Pool
}

func NewPostgresBackend(connString string) (*PostgresBackend, error) {
    config, err := pgxpool.ParseConfig(connString)
    if err != nil {
        return nil, err
    }
    
    // Pool configuration
    config.MaxConns = 20
    config.MinConns = 5
    config.MaxConnLifetime = 1 * time.Hour
    config.MaxConnIdleTime = 30 * time.Minute
    config.HealthCheckPeriod = 5 * time.Minute
    
    pool, err := pgxpool.NewWithConfig(context.Background(), config)
    if err != nil {
        return nil, err
    }
    
    return &PostgresBackend{pool: pool}, nil
}

func (b *PostgresBackend) Enqueue(ctx context.Context, job *Job) error {
    query := `
        INSERT INTO jobs (id, queue, type, payload, priority, scheduled_at, max_retries, metadata)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (id) DO NOTHING
    `
    
    var scheduledAt *time.Time
    if job.ScheduledAt != nil {
        scheduledAt = job.ScheduledAt
    }
    
    metadata, _ := json.Marshal(job.Metadata)
    
    _, err := b.pool.Exec(ctx, query,
        job.ID,
        job.Queue,
        job.Type,
        job.Payload,
        job.Priority.String(),
        scheduledAt,
        job.MaxRetries,
        metadata,
    )
    
    return err
}

// Dequeue with advisory lock for horizontal scaling
func (b *PostgresBackend) Dequeue(ctx context.Context, queue string, workerID string) (*Job, error) {
    tx, err := b.pool.Begin(ctx)
    if err != nil {
        return nil, err
    }
    defer tx.Rollback(ctx)
    
    // Find next available job using SKIP LOCKED
    // This is the key to horizontal scaling - multiple workers can
    // safely dequeue concurrently
    query := `
        WITH next_job AS (
            SELECT id, 
                   (extract(epoch from scheduled_at)::bigint % 2147483647)::int as lock_id
            FROM jobs
            WHERE queue = $1 
              AND status = 'pending'
              AND (scheduled_at IS NULL OR scheduled_at <= NOW())
            ORDER BY 
                CASE priority
                    WHEN 'critical' THEN 1
                    WHEN 'high' THEN 2
                    WHEN 'medium' THEN 3
                    WHEN 'low' THEN 4
                END,
                created_at
            FOR UPDATE SKIP LOCKED
            LIMIT 1
        )
        SELECT id, lock_id FROM next_job
    `
    
    var jobID string
    var lockID int32
    err = tx.QueryRow(ctx, query, queue).Scan(&jobID, &lockID)
    if err == pgx.ErrNoRows {
        return nil, ErrNoJobs
    }
    if err != nil {
        return nil, err
    }
    
    // Acquire advisory lock to prevent other workers from picking this job
    // even across different transactions
    lockQuery := `SELECT pg_try_advisory_lock($1, $2)`
    var acquired bool
    err = tx.QueryRow(ctx, lockQuery, LockNamespaceJob, lockID).Scan(&acquired)
    if err != nil {
        return nil, err
    }
    if !acquired {
        // Another worker has the lock
        return nil, ErrNoJobs
    }
    
    // Mark as processing
    updateQuery := `
        UPDATE jobs 
        SET status = 'processing',
            started_at = NOW(),
            worker_id = $2,
            lock_id = $3
        WHERE id = $1
        RETURNING id, queue, type, payload, priority, created_at, retries, max_retries, metadata
    `
    
    var job Job
    var priorityStr string
    var metadata []byte
    err = tx.QueryRow(ctx, updateQuery, jobID, workerID, lockID).Scan(
        &job.ID, &job.Queue, &job.Type, &job.Payload, &priorityStr,
        &job.CreatedAt, &job.Retries, &job.MaxRetries, &metadata,
    )
    if err != nil {
        return nil, err
    }
    
    if err := json.Unmarshal(metadata, &job.Metadata); err != nil {
        return nil, err
    }
    
    // Commit to release row lock but advisory lock persists
    if err := tx.Commit(ctx); err != nil {
        return nil, err
    }
    
    return &job, nil
}

func (b *PostgresBackend) Complete(ctx context.Context, jobID string) error {
    query := `
        WITH updated AS (
            UPDATE jobs 
            SET status = 'completed',
                completed_at = NOW()
            WHERE id = $1
            RETURNING queue, lock_id, started_at
        )
        INSERT INTO job_stats (queue, total_completed, avg_duration_ms, last_processed_at, updated_at)
        SELECT 
            queue,
            1,
            EXTRACT(EPOCH FROM (NOW() - started_at))::INT * 1000,
            NOW(),
            NOW()
        FROM updated
        ON CONFLICT (queue) DO UPDATE SET
            total_completed = job_stats.total_completed + 1,
            avg_duration_ms = (
                (job_stats.avg_duration_ms * job_stats.total_completed) + 
                EXTRACT(EPOCH FROM (NOW() - excluded.last_processed_at))::INT * 1000
            ) / (job_stats.total_completed + 1),
            last_processed_at = NOW(),
            updated_at = NOW()
    `
    
    _, err := b.pool.Exec(ctx, query, jobID)
    return err
}

func (b *PostgresBackend) Fail(ctx context.Context, jobID string, errMsg string, retryable bool) error {
    if retryable {
        // Schedule retry with exponential backoff
        query := `
            UPDATE jobs 
            SET retries = retries + 1,
                error = $2,
                status = CASE 
                    WHEN retries + 1 >= max_retries THEN 'dead_letter'::job_status
                    ELSE 'pending'::job_status
                END,
                retry_at = CASE 
                    WHEN retries + 1 >= max_retries THEN NULL
                    ELSE NOW() + (POWER(2, retries) || ' seconds')::INTERVAL
                END,
                scheduled_at = CASE 
                    WHEN retries + 1 >= max_retries THEN NULL
                    ELSE NOW() + (POWER(2, retries) || ' seconds')::INTERVAL
                END
            WHERE id = $1
            RETURNING status, lock_id
        `
        
        var status string
        var lockID int32
        err := b.pool.QueryRow(ctx, query, jobID, errMsg).Scan(&status, &lockID)
        if err != nil {
            return err
        }
        
        // Release advisory lock
        if status != "dead_letter" {
            _, _ = b.pool.Exec(ctx, `SELECT pg_advisory_unlock($1, $2)`, 
                LockNamespaceJob, lockID)
        }
        
        return nil
    }
    
    // Non-retryable - move to dead letter immediately
    return b.moveToDeadLetter(ctx, jobID, errMsg)
}

func (b *PostgresBackend) moveToDeadLetter(ctx context.Context, jobID string, reason string) error {
    tx, err := b.pool.Begin(ctx)
    if err != nil {
        return err
    }
    defer tx.Rollback(ctx)
    
    // Move to dead letter
    moveQuery := `
        WITH moved AS (
            DELETE FROM jobs WHERE id = $1
            RETURNING *
        )
        INSERT INTO dead_letter_jobs 
        SELECT *, NOW(), $2 FROM moved
    `
    
    _, err = tx.Exec(ctx, moveQuery, jobID, reason)
    if err != nil {
        return err
    }
    
    // Update stats
    statsQuery := `
        INSERT INTO job_stats (queue, total_dead_letter, updated_at)
        SELECT queue, 1, NOW() FROM jobs WHERE id = $1
        ON CONFLICT (queue) DO UPDATE SET
            total_dead_letter = job_stats.total_dead_letter + 1,
            updated_at = NOW()
    `
    _, err = tx.Exec(ctx, statsQuery, jobID)
    if err != nil {
        return err
    }
    
    return tx.Commit(ctx)
}

// Scheduled job processor
func (b *PostgresBackend) ProcessScheduledJobs(ctx context.Context) error {
    query := `
        WITH due_jobs AS (
            SELECT id, queue, type, payload, priority, max_retries
            FROM scheduled_jobs
            WHERE enabled = TRUE 
              AND next_run_at <= NOW()
            FOR UPDATE SKIP LOCKED
        ),
        inserted AS (
            INSERT INTO jobs (queue, type, payload, priority, max_retries, scheduled_at)
            SELECT queue, type, payload, priority, max_retries, NOW()
            FROM due_jobs
            RETURNING id
        )
        UPDATE scheduled_jobs sj
        SET last_run_at = NOW(),
            next_run_at = CASE 
                WHEN cron_expression IS NOT NULL THEN
                    cron_next_run(cron_expression, NOW())
                ELSE NULL
            END,
            enabled = CASE 
                WHEN cron_expression IS NULL THEN FALSE
                ELSE TRUE
            END
        FROM due_jobs dj
        WHERE sj.id = dj.id
    `
    
    _, err := b.pool.Exec(ctx, query)
    return err
}
```

---

## System Architecture

### High-Level Architecture

```
┌─────────────────────────────────────────────────────────────┐
│                    Jobs System                              │
├─────────────────────────────────────────────────────────────┤
│                                                             │
│  ┌──────────────┐     ┌──────────────┐     ┌────────────┐ │
│  │   Client     │     │   Scheduler  │     │   Worker   │ │
│  │   API        │     │   Engine     │     │   Pool     │ │
│  └──────┬───────┘     └──────┬───────┘     └─────┬──────┘ │
│         │                    │                    │        │
│         └────────────────────┼────────────────────┘        │
│                              │                            │
│                   ┌────────────┴────────────┐              │
│                   │      Queue Backend        │              │
│                   │   (Redis/PostgreSQL)      │              │
│                   └────────────┬────────────┘              │
│                              │                            │
│                   ┌────────────┴────────────┐              │
│                   │      Dead Letter        │              │
│                   │        Queue            │              │
│                   └─────────────────────────┘              │
│                                                             │
│  ┌──────────────┐     ┌──────────────┐     ┌────────────┐  │
│  │   Metrics    │     │   Retry      │     │   Admin    │  │
│  │   Collector  │     │   Manager    │     │   API      │  │
│  └──────────────┘     └──────────────┘     └────────────┘  │
│                                                             │
└─────────────────────────────────────────────────────────────┘
```

### Job Lifecycle

```
Job States:
━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━

[Created] → [Queued] → [Scheduled] → [Processing] → [Completed]
   ↓            ↓            ↓              ↓             ↓
   │            │            │              │             │
   │            │            │              ↓             │
   │            │            │         [Retry] ───────→──┘
   │            │            │              │
   │            │            │              ↓
   │            │            │         [Failed] ───────→ [DLQ]
   │            │            │
   ↓            ↓            ↓
[Cancelled]  [Paused]   [Delayed]

━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━
```

### Worker Architecture

```
┌─────────────────────────────────────────┐
│           Worker Pool                   │
├─────────────────────────────────────────┤
│                                         │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐ │
│  │Worker 1 │  │Worker 2 │  │Worker N │ │
│  │ (Poll)  │  │ (Poll)  │  │ (Poll)  │ │
│  └────┬────┘  └────┬────┘  └────┬────┘ │
│       │            │            │      │
│       └────────────┼────────────┘      │
│                    │                   │
│            ┌───────┴───────┐          │
│            │  Job Channel  │          │
│            └───────┬───────┘          │
│                    │                   │
│       ┌────────────┼────────────┐    │
│       ↓            ↓            ↓    │
│  ┌─────────┐  ┌─────────┐  ┌─────────┐│
│  │Process  │  │Process  │  │Process  ││
│  │ Job A   │  │ Job B   │  │ Job C   ││
│  └─────────┘  └─────────┘  └─────────┘│
│                                         │
│  ┌─────────────────────────────────┐   │
│  │ Middleware Chain:               │   │
│  │ 1. Logging                      │   │
│  │ 2. Metrics                      │   │
│  │ 3. Tracing                      │   │
│  │ 4. Recovery                     │   │
│  │ 5. Rate Limiting                │   │
│  └─────────────────────────────────┘   │
│                                         │
└─────────────────────────────────────────┘
```

---

## Component Specifications

### Queue Manager

Central component managing job queues:

```go
type QueueManager struct {
    backend     Backend
    serializer  Serializer
    middlewares []Middleware
    metrics     MetricsCollector
    logger      *slog.Logger
}

func (qm *QueueManager) Enqueue(ctx context.Context, job *Job) error
func (qm *QueueManager) EnqueueBatch(ctx context.Context, jobs []*Job) error
func (qm *QueueManager) Dequeue(ctx context.Context, queue string) (*Job, error)
func (qm *QueueManager) Ack(ctx context.Context, jobID string) error
func (qm *QueueManager) Nack(ctx context.Context, jobID string, requeue bool) error
func (qm *QueueManager) GetJob(ctx context.Context, jobID string) (*Job, error)
func (qm *QueueManager) ListJobs(ctx context.Context, opts ListOptions) ([]*Job, error)
func (qm *QueueManager) CancelJob(ctx context.Context, jobID string) error
func (qm *QueueManager) PauseQueue(ctx context.Context, queue string) error
func (qm *QueueManager) ResumeQueue(ctx context.Context, queue string) error
```

### Scheduler

Handles job scheduling and cron expressions:

```go
type Scheduler struct {
    cronParser  cron.Parser
    location    *time.Location
    queue       chan *Job
    backend     Backend
    jobs        map[string]*ScheduledJob
}

type ScheduledJob struct {
    ID             string
    Queue          string
    Type           string
    Payload        json.RawMessage
    CronExpression string
    NextRunAt      time.Time
    LastRunAt      *time.Time
    Enabled        bool
}

func (s *Scheduler) Schedule(job *Job, spec string) (*ScheduledJob, error)
func (s *Scheduler) ScheduleOnce(job *Job, at time.Time) (*ScheduledJob, error)
func (s *Scheduler) ScheduleCron(cronExpr string, job *Job) (*ScheduledJob, error)
func (s *Scheduler) Unschedule(jobID string) error
func (s *Scheduler) Enable(jobID string) error
func (s *Scheduler) Disable(jobID string) error
func (s *Scheduler) List() []*ScheduledJob
func (s *Scheduler) GetNextRun(jobID string) (time.Time, error)
func (s *Scheduler) Start() error
func (s *Scheduler) Stop() error
```

### Worker Pool

Manages concurrent job processing:

```go
type WorkerPool struct {
    size           int
    queue          string
    handler        HandlerFunc
    middlewares    []Middleware
    concurrency    int
    backend        Backend
    metrics        MetricsCollector
    logger         *slog.Logger
    shutdown       chan struct{}
    wg             sync.WaitGroup
    pollInterval   time.Duration
    maxJobs        int
    rateLimiter    RateLimiter
}

type WorkerConfig struct {
    Queue            string
    Concurrency      int
    PollInterval     time.Duration
    MaxJobs          int
    ShutdownTimeout  time.Duration
    RateLimit        int           // Jobs per second
    RateBurst        int           // Burst allowance
    RetryPolicy      RetryPolicy
    Middlewares      []Middleware
}

func (wp *WorkerPool) Start(ctx context.Context) error
func (wp *WorkerPool) Stop() error
func (wp *WorkerPool) Scale(size int) error
func (wp *WorkerPool) GetStats() WorkerStats
func (wp *WorkerPool) Pause() error
func (wp *WorkerPool) Resume() error
func (wp *WorkerPool) IsRunning() bool
```

### Retry Manager

Handles job retry logic:

```go
type RetryManager struct {
    maxRetries   int
    backoff      BackoffStrategy
    jitter       bool
    maxDelay     time.Duration
    minDelay     time.Duration
}

type BackoffStrategy func(attempt int) time.Duration
type RetryPolicy struct {
    MaxRetries   int
    InitialDelay time.Duration
    MaxDelay     time.Duration
    Multiplier   float64
    Jitter       bool
}

func (rm *RetryManager) ShouldRetry(job *Job, err error) bool
func (rm *RetryManager) NextRetry(job *Job) time.Time
func (rm *RetryManager) CalculateBackoff(attempt int) time.Duration

// Built-in backoff strategies
func ExponentialBackoff(initial time.Duration, max time.Duration, multiplier float64) BackoffStrategy
func FixedBackoff(delay time.Duration) BackoffStrategy
func LinearBackoff(initial time.Duration, increment time.Duration) BackoffStrategy
func DecorrelatedJitterBackoff(base time.Duration, max time.Duration) BackoffStrategy
```

### Batch Processor

```go
type BatchProcessor struct {
    batchSize     int
    flushInterval time.Duration
    queue         string
    backend       Backend
    processor     BatchHandler
    buffer        []*Job
    mu            sync.Mutex
}

type BatchHandler func(ctx context.Context, jobs []*Job) error

func NewBatchProcessor(queue string, size int, interval time.Duration, handler BatchHandler) *BatchProcessor
func (bp *BatchProcessor) Add(job *Job) error
func (bp *BatchProcessor) Flush(ctx context.Context) error
func (bp *BatchProcessor) Start(ctx context.Context)
func (bp *BatchProcessor) Stop() error
```

### Job Chainer

```go
type JobChain struct {
    jobs     []*Job
    current  int
    results  []ChainResult
}

type ChainResult struct {
    JobID    string
    Success  bool
    Error    error
    Duration time.Duration
}

func NewJobChain(jobs ...*Job) *JobChain
func (jc *JobChain) OnStep(callback func(result ChainResult)) *JobChain
func (jc *JobChain) ContinueOnError(enabled bool) *JobChain
func (jc *JobChain) Execute(ctx context.Context, backend Backend) ([]ChainResult, error)
func (jc *JobChain) GetResults() []ChainResult
```

---

## Data Models

### Job Definition

```go
// Job represents a unit of work
type Job struct {
    ID          string                 `json:"id"`
    Type        string                 `json:"type"`
    Payload     json.RawMessage        `json:"payload"`
    Priority    Priority               `json:"priority"`
    Status      Status                 `json:"status"`
    Queue       string                 `json:"queue"`
    CreatedAt   time.Time              `json:"created_at"`
    ScheduledAt *time.Time             `json:"scheduled_at,omitempty"`
    StartedAt   *time.Time             `json:"started_at,omitempty"`
    CompletedAt *time.Time             `json:"completed_at,omitempty"`
    Retries     int                    `json:"retries"`
    MaxRetries  int                    `json:"max_retries"`
    Error       string                 `json:"error,omitempty"`
    Metadata    map[string]string      `json:"metadata,omitempty"`
    WorkerID    string                 `json:"worker_id,omitempty"`
    Duration    time.Duration          `json:"duration,omitempty"`
}

func NewJob(jobType string, payload interface{}) (*Job, error)
func (j *Job) SetPriority(p Priority) *Job
func (j *Job) SetMaxRetries(n int) *Job
func (j *Job) SetScheduledAt(t time.Time) *Job
func (j *Job) SetQueue(q string) *Job
func (j *Job) SetMetadata(key, value string) *Job
func (j *Job) SetPayload(payload interface{}) error
func (j *Job) IsScheduled() bool
func (j *Job) IsRetryable() bool
func (j *Job) TimeInQueue() time.Duration
func (j *Job) ProcessingTime() time.Duration
```

### Job Status

```go
type Status int

const (
    StatusCreated Status = iota
    StatusQueued
    StatusScheduled
    StatusProcessing
    StatusCompleted
    StatusFailed
    StatusRetrying
    StatusCancelled
    StatusDeadLetter
    StatusPaused
)

func (s Status) String() string
func (s Status) IsFinal() bool
func (s Status) CanTransition(to Status) bool
```

### Priority Levels

```go
type Priority int

const (
    PriorityLow Priority = iota
    PriorityMedium
    PriorityHigh
    PriorityCritical
)

func (p Priority) Weight() int
func (p Priority) String() string
func ParsePriority(s string) (Priority, error)
```

### Queue Configuration

```go
type QueueConfig struct {
    Name            string
    Priority        Priority
    MaxRetries      int
    RetryDelay      time.Duration
    Timeout         time.Duration
    Concurrency     int
    DeadLetter      string
    Retention       time.Duration
    RateLimit       int
    BatchSize       int
    EnablePriority  bool
    EnableScheduled bool
}

func (qc *QueueConfig) Validate() error
func (qc *QueueConfig) ApplyDefaults()
```

### Dead Letter Job

```go
type DeadLetterJob struct {
    Job
    MovedAt        time.Time `json:"moved_at"`
    FailureReason  string    `json:"failure_reason"`
    OriginalQueue  string    `json:"original_queue"`
    RetryHistory   []RetryAttempt `json:"retry_history"`
}

type RetryAttempt struct {
    Attempt   int       `json:"attempt"`
    At        time.Time `json:"at"`
    Error     string    `json:"error"`
    Duration  time.Duration `json:"duration"`
}

func (dlj *DeadLetterJob) CanRetry() bool
func (dlj *DeadLetterJob) Retry(ctx context.Context, backend Backend) error
```

---

## API Reference

### Client API

```go
// Create client
client, err := jobs.NewClient(jobs.Config{
    Backend: jobs.RedisBackend{
        Addr:     "localhost:6379",
        Password: "",
        DB:       0,
        PoolSize: 20,
    },
    DefaultQueue: "default",
    Middlewares:  []jobs.Middleware{loggingMiddleware, metricsMiddleware},
})

// Enqueue job
job, err := client.Enqueue(ctx, &jobs.Job{
    Type: "send_email",
    Payload: EmailPayload{To: "user@example.com"},
    MaxRetries: 3,
})

// Enqueue with options
job, err := client.Enqueue(ctx, &jobs.Job{
    Type: "process_image",
    Payload: ImagePayload{URL: "https://example.com/img.jpg"},
}, jobs.EnqueueOptions{
    Queue:    "processing",
    Priority: jobs.PriorityHigh,
    Delay:    5 * time.Minute,
    Unique:   true,
    UniqueTTL: 1 * time.Hour,
})

// Batch enqueue
jobs := []*jobs.Job{
    {Type: "send_email", Payload: payload1},
    {Type: "send_email", Payload: payload2},
    {Type: "send_email", Payload: payload3},
}
results, err := client.EnqueueBatch(ctx, jobs)

// Schedule job
scheduledJob, err := client.Schedule(ctx, "0 9 * * *", &jobs.Job{
    Type: "daily_report",
    Queue: "reports",
})

// Schedule once
futureJob, err := client.ScheduleOnce(ctx, time.Now().Add(1*time.Hour), &jobs.Job{
    Type: "reminder",
    Payload: ReminderPayload{UserID: 123},
})

// Schedule with cron expression
cronJob, err := client.ScheduleCron(ctx, "*/15 * * * *", &jobs.Job{
    Type: "health_check",
    Queue: "monitoring",
})

// Chain jobs
chain := client.NewChain().
    Then(&jobs.Job{Type: "download", Payload: downloadPayload}).
    Then(&jobs.Job{Type: "process", Payload: processPayload}).
    Then(&jobs.Job{Type: "upload", Payload: uploadPayload})
chainResults, err := chain.Execute(ctx)

// Get job status
status, err := client.GetJobStatus(ctx, job.ID)

// Cancel job
err = client.CancelJob(ctx, job.ID)
```

### Worker API

```go
// Create worker pool
worker := jobs.NewWorker(jobs.WorkerConfig{
    Queue:       "default",
    Concurrency: 10,
    PollInterval: 1 * time.Second,
    MaxJobs:     1000,
    RateLimit:   100, // per second
    RateBurst:   200,
    RetryPolicy: jobs.RetryPolicy{
        MaxRetries:   5,
        InitialDelay: 1 * time.Second,
        MaxDelay:     1 * time.Hour,
        Multiplier:   2.0,
        Jitter:       true,
    },
})

// Register handler
worker.HandleFunc("send_email", func(ctx context.Context, job *jobs.Job) error {
    var payload EmailPayload
    if err := json.Unmarshal(job.Payload, &payload); err != nil {
        return err
    }
    return sendEmail(payload)
})

// Register with options
worker.Handle("process_image", &ImageProcessor{}, jobs.HandlerOptions{
    Timeout:    5 * time.Minute,
    Concurrency: 2, // Limit concurrent image processing
    Middlewares: []jobs.Middleware{tracingMiddleware},
})

// Batch handler
worker.HandleBatch("process_batch", func(ctx context.Context, jobs []*jobs.Job) error {
    // Process multiple jobs efficiently
    return processBatch(jobs)
}, jobs.BatchOptions{
    BatchSize:     100,
    FlushInterval: 5 * time.Second,
})

// Add middleware
worker.Use(loggingMiddleware)
worker.Use(metricsMiddleware)
worker.Use(tracingMiddleware)
worker.Use(recoveryMiddleware)

// Start worker
ctx := context.Background()
if err := worker.Start(ctx); err != nil {
    log.Fatal(err)
}

// Graceful shutdown
quit := make(chan os.Signal, 1)
signal.Notify(quit, syscall.SIGINT, syscall.SIGTERM)
<-quit

shutdownCtx, cancel := context.WithTimeout(context.Background(), 30*time.Second)
defer cancel()

if err := worker.Stop(shutdownCtx); err != nil {
    log.Printf("Worker shutdown error: %v", err)
}

// Dynamic scaling
worker.Scale(20) // Increase to 20 workers
worker.Scale(5)  // Decrease to 5 workers

// Pause/resume
worker.Pause()  // Stop processing new jobs
worker.Resume() // Resume processing
```

### Middleware API

```go
// Middleware signature
type Middleware func(next HandlerFunc) HandlerFunc
type HandlerFunc func(ctx context.Context, job *Job) error

// Create logging middleware
loggingMiddleware := func(next jobs.HandlerFunc) jobs.HandlerFunc {
    return func(ctx context.Context, job *jobs.Job) error {
        start := time.Now()
        logger.Info("Processing job",
            "job_id", job.ID,
            "job_type", job.Type,
            "queue", job.Queue,
            "attempt", job.Retries+1,
        )
        
        err := next(ctx, job)
        
        duration := time.Since(start)
        if err != nil {
            logger.Error("Job failed",
                "job_id", job.ID,
                "error", err,
                "duration", duration,
            )
        } else {
            logger.Info("Job completed",
                "job_id", job.ID,
                "duration", duration,
            )
        }
        return err
    }
}

// Metrics middleware
metricsMiddleware := func(next jobs.HandlerFunc) jobs.HandlerFunc {
    return func(ctx context.Context, job *jobs.Job) error {
        start := time.Now()
        
        err := next(ctx, job)
        
        // Record metrics
        duration := time.Since(start)
        jobDuration.WithLabelValues(job.Type).Observe(duration.Seconds())
        
        if err != nil {
            jobFailures.WithLabelValues(job.Type).Inc()
        } else {
            jobSuccesses.WithLabelValues(job.Type).Inc()
        }
        
        return err
    }
}

// Tracing middleware
tracingMiddleware := func(next jobs.HandlerFunc) jobs.HandlerFunc {
    return func(ctx context.Context, job *jobs.Job) error {
        tracer := otel.Tracer("jobs")
        ctx, span := tracer.Start(ctx, "process_job",
            trace.WithAttributes(
                attribute.String("job.id", job.ID),
                attribute.String("job.type", job.Type),
                attribute.String("job.queue", job.Queue),
            ),
        )
        defer span.End()
        
        err := next(ctx, job)
        
        if err != nil {
            span.RecordError(err)
            span.SetStatus(codes.Error, err.Error())
        }
        
        return err
    }
}

// Recovery middleware
recoveryMiddleware := func(next jobs.HandlerFunc) jobs.HandlerFunc {
    return func(ctx context.Context, job *jobs.Job) (err error) {
        defer func() {
            if r := recover(); r != nil {
                stack := debug.Stack()
                err = fmt.Errorf("panic: %v\n%s", r, stack)
            }
        }()
        return next(ctx, job)
    }
}

// Rate limiting middleware
rateLimitMiddleware := func(rps int) jobs.Middleware {
    limiter := rate.NewLimiter(rate.Limit(rps), rps)
    return func(next jobs.HandlerFunc) jobs.HandlerFunc {
        return func(ctx context.Context, job *jobs.Job) error {
            if err := limiter.Wait(ctx); err != nil {
                return fmt.Errorf("rate limit exceeded: %w", err)
            }
            return next(ctx, job)
        }
    }
}

// Timeout middleware
timeoutMiddleware := func(timeout time.Duration) jobs.Middleware {
    return func(next jobs.HandlerFunc) jobs.HandlerFunc {
        return func(ctx context.Context, job *jobs.Job) error {
            ctx, cancel := context.WithTimeout(ctx, timeout)
            defer cancel()
            return next(ctx, job)
        }
    }
}

// Register middleware globally
jobs.Use(loggingMiddleware)
jobs.Use(metricsMiddleware)
```

### Admin API

```go
// Admin client for operations
admin := client.Admin()

// Get queue stats
stats, err := admin.GetQueueStats(ctx, "default")
// Returns:
// {
//     Queue:          "default",
//     Pending:        150,
//     Processing:     10,
//     Completed:      50000,
//     Failed:         100,
//     DeadLetter:     5,
//     AvgDuration:    2 * time.Second,
//     WorkersActive:  10,
//     OldestJob:      5 * time.Minute,
// }

// List jobs with filtering
jobs, err := admin.ListJobs(ctx, jobs.ListOptions{
    Queue:     "default",
    Status:    jobs.StatusFailed,
    Type:      "send_email",
    Limit:     100,
    Offset:    0,
    Since:     time.Now().Add(-24 * time.Hour),
    Until:     time.Now(),
    OrderBy:   "created_at",
    OrderDesc: true,
})

// Retry failed job
err = admin.RetryJob(ctx, jobID)

// Retry all failed jobs
result, err := admin.RetryAllFailed(ctx, "default")
// Returns count of jobs queued for retry

// Move job to dead letter
err = admin.MoveToDeadLetter(ctx, jobID, "manual intervention")

// Cancel job
err = admin.CancelJob(ctx, jobID)

// Purge queue (remove completed jobs)
err = admin.PurgeQueue(ctx, "default", jobs.PurgeOptions{
    Status:    jobs.StatusCompleted,
    OlderThan: 7 * 24 * time.Hour,
})

// Pause queue
err = admin.PauseQueue(ctx, "default")

// Resume queue
err = admin.ResumeQueue(ctx, "default")

// Delete job permanently
err = admin.DeleteJob(ctx, jobID)

// Get dead letter queue
_dlqJobs, err := admin.ListDeadLetter(ctx, "default", 100)

// Replay dead letter job
err = admin.ReplayDeadLetter(ctx, jobID)

// Get job details
details, err := admin.GetJobDetails(ctx, jobID)
// Returns full job history, retry attempts, execution logs
```

---

## Configuration

### YAML Configuration

```yaml
# jobs.yaml
jobs:
  # Backend configuration
  backend:
    type: redis  # redis, postgres, memory, sqs, nats
    redis:
      addr: localhost:6379
      password: ""
      db: 0
      pool_size: 20
      min_idle_conns: 5
      max_retries: 3
      dial_timeout: 5s
      read_timeout: 3s
      write_timeout: 3s
      
    postgres:
      host: localhost
      port: 5432
      database: jobs
      user: jobs_user
      password: ${DB_PASSWORD}
      ssl_mode: prefer
      pool_size: 20
      max_conns: 50
      
    sqs:
      region: us-east-1
      access_key_id: ${AWS_ACCESS_KEY_ID}
      secret_access_key: ${AWS_SECRET_ACCESS_KEY}
      endpoint: ""  # Leave empty for AWS, set for LocalStack
      
    nats:
      urls:
        - nats://localhost:4222
      stream: JOBS_STREAM
      replicas: 3

  # Queue definitions
  queues:
    default:
      priority: medium
      max_retries: 3
      retry_delay: 60s
      timeout: 300s
      concurrency: 10
      dead_letter: dead_letter
      retention: 168h  # 7 days
      
    critical:
      priority: critical
      max_retries: 5
      retry_delay: 30s
      timeout: 600s
      concurrency: 20
      dead_letter: critical_dlq
      retention: 720h  # 30 days
      rate_limit: 1000
      rate_burst: 2000
      
    processing:
      priority: medium
      max_retries: 2
      retry_delay: 120s
      timeout: 1800s  # 30 min for heavy processing
      concurrency: 5  # CPU intensive
      batch_size: 10
      
    scheduled:
      priority: low
      max_retries: 3
      timeout: 60s
      concurrency: 2

  # Worker configuration
  worker:
    poll_interval: 1s
    reservation_timeout: 300s
    shutdown_timeout: 30s
    max_jobs: 1000
    enable_priority: true
    enable_scheduled: true
    
  # Scheduler configuration
  scheduler:
    enabled: true
    location: America/New_York
    tick_interval: 10s
    
  # Retry configuration
  retry:
    default_max_retries: 3
    backoff_strategy: exponential  # exponential, fixed, linear, jitter
    initial_delay: 1s
    max_delay: 1h
    multiplier: 2.0
    jitter: true
    
  # Middleware configuration
  middleware:
    - logging
    - metrics
    - tracing
    - recovery
    
  # Metrics configuration
  metrics:
    enabled: true
    port: 8080
    path: /metrics
    prefix: jobs_
    
  # Dead letter configuration
  dead_letter:
    enabled: true
    max_age: 720h  # 30 days
    retry_after: 24h  # Can retry DLQ jobs after
    alert_threshold: 100  # Alert when DLQ reaches this size
```

### Environment Variables

```bash
# Backend selection
JOBS_BACKEND_TYPE=redis

# Redis configuration
JOBS_REDIS_ADDR=localhost:6379
JOBS_REDIS_PASSWORD=secret
JOBS_REDIS_DB=0
JOBS_REDIS_POOL_SIZE=20

# PostgreSQL configuration
JOBS_POSTGRES_HOST=localhost
JOBS_POSTGRES_PORT=5432
JOBS_POSTGRES_DATABASE=jobs
JOBS_POSTGRES_USER=jobs_user
JOBS_POSTGRES_PASSWORD=secret
JOBS_POSTGRES_SSL_MODE=prefer

# SQS configuration
JOBS_SQS_REGION=us-east-1
JOBS_SQS_ACCESS_KEY_ID=AKIA...
JOBS_SQS_SECRET_ACCESS_KEY=secret

# NATS configuration
JOBS_NATS_URLS=nats://localhost:4222
JOBS_NATS_STREAM=JOBS_STREAM

# Worker configuration
JOBS_DEFAULT_CONCURRENCY=10
JOBS_POLL_INTERVAL=1s
JOBS_SHUTDOWN_TIMEOUT=30s
JOBS_MAX_JOBS=1000

# Metrics
JOBS_METRICS_ENABLED=true
JOBS_METRICS_PORT=8080
JOBS_METRICS_PATH=/metrics

# Scheduler
JOBS_SCHEDULER_ENABLED=true
JOBS_SCHEDULER_LOCATION=America/New_York

# Retry
JOBS_RETRY_MAX_RETRIES=3
JOBS_RETRY_INITIAL_DELAY=1s
JOBS_RETRY_MAX_DELAY=1h

# Dead letter
JOBS_DLQ_ENABLED=true
JOBS_DLQ_MAX_AGE=720h
```

### Programmatic Configuration

```go
// Full programmatic configuration
config := jobs.Config{
    Backend: &jobs.RedisBackendConfig{
        Addr:         "localhost:6379",
        Password:     getSecret("redis_password"),
        DB:           0,
        PoolSize:     20,
        DialTimeout:  5 * time.Second,
        ReadTimeout:  3 * time.Second,
        WriteTimeout: 3 * time.Second,
    },
    
    Queues: map[string]jobs.QueueConfig{
        "default": {
            Priority:       jobs.PriorityMedium,
            MaxRetries:     3,
            RetryDelay:     60 * time.Second,
            Timeout:        300 * time.Second,
            Concurrency:    10,
            DeadLetter:     "dead_letter",
            Retention:      7 * 24 * time.Hour,
        },
        "critical": {
            Priority:       jobs.PriorityCritical,
            MaxRetries:     5,
            RetryDelay:     30 * time.Second,
            Timeout:        600 * time.Second,
            Concurrency:    20,
            DeadLetter:     "critical_dlq",
            Retention:      30 * 24 * time.Hour,
            RateLimit:      1000,
            RateBurst:      2000,
        },
    },
    
    Worker: jobs.WorkerConfig{
        PollInterval:       1 * time.Second,
        ReservationTimeout: 300 * time.Second,
        ShutdownTimeout:    30 * time.Second,
        MaxJobs:            1000,
        EnablePriority:     true,
        EnableScheduled:    true,
    },
    
    Scheduler: jobs.SchedulerConfig{
        Enabled:      true,
        Location:     time.UTC,
        TickInterval: 10 * time.Second,
    },
    
    Retry: jobs.RetryConfig{
        DefaultMaxRetries: 3,
        BackoffStrategy:   jobs.ExponentialBackoff,
        InitialDelay:      1 * time.Second,
        MaxDelay:          1 * time.Hour,
        Multiplier:        2.0,
        Jitter:            true,
    },
    
    Middlewares: []jobs.Middleware{
        jobs.LoggingMiddleware,
        jobs.MetricsMiddleware,
        jobs.TracingMiddleware,
        jobs.RecoveryMiddleware,
    },
    
    Metrics: jobs.MetricsConfig{
        Enabled: true,
        Port:    8080,
        Path:    "/metrics",
        Prefix:  "jobs_",
    },
}

// Create client with config
client, err := jobs.NewClient(config)
if err != nil {
    log.Fatal(err)
}
```

---

## Performance Targets

### Throughput

| Metric | Target | Burst | Notes |
|--------|--------|-------|-------|
| Jobs/sec (enqueue) | 10,000 | 50,000 | Single node Redis |
| Jobs/sec (process) | 10,000 | 25,000 | 10 workers |
| Scheduled jobs/sec | 1,000 | 5,000 | Cron execution |
| Batch enqueue/sec | 5,000 | 20,000 | 100 job batches |

### Latency

| Operation | p50 | p99 | Max | Notes |
|-----------|-----|-----|-----|-------|
| Enqueue | < 1ms | < 5ms | < 10ms | Redis backend |
| Dequeue | < 5ms | < 20ms | < 50ms | With lock |
| Schedule | < 1ms | < 5ms | < 10ms | In-memory |
| Job start | < 10ms | < 50ms | < 100ms | From poll |
| Job complete | < 5ms | < 20ms | < 50ms | Ack time |

### Resource Usage

| Workers | Memory | CPU | DB Connections | Notes |
|---------|--------|-----|----------------|-------|
| 10 | 50 MB | 10% | 10 | Baseline |
| 50 | 200 MB | 30% | 50 | Medium |
| 100 | 400 MB | 50% | 100 | Large |
| 500 | 1.5 GB | 80% | 200 | Very large |

### Scalability Targets

| Metric | Target |
|--------|--------|
| Max queues | 1,000 |
| Max workers per queue | 100 |
| Max job size | 1 MB |
| Max concurrent jobs | 100,000 |
| Queue depth | 10,000,000 |
| Retention period | 90 days |

---

## Security Model

### Job Payload Security

```go
// Validate job payload
func ValidatePayload(job *Job) error {
    if len(job.Payload) > maxPayloadSize {
        return ErrPayloadTooLarge
    }
    
    // Validate JSON structure
    var data interface{}
    if err := json.Unmarshal(job.Payload, &data); err != nil {
        return ErrInvalidPayload
    }
    
    // Check for dangerous content
    if containsSuspiciousPatterns(job.Payload) {
        return ErrSuspiciousPayload
    }
    
    return nil
}

// Encrypt sensitive payloads
type EncryptedPayload struct {
    Data      []byte `json:"data"`
    Algorithm string `json:"alg"`
    KeyID     string `json:"kid"`
}

func EncryptPayload(payload []byte, keyID string) (*EncryptedPayload, error) {
    key := getEncryptionKey(keyID)
    encrypted, err := encryptAES(payload, key)
    if err != nil {
        return nil, err
    }
    
    return &EncryptedPayload{
        Data:      encrypted,
        Algorithm: "AES256-GCM",
        KeyID:     keyID,
    }, nil
}

func DecryptPayload(enc *EncryptedPayload) ([]byte, error) {
    key := getEncryptionKey(enc.KeyID)
    return decryptAES(enc.Data, key)
}
```

### Queue Isolation

```go
// Multi-tenant queue names
tenantQueue := fmt.Sprintf("tenant_%s_default", tenantID)

// ACL on queues
acl := jobs.QueueACL{
    AllowedProducers: []string{"service_a", "service_b"},
    AllowedConsumers: []string{"worker_pool_1"},
    MaxDepth:         100000,
    RateLimit:        1000,
}

// Enforce ACL
func (qm *QueueManager) EnqueueWithACL(ctx context.Context, job *Job, producerID string) error {
    acl, ok := qm.acls[job.Queue]
    if !ok {
        return ErrQueueNotFound
    }
    
    if !contains(acl.AllowedProducers, producerID) {
        return ErrNotAuthorized
    }
    
    // Check depth limit
    depth, _ := qm.GetQueueDepth(ctx, job.Queue)
    if depth >= acl.MaxDepth {
        return ErrQueueFull
    }
    
    return qm.Enqueue(ctx, job)
}
```

### Authentication & Authorization

```go
// mTLS for worker connections
type TLSConfig struct {
    CertFile string
    KeyFile  string
    CAFile   string
}

func (b *RedisBackend) WithTLS(config TLSConfig) (*RedisBackend, error) {
    cert, err := tls.LoadX509KeyPair(config.CertFile, config.KeyFile)
    if err != nil {
        return nil, err
    }
    
    caCert, err := os.ReadFile(config.CAFile)
    if err != nil {
        return nil, err
    }
    
    caCertPool := x509.NewCertPool()
    caCertPool.AppendCertsFromPEM(caCert)
    
    tlsConfig := &tls.Config{
        Certificates: []tls.Certificate{cert},
        RootCAs:      caCertPool,
        ClientCAs:    caCertPool,
        ClientAuth:   tls.RequireAndVerifyClientCert,
    }
    
    b.client.Options().TLSConfig = tlsConfig
    return b, nil
}

// Token-based authentication for admin API
type AdminAuth struct {
    Token     string
    ExpiresAt time.Time
    Scopes    []string
}

func (a *AdminAPI) Authenticate(token string) (*AdminAuth, error) {
    // Verify JWT
    claims, err := verifyJWT(token, a.jwtSecret)
    if err != nil {
        return nil, ErrInvalidToken
    }
    
    // Check expiration
    if claims.ExpiresAt < time.Now().Unix() {
        return nil, ErrTokenExpired
    }
    
    return &AdminAuth{
        Token:     token,
        ExpiresAt: time.Unix(claims.ExpiresAt, 0),
        Scopes:    claims.Scopes,
    }, nil
}

func (a *AdminAPI) RequireScope(auth *AdminAuth, scope string) error {
    if !contains(auth.Scopes, scope) {
        return ErrInsufficientScope
    }
    return nil
}
```

---

## Testing Strategy

### Unit Testing

```go
func TestJobEnqueue(t *testing.T) {
    client := setupTestClient()
    
    job, err := client.Enqueue(ctx, &Job{
        Type: "test",
        Payload: []byte(`{"test": true}`),
    })
    
    require.NoError(t, err)
    assert.NotEmpty(t, job.ID)
    assert.Equal(t, StatusQueued, job.Status)
    assert.WithinDuration(t, time.Now(), job.CreatedAt, time.Second)
}

func TestJobRetry(t *testing.T) {
    rm := NewRetryManager(RetryPolicy{
        MaxRetries: 3,
        InitialDelay: 1 * time.Second,
        Multiplier: 2,
    })
    
    job := &Job{
        Retries: 1,
        MaxRetries: 3,
    }
    
    assert.True(t, rm.ShouldRetry(job, errors.New("test error")))
    
    job.Retries = 3
    assert.False(t, rm.ShouldRetry(job, errors.New("test error")))
}

func TestBackoffCalculation(t *testing.T) {
    tests := []struct {
        attempt  int
        expected time.Duration
    }{
        {0, 1 * time.Second},
        {1, 2 * time.Second},
        {2, 4 * time.Second},
        {3, 8 * time.Second},
    }
    
    backoff := ExponentialBackoff(1*time.Second, 1*time.Hour, 2)
    
    for _, tt := range tests {
        t.Run(fmt.Sprintf("attempt_%d", tt.attempt), func(t *testing.T) {
            result := backoff(tt.attempt)
            assert.Equal(t, tt.expected, result)
        })
    }
}

func TestPriorityOrdering(t *testing.T) {
    q := NewPriorityQueue()
    
    q.Enqueue(&Job{ID: "1", Priority: PriorityLow})
    q.Enqueue(&Job{ID: "2", Priority: PriorityHigh})
    q.Enqueue(&Job{ID: "3", Priority: PriorityMedium})
    q.Enqueue(&Job{ID: "4", Priority: PriorityCritical})
    
    // Should dequeue in priority order
    job, _ := q.Dequeue()
    assert.Equal(t, "4", job.ID) // Critical
    
    job, _ = q.Dequeue()
    assert.Equal(t, "2", job.ID) // High
    
    job, _ = q.Dequeue()
    assert.Equal(t, "3", job.ID) // Medium
    
    job, _ = q.Dequeue()
    assert.Equal(t, "1", job.ID) // Low
}
```

### Integration Testing

```go
func TestWorkerProcessing(t *testing.T) {
    processed := make(chan string, 1)
    
    worker.HandleFunc("test", func(ctx context.Context, job *Job) error {
        processed <- job.ID
        return nil
    })
    
    job, _ := client.Enqueue(ctx, &Job{Type: "test"})
    
    select {
    case id := <-processed:
        assert.Equal(t, job.ID, id)
    case <-time.After(5 * time.Second):
        t.Fatal("timeout waiting for job processing")
    }
}

func TestJobRetryIntegration(t *testing.T) {
    attemptCount := 0
    failUntilAttempt := 3
    
    worker.HandleFunc("flaky", func(ctx context.Context, job *Job) error {
        attemptCount++
        if attemptCount < failUntilAttempt {
            return errors.New("intentional failure")
        }
        return nil
    })
    
    job, _ := client.Enqueue(ctx, &Job{
        Type: "flaky",
        MaxRetries: 5,
    })
    
    // Wait for completion
    var completed bool
    for i := 0; i < 30; i++ {
        status, _ := client.GetJobStatus(ctx, job.ID)
        if status == StatusCompleted {
            completed = true
            break
        }
        time.Sleep(100 * time.Millisecond)
    }
    
    assert.True(t, completed)
    assert.Equal(t, failUntilAttempt, attemptCount)
}

func TestScheduledJobExecution(t *testing.T) {
    executed := make(chan time.Time, 1)
    
    worker.HandleFunc("scheduled", func(ctx context.Context, job *Job) error {
        executed <- time.Now()
        return nil
    })
    
    scheduleAt := time.Now().Add(500 * time.Millisecond)
    _, err := client.ScheduleOnce(ctx, scheduleAt, &Job{Type: "scheduled"})
    require.NoError(t, err)
    
    select {
    case execTime := <-executed:
        assert.WithinDuration(t, scheduleAt, execTime, 200*time.Millisecond)
    case <-time.After(2 * time.Second):
        t.Fatal("scheduled job did not execute")
    }
}

func TestDeadLetterQueue(t *testing.T) {
    worker.HandleFunc("always_fail", func(ctx context.Context, job *Job) error {
        return errors.New("permanent failure")
    })
    
    job, _ := client.Enqueue(ctx, &Job{
        Type: "always_fail",
        MaxRetries: 2,
        Queue: "test",
    })
    
    // Wait for all retries to complete
    time.Sleep(5 * time.Second)
    
    // Check DLQ
    dlqJobs, err := admin.ListDeadLetter(ctx, "test", 100)
    require.NoError(t, err)
    
    found := false
    for _, dlqJob := range dlqJobs {
        if dlqJob.ID == job.ID {
            found = true
            assert.Equal(t, 2, dlqJob.Retries)
            break
        }
    }
    assert.True(t, found, "job should be in DLQ")
}
```

### Load Testing

```go
func BenchmarkEnqueue(b *testing.B) {
    client := setupTestClient()
    ctx := context.Background()
    
    b.ResetTimer()
    b.RunParallel(func(pb *testing.PB) {
        counter := 0
        for pb.Next() {
            counter++
            client.Enqueue(ctx, &Job{
                Type: "benchmark",
                Payload: []byte(fmt.Sprintf(`{"n":%d}`, counter)),
            })
        }
    })
}

func BenchmarkDequeue(b *testing.B) {
    backend := setupTestBackend()
    ctx := context.Background()
    
    // Pre-populate queue
    for i := 0; i < b.N; i++ {
        backend.Enqueue(ctx, "benchmark", &Job{Type: "test"})
    }
    
    b.ResetTimer()
    for i := 0; i < b.N; i++ {
        backend.Dequeue(ctx, "benchmark", "worker-1")
    }
}

func TestLoadTest(t *testing.T) {
    if testing.Short() {
        t.Skip("skipping load test in short mode")
    }
    
    const (
        numJobs     = 10000
        numWorkers  = 20
        targetRate  = 1000 // jobs per second
    )
    
    processed := make(chan time.Duration, numJobs)
    
    // Setup workers
    worker := jobs.NewWorker(jobs.WorkerConfig{
        Queue:       "load_test",
        Concurrency: numWorkers,
    })
    
    worker.HandleFunc("load", func(ctx context.Context, job *Job) error {
        // Simulate work
        time.Sleep(10 * time.Millisecond)
        processed <- time.Since(job.CreatedAt)
        return nil
    })
    
    ctx := context.Background()
    worker.Start(ctx)
    defer worker.Stop()
    
    // Enqueue jobs at target rate
    start := time.Now()
    for i := 0; i < numJobs; i++ {
        client.Enqueue(ctx, &Job{Type: "load", Queue: "load_test"})
        if i%targetRate == 0 {
            time.Sleep(time.Second)
        }
    }
    
    // Wait for all jobs
    var totalDuration time.Duration
    for i := 0; i < numJobs; i++ {
        totalDuration += <-processed
    }
    
    elapsed := time.Since(start)
    actualRate := float64(numJobs) / elapsed.Seconds()
    avgLatency := totalDuration / numJobs
    
    t.Logf("Processed %d jobs in %v", numJobs, elapsed)
    t.Logf("Actual rate: %.2f jobs/sec (target: %d)", actualRate, targetRate)
    t.Logf("Average latency: %v", avgLatency)
    
    assert.Greater(t, actualRate, float64(targetRate)*0.8)
    assert.Less(t, avgLatency, 100*time.Millisecond)
}
```

---

## Deployment Guide

### Kubernetes

```yaml
# Namespace
apiVersion: v1
kind: Namespace
metadata:
  name: jobs-system
  labels:
    app.kubernetes.io/name: jobs
    app.kubernetes.io/component: job-queue

---
# ConfigMap
apiVersion: v1
kind: ConfigMap
metadata:
  name: jobs-config
  namespace: jobs-system
data:
  jobs.yaml: |
    jobs:
      backend:
        type: redis
        redis:
          addr: redis:6379
      queues:
        default:
          concurrency: 10
          max_retries: 3
        critical:
          concurrency: 20
          max_retries: 5
      worker:
        poll_interval: 1s
        shutdown_timeout: 30s
      metrics:
        enabled: true
        port: 8080

---
# Secret
apiVersion: v1
kind: Secret
metadata:
  name: jobs-secrets
  namespace: jobs-system
type: Opaque
stringData:
  redis-password: "${REDIS_PASSWORD}"
  db-password: "${DB_PASSWORD}"

---
# Deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: jobs-worker
  namespace: jobs-system
  labels:
    app: jobs-worker
spec:
  replicas: 5
  strategy:
    type: RollingUpdate
    rollingUpdate:
      maxSurge: 25%
      maxUnavailable: 0
  selector:
    matchLabels:
      app: jobs-worker
  template:
    metadata:
      labels:
        app: jobs-worker
      annotations:
        prometheus.io/scrape: "true"
        prometheus.io/port: "8080"
    spec:
      serviceAccountName: jobs-worker
      affinity:
        podAntiAffinity:
          preferredDuringSchedulingIgnoredDuringExecution:
            - weight: 100
              podAffinityTerm:
                labelSelector:
                  matchExpressions:
                    - key: app
                      operator: In
                      values:
                        - jobs-worker
                topologyKey: kubernetes.io/hostname
      containers:
      - name: worker
        image: myapp/jobs-worker:v1.0.0
        command: ["./worker"]
        args: ["--config", "/config/jobs.yaml"]
        ports:
        - name: metrics
          containerPort: 8080
          protocol: TCP
        env:
        - name: JOBS_BACKEND_TYPE
          value: redis
        - name: JOBS_REDIS_ADDR
          value: redis:6379
        - name: JOBS_REDIS_PASSWORD
          valueFrom:
            secretKeyRef:
              name: jobs-secrets
              key: redis-password
        - name: JOBS_CONCURRENCY
          value: "10"
        - name: POD_NAME
          valueFrom:
            fieldRef:
              fieldPath: metadata.name
        - name: NODE_NAME
          valueFrom:
            fieldRef:
              fieldPath: spec.nodeName
        resources:
          requests:
            memory: "128Mi"
            cpu: "100m"
          limits:
            memory: "512Mi"
            cpu: "1000m"
        livenessProbe:
          httpGet:
            path: /health
            port: 8080
          initialDelaySeconds: 30
          periodSeconds: 10
          timeoutSeconds: 5
          failureThreshold: 3
        readinessProbe:
          httpGet:
            path: /ready
            port: 8080
          initialDelaySeconds: 5
          periodSeconds: 5
          timeoutSeconds: 3
          failureThreshold: 3
        volumeMounts:
        - name: config
          mountPath: /config
          readOnly: true
        - name: tmp
          mountPath: /tmp
        securityContext:
          allowPrivilegeEscalation: false
          runAsNonRoot: true
          runAsUser: 1000
          capabilities:
            drop:
              - ALL
          readOnlyRootFilesystem: true
      volumes:
      - name: config
        configMap:
          name: jobs-config
      - name: tmp
        emptyDir: {}
      terminationGracePeriodSeconds: 60

---
# Service for metrics
apiVersion: v1
kind: Service
metadata:
  name: jobs-worker-metrics
  namespace: jobs-system
  labels:
    app: jobs-worker
spec:
  selector:
    app: jobs-worker
  ports:
  - name: metrics
    port: 8080
    targetPort: 8080
  type: ClusterIP

---
# Horizontal Pod Autoscaler
apiVersion: autoscaling/v2
kind: HorizontalPodAutoscaler
metadata:
  name: jobs-worker-hpa
  namespace: jobs-system
spec:
  scaleTargetRef:
    apiVersion: apps/v1
    kind: Deployment
    name: jobs-worker
  minReplicas: 3
  maxReplicas: 100
  metrics:
  - type: Pods
    pods:
      metric:
        name: jobs_queue_depth
      target:
        type: AverageValue
        averageValue: "100"
  - type: Resource
    resource:
      name: cpu
      target:
        type: Utilization
        averageUtilization: 70
  behavior:
    scaleUp:
      stabilizationWindowSeconds: 60
      policies:
      - type: Pods
        value: 10
        periodSeconds: 60
    scaleDown:
      stabilizationWindowSeconds: 300
      policies:
      - type: Pods
        value: 5
        periodSeconds: 60

---
# PodDisruptionBudget
apiVersion: policy/v1
kind: PodDisruptionBudget
metadata:
  name: jobs-worker-pdb
  namespace: jobs-system
spec:
  minAvailable: 2
  selector:
    matchLabels:
      app: jobs-worker

---
# ServiceMonitor for Prometheus
apiVersion: monitoring.coreos.com/v1
kind: ServiceMonitor
metadata:
  name: jobs-metrics
  namespace: jobs-system
  labels:
    release: prometheus
spec:
  selector:
    matchLabels:
      app: jobs-worker
  endpoints:
  - port: metrics
    interval: 15s
    path: /metrics
    scheme: http

---
# NetworkPolicy
apiVersion: networking.k8s.io/v1
kind: NetworkPolicy
metadata:
  name: jobs-worker-netpol
  namespace: jobs-system
spec:
  podSelector:
    matchLabels:
      app: jobs-worker
  policyTypes:
  - Ingress
  - Egress
  ingress:
  - from:
    - namespaceSelector:
        matchLabels:
          name: monitoring
    ports:
    - protocol: TCP
      port: 8080
  egress:
  - to:
    - podSelector:
        matchLabels:
          app: redis
    ports:
    - protocol: TCP
      port: 6379
  - to:
    - namespaceSelector: {}
      podSelector:
        matchLabels:
          k8s-app: kube-dns
    ports:
    - protocol: UDP
      port: 53
```

### Docker Compose

```yaml
# docker-compose.yml
version: '3.8'

services:
  redis:
    image: redis:7-alpine
    ports:
      - "6379:6379"
    volumes:
      - redis_data:/data
    command: redis-server --appendonly yes --maxmemory 256mb --maxmemory-policy allkeys-lru
    healthcheck:
      test: ["CMD", "redis-cli", "ping"]
      interval: 5s
      timeout: 3s
      retries: 5

  postgres:
    image: postgres:15-alpine
    environment:
      POSTGRES_USER: jobs
      POSTGRES_PASSWORD: jobs_password
      POSTGRES_DB: jobs
    ports:
      - "5432:5432"
    volumes:
      - postgres_data:/var/lib/postgresql/data
      - ./init.sql:/docker-entrypoint-initdb.d/init.sql
    healthcheck:
      test: ["CMD-SHELL", "pg_isready -U jobs"]
      interval: 5s
      timeout: 3s
      retries: 5

  worker:
    build:
      context: .
      dockerfile: Dockerfile.worker
    environment:
      JOBS_BACKEND_TYPE: redis
      JOBS_REDIS_ADDR: redis:6379
      JOBS_DEFAULT_CONCURRENCY: "10"
    depends_on:
      redis:
        condition: service_healthy
    deploy:
      replicas: 3
      restart_policy:
        condition: on-failure
        delay: 5s
        max_attempts: 3

  scheduler:
    build:
      context: .
      dockerfile: Dockerfile.scheduler
    environment:
      JOBS_BACKEND_TYPE: redis
      JOBS_REDIS_ADDR: redis:6379
    depends_on:
      redis:
        condition: service_healthy

  prometheus:
    image: prom/prometheus:latest
    ports:
      - "9090:9090"
    volumes:
      - ./prometheus.yml:/etc/prometheus/prometheus.yml
      - prometheus_data:/prometheus
    command:
      - '--config.file=/etc/prometheus/prometheus.yml'
      - '--storage.tsdb.path=/prometheus'
      - '--web.console.libraries=/usr/share/prometheus/console_libraries'
      - '--web.console.templates=/usr/share/prometheus/consoles'

  grafana:
    image: grafana/grafana:latest
    ports:
      - "3000:3000"
    environment:
      GF_SECURITY_ADMIN_PASSWORD: admin
    volumes:
      - grafana_data:/var/lib/grafana
      - ./grafana/dashboards:/etc/grafana/provisioning/dashboards
      - ./grafana/datasources:/etc/grafana/provisioning/datasources

volumes:
  redis_data:
  postgres_data:
  prometheus_data:
  grafana_data:
```

---

## Monitoring & Observability

### Metrics

```go
// Prometheus metrics
var (
    jobsEnqueued = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "jobs_enqueued_total",
            Help: "Total number of jobs enqueued",
        },
        []string{"queue", "job_type"},
    )
    
    jobsProcessed = prometheus.NewCounterVec(
        prometheus.CounterOpts{
            Name: "jobs_processed_total",
            Help: "Total number of jobs processed",
        },
        []string{"queue", "job_type", "status"},
    )
    
    jobDuration = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "jobs_duration_seconds",
            Help:    "Job processing duration in seconds",
            Buckets: []float64{0.001, 0.01, 0.1, 0.5, 1, 2, 5, 10, 30, 60},
        },
        []string{"queue", "job_type"},
    )
    
    queueDepth = prometheus.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "jobs_queue_depth",
            Help: "Current depth of job queues",
        },
        []string{"queue", "status"},
    )
    
    workersActive = prometheus.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "jobs_workers_active",
            Help: "Number of active workers",
        },
        []string{"queue"},
    )
    
    retryAttempts = prometheus.NewHistogramVec(
        prometheus.HistogramOpts{
            Name:    "jobs_retry_attempts",
            Help:    "Number of retry attempts per job",
            Buckets: []float64{0, 1, 2, 3, 5, 10},
        },
        []string{"queue", "job_type"},
    )
    
    scheduledJobs = prometheus.NewGauge(
        prometheus.GaugeOpts{
            Name: "jobs_scheduled_total",
            Help: "Number of scheduled jobs",
        },
    )
    
    deadLetterQueue = prometheus.NewGaugeVec(
        prometheus.GaugeOpts{
            Name: "jobs_dead_letter_queue_depth",
            Help: "Depth of dead letter queues",
        },
        []string{"queue"},
    )
)

func init() {
    prometheus.MustRegister(
        jobsEnqueued,
        jobsProcessed,
        jobDuration,
        queueDepth,
        workersActive,
        retryAttempts,
        scheduledJobs,
        deadLetterQueue,
    )
}
```

### Health Checks

```go
// Health check endpoints
type HealthStatus struct {
    Status    string                 `json:"status"`
    Checks    map[string]HealthCheck `json:"checks"`
    Timestamp time.Time              `json:"timestamp"`
    Version   string                 `json:"version"`
}

type HealthCheck struct {
    Status    string        `json:"status"`
    Message   string        `json:"message,omitempty"`
    Duration  time.Duration `json:"duration"`
    LastCheck time.Time     `json:"last_check"`
}

func (s *Server) healthHandler(w http.ResponseWriter, r *http.Request) {
    status := HealthStatus{
        Status:    "healthy",
        Checks:    make(map[string]HealthCheck),
        Timestamp: time.Now(),
        Version:   version.Version,
    }
    
    // Backend health
    backendStart := time.Now()
    if err := s.backend.Ping(r.Context()); err != nil {
        status.Checks["backend"] = HealthCheck{
            Status:   "unhealthy",
            Message:  err.Error(),
            Duration: time.Since(backendStart),
        }
        status.Status = "unhealthy"
    } else {
        status.Checks["backend"] = HealthCheck{
            Status:   "healthy",
            Duration: time.Since(backendStart),
        }
    }
    
    // Queue depth check
    for queueName := range s.queues {
        depth, _ := s.backend.GetQueueDepth(r.Context(), queueName)
        if depth > 10000 {
            status.Checks[fmt.Sprintf("queue_%s", queueName)] = HealthCheck{
                Status:  "warning",
                Message: fmt.Sprintf("Queue depth high: %d", depth),
            }
        }
    }
    
    // DLQ check
    dlqDepth, _ := s.backend.GetDeadLetterDepth(r.Context())
    if dlqDepth > 100 {
        status.Checks["dead_letter"] = HealthCheck{
            Status:  "warning",
            Message: fmt.Sprintf("DLQ has %d jobs", dlqDepth),
        }
    }
    
    w.Header().Set("Content-Type", "application/json")
    if status.Status != "healthy" {
        w.WriteHeader(http.StatusServiceUnavailable)
    }
    json.NewEncoder(w).Encode(status)
}

func (s *Server) readyHandler(w http.ResponseWriter, r *http.Request) {
    // Check if workers are running
    if !s.workerPool.IsRunning() {
        w.WriteHeader(http.StatusServiceUnavailable)
        json.NewEncoder(w).Encode(map[string]string{
            "status":  "not_ready",
            "message": "worker pool not running",
        })
        return
    }
    
    // Check backend connectivity
    if err := s.backend.Ping(r.Context()); err != nil {
        w.WriteHeader(http.StatusServiceUnavailable)
        json.NewEncoder(w).Encode(map[string]string{
            "status":  "not_ready",
            "message": fmt.Sprintf("backend unavailable: %v", err),
        })
        return
    }
    
    w.WriteHeader(http.StatusOK)
    json.NewEncoder(w).Encode(map[string]string{"status": "ready"})
}
```

### Logging

```go
// Structured logging
type JobLogEntry struct {
    Level      string                 `json:"level"`
    Message    string                 `json:"msg"`
    JobID      string                 `json:"job_id,omitempty"`
    JobType    string                 `json:"job_type,omitempty"`
    Queue      string                 `json:"queue,omitempty"`
    WorkerID   string                 `json:"worker_id,omitempty"`
    Duration   time.Duration          `json:"duration,omitempty"`
    Error      string                 `json:"error,omitempty"`
    RetryCount int                    `json:"retry_count,omitempty"`
    Fields     map[string]interface{} `json:"fields,omitempty"`
    Timestamp  time.Time              `json:"ts"`
}

func (l *JobLogger) LogJobStart(job *Job, workerID string) {
    l.logger.Info("Job started",
        slog.String("job_id", job.ID),
        slog.String("job_type", job.Type),
        slog.String("queue", job.Queue),
        slog.String("worker_id", workerID),
        slog.Int("retry_count", job.Retries),
        slog.Time("created_at", job.CreatedAt),
        slog.Duration("time_in_queue", time.Since(job.CreatedAt)),
    )
}

func (l *JobLogger) LogJobComplete(job *Job, duration time.Duration) {
    l.logger.Info("Job completed",
        slog.String("job_id", job.ID),
        slog.String("job_type", job.Type),
        slog.Duration("duration", duration),
        slog.String("status", "success"),
    )
}

func (l *JobLogger) LogJobFailed(job *Job, err error, willRetry bool) {
    level := slog.LevelError
    if willRetry {
        level = slog.LevelWarn
    }
    
    l.logger.Log(level, "Job failed",
        slog.String("job_id", job.ID),
        slog.String("job_type", job.Type),
        slog.String("error", err.Error()),
        slog.Int("retry_count", job.Retries),
        slog.Bool("will_retry", willRetry),
    )
}
```

---

## Scaling Strategies

### Horizontal Scaling

```go
// Worker pool scaling
type AutoScaler struct {
    workerPool  *WorkerPool
    backend     Backend
    queueName   string
    minWorkers  int
    maxWorkers  int
    targetDepth int
    cooldown    time.Duration
    lastScale   time.Time
}

func (as *AutoScaler) Run(ctx context.Context) {
    ticker := time.NewTicker(10 * time.Second)
    defer ticker.Stop()
    
    for {
        select {
        case <-ctx.Done():
            return
        case <-ticker.C:
            as.evaluate()
        }
    }
}

func (as *AutoScaler) evaluate() {
    // Check cooldown
    if time.Since(as.lastScale) < as.cooldown {
        return
    }
    
    // Get current metrics
    depth, _ := as.backend.GetQueueDepth(context.Background(), as.queueName)
    currentWorkers := as.workerPool.GetWorkerCount()
    
    // Calculate target workers
    // Target: each worker should handle ~10 jobs
    targetWorkers := depth / 10
    if targetWorkers < as.minWorkers {
        targetWorkers = as.minWorkers
    }
    if targetWorkers > as.maxWorkers {
        targetWorkers = as.maxWorkers
    }
    
    // Scale if difference is significant
    diff := targetWorkers - currentWorkers
    if abs(diff) > 5 {
        if err := as.workerPool.Scale(targetWorkers); err == nil {
            as.lastScale = time.Now()
            slog.Info("Auto-scaled workers",
                "queue", as.queueName,
                "from", currentWorkers,
                "to", targetWorkers,
                "depth", depth,
            )
        }
    }
}
```

### Queue Partitioning

```go
// Sharded queue for high throughput
type ShardedQueue struct {
    numShards int
    backends  []Backend
    hasher    hash.Hash32
}

func NewShardedQueue(numShards int, backendFactory func(shard int) (Backend, error)) (*ShardedQueue, error) {
    backends := make([]Backend, numShards)
    for i := 0; i < numShards; i++ {
        backend, err := backendFactory(i)
        if err != nil {
            return nil, err
        }
        backends[i] = backend
    }
    
    return &ShardedQueue{
        numShards: numShards,
        backends:  backends,
        hasher:    fnv.New32a(),
    }, nil
}

func (sq *ShardedQueue) getShard(jobID string) int {
    sq.hasher.Reset()
    sq.hasher.Write([]byte(jobID))
    return int(sq.hasher.Sum32()) % sq.numShards
}

func (sq *ShardedQueue) Enqueue(ctx context.Context, job *Job) error {
    shard := sq.getShard(job.ID)
    return sq.backends[shard].Enqueue(ctx, job.Queue, job)
}

func (sq *ShardedQueue) Dequeue(ctx context.Context, queue string, workerID string) (*Job, error) {
    // Try each shard in round-robin
    for i := 0; i < sq.numShards; i++ {
        idx := (i + sq.roundRobinCounter) % sq.numShards
        sq.roundRobinCounter++
        
        job, err := sq.backends[idx].Dequeue(ctx, queue, workerID)
        if err == nil {
            return job, nil
        }
        if err != ErrNoJobs {
            return nil, err
        }
    }
    return nil, ErrNoJobs
}
```

---

## Troubleshooting

### Common Issues

**1. Jobs not being processed**
```
Symptom: Jobs enqueued but not processed
Cause: Workers not running or wrong queue
Solution: 
  1. Check worker status: `go run cmd/admin/main.go workers`
  2. Verify queue names match between enqueue and worker
  3. Check worker logs for errors
  4. Ensure backend connectivity
```

**2. Job timeouts**
```
Symptom: Jobs failing with timeout
Cause: Job taking longer than timeout setting
Solution:
  1. Check job logs for actual duration
  2. Increase timeout in queue config
  3. Optimize job performance
  4. Split job into smaller tasks
```

**3. Redis connection issues**
```
Symptom: Cannot enqueue jobs
Cause: Redis unavailable or misconfigured
Solution:
  1. Check Redis status: `redis-cli ping`
  2. Verify connection string
  3. Check network connectivity
  4. Review Redis max connections
  5. Check Redis memory usage
```

**4. Dead letter queue growing**
```
Symptom: DLQ size increasing rapidly
Cause: Jobs consistently failing
Solution:
  1. Analyze DLQ job patterns
  2. Check for code bugs in handlers
  3. Verify external dependencies
  4. Review error messages
  5. Implement circuit breakers
```

**5. Memory leaks**
```
Symptom: Worker memory growing over time
Cause: Resources not being released
Solution:
  1. Check for goroutine leaks
  2. Verify DB connections are closed
  3. Review job handler cleanup
  4. Check metrics collection
  5. Profile with pprof
```

### Debug Commands

```bash
# Check queue stats
redis-cli --eval queue_stats.lua

# List failed jobs
go run cmd/admin/main.go list --status=failed --limit=100

# Retry failed job
go run cmd/admin/main.go retry --id=<job-id>

# Inspect job details
go run cmd/admin/main.go inspect --id=<job-id>

# Purge completed jobs
go run cmd/admin/main.go purge --queue=default --older-than=7d

# Check worker health
curl http://worker:8080/health

# View metrics
curl http://worker:8080/metrics

# Real-time queue monitoring
watch -n 1 'redis-cli LLEN jobs:queue:default'
```

---

## Appendices

### Appendix A: Complete API Reference

#### Client Methods

```go
// Enqueue methods
type Client interface {
    // Basic enqueue
    Enqueue(ctx context.Context, job *Job) (*Job, error)
    EnqueueWithOptions(ctx context.Context, job *Job, opts EnqueueOptions) (*Job, error)
    EnqueueBatch(ctx context.Context, jobs []*Job) ([]EnqueueResult, error)
    
    // Scheduling
    Schedule(ctx context.Context, cronExpr string, job *Job) (*ScheduledJob, error)
    ScheduleOnce(ctx context.Context, at time.Time, job *Job) (*ScheduledJob, error)
    ScheduleCron(ctx context.Context, cronExpr string, job *Job) (*ScheduledJob, error)
    Unschedule(ctx context.Context, jobID string) error
    
    // Chaining
    NewChain() *JobChain
    
    // Job management
    GetJob(ctx context.Context, jobID string) (*Job, error)
    GetJobStatus(ctx context.Context, jobID string) (Status, error)
    CancelJob(ctx context.Context, jobID string) error
    DeleteJob(ctx context.Context, jobID string) error
    
    // Admin
    Admin() AdminClient
}

type EnqueueOptions struct {
    Queue      string
    Priority   Priority
    Delay      time.Duration
    MaxRetries int
    Unique     bool
    UniqueTTL  time.Duration
    Metadata   map[string]string
}
```

#### Worker Methods

```go
type Worker interface {
    // Handler registration
    HandleFunc(jobType string, handler HandlerFunc)
    Handle(jobType string, handler Handler, opts HandlerOptions)
    HandleBatch(jobType string, handler BatchHandler, opts BatchOptions)
    
    // Middleware
    Use(middleware ...Middleware)
    
    // Lifecycle
    Start(ctx context.Context) error
    Stop(ctx context.Context) error
    Pause() error
    Resume() error
    
    // Scaling
    Scale(n int) error
    
    // Status
    IsRunning() bool
    GetStats() WorkerStats
}
```

### Appendix B: Backend Configuration Reference

#### Redis Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| Addr | string | localhost:6379 | Redis server address |
| Password | string | "" | Redis password |
| DB | int | 0 | Redis database number |
| PoolSize | int | 10 | Connection pool size |
| MinIdleConns | int | 2 | Minimum idle connections |
| MaxRetries | int | 3 | Max retry attempts |
| DialTimeout | time.Duration | 5s | Connection timeout |
| ReadTimeout | time.Duration | 3s | Read timeout |
| WriteTimeout | time.Duration | 3s | Write timeout |

#### PostgreSQL Configuration

| Option | Type | Default | Description |
|--------|------|---------|-------------|
| Host | string | localhost | Database host |
| Port | int | 5432 | Database port |
| Database | string | jobs | Database name |
| User | string | jobs | Database user |
| Password | string | "" | Database password |
| SSLMode | string | prefer | SSL mode |
| PoolSize | int | 20 | Max connections |

### Appendix C: Migration Guide

#### Migrating from Asynq

```go
// Before (Asynq)
client := asynq.NewClient(asynq.RedisClientOpt{Addr: "localhost:6379"})
task := asynq.NewTask("send_email", payload)
info, err := client.Enqueue(task)

// After (this library)
client, _ := jobs.NewClient(jobs.Config{
    Backend: &jobs.RedisBackendConfig{Addr: "localhost:6379"},
})
job, err := client.Enqueue(ctx, &jobs.Job{
    Type: "send_email",
    Payload: payload,
})
```

#### Migrating from Machinery

```go
// Before (Machinery)
signature := &tasks.Signature{
    Name: "send_email",
    Args: []tasks.Arg{{Type: "string", Value: email}},
}
asyncResult, err := server.SendTaskWithContext(ctx, signature)

// After (this library)
job, err := client.Enqueue(ctx, &jobs.Job{
    Type: "send_email",
    Payload: mustMarshal(EmailPayload{Email: email}),
})
```

### Appendix D: Comparison Matrix

| Feature | This Library | Asynq | River | Machinery | Temporal |
|---------|-------------|-------|-------|-----------|----------|
| Redis Backend | ✓ | ✓ | - | ✓ | Custom |
| PostgreSQL Backend | ✓ | - | ✓ | ✓ | Custom |
| SQS Backend | ✓ | - | - | ✓ | - |
| NATS Backend | ✓ | - | - | - | - |
| Cron Scheduling | ✓ | ✓ | ✓ | - | ✓ |
| Priority Queues | ✓ | ✓ | ✓ | ✓ | ✓ |
| Dead Letter Queue | ✓ | ✓ | ✓ | - | ✓ |
| Middleware | ✓ | ✓ | - | - | Interceptors |
| Batch Processing | ✓ | - | - | ✓ | ✓ |
| Job Chaining | ✓ | - | - | ✓ | Workflows |
| Metrics | ✓ | ✓ | ✓ | - | ✓ |
| Transactions | ✓ | - | ✓ | - | ✓ |
| Unique Jobs | ✓ | ✓ | ✓ | - | - |
| Distributed Locks | ✓ | ✓ | Advisory | - | - |
| Web UI | - | Built-in | - | - | ✓ |
| Language | Go | Go | Go | Go | Multi |

### Appendix E: Performance Tuning

#### Redis Tuning

```conf
# redis.conf optimizations for job queues
maxmemory 2gb
maxmemory-policy allkeys-lru
save ""  # Disable RDB for pure queue use
dir /data
appendonly yes
appendfsync everysec
no-appendfsync-on-rewrite yes
auto-aof-rewrite-percentage 100
auto-aof-rewrite-min-size 64mb

# Network
tcp-keepalive 300
tcp-backlog 511
timeout 0

# Performance
databases 1
lazyfree-lazy-eviction yes
lazyfree-lazy-expire yes
lazyfree-lazy-server-del yes
```

#### Worker Tuning

```go
// High-throughput configuration
config := jobs.WorkerConfig{
    Concurrency:      50,              // More workers
    PollInterval:     100 * time.Millisecond, // Faster polling
    MaxJobs:          10000,           // Larger buffer
    EnablePriority:   true,
    EnableScheduled:  true,
}

// Low-latency configuration
config := jobs.WorkerConfig{
    Concurrency:      10,
    PollInterval:     10 * time.Millisecond, // Very fast polling
    MaxJobs:          100,
}

// Memory-efficient configuration
config := jobs.WorkerConfig{
    Concurrency:      5,
    PollInterval:     1 * time.Second,
    MaxJobs:          100,
}
```

### Appendix F: Security Checklist

- [ ] Enable TLS for backend connections
- [ ] Use strong authentication for Redis/PostgreSQL
- [ ] Validate job payloads before processing
- [ ] Implement payload encryption for sensitive data
- [ ] Set up queue ACLs for multi-tenancy
- [ ] Configure job timeouts to prevent resource exhaustion
- [ ] Enable audit logging for job operations
- [ ] Implement rate limiting on job enqueue
- [ ] Sanitize error messages before logging
- [ ] Use mTLS for inter-service communication
- [ ] Rotate encryption keys regularly
- [ ] Monitor for unusual job patterns (potential attacks)

### Appendix G: Testing Patterns

#### Table-Driven Tests

```go
func TestJobTransitions(t *testing.T) {
    tests := []struct {
        name       string
        from       Status
        to         Status
        shouldWork bool
    }{
        {"pending to processing", StatusPending, StatusProcessing, true},
        {"processing to completed", StatusProcessing, StatusCompleted, true},
        {"processing to failed", StatusProcessing, StatusFailed, true},
        {"completed to processing", StatusCompleted, StatusProcessing, false},
        {"failed to completed", StatusFailed, StatusCompleted, false},
    }
    
    for _, tt := range tests {
        t.Run(tt.name, func(t *testing.T) {
            result := tt.from.CanTransition(tt.to)
            assert.Equal(t, tt.shouldWork, result)
        })
    }
}
```

#### Property-Based Testing

```go
func TestJobPriorityOrdering(t *testing.T) {
    // Property: Higher priority jobs are always dequeued before lower priority
    if err := quick.Check(func(priorities []Priority) bool {
        q := NewPriorityQueue()
        
        // Enqueue jobs with random priorities
        for i, p := range priorities {
            q.Enqueue(&Job{ID: fmt.Sprintf("%d", i), Priority: p})
        }
        
        // Dequeue and verify ordering
        lastPriority := PriorityCritical + 1
        for q.Len() > 0 {
            job, _ := q.Dequeue()
            if job.Priority > lastPriority {
                return false
            }
            lastPriority = job.Priority
        }
        return true
    }, nil); err != nil {
        t.Error(err)
    }
}
```

### Appendix H: Deployment Checklist

Pre-deployment:
- [ ] Load tests passed
- [ ] All migrations applied
- [ ] Configuration validated
- [ ] Secrets configured
- [ ] Monitoring enabled
- [ ] Alerts configured
- [ ] Health checks verified
- [ ] Rollback plan prepared

Deployment:
- [ ] Deploy to staging
- [ ] Verify metrics collection
- [ ] Run smoke tests
- [ ] Deploy to production (canary)
- [ ] Monitor error rates
- [ ] Scale up gradually
- [ ] Verify job processing

Post-deployment:
- [ ] Monitor queue depths
- [ ] Check worker health
- [ ] Verify DLQ is empty
- [ ] Review latency metrics
- [ ] Document any issues

### Appendix I: Troubleshooting Matrix

| Symptom | Possible Causes | Diagnostic Steps | Solution |
|---------|----------------|------------------|----------|
| Jobs not processing | Workers down, backend down, wrong queue | Check worker status, ping backend, verify queue names | Restart workers, fix backend connection, correct queue config |
| High latency | Slow handlers, resource contention, backend slow | Profile handlers, check CPU/memory, measure backend latency | Optimize handlers, scale resources, tune backend |
| Memory growth | Goroutine leaks, unbounded queues, large payloads | pprof goroutines, check queue depths, validate payload sizes | Fix goroutine cleanup, add queue limits, implement payload validation |
| DLQ growing | Code bugs, external failures, bad data | Analyze DLQ patterns, check error logs, inspect payloads | Fix code bugs, add retries, validate data |
| Connection errors | Network issues, backend overloaded, auth failures | Check connectivity, monitor backend load, verify credentials | Fix network, scale backend, rotate credentials |
| Duplicate jobs | Unique constraints failing, retries, bugs | Check unique key collisions, review retry logic, audit code | Fix unique constraints, adjust retry policy, fix bugs |

### Appendix J: Changelog

#### Version 1.0.0 (2026-04-05)
- Initial stable release
- Redis and PostgreSQL backends
- Job scheduling with cron
- Priority queues
- Dead letter queue
- Middleware support
- Prometheus metrics
- Kubernetes deployment support

#### Version 0.9.0 (2026-03-01)
- Beta release
- Worker auto-scaling
- Batch processing
- Job chaining
- Improved retry policies

#### Version 0.8.0 (2026-02-01)
- Alpha release
- NATS backend support
- SQS backend support
- Admin API
- Web dashboard (experimental)

---

*End of jobs Specification - 2,500+ lines*
