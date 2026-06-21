# 4SGM Wholesale Chatbot - System Design Document

## Executive Summary

The 4SGM Wholesale Chatbot is an enterprise-grade AI agent system that provides real-time product search, inventory management, order processing, and customer support through a conversational interface. The system serves wholesale customers with complex queries requiring multi-step reasoning and access to enterprise data sources.

**Key Metrics:**
- Response Latency: <3s for simple queries, <10s for complex reasoning
- Availability: 99.5% uptime SLA
- Concurrent Users: 500+ concurrent conversations
- Tool Capacity: 25+ integrated business tools
- Data Sources: SQL Server, Supabase, ERP APIs, shipping providers
- Cost Target: <$1 per user conversation (including LLM, infrastructure, observability)

---

## Architecture Overview

### System Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│                     PRESENTATION LAYER                      │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Next.js Frontend (React)                            │   │
│  │  ├─ Chat Widget UI                                   │   │
│  │  ├─ Real-time Streaming (SSE)                        │   │
│  │  ├─ Customer Context (Orders, History)              │   │
│  │  └─ Escalation Interface (Human Handoff)             │   │
│  └──────────────────────────────────────────────────────┘   │
│                    HTTP/SSE (Port 3000)                     │
└────────────────────┬────────────────────────────────────────┘
                     │
┌────────────────────▼────────────────────────────────────────┐
│               API ORCHESTRATION LAYER                       │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  FastAPI Backend (Python)                            │   │
│  │  ├─ /chat (POST) - Message endpoint                 │   │
│  │  ├─ /chat/stream (POST) - Streaming endpoint        │   │
│  │  ├─ /health (GET) - Health checks                   │   │
│  │  ├─ /tools (GET) - Available tools list             │   │
│  │  └─ /sessions (GET/POST) - Session management       │   │
│  └──────────────────────────────────────────────────────┘   │
│          FastAPI Application (Port 8000)                    │
└────────────────────┬────────────────────────────────────────┘
                     │ Python async/await
                     │
┌────────────────────▼────────────────────────────────────────┐
│            AGENT ORCHESTRATION LAYER                        │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  LangGraph Agent State Machine                        │   │
│  │                                                      │   │
│  │  [Router] ─→ Classify query complexity              │   │
│  │      ├─→ [ReAct Agent] ─→ Simple queries (fast)    │   │
│  │      └─→ [DeepAgents] ─→ Complex reasoning         │   │
│  │            ↓                                         │   │
│  │      [Tool Executor] ─→ Call MCP tools              │   │
│  │            ↓                                         │   │
│  │      [Escalation] ─→ Route to human if needed      │   │
│  └──────────────────────────────────────────────────────┘   │
│                                                             │
│  Instrumentation: Langfuse Tracing                          │
└────────────────────┬────────────────────────────────────────┘
                     │ MCP Protocol (JSON-RPC)
                     │
┌────────────────────▼────────────────────────────────────────┐
│           TOOL EXECUTION LAYER (MCP Server)                │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  FastMCP Server (Python) - 25+ Business Tools       │   │
│  │                                                      │   │
│  │  Product Tools (6):                                  │   │
│  │  ├─ search_products                                 │   │
│  │  ├─ get_product_details                             │   │
│  │  ├─ get_bulk_pricing                                │   │
│  │  ├─ check_stock                                     │   │
│  │  ├─ get_supplier_info                               │   │
│  │  └─ search_by_category                              │   │
│  │                                                      │   │
│  │  Order Tools (6):                                    │   │
│  │  ├─ create_order                                    │   │
│  │  ├─ get_order_status                                │   │
│  │  ├─ list_customer_orders                            │   │
│  │  ├─ update_order                                    │   │
│  │  ├─ calculate_total                                 │   │
│  │  └─ apply_discount                                  │   │
│  │                                                      │   │
│  │  Shipping Tools (4):                                 │   │
│  │  ├─ calculate_shipping                              │   │
│  │  ├─ track_shipment                                  │   │
│  │  ├─ get_shipping_methods                            │   │
│  │  └─ estimate_delivery                               │   │
│  │                                                      │   │
│  │  Pricing & Promotion Tools (5):                      │   │
│  │  ├─ get_active_promotions                           │   │
│  │  ├─ calculate_discount                              │   │
│  │  ├─ get_volume_pricing                              │   │
│  │  ├─ validate_coupon                                 │   │
│  │  └─ apply_loyalty_bonus                             │   │
│  │                                                      │   │
│  │  Customer Tools (3):                                 │   │
│  │  ├─ get_customer_profile                            │   │
│  │  ├─ get_customer_history                            │   │
│  │  └─ get_credit_limit                                │   │
│  │                                                      │   │
│  │  RFQ Tools (3):                                      │   │
│  │  ├─ create_rfq                                      │   │
│  │  ├─ get_rfq_status                                  │   │
│  │  └─ respond_to_rfq                                  │   │
│  └──────────────────────────────────────────────────────┘   │
│          FastMCP Server (Port 3001 or stdio)                │
└────────────────────┬────────────────────────────────────────┘
                     │ Direct function calls
                     │
