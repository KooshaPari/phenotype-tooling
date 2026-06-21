# Langfuse Quick Reference

Rapid guide for Langfuse observability integration.

## Setup (5 minutes)

### 1. Get Credentials
1. Go to https://cloud.langfuse.com
2. Sign up → Create project
3. Settings → API Keys
4. Copy `pk-lf-*` and `sk-lf-*`

### 2. Configure
```bash
# 4sgm/backend/.env
LANGFUSE_PUBLIC_KEY=pk-lf-your-key
LANGFUSE_SECRET_KEY=sk-lf-your-key
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_ENV=development
LANGFUSE_SAMPLE_RATE=1.0
```

### 3. Verify
```bash
cd 4sgm/backend
python scripts/verify_langfuse.py
```

Expected: ✅ LANGFUSE INTEGRATION VERIFIED

## Usage

### Backend (Automatic)
Langfuse is automatically attached to DeepAgent:

```python
from agents.deep_agent import create_4sgm_agent

# Create agent - Langfuse is automatically wired
agent = create_4sgm_agent(
    mcp_tools=your_tools,
    enable_langfuse=True  # Default: True
)

# All agent actions are traced
result = agent.invoke({"input": "user message"})
```

**What gets traced:**
- Agent decisions
- Tool calls (MCP)
- LLM requests
- Execution time
- Token usage
- Errors

### Frontend (Optional)

Initialize in root layout:

```typescript
// app/layout.tsx
'use client'

import { useEffect } from 'react'
import { initLangfuse, setupErrorTracking } from '@/lib/langfuse'

export default function RootLayout({ children }) {
  useEffect(() => {
    initLangfuse()
    setupErrorTracking()
  }, [])

  return <html><body>{children}</body></html>
}
```

Track user interactions:

```typescript
import { trackChatMessage } from '@/lib/langfuse'

export function ChatWidget() {
  const sendMessage = async (text) => {
    const { traceId, endTrace } = trackChatMessage(
      sessionId,
      userId,
      text,
      'user'
    )

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ message: text })
      })
      endTrace()
    } catch (error) {
      endTrace()
      throw error
    }
  }
}
```

## Dashboard

### View Traces
1. https://cloud.langfuse.com → Dashboard
2. Click "Traces"
3. Filter by:
   - Agent type
   - User
   - Time range
   - Status

### Common Queries
```
# Recent failures
status=failed order=newest limit=10

# Slow operations
latency>1000 order=slowest

# Specific user
user_id=user123

# Token usage
session_id=sess456
```

## Configuration

### Sample Rates
```bash
# Development: capture all traces
LANGFUSE_SAMPLE_RATE=1.0

# Staging: capture 50%
LANGFUSE_SAMPLE_RATE=0.5

# Production: capture 10% to save costs
LANGFUSE_SAMPLE_RATE=0.1
```

### Custom Spans

Manual tracing outside LangChain:

```python
from agents.callbacks.langfuse import get_langfuse_client

client = get_langfuse_client()
if client:
    trace = client.trace(name="order_processing")
    span = trace.span(name="validate_order", input={"order_id": 123})

    # Do work
    result = validate_order(order_id=123)

    span.end(output={"valid": result})
    trace.update(output={"status": "success"})
    client.flush()
```

## Common Issues

### No traces appearing
```bash
# Check credentials
echo $LANGFUSE_PUBLIC_KEY
echo $LANGFUSE_SECRET_KEY

# Run verification
python scripts/verify_langfuse.py
```

### Missing backend traces
```python
# Verify handler is initialized
from agents.callbacks.langfuse import get_langfuse_handler
handler = get_langfuse_handler()
print(handler)  # Should not be None
```

### High latency
Reduce sample rate in production:
```bash
LANGFUSE_SAMPLE_RATE=0.1
```

### Self-hosted Langfuse
```bash
LANGFUSE_HOST=https://langfuse.mycompany.com
```

## API Reference

### Backend (`agents/callbacks/langfuse.py`)

```python
# Get callback handler for agents
handler = get_langfuse_handler()

# Get direct client for manual tracing
client = get_langfuse_client()

# Check if enabled
if is_langfuse_enabled():
    # Tracing is configured
    pass
```

### Frontend (`lib/langfuse.ts`)

```typescript
// Initialize SDK
initLangfuse()

// Create trace
const { traceId, endTrace } = createTrace("operation_name", {
  custom: "metadata"
})
endTrace()

// Track chat
trackChatMessage(sessionId, userId, message, "user")

// Track API calls
const { traceId, endTrace } = trackApiCall("/api/endpoint", "POST")

// Track errors
trackError(error, { context: "data" })

// Track pages
trackPageView("/chat")

// Setup error handlers
setupErrorTracking()

// Debug mode
setDebugMode(true)
```

## Environment Variables

| Variable | Required | Example |
|----------|----------|---------|
| `LANGFUSE_PUBLIC_KEY` | Yes | `pk-lf-xxx` |
| `LANGFUSE_SECRET_KEY` | Yes | `sk-lf-xxx` |
| `LANGFUSE_HOST` | No | `https://cloud.langfuse.com` |
| `LANGFUSE_ENV` | No | `development` |
| `LANGFUSE_SAMPLE_RATE` | No | `1.0` |
| `NEXT_PUBLIC_LANGFUSE_PUBLIC_KEY` | No | `pk-lf-xxx` (frontend) |
| `NEXT_PUBLIC_LANGFUSE_HOST` | No | `https://cloud.langfuse.com` (frontend) |
| `NEXT_PUBLIC_LANGFUSE_ENABLED` | No | `true` (frontend) |

## Costs

### Estimate
- Free tier: 100k traces/month
- Cloud: $100/month (pay-as-you-go)
- Self-hosted: Deployment cost only

### Optimize
1. Use sampling in production (10%)
2. Enable retention policies (90 days)
3. Archive old traces (30 days)
4. Monitor token usage

## Resources

- **Dashboard**: https://cloud.langfuse.com
- **Docs**: https://langfuse.com/docs
- **GitHub**: https://github.com/langfuse/langfuse
- **Discord**: https://discord.gg/7NXusGorq9

## Files

- Config: `.langfuse.yaml`
- Backend callback: `4sgm/backend/agents/callbacks/langfuse.py`
- Frontend SDK: `4sgm/frontend/lib/langfuse.ts`
- Verification: `4sgm/backend/scripts/verify_langfuse.py`
- Tests: `4sgm/backend/tests/test_langfuse_integration.py`
- Setup guide: `docs/LANGFUSE_SETUP.md`

## Next Steps

1. ✅ Setup account and credentials
2. ✅ Configure environment variables
3. ✅ Run verification script
4. ✅ Check dashboard for traces
5. ✅ Add frontend tracing (optional)
6. ✅ Set sampling rates for production
7. ✅ Monitor costs

Done! Your observability is ready.
