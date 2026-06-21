# Hybrid DeepAgent Architecture - 4SGM Wholesale Chatbot

## Overview

The 4SGM Wholesale Chatbot now implements a **Hybrid DeepAgent Architecture** that combines:
- **Claude 3.5 Sonnet** as the main LLM (replacing hardcoded GPT-4)
- **Specialized StateGraph subagents** for domain-specific workflows
- **Langfuse observability** for production monitoring
- **Composite backend** for flexible state storage

This architecture enables:
- Dynamic routing to specialized workflows based on user intent
- Domain-specific logic for orders, shipping, and RFQ processing
- Full observability and tracing via Langfuse
- Hybrid state management (in-memory + persistent storage)

## Architecture Diagram

```
┌─────────────────────────────────────────────────────────────┐
│ FastAPI Server (app.py)                                     │
│                                                             │
│  POST /chat ──────────────────────┐                        │
│  POST /chat/stream ───────────────┼──> should_use_subagent │
│                                   │                        │
│                    ┌──────────────┴─────────────────┐      │
│                    │                                │      │
│                    v                                │      │
│        ┌──────────────────────┐         ┌──────────v──┐   │
│        │  DeepAgent (Claude)  │         │  Subagent?  │   │
│        │                      │         └─────┬────────┘   │
│        │ - MCP Tools          │               │            │
│        │ - Langfuse Callback  │               │            │
│        │ - Composite Backend  │               │            │
│        └──────────────────────┘               │            │
│                    ^                          │            │
│                    │                    ┌─────v─────┐      │
│                    │                    │  route_to │      │
│                    │                    │ _subagent │      │
│                    │                    └─────┬─────┘      │
│                    │                          │            │
│        ┌───────────┴──────────────────────────┘            │
│        │                                                   │
│        v                                                   │
└────────────────────────────────────────────────────────────┘
         │
         │
    ┌────┴─────────────────────────────────────────────┐
    │                                                  │
    v                    v                    v       │
┌──────────────┐  ┌──────────────┐  ┌──────────────┐ │
│ Order        │  │ Shipping     │  │ RFQ          │ │
│ StateGraph   │  │ StateGraph   │  │ StateGraph   │ │
│              │  │              │  │              │ │
│ - Initialize │  │ - Validate   │  │ - Parse      │ │
│ - Validate   │  │ - Select     │  │ - Inventory  │ │
│ - Calculate  │  │   Carrier    │  │ - Generate   │ │
│ - Payment    │  │ - Calculate  │  │   Quotes     │ │
│ - Confirm    │  │ - Label      │  │ - Discount   │ │
│              │  │ - Schedule   │  │ - Format     │ │
└──────────────┘  └──────────────┘  └──────────────┘ │
    │                    │                    │       │
    └────────────────────┴────────────────────┘       │
                         │                            │
                    Composite Backend                 │
                  ┌──────────────────┐                │
                  │ State: In-Memory  │<───────────────┘
                  │ Store: Persistent │
                  │  (if DB_URL set)  │
                  └──────────────────┘
```

## File Structure

```
backend/agents/
├── __init__.py                          # Package exports
├── deep_agent.py                        # Main factory function
│
├── subagents/                           # Domain-specific workflows
│   ├── __init__.py
│   ├── order_workflow.py                # Order processing StateGraph
│   ├── shipping_workflow.py             # Shipping management StateGraph
│   └── rfq_workflow.py                  # RFQ processing StateGraph
│
├── backends/                            # State storage configuration
│   ├── __init__.py
│   └── composite.py                     # Hybrid storage backend setup
│
└── callbacks/                           # Observability integration
    ├── __init__.py
    └── langfuse.py                      # Langfuse callback handler
```

## Component Details

### 1. DeepAgent Factory (`deep_agent.py`)

Creates the main agent with all components integrated.

**Key Function: `create_4sgm_agent()`**
```python
agent = create_4sgm_agent(
    mcp_tools=mcp_tools,
    enable_langfuse=True
)
```

**Features:**
- Uses Claude 3.5 Sonnet (via `AGENT_MODEL` env var)
- Integrates all three subagents
- Enables Langfuse observability if credentials present
- Configures composite backend for state storage

**Routing Logic: `should_use_subagent()`**
- Analyzes message keywords to determine if subagent is needed
- Returns subagent name: "order", "shipping", "rfq", or None
- Falls back to main agent for general queries

**Subagent Execution: `route_to_subagent()`**
- Routes to appropriate StateGraph workflow
- Initializes domain-specific state
- Executes workflow and returns results
- Handles errors gracefully

### 2. Order Workflow Subagent (`subagents/order_workflow.py`)