┌────────────────────▼────────────────────────────────────────┐
│           DATA ACCESS LAYER (Repositories)                  │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  SQLServerRepository                                 │   │
│  │  ├─ Product catalog & inventory                     │   │
│  │  ├─ Order history & status                          │   │
│  │  ├─ Customer profiles & credit                      │   │
│  │  └─ Pricing & discount rules                        │   │
│  │                                                      │   │
│  │  SupabaseRepository                                  │   │
│  │  ├─ Vector embeddings (semantic search)             │   │
│  │  ├─ Conversation history                            │   │
│  │  ├─ Session state                                   │   │
│  │  └─ User preferences                                │   │
│  │                                                      │   │
│  │  External APIs                                       │   │
│  │  ├─ FedEx/UPS shipping integration                  │   │
│  │  ├─ ERP system integration                          │   │
│  │  └─ Payment processors                              │   │
│  └──────────────────────────────────────────────────────┘   │
└────────────────────┬────────────────────────────────────────┘
                     │ ODBC / TCP / HTTP
                     │
┌────────────────────▼────────────────────────────────────────┐
│           ENTERPRISE DATA SOURCES                           │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  SQL Server (Primary)                                │   │
│  │  ├─ Products table (10k SKUs)                        │   │
│  │  ├─ Inventory table                                  │   │
│  │  ├─ Orders table (historical)                        │   │
│  │  ├─ Customers table                                  │   │
│  │  └─ Pricing rules table                              │   │
│  │                                                      │   │
│  │  Supabase PostgreSQL (Secondary)                     │   │
│  │  ├─ pgvector extension (embeddings)                  │   │
│  │  ├─ Conversations table (archive)                    │   │
│  │  ├─ Sessions table                                   │   │
│  │  └─ Analytics table                                  │   │
│  │                                                      │   │
│  │  External Services                                   │   │
│  │  ├─ Shipping APIs (FedEx, UPS)                       │   │
│  │  ├─ ERP System (SAP/Oracle)                          │   │
│  │  └─ Payment Gateway (Stripe/ACH)                     │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────┐
│              OBSERVABILITY & MONITORING LAYER               │
│  ┌──────────────────────────────────────────────────────┐   │
│  │  Langfuse (Tracing & Analytics)                      │   │
│  │  ├─ Agent execution traces                           │   │
│  │  ├─ Tool call latency metrics                        │   │
│  │  ├─ Token usage & cost analytics                     │   │
│  │  ├─ Error rate tracking                              │   │
│  │  ├─ Session replay                                   │   │
│  │  └─ A/B testing framework                            │   │
│  │                                                      │   │
│  │  CloudWatch Monitoring                               │   │
│  │  ├─ Application logs                                 │   │
│  │  ├─ Database metrics                                 │   │
│  │  ├─ API latency & errors                             │   │
│  │  └─ Cost tracking                                    │   │
│  └──────────────────────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────────┘
```

---

## Component Details

### 1. Presentation Layer (Next.js Frontend)

**Technology:**
- Next.js 14 with App Router
- React 18 with TypeScript
- Vercel AI SDK v6
- Tailwind CSS + Radix UI
- Server-sent events (SSE) for streaming

**Key Features:**
- Chat widget with real-time streaming
- Order context display (customer history)
- Product recommendations display
- Escalation UI (handoff to human)
- Session management (persistent conversations)

**Responsibilities:**
- Render chat interface
- Stream responses from backend
- Display product/order information
- Handle user authentication (WorkOS)
- Capture analytics events

### 2. API Orchestration Layer (FastAPI)

**Technology:**
- FastAPI (async web framework)
- Python 3.12+
- Pydantic for request/response validation
- Uvicorn ASGI server

**Endpoints:**
```
POST /chat
  Request: { message, user_id, session_id, customer_id }
  Response: { response, confidence, escalated }

