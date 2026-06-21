# 4SGM Repository Consolidation Plan

## Current State

### backend/repositories/
- **Pattern:** Protocol-based with TypeVar
- **Philosophy:** Structural typing, swappable implementations (Supabase, Oracle, SAP)
- **Files:** 19 (base.py, product.py, cart.py, order.py, customer.py, shipping.py, rfq.py, adapters/, etc.)
- **LOC:** ~2,500 lines

### mcp_server/repositories/
- **Pattern:** ABC-based (simpler)
- **Philosophy:** Simple in-memory implementations for MCP server
- **Files:** 12 (base.py, product.py, cart.py, order.py, customer.py, shipping.py, rfq.py, impl/, etc.)
- **LOC:** ~1,500 lines

## Identified Duplication

| Entity | backend/ | mcp_server/ | Can Share? |
|--------|----------|-------------|-------------|
| BaseRepository | ✅ Protocol | ✅ ABC | Yes - create shared |
| ProductRepository | ✅ | ✅ | Yes - share interface |
| CartRepository | ✅ | ✅ | Yes - share interface |
| OrderRepository | ✅ | ✅ | Yes - share interface |
| CustomerRepository | ✅ | ✅ | Yes - share interface |
| ShippingRepository | ✅ | ✅ | Yes - share interface |
| RFQRepository | ✅ | ✅ | Yes - share interface |

## Consolidation Architecture

```
4sgm/
├── shared/
│   └── repositories/
│       ├── __init__.py
│       ├── base.py          # Unified BaseRepository protocol
│       ├── interfaces.py    # All domain repository protocols
│       └── models.py       # Shared domain models
├── backend/
│   └── repositories/
│       ├── adapters/       # Supabase, Mock implementations
│       └── __init__.py     # Re-exports from shared
├── mcp_server/
│   └── repositories/
│       ├── impl/          # In-memory implementations
│       └── __init__.py     # Re-exports from shared
```

## Implementation Steps

### Phase 1: Create Shared Module
1. Create `4sgm/shared/repositories/base.py` - Unified BaseRepository
2. Create `4sgm/shared/repositories/interfaces.py` - Domain protocols
3. Create `4sgm/shared/repositories/models.py` - Shared models

### Phase 2: Update Backend
1. Update `backend/repositories/base.py` to import from shared
2. Keep Supabase/Mock adapters locally
3. Update imports in domain repositories

### Phase 3: Update MCP Server
1. Update `mcp_server/repositories/base.py` to import from shared
2. Keep in-memory implementations locally
3. Update imports in domain repositories

### Phase 4: Testing
1. Run all backend tests
2. Run all MCP server tests
3. Verify end-to-end functionality

## Estimated LOC Reduction

| Component | Current | After | Reduction |
|-----------|---------|-------|-----------|
| base.py (duplicated) | 300 | 100 (shared) | 66% |
| Protocol definitions | 400 | 200 (shared) | 50% |
| **Total** | ~700 | ~300 | ~57% |

## Risk Assessment
- **Low-Medium Risk:** No breaking API changes, just reorganization
- **Mitigation:** Keep both implementations working during transition
- **Timeline:** 1-2 hours for complete refactor
