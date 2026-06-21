# SPEC-4SGM-001: 4SGM Technical Specification

**Status:** Active
**Version:** 1.0.0
**Date:** 2026-02-24
**Last Modified:** 2026-02-24

---

## 1. System Architecture

### 1.1 High-Level Design

```
┌─────────────────────────────────────────────────────────────────┐
│                        User (Browser)                           │
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTPS/SSE
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                    Next.js Frontend (Layer 7)                   │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐│
│  │ Chat UI     │  │ Product     │  │ Admin Dashboard          ││
│  │ Component   │  │ Cards       │  │                         ││
│  └─────────────┘  └─────────────┘  └─────────────────────────┘│
└──────────────────────────┬──────────────────────────────────────┘
                           │ HTTP/WebSocket
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│                   MCP Server (Layer 6)                          │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐│
│  │ FastMCP     │  │ Tool        │  │ OAuth/Auth             ││
│  │ Server      │  │ Registry    │  │ Handler                ││
│  └─────────────┘  └─────────────┘  └─────────────────────────┘│
└──────────────────────────┬──────────────────────────────────────┘
                           │ LangGraph
                           ▼
┌─────────────────────────────────────────────────────────────────┐
│               Agent Orchestration (Layer 5)                     │
│  ┌─────────────┐  ┌─────────────┐  ┌─────────────────────────┐│
│  │ Router      │  │ ReAct       │  │ Deep Agents            ││
│  │ Agent       │  │ Agent       │  │ (Reasoning)            ││
│  └─────────────┘  └─────────────┘  └─────────────────────────┘│
└──────────────────────────┬──────────────────────────────────────┘
                           │
         ┌─────────────────┼─────────────────┐
         ▼                 ▼                 ▼
┌─────────────────┐ ┌─────────────┐ ┌─────────────────┐
│  Search Service  │ │  Rec       │ │  Order Service  │
│  (PostgreSQL)   │ │  Engine    │ │  (ERP Sync)     │
└─────────────────┘ └─────────────┘ └─────────────────┘
```

---

## 2. Technology Stack

### 2.1 Frontend

| Technology | Version | Purpose |
|------------|---------|---------|
| Next.js | 14.x | React framework |
| TypeScript | 5.x | Type safety |
| Tailwind CSS | 3.x | Styling |
| Shadcn UI | latest | Component library |
| SSE | - | Real-time updates |

### 2.2 Backend

| Technology | Version | Purpose |
|------------|---------|---------|
| Python | 3.11+ | Runtime |
| FastMCP | 2.13 | MCP server |
| LangGraph | 0.x | Agent orchestration |
| Langfuse | latest | Observability |
| PostgreSQL | 15+ | Database |
| Redis | 7+ | Caching |

### 2.3 LLM Integration

| Provider | Model | Use Case |
|----------|-------|----------|
| Anthropic | Claude 3.5 | Primary reasoning |
| OpenAI | GPT-4o | Fallback |

---

## 3. API Specification

### 3.1 Search API

```python
# Request
POST /api/search
{
    "query": "LED bulbs 12W warm white",
    "filters": {
        "price_min": 0,
        "price_max": 50,
        "category": "lighting"
    },
    "limit": 20
}

# Response
{
    "results": [
        {
            "id": "prod_123",
            "name": "LED Bulb 12W E27 Warm White",
            "sku": "LED-12W-E27-WW",
            "price": 9.99,
            "stock": 500,
            "thumbnail": "https://...",
            "confidence": 0.95
        }
    ],
    "total": 45,
    "query_time_ms": 234
}
```

### 3.2 Recommendations API

```python
# Request
GET /api/recommend?user_id=user_123&context=browsing&limit=10

# Response
{
    "recommendations": [
        {
            "product_id": "prod_456",
            "score": 0.92,
            "reason": "Frequently bought together"
        }
    ],
    "algorithm": "hybrid_collaborative"
}
```

### 3.3 Order API

```python
# Create Order
POST /api/orders
{
    "items": [
        {"product_id": "prod_123", "quantity": 100}
    ],
    "shipping_address": {...},
    "payment_method": "invoice"
}

# Response
{
    "order_id": "ord_789",
    "status": "confirmed",
    "total": 899.10,
    "estimated_delivery": "2026-03-01"
}
```

---

## 4. Database Schema

### 4.1 Products Table

```sql
CREATE TABLE products (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sku VARCHAR(50) UNIQUE NOT NULL,
    name VARCHAR(255) NOT NULL,
    description TEXT,
    category VARCHAR(100),
    brand VARCHAR(100),
    price DECIMAL(10, 2) NOT NULL,
    cost DECIMAL(10, 2),
    stock_quantity INTEGER DEFAULT 0,
    reorder_point INTEGER DEFAULT 10,
    image_urls JSONB,
    attributes JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_products_sku ON products(sku);
CREATE INDEX idx_products_category ON products(category);
CREATE INDEX idx_products_search ON products USING gin(to_tsvector('english', name || ' ' || description));
```