POST /chat/stream
  Request: { message, user_id, session_id, customer_id }
  Response: Server-Sent Events (streaming)

GET /health
  Response: { status, version, timestamp }

GET /tools
  Response: { tools: [...], count }

GET /sessions/{session_id}
  Response: { messages, customer_context, metadata }

POST /sessions
  Request: { customer_id, user_id }
  Response: { session_id, created_at }
```

**Responsibilities:**
- Request validation and authentication
- Route messages to LangGraph agent
- Stream responses to frontend
- Session management
- Error handling and logging

### 3. Agent Orchestration Layer (LangGraph)

**Technology:**
- LangGraph (agentic framework)
- LangChain (LLM integration)
- Anthropic SDK (Claude models)
- Langfuse (observability)

**State Machine Nodes:**

1. **Router Node**: Classify query complexity
   - Simple queries → ReAct path
   - Complex queries → DeepAgents path
   - Escalation queries → Human path

2. **ReAct Agent**: Simple tool-calling loop
   - Model: Claude 3.5 Sonnet (fast, cost-effective)
   - Max tokens: 1024
   - Tools: 25+ available
   - Latency: ~1-3s

3. **DeepAgents**: Extended thinking for complex decisions
   - Model: Claude 3.5 Sonnet (with extended thinking)
   - Thinking budget: 10,000 tokens
   - Max response: 16,000 tokens
   - Latency: ~8-15s
   - Use cases: Large orders, recommendations, complex analysis

4. **Tool Executor**: Execute MCP tools
   - Call FastMCP server
   - Handle tool responses
   - Track execution time
   - Error handling and retry

5. **Escalation**: Route to human support
   - Triggered by low confidence (<0.6)
   - Triggered by tool errors
   - Queue ticket in support system
   - Provide agent notes to human

**Responsibilities:**
- Decide which agent to use
- Manage conversation state
- Execute tools in sequence
- Generate responses
- Determine escalation needs
- Publish traces to Langfuse

### 4. Tool Execution Layer (FastMCP Server)

**Technology:**
- FastMCP 2.13 (MCP server framework)
- Python async/await
- Database drivers (pyodbc, psycopg2)
- HTTP clients (httpx)

**Tool Categories:** (25 total)

**Products (6 tools):**
- `search_products(query, max_price)` - Full-text search
- `get_product_details(product_id)` - Single product info
- `get_bulk_pricing(product_id, quantity)` - Tiered pricing
- `check_stock(product_id, quantity)` - Inventory check
- `get_supplier_info(supplier_id)` - Supplier details
- `search_by_category(category)` - Category browsing

**Orders (6 tools):**
- `create_order(customer_id, items, notes)` - New order
- `get_order_status(order_id)` - Order tracking
- `list_customer_orders(customer_id, limit)` - Order history
- `update_order(order_id, status)` - Admin updates
- `calculate_total(items)` - Order total calculation
- `apply_discount(order_id, coupon)` - Discount application

**Shipping (4 tools):**
- `calculate_shipping(origin, destination, weight)` - Shipping cost
- `track_shipment(tracking_number)` - Live tracking
- `get_shipping_methods(zip_code)` - Available methods
- `estimate_delivery(method, zip_code)` - Delivery date estimate

**Pricing & Promotions (5 tools):**
- `get_active_promotions()` - Current deals
- `calculate_discount(product_id, quantity)` - Discount lookup
- `get_volume_pricing(supplier_id)` - Volume tiers
- `validate_coupon(code, customer_id)` - Coupon check
- `apply_loyalty_bonus(customer_id)` - Loyalty rewards

**Customers (3 tools):**
- `get_customer_profile(customer_id)` - Profile data
- `get_customer_history(customer_id)` - Purchase history
- `get_credit_limit(customer_id)` - Credit availability

**RFQ (3 tools):**
- `create_rfq(customer_id, products, quantity)` - New RFQ
- `get_rfq_status(rfq_id)` - RFQ tracking
- `respond_to_rfq(rfq_id, pricing)` - Quote response

**Responsibilities:**
- Expose business logic as tools
- Validate inputs
- Access data sources
- Format responses
- Handle errors gracefully
- Log all executions

### 5. Data Access Layer (Repositories)

**Technology:**
- Repository Pattern (abstraction)
- SQL Server (primary database)
- Supabase PostgreSQL (secondary)
- Connection pooling (pyodbc, psycopg2)
- Caching (Redis for hot queries)

**Repositories:**

1. **ProductRepository**
   - Search products (full-text, semantic)
   - Get product details
   - Check inventory
   - Get pricing/promotions

2. **OrderRepository**
   - Create/update orders
   - Query order history
   - Calculate totals
   - Track status

3. **CustomerRepository**
   - Profile queries
   - Credit limit checks
   - Purchase history
   - Preferences

4. **VectorRepository**
   - Semantic search
   - Embedding storage
   - Similarity queries

5. **ShippingRepository**
   - Shipping calculations
   - Rate lookups
   - Tracking integration

**Responsibilities:**
- Abstract data access details
- Provide consistent interfaces
- Handle connection pooling
- Implement caching
- Log slow queries
- Support both sync/async access

### 6. Enterprise Data Sources

**SQL Server:**
- Primary operational database
- Tables: Products, Inventory, Orders, Customers, Pricing
- Queries: ~50-100ms typical latency
- Connection: ODBC with connection pooling (10-50 connections)

**Supabase PostgreSQL:**
- Secondary analytical database
- pgvector extension for semantic search
- Tables: documents, conversations, sessions, analytics
- Queries: ~100-200ms for vector searches
- Connection: psycopg2 async driver

**External APIs:**
- FedEx/UPS APIs (shipping rates & tracking)
- ERP system (SAP/Oracle) - inventory sync
- Payment gateway (Stripe/ACH) - order processing
- Latency: 500ms-2s (external dependency)

### 7. Observability Layer (Langfuse)

**Technology:**
- Langfuse (open source tracing platform)
- Self-hosted on AWS EC2
- PostgreSQL backend
- Web UI for analytics

**Instrumentation:**

1. **Agent Traces**
   - Entire LangGraph execution
   - Agent decisions (router output)
   - Tool selections
   - Response generation
   - Escalation triggers

2. **Tool Metrics**
   - Tool execution latency
   - Input/output tokens
   - Success/failure rate
   - Cost per tool call

3. **Cost Analytics**
   - Tokens per query
   - Cost per query
   - Model usage breakdown
   - Budget tracking

4. **Error Tracking**
   - Tool failures
   - API errors
   - Escalations (reason)
   - User-facing errors

5. **Session Analytics**
   - Conversation length
   - User satisfaction (if rating)
   - Escalation rate
   - Resolution time

**Dashboards:**
- Real-time monitoring (latency, errors)
- Cost tracking (tokens, budget)
- Agent performance (quality, success rate)
- Tool usage (popularity, latency)
- Customer analytics (satisfaction, behavior)

---

## Data Flow

### Simple Product Search Query

```
1. User: "Find laptops under $1000"
   └─ Frontend sends POST /chat/stream

