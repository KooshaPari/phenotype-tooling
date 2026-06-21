# Langfuse Observability Index

Quick navigation guide for all Langfuse observability documentation and code.

## Start Here

**First time?** Start with [5-Minute Quick Start](#5-minute-quick-start)

**Need to understand the architecture?** See [Architecture Overview](#architecture-overview)

**Looking for specific code?** Check [File Reference](#file-reference)

---

## 5-Minute Quick Start

1. **Create Account**
   - Visit https://cloud.langfuse.com
   - Sign up for free account
   - Create new project for "4SGM"

2. **Get API Keys**
   - Go to Project Settings → API
   - Copy public key (pk-lf-*)
   - Copy secret key (sk-lf-*)

3. **Configure Environment**
   ```bash
   cd 4sgm/backend
   # Edit .env and add your keys:
   LANGFUSE_PUBLIC_KEY=pk-lf-your-key
   LANGFUSE_SECRET_KEY=sk-lf-your-key
   ```

4. **Verify Setup**
   ```bash
   python scripts/verify_langfuse.py
   ```

5. **View Traces**
   - Go to Langfuse dashboard
   - Click "Traces"
   - See your first traces!

**Total time**: ~5 minutes

---

## Documentation Guide

### For Setup & Configuration
- **Quick Reference**: `docs/LANGFUSE_QUICK_REFERENCE.md`
  - 5-minute setup
  - Common commands
  - Quick API reference
  - Estimated: 5 min read

- **Complete Setup Guide**: `docs/LANGFUSE_SETUP.md`
  - Architecture diagram
  - Detailed configuration
  - Backend integration details
  - Frontend integration guide
  - Dashboard usage
  - Troubleshooting
  - Estimated: 20 min read

### For Integration Details
- **Integration Checklist**: `LANGFUSE_INTEGRATION_CHECKLIST.md`
  - What was implemented
  - Architecture diagrams
  - Data flow explanation
  - Testing coverage
  - Deployment checklist
  - Estimated: 15 min read

### For Delivery & Status
- **Delivery Document**: `WAVE_2_LANGFUSE_DELIVERY.md`
  - Executive summary
  - File manifest
  - Verification steps
  - Success criteria
  - Support resources
  - Estimated: 10 min read

---

## Architecture Overview

```
Frontend (Optional Langfuse SDK)
    ↓
Backend Chat API
    ↓
DeepAgent (Automatic Langfuse Callback)
    ├─ Claude LLM
    ├─ MCP Tools
    └─ Subagents (Order, Shipping, RFQ)
    ↓
Langfuse Cloud Dashboard
    ├─ Traces
    ├─ Analytics
    ├─ Performance Metrics
    └─ Cost Tracking
```

**Key Points**:
- Backend tracing is **automatic** (no code changes needed)
- Frontend tracing is **optional** (add if you want)
- All components wire automatically if credentials are set

---

## File Reference

### Configuration Files

#### `.langfuse.yaml` (Root)
- **Purpose**: Project-level observability configuration
- **Contains**: Tracing settings, callbacks, metrics, retention, privacy
- **When to modify**: Adjust sampling rate, retention policies, privacy settings
- **Location**: `$HOME/temp-PRODVERCEL/485/kush/4sgm/.langfuse.yaml`

#### `.env.example` (Backend)
- **Purpose**: Environment variable template
- **Contains**: Langfuse credentials and configuration
- **When to modify**: When deploying (create `.env` from this template)
- **Location**: `$HOME/temp-PRODVERCEL/485/kush/4sgm/4sgm/backend/.env.example`

### Code Files

#### `agents/callbacks/langfuse.py` (Backend)
- **Purpose**: Langfuse callback handler for DeepAgent
- **Functions**:
  - `get_langfuse_handler()` - Get callback handler
  - `is_langfuse_enabled()` - Check if configured
  - `get_langfuse_client()` - Get direct client
- **Integration**: Automatically attached to DeepAgent
- **Location**: `$HOME/temp-PRODVERCEL/485/kush/4sgm/4sgm/backend/agents/callbacks/langfuse.py`
- **Size**: 124 lines

#### `lib/langfuse.ts` (Frontend)
- **Purpose**: Browser-side Langfuse SDK integration
- **Functions**:
  - `initLangfuse()` - Initialize
  - `trackChatMessage()` - Track chat
  - `trackApiCall()` - Track API
  - `trackError()` - Track errors
  - `trackPageView()` - Track pages
  - `setupErrorTracking()` - Global handler
  - `setDebugMode()` - Debug mode
- **Integration**: Optional, add to root layout
- **Location**: `$HOME/temp-PRODVERCEL/485/kush/4sgm/4sgm/frontend/lib/langfuse.ts`
- **Size**: 234 lines

### Utility Scripts

#### `scripts/verify_langfuse.py` (Backend)
- **Purpose**: Verify Langfuse integration is working
- **What it tests**:
  1. Environment variables
  2. Client initialization
  3. Trace creation
  4. Callback handler
  5. DeepAgent integration
- **How to run**: `python scripts/verify_langfuse.py`
- **Location**: `$HOME/temp-PRODVERCEL/485/kush/4sgm/4sgm/backend/scripts/verify_langfuse.py`
- **Size**: 181 lines

### Test Files

#### `tests/test_langfuse_integration.py` (Backend)
- **Purpose**: Integration tests for Langfuse
- **Test coverage**:
  - Configuration validation (5 tests)
  - Environment variables (3 tests)
  - Client initialization (3 tests)
  - DeepAgent integration (2 tests)
- **How to run**: `pytest tests/test_langfuse_integration.py -v`
- **Location**: `$HOME/temp-PRODVERCEL/485/kush/4sgm/4sgm/backend/tests/test_langfuse_integration.py`
- **Size**: 250 lines

### Documentation Files

See [Documentation Guide](#documentation-guide) above for details.

---

## Common Tasks

### Task: Setup Langfuse for First Time
1. Read: `docs/LANGFUSE_QUICK_REFERENCE.md` (5 min setup section)
2. Create account at https://cloud.langfuse.com
3. Configure credentials in `4sgm/backend/.env`
4. Run: `python 4sgm/backend/scripts/verify_langfuse.py`
5. Check dashboard for traces

**Time**: ~10 minutes

### Task: Add Frontend Tracing
1. Read: `docs/LANGFUSE_SETUP.md` (Frontend Integration section)
2. Add to `4sgm/frontend/app/layout.tsx`:
   ```typescript
   import { initLangfuse, setupErrorTracking } from '@/lib/langfuse'
   useEffect(() => {
     initLangfuse()
     setupErrorTracking()
   }, [])
   ```
3. Track events in components using functions from `lib/langfuse.ts`

**Time**: ~15 minutes

### Task: Optimize for Production
1. Read: `docs/LANGFUSE_SETUP.md` (Cost Optimization section)
2. Set in `.env`:
   ```bash
   LANGFUSE_ENV=production
   LANGFUSE_SAMPLE_RATE=0.1
   ```
3. Configure retention policies in Langfuse UI
4. Monitor dashboard for cost trends

**Time**: ~10 minutes

### Task: Debug a Failed Trace
1. Read: `docs/LANGFUSE_SETUP.md` (Troubleshooting section)
2. Check `4sgm/backend/.env` has valid credentials
3. Run: `python 4sgm/backend/scripts/verify_langfuse.py`
4. View error message and follow suggestions
5. Check Langfuse dashboard for detailed trace

**Time**: ~5-10 minutes

### Task: Run Integration Tests
```bash
cd 4sgm/backend
pytest tests/test_langfuse_integration.py -v
```

Expected: 13 tests, all passing

**Time**: ~2 minutes

---

## API Reference Quick Links

### Backend Python

```python
from agents.callbacks.langfuse import (
    get_langfuse_handler,      # Get callback handler
    is_langfuse_enabled,       # Check if enabled
    get_langfuse_client        # Get direct client
)

# In DeepAgent
agent = create_4sgm_agent(
    mcp_tools=tools,
    enable_langfuse=True       # Automatically enables tracing
)
```

See: `4sgm/backend/agents/callbacks/langfuse.py`

### Frontend TypeScript

```typescript
import {
    initLangfuse,              // Initialize SDK
    createTrace,               // Manual trace
    trackChatMessage,          // Track chat
    trackApiCall,              // Track API calls
    trackError,                // Track errors
    trackPageView,             // Track pages
    setupErrorTracking,        // Global handler
    setDebugMode,              // Debug mode
    getLangfuseConfig          // Get config
} from '@/lib/langfuse'
```

See: `4sgm/frontend/lib/langfuse.ts`

---

## Environment Variables

| Variable | Required | Default | Purpose |
|----------|----------|---------|---------|
| `LANGFUSE_PUBLIC_KEY` | Yes | - | Public key from Langfuse |
| `LANGFUSE_SECRET_KEY` | Yes | - | Secret key from Langfuse |
| `LANGFUSE_HOST` | No | cloud.langfuse.com | Langfuse instance |
| `LANGFUSE_ENV` | No | development | Environment name |
| `LANGFUSE_SAMPLE_RATE` | No | 1.0 | Sampling rate (0-1) |

**For Frontend** (add NEXT_PUBLIC_ prefix in `.env.local`):
- `NEXT_PUBLIC_LANGFUSE_PUBLIC_KEY`
- `NEXT_PUBLIC_LANGFUSE_HOST`
- `NEXT_PUBLIC_LANGFUSE_ENABLED`

See: `docs/LANGFUSE_QUICK_REFERENCE.md` (Environment Variables section)

---

## Dashboard Navigation

1. **Login**: https://cloud.langfuse.com
2. **View Traces**: Click "Traces" in left sidebar
3. **Filter**: Use filters to search by time, user, status
4. **Details**: Click trace to see full breakdown
5. **Analytics**: Check "Analytics" for trends and metrics
6. **Settings**: Configure retention, alerts, etc.

See: `docs/LANGFUSE_SETUP.md` (Dashboard Usage section)

---

## Troubleshooting

| Problem | Solution | Reference |
|---------|----------|-----------|
| No traces appearing | Run verify script, check credentials | `docs/LANGFUSE_SETUP.md` Troubleshooting |
| High costs | Reduce sample rate to 0.1 | `docs/LANGFUSE_SETUP.md` Cost Optimization |
| Missing backend traces | Verify handler is attached | `docs/LANGFUSE_SETUP.md` Backend Integration |
| Test failing | Check .env has valid keys | `4sgm/backend/tests/test_langfuse_integration.py` |
| Self-hosted | Set LANGFUSE_HOST | `docs/LANGFUSE_QUICK_REFERENCE.md` |

See: `docs/LANGFUSE_SETUP.md` (Troubleshooting section)

---

## Resources

| Resource | URL | Purpose |
|----------|-----|---------|
| Langfuse Cloud | https://cloud.langfuse.com | Main dashboard |
| Documentation | https://langfuse.com/docs | Official docs |
| GitHub | https://github.com/langfuse/langfuse | Source code |
| Discord | https://discord.gg/7NXusGorq9 | Community support |
| Pricing | https://langfuse.com/pricing | Cost info |

---

## Summary

**Langfuse integration is complete and production-ready.**

- ✅ Backend tracing: Automatic via DeepAgent
- ✅ Frontend tracing: Optional via SDK
- ✅ Configuration: All documented
- ✅ Verification: Script provided
- ✅ Testing: 13 integration tests
- ✅ Documentation: 4 comprehensive guides

**Start**: Create account → Configure credentials → Run verification

**Time to first traces**: ~10 minutes

---

## Document Version

- **Created**: December 19, 2025
- **Status**: Production Ready
- **Last Updated**: December 19, 2025
- **Next Review**: Q1 2026

---

**Need help?** See the documentation files listed above or check Langfuse Discord community.