### 4.2 Orders Table

```sql
CREATE TABLE orders (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    user_id UUID REFERENCES users(id),
    status VARCHAR(50) DEFAULT 'pending',
    subtotal DECIMAL(10, 2),
    tax DECIMAL(10, 2),
    shipping DECIMAL(10, 2),
    total DECIMAL(10, 2),
    shipping_address JSONB,
    created_at TIMESTAMP DEFAULT NOW(),
    updated_at TIMESTAMP DEFAULT NOW()
);

CREATE INDEX idx_orders_user ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
```

---

## 5. Agent Flow

### 5.1 Conversation Flow

```
User Message
    │
    ▼
┌──────────────────┐
│  Router Agent    │ ← Classify intent
└────────┬─────────┘
         │
    ┌────┴────┐
    ▼         ▼
┌───────┐ ┌───────┐
│ ReAct │ │ Deep  │ ← Determine complexity
│ Agent │ │Agent  │
└───┬───┘ └───┬───┘
    │         │
    └────┬────┘
         │
         ▼
┌──────────────────┐
│   Tool Executor  │
└────────┬─────────┘
         │
         ▼
┌──────────────────┐
│ Response Gen    │
└────────┬─────────┘
         │
         ▼
    User Response
```

### 5.2 Intent Classification

| Intent | Handler | Example |
|--------|---------|---------|
| SEARCH | ReAct | "Find LED bulbs" |
| RECOMMEND | DeepAgent | "What should I buy?" |
| ORDER | DeepAgent | "Order 100 units" |
| TRACK | ReAct | "Where's my order?" |
| QUOTE | DeepAgent | "Get a quote for X" |

---

## 6. Security

### 6.1 Authentication

| Method | Use Case |
|--------|----------|
| JWT | API authentication |
| OAuth 2.0 | Social login |
| API Keys | Server-to-server |

### 6.2 Authorization

```python
ROLES = {
    "admin": ["*"],
    "manager": ["read", "write", "order"],
    "buyer": ["read", "order"],
    "viewer": ["read"]
}
```

---

## 7. Observability

### 7.1 Langfuse Integration

```python
from langfuse import Langfuse

langfuse = Langfuse(
    public_key=os.getenv("LANGFUSE_PUBLIC_KEY"),
    secret_key=os.getenv("LANGFUSE_SECRET_KEY"),
    host=os.getenv("LANGFUSE_HOST")
)

# Track generations
langfuse.trace_create(
    name="product-search",
    input={"query": "LED"},
    output={"results": [...]}
)
```

### 7.2 Metrics

| Metric | Target | Alert |
|--------|--------|-------|
| Search latency p99 | <500ms | >1s |
| Recommendation latency p99 | <1s | >2s |
| Error rate | <0.1% | >1% |
| Availability | 99.9% | <99.5% |

---

## 8. Deployment

### 8.1 Infrastructure

| Component | AWS Service | Spec |
|-----------|-------------|------|
| Frontend | CloudFront + S3 | Static hosting |
| API | ECS Fargate | 2+ instances |
| Database | RDS PostgreSQL | db.t3.medium |
| Cache | ElastiCache | cache.t3.micro |
| Observability | Self-hosted Langfuse | EC2 t3.small |

### 8.2 Environment Variables

```bash
# Required
DATABASE_URL=postgresql://...
REDIS_URL=redis://...
ANTHROPIC_API_KEY=sk-...
OPENAI_API_KEY=sk-...
LANGFUSE_PUBLIC_KEY=pk-...
LANGFUSE_SECRET_KEY=sk-...

# Optional
JWT_SECRET=...
OAUTH_CLIENT_ID=...
```

---

## 9. Testing Strategy

### 9.1 Unit Tests

| Coverage Target | Current |
|-----------------|---------|
| Services | ≥80% |
| Agents | ≥70% |
| Utils | ≥90% |

### 9.2 Integration Tests

- API endpoint tests
- Database operation tests
- LLM response validation

### 9.3 E2E Tests

- User flows: search → recommend → order
- Admin flows: product management

---

## 10. Performance Targets

| Metric | Target | Measurement |
|--------|--------|-------------|
| Cold start | <3s | Lambda/ECS |
| Search p95 | <500ms | APM |
| Recommendation p95 | <1s | APM |
| Page load | <2s | RUM |
| Time to first byte | <200ms | CDN |

---

## References

- PRD: docs/PRD.md
- Architecture: docs/architecture/README.md
- ADRs: docs/architecture/adr/