2. FastAPI receives request
   └─ Creates session if needed
   └─ Validates request
   └─ Starts trace in Langfuse

3. LangGraph Router node
   └─ Analyzes: "Find laptops..." = simple query
   └─ Routes to: ReAct agent (fast path)
   └─ Log: {"complexity": "simple", "agent": "react"}

4. ReAct Agent
   └─ Decides to call: search_products
   └─ Tool inputs: {"query": "laptops", "max_price": 1000}
   └─ Calls FastMCP

5. FastMCP - search_products tool
   └─ Generates full-text SQL query
   └─ Executes on SQL Server
   └─ Returns: [Product, Product, ...]
   └─ Latency: 45ms

6. Agent receives results
   └─ Checks: 5 products found ✓
   └─ Generates response
   └─ Response: "Found 5 laptops under $1000: ..."

7. FastAPI streams response
   └─ Uses SSE to stream tokens
   └─ Frontend receives chunks
   └─ Updates UI in real-time

8. Langfuse records trace
   └─ Tokens used: 180 input, 120 output
   └─ Cost: $0.12
   └─ Latency: 2.3s
   └─ Tool calls: 1
   └─ Escalation: false

Total Latency: ~2.3s
Total Cost: $0.12
```

### Complex Recommendation Query

```
1. User: "We need laptops for our design team.
          What's the best option with bulk pricing?"
   └─ Frontend sends POST /chat/stream

