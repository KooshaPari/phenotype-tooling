# Langfuse Observability Setup Guide

Complete observability integration for the 4SGM Wholesale Chatbot with Langfuse tracing.

## Overview

Langfuse provides production-grade observability for your LLM application:

- **Trace Monitoring**: Track all agent actions, tool calls, and LLM interactions
- **Performance Analytics**: Measure latency, token usage, and costs
- **Error Tracking**: Capture and debug failures across the system
- **User Analytics**: Monitor user behavior and conversation patterns
- **Cost Optimization**: Track spending by model, endpoint, and user

## Architecture

```
┌─────────────────────────────────────────────────────────┐
│                   4SGM Chatbot Frontend                  │
│              (React/Next.js with Langfuse SDK)           │
└──────────────────────┬──────────────────────────────────┘
                       │
                       ↓
         ┌─────────────────────────────┐
         │   Chat API Endpoint         │
         │  /api/chat (Next.js)        │
         └──────────────┬──────────────┘
                        │
                        ↓
         ┌─────────────────────────────┐
         │   Backend Agent Server      │
         │   (FastAPI + FastMCP)       │
         │   + Langfuse CallbackHandler│
         └──────────────┬──────────────┘
                        │
        ┌───────────────┼───────────────┐
        ↓               ↓               ↓
    ┌────────┐    ┌────────┐    ┌─────────────┐
    │ Claude │    │  Tools │    │ Langfuse    │
    │  LLM   │    │  (MCP) │    │  Dashboard  │
    └────────┘    └────────┘    └─────────────┘
                                     ↑
                              ┌──────────────────┐
                              │ Trace Ingestion  │
                              │  via HTTP API    │
                              └──────────────────┘
```

## Quick Start

### 1. Create Langfuse Account

