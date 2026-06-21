# DeepAgent Quick Start Guide

## What Changed?

The 4SGM chatbot now uses a **Hybrid DeepAgent Architecture** instead of hardcoded OpenAI GPT-4. Key improvements:

1. **Claude 3.5 Sonnet** - Better reasoning, longer context
2. **Specialized Workflows** - Order, Shipping, RFQ processing
3. **Smart Routing** - Automatic detection of user intent
4. **Full Observability** - Optional Langfuse integration
5. **Flexible Storage** - In-memory or persistent state

## Quick Setup

### 1. Minimum Configuration
```bash
cd backend
export AGENT_MODEL=anthropic:claude-3-5-sonnet-20241022
python -m uvicorn app:app --reload
```

### 2. With Observability
```bash
export AGENT_MODEL=anthropic:claude-3-5-sonnet-20241022
export LANGFUSE_PUBLIC_KEY=pk_xxx
export LANGFUSE_SECRET_KEY=sk_xxx
uvicorn app:app --reload
```

### 3. With Persistent Storage
```bash
export AGENT_MODEL=anthropic:claude-3-5-sonnet-20241022
export DATABASE_URL=postgresql://user:pass@host/db
uvicorn app:app --reload
```

## Testing

### Order Processing
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "I want to order 100 units"}'
```
Routes to Order StateGraph workflow.

### Shipping Inquiry
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "What is the shipping cost?"}'
```
Routes to Shipping StateGraph workflow.

### Quote Request
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "I need a bulk quote"}'
```
Routes to RFQ StateGraph workflow.

### General Query
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "How do I return a product?"}'
```
Uses main DeepAgent (no keyword match).

## File Locations

**New Directories:**
```
backend/agents/
├── deep_agent.py              # Main factory
├── subagents/                 # Workflows
│   ├── order_workflow.py
│   ├── shipping_workflow.py
│   └── rfq_workflow.py
├── backends/                  # Storage
│   └── composite.py
└── callbacks/                 # Observability
    └── langfuse.py
```

**Architecture Guide:**
```
backend/DEEPAGENT_ARCHITECTURE.md
```

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| AGENT_MODEL | No | claude-3-5-sonnet-20241022 | LLM model to use |
| LANGFUSE_PUBLIC_KEY | No | - | Observability (optional) |
| LANGFUSE_SECRET_KEY | No | - | Observability (optional) |
| DATABASE_URL | No | - | Persistent storage (optional) |
| LOG_LEVEL | No | INFO | Logging verbosity |

## Keyword Routing

**Order Keywords:**
- "order", "purchase", "buy", "order number", "order status"

**Shipping Keywords:**
- "ship", "shipping", "delivery", "tracking", "address", "carrier"

**RFQ Keywords:**
- "quote", "rfq", "pricing", "bulk", "wholesale"

No keyword match → Uses main DeepAgent

## Workflow Steps

### Order Workflow
```
Initialize → Validate → Calculate → Payment → Confirm
```

### Shipping Workflow
```
Validate Address → Select Carrier → Calculate Cost → Generate Label → Schedule
```

### RFQ Workflow
```
Parse Request → Check Inventory → Generate Quotes → Apply Discounts → Format
```

## API Endpoints

**Create Session** (unchanged)
```
POST /api/session
→ Returns sessionId
```

**Get Session** (unchanged)
```
GET /api/session/{session_id}
→ Returns session data
```

**Chat** (updated)
```
POST /chat
{
  "text": "I want to order...",
  "session_id": "optional"
}
→ Routes to appropriate workflow or main agent
```

**Stream Chat** (updated)
```
POST /chat/stream
{
  "text": "I want to order...",
  "session_id": "optional"
}
→ Streams responses
```

**List Tools** (unchanged)
```
GET /tools
→ Returns available MCP tools
```

**Health** (unchanged)
```
GET /health
→ Returns status
```

## Troubleshooting

**Agent not initializing?**
- Check MCP server: `4sgm mcp`
- Check logs: Set `LOG_LEVEL=DEBUG`

**Subagent not routing?**
- Verify keywords match
- Check logs for routing decision

**Langfuse not logging?**
- Verify credentials: `echo $LANGFUSE_PUBLIC_KEY`
- Check dashboard: https://cloud.langfuse.com

**StateGraph errors?**
- Check state TypedDict matches
- Verify all nodes registered
- Review edge definitions

## Code Structure

```python
# Create agent (happens automatically)
agent = create_4sgm_agent(mcp_tools)

# Router detects intent
subagent = should_use_subagent("I need to order...")  # Returns "order"

# Route to workflow
result = await route_to_subagent(agent, message, "order")

# Or use main agent for general queries
result = await agent.ainvoke({"messages": [...]})
```

## Next Steps

1. Start MCP server: `4sgm mcp`
2. Run FastAPI: `uvicorn app:app --reload`
3. Test endpoints with curl or Postman
4. Monitor logs: `LOG_LEVEL=DEBUG`
5. (Optional) Set up Langfuse for observability
6. Review `/backend/DEEPAGENT_ARCHITECTURE.md` for advanced usage

## Need Help?

See `/backend/DEEPAGENT_ARCHITECTURE.md` for:
- Complete architecture overview
- Detailed component documentation
- Extension points for new workflows
- Performance characteristics
- Security considerations