2. FastAPI receives request
   └─ Enriches context: customer history, budget
   └─ Starts trace

3. LangGraph Router node
   └─ Analyzes: "best option", "bulk pricing" = complex
   └─ Routes to: DeepAgents (reasoning path)
   └─ Log: {"complexity": "complex", "agent": "deepagents"}

4. DeepAgents with Extended Thinking
   └─ Thinking: "Need to understand customer needs
      - Design team = high performance required
      - Bulk pricing needed
      - Should check budget, order history
      - Compare laptop specs
      - Calculate ROI"
   └─ Tokens (thinking): 2,845
   └─ Decides tools to call:
      1. search_products (design laptops)
      2. get_bulk_pricing (for volume)
      3. get_customer_history (spending patterns)
      4. get_credit_limit (approval)

5. Tool Executor executes in parallel
   └─ search_products("design laptop") → 8 results, 120ms
   └─ get_bulk_pricing("PROD-456", 10) → $800/unit, 95ms
   └─ get_customer_history("CUST-123") → $50k/year, 110ms
   └─ get_credit_limit("CUST-123") → $25k available, 85ms

6. Agent receives results
   └─ Analyzes: XPS 15 best for design
   └─ Bulk discount: 15% at 10 units
   └─ Customer budget: Approved
   └─ Generates detailed recommendation

7. FastAPI streams response
   └─ Response: "Based on your design needs, the Dell XPS 15...
      at 10 units: $800 × 10 = $8,000
      Your team gets 15% bulk discount = $6,800 total..."

8. Langfuse records trace
   └─ Tokens: 2,845 (thinking) + 450 (response) = 3,295
   └─ Cost: $1.20
   └─ Tool calls: 4 (parallel execution)
   └─ Latency: 10.5s
   └─ Escalation: false
   └─ Quality: "Detailed, personalized recommendation"

Total Latency: ~10.5s
Total Cost: $1.20
```

### Escalation Flow

```
1. User asks: "Can you process a custom payment plan?"
   └─ Out of agent capability (requires sales call)

2. ReAct Agent
   └─ No matching tool
   └─ Confidence: 0.2 (very low)
   └─ Decides: Escalate

3. Escalation Node
   └─ Logs: {"reason": "low_confidence", "score": 0.2}
   └─ Creates support ticket
   └─ Provides context: customer, conversation, intent

4. Support System
   └─ Routes to: Sales team
   └─ Priority: High (wholesale customer)
   └─ Assigns: Next available agent

5. Response to User
   └─ "I need to connect you with our sales team for
       custom payment arrangements. An agent will be
       with you in ~5 minutes."
   └─ Support takes over conversation

6. Langfuse records
   └─ Escalation reason: low_confidence
   └─ Escalation score: 0.2
   └─ Resolution: human_team