1. Visit [Langfuse Cloud](https://cloud.langfuse.com)
2. Sign up for a free account
3. Create a new project for "4SGM Wholesale Chatbot"
4. Go to **Project Settings** → **API**
5. Copy:
   - **Public Key** (starts with `pk-lf-`)
   - **Secret Key** (starts with `sk-lf-`)

### 2. Configure Environment Variables

Add to `.env` in `4sgm/backend/`:

```bash
# Langfuse Observability
LANGFUSE_PUBLIC_KEY=pk-lf-your-key-here
LANGFUSE_SECRET_KEY=sk-lf-your-key-here
LANGFUSE_HOST=https://cloud.langfuse.com
LANGFUSE_ENV=development
LANGFUSE_SAMPLE_RATE=1.0
```

### 3. Verify Integration

Run the verification script:

```bash
cd 4sgm/backend
python scripts/verify_langfuse.py
```

Expected output:

```
============================================================
Langfuse Integration Verification
============================================================

[1/5] Checking environment variables...
  ✓ Public Key configured: pk-lf-...
  ✓ Secret Key configured: sk-lf-...
  ✓ Host: https://cloud.langfuse.com
  ✓ Environment: development
  ✓ Sample Rate: 100.0%

[2/5] Initializing Langfuse client...
  ✓ Langfuse client initialized

[3/5] Creating test trace...
  ✓ Created trace: trace_xxx
  ✓ Created span: span_xxx
  ✓ Span completed
  ✓ Trace updated

[4/5] Testing callback handler...
  ✓ Langfuse callback handler loaded

[5/5] Flushing data to Langfuse...
  ✓ Data flushed successfully

============================================================
✅ LANGFUSE INTEGRATION VERIFIED
============================================================
```

### 4. View Traces in Dashboard

1. Visit [Langfuse Dashboard](https://cloud.langfuse.com)
2. Navigate to **Traces**
3. Click on a trace to see:
   - Agent actions and decisions
   - Tool invocations and results
   - LLM prompts and responses
   - Token usage and latency
   - Custom metadata

## Configuration

### Project Configuration (`.langfuse.yaml`)

The `.langfuse.yaml` file defines observability settings:

```yaml
project:
  name: "4sgm-wholesale-chatbot"
  environment: "development"

tracing:
  enabled: true
  sample_rate: 1.0  # Adjust in production
  batch_size: 100
  flush_interval: 5000

callbacks:
  on_agent_action: true
  on_tool_start: true
  on_llm_start: true

metrics:
  track_latency: true
  track_tokens: true
  track_cost: true
```

### Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `LANGFUSE_PUBLIC_KEY` | Yes | - | Public key from Langfuse dashboard |
| `LANGFUSE_SECRET_KEY` | Yes | - | Secret key (keep private!) |
| `LANGFUSE_HOST` | No | `https://cloud.langfuse.com` | Langfuse instance URL |
| `LANGFUSE_ENV` | No | `development` | Environment (dev/staging/prod) |
| `LANGFUSE_SAMPLE_RATE` | No | `1.0` | Sample rate (0.0-1.0) |

### Sampling for Production

To reduce costs in production, adjust the sampling rate:

```bash
# Development: capture 100% of traces
LANGFUSE_SAMPLE_RATE=1.0

# Production: capture 10% to save costs
LANGFUSE_SAMPLE_RATE=0.1
```

## Backend Integration

### Callback Handler

The callback handler is automatically initialized in `create_4sgm_agent()`:

```python
# In 4sgm/backend/agents/deep_agent.py
from agents.callbacks.langfuse import get_langfuse_handler

def create_4sgm_agent(mcp_tools: list[Any], enable_langfuse: bool = True):
    # Get handler if credentials available
    langfuse_handler = None
    callbacks = []

    if enable_langfuse:
        langfuse_handler = get_langfuse_handler()
        if langfuse_handler:
            callbacks.append(langfuse_handler)
            logger.info("Langfuse observability enabled")

    # Handler is automatically attached to agent
    agent._callbacks = callbacks
```

### What Gets Traced

All of these events are automatically captured:

- **Agent Events**
  - Agent start/finish
  - Agent decisions and reasoning
  - Subagent routing

- **Tool Events**
  - Tool invocations (MCP tools)
  - Tool inputs and outputs
  - Tool execution time
  - Tool errors

- **LLM Events**
  - LLM model and version
  - Prompt tokens used
  - Completion tokens used
  - Cost estimation

- **Custom Events**
  - Order workflow steps
  - Shipping calculations
  - RFQ processing

## Frontend Integration (Optional)

Browser-side tracing is optional but recommended for complete observability.

### Setup

1. Add environment variables to `.env.local`:

```bash
NEXT_PUBLIC_LANGFUSE_PUBLIC_KEY=pk-lf-your-key-here
NEXT_PUBLIC_LANGFUSE_HOST=https://cloud.langfuse.com
NEXT_PUBLIC_LANGFUSE_ENABLED=true
```

2. Initialize in your app root:

```typescript
// app/layout.tsx
'use client'

import { useEffect } from 'react'
import { initLangfuse, setupErrorTracking } from '@/lib/langfuse'

export default function RootLayout({
  children
}: {
  children: React.ReactNode
}) {
  useEffect(() => {
    // Initialize Langfuse
    initLangfuse()

    // Setup global error tracking
    setupErrorTracking()
  }, [])

  return (
    <html>
      <body>{children}</body>
    </html>
  )
}
```

### Track User Interactions

```typescript
// In your chat component
import { trackChatMessage, trackError } from '@/lib/langfuse'

export function ChatWidget() {
  const handleSendMessage = async (message: string) => {
    const { traceId, endTrace } = trackChatMessage(
      sessionId,
      userId,
      message,
      'user'
    )

    try {
      const response = await fetch('/api/chat', {
        method: 'POST',
        body: JSON.stringify({ message })
      })

      endTrace()

      if (!response.ok) {
        trackError(new Error('Chat failed'), { traceId })
      }
    } catch (error) {
      trackError(error, { traceId })
      endTrace()
    }
  }
}
```

## Dashboard Usage

### Key Metrics

1. **Traces**: All interactions with the system
   - Filter by agent type, user, time range
   - View execution timeline and dependencies

2. **Latency**: Response times
   - P50, P95, P99 percentiles
   - Identify slow components

3. **Token Usage**: LLM consumption
   - Tokens per trace
   - Cost breakdown by model

4. **Error Rate**: System reliability
   - Failed traces
   - Error types and frequency

5. **User Analytics**: User behavior
   - Active users
   - Conversation patterns
   - Common topics

### Debugging Traces

For each trace, you can:

- View full conversation history
- Inspect LLM prompts and responses
- Check tool execution details
- Review custom metadata
- Export data for analysis

## Cost Optimization

### Sampling Strategy

```
Development:   sample_rate = 1.0   (100% traces)
Staging:       sample_rate = 0.5   (50% traces)
Production:    sample_rate = 0.1   (10% traces)
```

### Retention Policy

- Development traces: 30 days
- Production traces: 90 days
- Failed traces: 180 days (for debugging)

Configure in `.langfuse.yaml`:

```yaml
retention:
  traces_days: 90
  failed_traces_days: 180
  archive_days: 30
```

## Troubleshooting

### No Traces Appearing

1. Check environment variables are set:
   ```bash
   echo $LANGFUSE_PUBLIC_KEY
   echo $LANGFUSE_SECRET_KEY
   ```

2. Run verification script:
   ```bash
   python scripts/verify_langfuse.py
   ```

3. Check logs for errors:
   ```bash
   grep -i langfuse /var/log/app.log
   ```

### Traces but No Details

1. Ensure callbacks are enabled:
   ```python
   agent = create_4sgm_agent(mcp_tools=[], enable_langfuse=True)
   ```

2. Verify handler is initialized:
   ```python
   from agents.callbacks.langfuse import get_langfuse_handler
   handler = get_langfuse_handler()
   print(handler)  # Should not be None
   ```

### High Latency

1. Reduce sampling rate in production:
   ```bash
   LANGFUSE_SAMPLE_RATE=0.1
   ```

2. Increase batch size:
   ```yaml
   tracing:
     batch_size: 500
     flush_interval: 10000
   ```

### Authentication Errors

1. Verify keys in dashboard
2. Check key permissions (public vs. secret)
3. Try regenerating keys

## Advanced Topics

### Custom Spans

Add custom spans to track domain-specific logic:

```python
from langfuse.langchain import CallbackHandler

def my_custom_logic(context):
    handler = get_langfuse_handler()
    if handler:
        span = handler.get_trace().span(
            name="order_processing",
            input={"order_id": context["order_id"]}
        )

        # Do work
        process_order(context)

        span.end(output={"status": "completed"})
```

### Filtering PII

Langfuse automatically masks sensitive data defined in `.langfuse.yaml`:

```yaml
privacy:
  mask_pii: true
  exclude_patterns:
    - "password"
    - "api_key"
    - "credit_card"
```

### Self-Hosted Instance

To use a self-hosted Langfuse:

1. Deploy Langfuse server
2. Update `LANGFUSE_HOST`:
   ```bash
   LANGFUSE_HOST=https://langfuse.mycompany.com
   ```
3. Configure authentication as needed

## Support

- **Documentation**: https://langfuse.com/docs
- **Dashboard**: https://cloud.langfuse.com
- **GitHub**: https://github.com/langfuse/langfuse
- **Community**: https://discord.gg/7NXusGorq9

## Next Steps

1. ✅ Setup Langfuse account and credentials
2. ✅ Configure environment variables
3. ✅ Run verification script
4. ✅ View traces in dashboard
5. ✅ Add frontend tracing (optional)
6. ✅ Set sampling rates for production
7. ✅ Monitor costs and optimize

Your observability infrastructure is now complete!