Handles order processing with 5-step workflow:

**State Definition:**
```python
class OrderState(TypedDict):
    messages: list[AnyMessage]
    order_id: str
    customer_id: str
    status: str
    items: list[dict]
    total: float
```

**Workflow Steps:**
1. **Initialize** - Set up order processing
2. **Validate** - Check items have SKU and quantity
3. **Calculate** - Sum item prices with quantities
4. **Payment** - Process payment (placeholder)
5. **Confirm** - Confirm order creation

**Keywords Detected:**
- "order", "purchase", "buy", "order number", "order status"

### 3. Shipping Workflow Subagent (`subagents/shipping_workflow.py`)

Manages shipments with 5-step workflow:

**State Definition:**
```python
class ShippingState(TypedDict):
    messages: list[AnyMessage]
    order_id: str
    status: str
    address: dict
    carrier: str
    tracking_number: str
    cost: float
```

**Workflow Steps:**
1. **Validate** - Check address completeness
2. **Select Carrier** - Choose carrier by country
3. **Calculate** - Compute shipping cost
4. **Generate Label** - Create tracking number
5. **Schedule** - Arrange pickup

**Keywords Detected:**
- "ship", "shipping", "delivery", "tracking", "address", "carrier"

**Carrier Selection Logic:**
- USA → UPS
- Canada → Canada Post
- Other → DHL

### 4. RFQ Workflow Subagent (`subagents/rfq_workflow.py`)

Processes quote requests with 5-step workflow:

**State Definition:**
```python
class RFQState(TypedDict):
    messages: list[AnyMessage]
    rfq_id: str
    customer_id: str
    status: str
    items: list[dict]
    quotes: list[dict]
    selected_quote: dict
```

**Workflow Steps:**
1. **Parse** - Extract items from RFQ
2. **Inventory** - Check availability
3. **Generate** - Create pricing quotes (10% bulk discount)
4. **Apply Discounts** - Volume-based pricing (5%-15%)
5. **Format** - Prepare final quote

**Discount Tiers:**
- Total > $1000: 15% discount
- Total > $500: 10% discount
- Default: 5% discount

**Keywords Detected:**
- "quote", "rfq", "pricing", "bulk", "wholesale"

### 5. Langfuse Integration (`callbacks/langfuse.py`)

Provides observability and tracing.

**Setup Required:**
```bash
export LANGFUSE_PUBLIC_KEY="pk_xxx"
export LANGFUSE_SECRET_KEY="sk_xxx"
export LANGFUSE_HOST="https://cloud.langfuse.com"  # Optional
```

**Features:**
- Automatic request/response tracing
- Token usage monitoring
- Latency tracking
- Error logging
- Custom metrics support

**Graceful Degradation:**
- If credentials missing → observability disabled (not an error)
- If langfuse package missing → warning logged
- Production functionality not affected

### 6. Composite Backend (`backends/composite.py`)

Flexible state storage with routing.

**Configuration:**
```python
{
    "type": "composite",
    "default_backend": "state",      # In-memory
    "routes": {
        "/memories/": "store"        # Persistent DB (if DB_URL set)
    }
}
```

**Behavior:**
- Default: In-memory state (fast, session-scoped)
- Optional: Persistent storage for memories (requires DATABASE_URL)
- Routes requests to appropriate backend

## Integration with app.py

### Modified Endpoints

**POST /chat** - Main chat endpoint
- Lazy-loads MCP tools and agent on first request
- Routes to subagent if keywords detected
- Falls back to main agent for general queries
- Returns structured response with session ID

**POST /chat/stream** - Streaming chat endpoint
- Supports streaming responses
- Routes subagent requests (non-streaming)
- Streams main agent responses
- SSE format for client compatibility

### Initialization Flow

```python
# In lifespan context manager:
1. init_mcp() → Load MCP tools
2. init_agent() → Create DeepAgent with tools
3. Agent ready for chat requests
```

### Error Handling

- Missing MCP: HTTP 503 "Tools not loaded"
- Missing agent: HTTP 503 "Agent not ready"
- Execution error: HTTP 500 with error detail

## Usage Examples

### Example 1: Order Processing
```
User: "I want to order 100 units of SKU-12345"
        ↓
should_use_subagent() → detects "order"
        ↓
route_to_subagent() → Order StateGraph
        ↓
Workflow: Initialize → Validate → Calculate → Payment → Confirm
        ↓
Response: "Request processed by order workflow. Status: confirmed"
```