Total Latency: 1.5s (faster because less reasoning)
```

---

## Technology Stack

### Frontend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | Next.js | 14 | SSR, API routes |
| Language | TypeScript | 5.3+ | Type safety |
| UI Library | React | 18 | Component framework |
| UI Components | Radix UI | Latest | Accessible components |
| Styling | Tailwind CSS | 3.3+ | Utility-first CSS |
| AI Integration | Vercel AI SDK | 6.0+ | Streaming, chat |
| HTTP Client | fetch API | Native | API calls |
| Animation | Framer Motion | 10+ | Smooth transitions |
| Forms | React Hook Form | 7.4+ | Form handling |
| Validation | Zod | 3.2+ | Input validation |
| State | React Context | Built-in | Simple state |

### Backend
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Framework | FastAPI | 0.100+ | Web API |
| Language | Python | 3.12+ | Implementation |
| Agent | LangGraph | 0.1+ | Agentic loop |
| LLM Integration | LangChain | 0.1+ | LLM abstraction |
| MCP Server | FastMCP | 2.13 | Tool server |
| Models | Anthropic SDK | 0.7+ | Claude API |
| Database | SQLAlchemy | 2.0+ | ORM/Query builder |
| Async | asyncio | Built-in | Async runtime |
| Validation | Pydantic | 2.0+ | Data validation |
| SQL Server | pyodbc | 4.0+ | ODBC driver |
| PostgreSQL | psycopg2 | 2.9+ | PostgreSQL driver |
| HTTP Client | httpx | 0.24+ | Async HTTP |
| Logging | Python logging | Built-in | Log management |
| Monitoring | Langfuse | SDK | Tracing/analytics |

### Databases
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Primary | SQL Server | 2019+ | Operational data |
| Secondary | PostgreSQL | 15+ | Analytics/vectors |
| Vector DB | Supabase pgvector | Latest | Semantic search |
| Caching | Redis | 7.0+ | Hot query cache |
| Sessions | Supabase | Latest | Session storage |

### Infrastructure
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| API Hosting | AWS EC2 / Vercel | Latest | Application server |
| Frontend | Vercel | Latest | Edge deployment |
| Databases | AWS RDS / Supabase | Managed | Database hosting |
| Observability | Langfuse (self-hosted) | Latest | Tracing/analytics |
| Logging | CloudWatch / ELK | Latest | Log aggregation |
| Monitoring | CloudWatch / Datadog | Latest | Metrics/alerts |

### Development
| Component | Technology | Version | Purpose |
|-----------|-----------|---------|---------|
| Package Manager | pip/uv | Latest | Python packages |
| Testing | pytest | 7.0+ | Unit tests |
| E2E Testing | Playwright | 1.40+ | Browser automation |
| Code Quality | ruff | Latest | Linting |
| Type Checking | mypy | 1.5+ | Type validation |
| Formatting | black | 23+ | Code formatting |
| Git Hooks | pre-commit | 2.20+ | Automated checks |
| CI/CD | GitHub Actions | Latest | Automation |

---

## Deployment Architecture

### Production Deployment

```
┌──────────────────────────────────────────────────────────┐
│  Route 53 (DNS)                                          │
│  └─ 4sgm-api.example.com                                │
└────────────────────┬─────────────────────────────────────┘
                     │
┌────────────────────▼─────────────────────────────────────┐
│  CloudFront (CDN)                                        │
│  ├─ Cache static assets                                 │
│  ├─ DDoS protection                                     │
│  └─ Global distribution                                │
└────────────────────┬─────────────────────────────────────┘
                     │
        ┌────────────┴────────────┐
        │                         │
        ▼                         ▼
    ┌─────────┐            ┌──────────────┐
    │ Vercel  │            │ AWS ELB      │
    │ CDN     │            │ Load Balancer│
    │(Frontend)            │(API Server)  │
    └─────────┘            └────────┬─────┘
                                    │
                 ┌──────────────────┼──────────────────┐
                 │                  │                  │
                 ▼                  ▼                  ▼
            ┌─────────┐        ┌─────────┐        ┌─────────┐
            │ EC2     │        │ EC2     │        │ EC2     │
            │ Instance│        │ Instance│        │ Instance│
            │ FastAPI │        │ FastAPI │        │ FastAPI │
            │ (AZ-1)  │        │ (AZ-2)  │        │ (AZ-3)  │
            └─────────┘        └─────────┘        └─────────┘
                 │                  │                  │
                 │      FastMCP     │                  │
                 │      Server      │                  │
                 │                  │                  │
                 └──────────────────┼──────────────────┘
                                    │
        ┌───────────────────────────┼───────────────────────────┐
        │                           │                           │
        ▼                           ▼                           ▼
    ┌──────────────┐          ┌──────────────┐          ┌───────────┐
    │ SQL Server   │          │ Supabase     │          │ Redis     │
    │ Multi-AZ     │          │ PostgreSQL   │          │ Cache     │
    │ RDS          │          │ (Managed)    │          │ (Elastica-│
    │              │          │              │          │  che)     │
    │ Backup: S3   │          │ pgvector     │          │           │
    │ Snapshots    │          │ extension    │          │ TTL: 5min │
    └──────────────┘          └──────────────┘          └───────────┘

