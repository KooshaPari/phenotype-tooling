# Performance Optimization Reference

## 1. Algorithm Complexity

### Big O Notation

| Operation | List | Dict | Set |
|-----------|------|------|-----|
| Access | O(1) | O(1) | N/A |
| Search | O(n) | O(1) | O(1) |
| Insert | O(1)* | O(1) | O(1) |
| Delete | O(n) | O(1) | O(1) |
| Sort | O(n log n) | N/A | N/A |

*Amortized for append

### Code Examples

**Use dict/set for lookups:**
```python
# BAD: O(n) lookup
def find_user(users: list, user_id: int):
    for user in users:
        if user["id"] == user_id:
            return user

# GOOD: O(1) lookup
def find_user(users: list, user_id: int):
    users_by_id = {u["id"]: u for u in users}
    return users_by_id.get(user_id)
```

**Use heapq for top-k:**
```python
import heapq

def get_top_k(items: list, k: int) -> list:
    heap = []
    for item in items:
        heapq.heappush(heap, (item["score"], item))
        if len(heap) > k:
            heapq.heappop(heap)
    return [item for _, item in heap]
```

---

## 2. Caching Strategies

### Memoization
```python
from functools import lru_cache

@lru_cache(maxsize=128)
def expensive_computation(n: int) -> int:
    if n <= 1:
        return n
    return expensive_computation(n-1) + expensive_computation(n-2)
```

### Redis Cache
```python
import redis
import json
import hashlib

redis_pool = redis.ConnectionPool(host='localhost', port=6379, max_connections=20)

def redis_cache(ttl: int = 300):
    def decorator(func):
        def make_key(*args, **kwargs):
            key_data = f"{func.__name__}:{args}:{kwargs}"
            return hashlib.md5(key_data.encode()).hexdigest()

        def wrapper(*args, **kwargs):
            r = redis.Redis(connection_pool=redis_pool)
            cached = r.get(make_key(*args, **kwargs))
            if cached:
                return json.loads(cached)
            result = func(*args, **kwargs)
            r.setex(make_key(*args, **kwargs), ttl, json.dumps(result))
            return result
        return wrapper
    return decorator
```

---

## 3. Database Optimization

### N+1 Prevention
```python
from sqlalchemy.orm import joinedload, selectinload

# BAD: N+1 queries
def get_orders_with_users_slow(session):
    orders = session.execute(select(Order)).scalars().all()
    for order in orders:
        print(order.user.name)  # Triggers query per order!

# GOOD: Eager loading
def get_orders_with_users_fast(session):
    orders = session.execute(
        select(Order).options(joinedload(Order.user))
    ).scalars().unique().all()
    return orders
```

### Batch Operations
```python
# Bulk insert
def insert_users_fast(session, users_data: list):
    session.execute(User.__table__.insert(), users_data)
    session.commit()

# Upsert for PostgreSQL
from sqlalchemy.dialects.postgresql import insert as pg_insert
def upsert_users(session, users_data: list):
    stmt = pg_insert(User.__table__).values(users_data)
    stmt = stmt.on_conflict_do_update(
        index_elements=['email'],
        set_={k: stmt.excluded[k] for k in ['name', 'updated_at']}
    )
    session.execute(stmt)
    session.commit()
```

---

## 4. Async/Parallel Patterns

### asyncio with Semaphore
```python
import asyncio

async def fetch_all_urls(urls: list, max_concurrent: int = 10):
    semaphore = asyncio.Semaphore(max_concurrent)

    async def bounded_fetch(url: str):
        async with semaphore:
            async with aiohttp.ClientSession() as session:
                return await session.get(url)

    tasks = [bounded_fetch(url) for url in urls]
    return await asyncio.gather(*tasks)
```

### ProcessPoolExecutor for CPU-bound
```python
from concurrent.futures import ProcessPoolExecutor

def process_item(item: dict) -> dict:
    return heavy_computation(item)

def process_batch_parallel(items: list, workers: int = 4) -> list:
    with ProcessPoolExecutor(max_workers=workers) as executor:
        return list(executor.map(process_item, items))
```

---

## 5. Memory Management

### Streaming
```python
# BAD: Load all into memory
def process_large_file_slow(filepath: str):
    with open(filepath) as f:
        lines = f.readlines()
    return [process_line(line) for line in lines]

# GOOD: Stream line by line
def process_large_file_fast(filepath: str):
    with open(filepath) as f:
        for line in f:
            yield process_line(line)
```

### Pagination
```python
def fetch_items_paginated(session, cursor: str = None, page_size: int = 100):
    query = session.query(Item).order_by(Item.id)
    if cursor:
        query = query.filter(Item.id > int(cursor))
    items = query.limit(page_size + 1).all()
    has_more = len(items) > page_size
    if has_more:
        items = items[:page_size]
    next_cursor = str(items[-1].id) if items and has_more else None
    return {"items": items, "next_cursor": next_cursor}
```

---

## 6. Profiling Tools

### Python Profiling
```bash
# cProfile (built-in)
python -m cProfile -s time myscript.py

# py-spy (sampling profiler, no code changes)
pip install py-spy
py-spy record -o profile.svg -- python myscript.py

# memory_profiler
pip install memory-profiler
python -m memory_profiler myscript.py
```

### Line Profiler
```python
# pip install line-profiler
@profile  # Decorator for line-by-line profiling
def slow_function():
    data = expensive_operation()
    return process(data)

# Run: kernprof -l -v script.py
```