### Example 2: Shipping Inquiry
```
User: "What's the shipping cost to Toronto?"
        ↓
should_use_subagent() → detects "shipping"
        ↓
route_to_subagent() → Shipping StateGraph
        ↓
Workflow: Validate → Select Carrier (Canada Post) → Calculate → Label → Schedule
        ↓
Response: "Request processed by shipping workflow. Status: pickup_scheduled"
```

### Example 3: Quote Request
```
User: "I need a bulk quote for 500 units"
        ↓
should_use_subagent() → detects "quote"
        ↓
route_to_subagent() → RFQ StateGraph
        ↓
Workflow: Parse → Inventory → Generate (10% discount) → Apply Discounts (10% more) → Format
        ↓
Response: "Request processed by rfq workflow. Status: quote_ready"
```

### Example 4: General Query
```
User: "How do I return a product?"
        ↓
should_use_subagent() → None (no keywords)
        ↓
Use main DeepAgent with MCP tools
        ↓
Claude processes with full tool access
        ↓
Response: General answer about returns policy
```

## Environment Variables

```bash
# Model Configuration
AGENT_MODEL=anthropic:claude-3-5-sonnet-20241022

# Observability
LANGFUSE_PUBLIC_KEY=pk_xxx          # Optional
LANGFUSE_SECRET_KEY=sk_xxx          # Optional
LANGFUSE_HOST=https://cloud.langfuse.com  # Optional, defaults to cloud

# Storage
DATABASE_URL=postgresql://...       # Optional, enables persistent storage

# Logging
LOG_LEVEL=INFO                      # DEBUG, INFO, WARNING, ERROR
```

## Testing the Architecture

### 1. Test Order Workflow
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "I want to order 10 units of SKU-001", "session_id": "test-1"}'
```

### 2. Test Shipping Workflow
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "What is the shipping cost?", "session_id": "test-2"}'
```

### 3. Test RFQ Workflow
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "I need a wholesale quote for bulk orders", "session_id": "test-3"}'
```

### 4. Test General Query
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "What are your return policies?", "session_id": "test-4"}'
```

### 5. Test Streaming
```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"text": "I want to order 5 units", "session_id": "test-5"}'
```

## Extension Points

### Adding a New Subagent

1. Create new workflow file: `subagents/new_workflow.py`
2. Define state TypedDict
3. Create StateGraph with nodes and edges
4. Implement `create_graph()` and `compile()` functions
5. Update `deep_agent.py`:
   - Import new workflow
   - Add to `agent._subagents` dict
   - Add keywords to `should_use_subagent()`
   - Add routing logic to `route_to_subagent()`

### Customizing Subagent Logic

Edit individual workflow files to:
- Modify state transitions
- Add business logic nodes
- Change keyword detection
- Adjust discount/pricing rules

### Extending Observability

1. Enable Langfuse credentials
2. Add custom metadata to traces:
   ```python
   # In workflow nodes
   logger.info(f"Custom metric: {value}")
   ```
3. View traces at https://cloud.langfuse.com

## Performance Notes

- **Subagent routing**: <10ms (keyword detection)
- **StateGraph execution**: <100ms (simple workflows)
- **LLM inference**: 0.5-2s (Claude with MCP tools)
- **Langfuse logging**: Async (non-blocking)
- **Composite backend**: O(1) lookup (hash-based routing)

## Security Considerations

- MCP tools validated by MCP framework
- Subagent state isolated per workflow
- No service-side state persistence by default
- Optional persistent storage encrypted at DB level
- Langfuse keys stored in environment only

## Troubleshooting

### Agent not initializing
1. Check MCP server is running: `4sgm mcp`
2. Verify MCP tools loaded: GET /tools
3. Check logs for specific errors

### Subagent not routing
1. Check keywords in `should_use_subagent()`
2. Add debug logging: `LOG_LEVEL=DEBUG`
3. Verify message contains detection keyword

### Langfuse not logging
1. Verify credentials set: `echo $LANGFUSE_PUBLIC_KEY`
2. Check connection: Test with `python -c "from langfuse import Langfuse; print(Langfuse())"`
3. Review endpoint in dashboard

### StateGraph errors
1. Check state TypedDict matches workflow inputs
2. Verify node function signatures
3. Review edge definitions
4. Check for missing node registrations

## Future Enhancements

1. **Memory persistence**: Full chat history via persistent backend
2. **Multi-turn workflows**: Support for workflows spanning multiple exchanges
3. **Confidence scoring**: Add confidence threshold routing
4. **Tool selection**: Have LLM choose which subagent to use
5. **Parallel execution**: Run multiple subagents concurrently
6. **Custom validators**: Add domain-specific validation nodes
7. **Analytics dashboard**: Visualize workflow metrics