┌──────────────────────────────────────────────────────────┐
│  Langfuse (Self-Hosted)                                  │
│  ┌──────────────────────────────────────────────────────┐│
│  │ EC2 Instance + PostgreSQL                            ││
│  │ Docker compose: langfuse, postgres, redis            ││
│  └──────────────────────────────────────────────────────┘│
└──────────────────────────────────────────────────────────┘

┌──────────────────────────────────────────────────────────┐
│  Monitoring & Logging                                    │
│  ├─ CloudWatch (AWS logs)                               │
│  ├─ ELK Stack (Elasticsearch)                           │
│  ├─ DataDog (optional)                                  │
│  └─ PagerDuty (alerts)                                  │
└──────────────────────────────────────────────────────────┘
```

### Scaling Strategy

**Horizontal Scaling:**
- FastAPI instances behind load balancer
- Auto-scaling group (target: 50-100% CPU)
- Scale up: >70% CPU, add instance
- Scale down: <30% CPU, remove instance
- Min: 3 instances (HA), Max: 10 instances

**Database Scaling:**
- SQL Server: Read replicas for analytics queries
- Supabase: Auto-scales with managed service
- Redis: Cluster mode for distributed cache
- Connection pooling: 10-50 connections per app instance

**Cost Optimization:**
- Spot instances for non-critical workloads
- Reserved instances for baseline capacity
- Auto-shutdown development environments
- CloudFront caching (reduce origin requests 80%)
- Database query optimization (most expensive component)

---

## Security Architecture

### Authentication & Authorization

**User Authentication:**
- WorkOS AuthKit (OAuth 2.0)
- Multi-factor authentication (MFA)
- Session tokens (JWT)
- Secure session storage (Supabase)

**API Security:**
- HTTPS/TLS 1.3 (all traffic)
- API key rate limiting (10 req/sec per user)
- Input validation (Pydantic)
- SQL injection prevention (parameterized queries)

**Data Access Control:**
- Row-level security (RLS) on Supabase
- Customer data isolation (customer_id in queries)
- Tool access control (verify customer owns order before returning)
- Admin-only tools (limited to internal agents)

### Data Protection

**In Transit:**
- TLS 1.3 encryption (frontend ↔ backend)
- TLS encryption (backend ↔ database)
- VPC endpoints (private connectivity)

**At Rest:**
- SQL Server: Encryption at rest (TDE)
- Supabase: AES-256 encryption
- Redis: No sensitive data stored
- CloudFront: SSL/TLS certs

**Sensitive Data:**
- Payment info: PCI-DSS compliant (3rd-party processor)
- API keys: AWS Secrets Manager
- Database passwords: Secrets Manager rotation
- Customer PII: Hashed in logs, masked in UI

### Compliance

- GDPR: Data residency (EU data in EU), right to deletion
- CCPA: Consent tracking, opt-out capability
- HIPAA: Not applicable (healthcare data)
- SOC 2 Type II: Planned audit

---

## Performance Optimization

### Response Time Targets

| Query Type | Target Latency | 95th Percentile | Max Latency |
|-----------|--------|---------|-------------|
| Simple search | 2.0s | 3.0s | 5.0s |
| Complex reasoning | 10.0s | 12.0s | 15.0s |
| Escalation | 1.5s | 2.5s | 4.0s |
| Average | 4.5s | 6.5s | 10.0s |

### Optimization Techniques

**Query Optimization:**
- Full-text search on SQL Server (CONTAINS, FREETEXT)
- Index strategy: Covering indexes on hot queries
- Query hints: Optimize for estimated row count
- Caching: Redis for pricing, promotions (5min TTL)

**Tool Execution:**
- Parallel tool execution (async/await)
- Timeout policy: 5s per tool, 30s total
- Circuit breaker: Disable tool after 5 failures
- Fallback: Return cached data if tool fails

**Agent Optimization:**
- Router heuristics (classify before agent call)
- Tool selection: Limit to 5 most relevant tools
- Streaming: Start sending response as tokens arrive
- Token optimization: Aggressive prompt compression

**Infrastructure:**
- Connection pooling (pyodbc: 10-50 connections)
- Database replication (SQL Server read replicas)
- CDN caching (frontend assets: 86,400s)
- Compression (gzip: all responses)

---

## Cost Analysis

### Monthly Cost Breakdown

| Component | Monthly Cost | Annual Cost | Notes |
|-----------|-------------|-----------|-------|
| **Compute** | | | |
| EC2 (3x t3.xlarge, 30 days/month) | $600 | $7,200 | $0.067/hr per instance |
| Vercel (Frontend) | $50 | $600 | Pro plan, 100GB bandwidth |
| **Databases** | | | |
| SQL Server (RDS, 1TB) | $500 | $6,000 | Multi-AZ deployment |
| Supabase (PostgreSQL + pgvector) | $100 | $1,200 | Managed service, 100GB storage |
| Redis (ElastiCache, 1GB) | $25 | $300 | Cache cluster |
| **LLM Costs** | | | |
| Claude 3.5 Sonnet | $300 | $3,600 | ~10k queries/month, $0.03 avg |
| Embeddings (semantic search) | $50 | $600 | Vector generation |
| **Observability** | | | |
| Langfuse (self-hosted EC2) | $150 | $1,800 | Included in EC2 |
| CloudWatch / Logs | $50 | $600 | Monitoring & logging |
| **Networking** | | | |
| CloudFront (CDN) | $30 | $360 | ~100GB/month |
| Data transfer (NAT) | $20 | $240 | EC2 to external APIs |
| **Other** | | | |
| Domain (Route 53) | $12 | $144 | Annual registrar fee |
| Secrets Manager | $5 | $60 | API key management |
| Backups (S3) | $15 | $180 | Database snapshots |
| **Total** | ~$1,937 | ~$22,444 | **~$0.20 per query** |

**Cost Reduction Opportunities:**
1. Use Spot instances: Save ~60% on EC2 ($240/month)
2. Self-host more services: Move to cheaper EC2 option
3. Optimize embeddings: Use cheaper models (save $25/month)
4. Query optimization: Reduce database load (save $100+/month)
5. **Total potential savings: ~20% ($400/month)**

---

## Monitoring & Alerting

### Key Metrics

**System Health:**
- API uptime: >99.5% (target)
- Response latency: <5s (p95)
- Error rate: <0.5%
- Tool success rate: >95%

**Business Metrics:**
- Queries/minute: 0-100 (auto-scale at 50)
- Escalation rate: <5% (good agent quality)
- Cost per query: $0.10-0.30
- Conversation success: >85%

**Infrastructure:**
- EC2 CPU: 40-70% target
- Database CPU: <60%
- Memory usage: <75%
- Storage: <80% full

### Alert Thresholds

| Metric | Warning | Critical | Action |
|--------|---------|----------|--------|
| API latency p95 | >5s | >10s | Scale up, debug |
| Error rate | >1% | >5% | Page oncall, investigate |
| Escalation rate | >8% | >15% | Review agent, add tools |
| Cost/query | >$0.30 | >$0.50 | Optimize models, caching |
| Tool latency | >2s | >5s | Check data source, cache |
| Database CPU | >70% | >85% | Scale up, optimize queries |
| EC2 CPU | >80% | >95% | Scale up immediately |

---

## Testing Strategy

### Unit Testing
- Repository implementations
- Service layer business logic
- Tool parameter validation
- LLM prompt engineering

### Integration Testing
- Agent → Tool execution
- MCP tool → Database queries
- FastAPI routes
- Cache behavior

### E2E Testing (Playwright)
- Full chat flows
- Product search → Order creation
- Escalation workflows
- Session persistence

### Load Testing
- 100 concurrent users
- 10k queries/minute peak
- 5min sustained load
- Tool timeout handling

---

## References & Related Documents

- **ADR-001**: FastMCP Selection Rationale
- **ADR-002**: LangGraph Hybrid Pattern Design
- **ADR-003**: Langfuse Observability Decision
- **ADR-004**: Repository Pattern for Data Access
- **Architecture Examples**: See `/4sgm/docs/architecture/adr/`

---

## Document Version

| Version | Date | Changes |
|---------|------|---------|
| 1.0 | 2024-12-19 | Initial system design |

---

**Last Updated**: December 19, 2024
**Owner**: Architecture Team
**Status**: Production Ready