### Async Profiling
```python
import yappi

yappi.set_clock_type("wall")
yappi.start()

# ... async code ...

yappi.stop()
threads = yappi.get_thread_stats()
for thread in threads:
    print(f"Thread {thread.name}: {thread.ttot}s")
```

---

## 7. Database Query Optimization

### Query Analysis
```sql
-- PostgreSQL EXPLAIN ANALYZE
EXPLAIN (ANALYZE, BUFFERS, FORMAT JSON)
SELECT * FROM orders WHERE user_id = 123;

-- Check for:
-- - Sequential scans (should use index)
-- - High row estimates vs actual
-- - Hash joins on large tables
```

### Index Strategies
```sql
-- Composite index for common query patterns
CREATE INDEX idx_orders_user_status ON orders(user_id, status);

-- Partial index for common filters
CREATE INDEX idx_orders_active ON orders(created_at)
WHERE status = 'active';

-- Covering index (include frequently selected columns)
CREATE INDEX idx_orders_covering ON orders(user_id)
INCLUDE (total, status);
```

### Connection Pooling
```python
from sqlalchemy import create_engine

# Good pool configuration
engine = create_engine(
    DATABASE_URL,
    pool_size=10,          # Permanent connections
    max_overflow=5,        # Additional connections under load
    pool_timeout=30,       # Wait time for connection
    pool_recycle=1800,     # Recycle connections after 30 min
    pool_pre_ping=True,    # Check connection health
)
```

---

## 8. Caching Strategies

### Cache Patterns
| Pattern | Use Case | Cache Key |
|---------|----------|-----------|
| Cache-Aside | Read-heavy, stale OK | `entity:{id}` |
| Write-Through | Consistency critical | `entity:{id}` |
| Write-Behind | Write-heavy, eventual OK | `entity:{id}` |
| Refresh-Ahead | Predictable access | Pre-warm before expiry |

### Cache Invalidation
```python
# Tag-based invalidation
def cache_with_tags(key: str, tags: list[str], ttl: int = 300):
    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            result = func(*args, **kwargs)
            redis.setex(key, ttl, json.dumps(result))
            # Map key to tags for bulk invalidation
            for tag in tags:
                redis.sadd(f"tag:{tag}", key)
            return result
        return wrapper
    return decorator

def invalidate_tag(tag: str):
    """Invalidate all keys with this tag"""
    keys = redis.smembers(f"tag:{tag}")
    if keys:
        redis.delete(*keys)
    redis.delete(f"tag:{tag}")
```

---

## 9. Frontend Performance

### Core Web Vitals
| Metric | Target | Measurement |
|--------|--------|-------------|
| LCP (Largest Contentful Paint) | < 2.5s | Main content visible |
| FID (First Input Delay) | < 100ms | Interactivity |
| CLS (Cumulative Layout Shift) | < 0.1 | Visual stability |
| TTFB (Time to First Byte) | < 600ms | Server response |

### Optimization Techniques
```javascript
// Code splitting
const LazyComponent = React.lazy(() => import('./HeavyComponent'));

// Image optimization
<img src="image.webp" loading="lazy" decoding="async" />

// Preload critical resources
<link rel="preload" href="critical.css" as="style" />
<link rel="preconnect" href="https://api.example.com" />

// Bundle analysis
// import { visualize } from 'rollup-plugin-visualizer'
```

---

## 10. Load Testing

### Locust (Python)
```python
from locust import HttpUser, task, between

class APIUser(HttpUser):
    wait_time = between(1, 3)

    @task(3)
    def get_users(self):
        self.client.get("/api/users")

    @task(1)
    def create_user(self):
        self.client.post("/api/users", json={"name": "test"})

# Run: locust -f locustfile.py --host http://localhost:8000
```

### k6 (JavaScript)
```javascript
import http from 'k6/http';
import { check, sleep } from 'k6';

export const options = {
  stages: [
    { duration: '30s', target: 20 },   // Ramp up
    { duration: '1m', target: 20 },    // Steady
    { duration: '30s', target: 100 },  // Spike
    { duration: '1m', target: 100 },   // Sustained
    { duration: '30s', target: 0 },    // Ramp down
  ],
  thresholds: {
    http_req_duration: ['p(95)<500'],  // 95% < 500ms
    http_req_failed: ['rate<0.01'],     // < 1% errors
  },
};

export default function () {
  http.get('https://api.example.com/users');
  sleep(1);
}
```

---

## Summary

| Scenario | Optimization |
|----------|--------------|
| Frequent lookups | dict/set |
| Expensive function calls | @lru_cache, Redis |
| Database N+1 | joinedload, selectinload |
| Large file processing | generators, streaming |
| I/O-bound concurrency | asyncio.gather |
| CPU-bound parallel | ProcessPoolExecutor |
| API rate limits | asyncio.Semaphore |
| Large result sets | pagination, cursor |
| Slow queries | EXPLAIN ANALYZE, indexes |
| High latency | CDN, edge caching |
| Memory pressure | generators, object pooling |
| Frontend LCP | code splitting, image optimization |

---

## Performance Production Checklist

- [ ] Profiling done for hot paths
- [ ] Database queries optimized (no sequential scans on large tables)
- [ ] Connection pooling configured
- [ ] Caching implemented for read-heavy data
- [ ] N+1 queries eliminated
- [ ] Pagination for all list endpoints
- [ ] Rate limiting configured
- [ ] Load testing completed
- [ ] P95 latency < 500ms
- [ ] Memory profile stable (no leaks)
- [ ] Core Web Vitals meeting targets (frontend)
- [ ] CDN configured for static assets
