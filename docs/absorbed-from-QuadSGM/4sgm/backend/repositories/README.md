# Repository Pattern Implementation

## Overview

This directory implements the **repository pattern** for 4SGM using Python's `typing.Protocol`. The pattern provides clean, testable data access while allowing trivial backend swapping (Supabase → Oracle, SAP, or custom systems).

## Architecture

### Protocol-Based Design

All repositories are defined as protocols (structural subtypes), not interfaces. This means:

- Any class with the required methods satisfies the protocol
- No inheritance or explicit interface declaration needed
- Concrete implementations in separate adapters
- Runtime behavior unchanged, compile-time type checking works

```
repositories/
├── base.py                   # Protocol definitions
├── product.py                # Protocol re-exports
├── cart.py
├── order.py
├── customer.py
├── shipping.py
├── rfq.py
├── adapters/
│   ├── supabase.py          # Supabase implementations
│   ├── mock.py              # In-memory for testing
│   └── __init__.py
├── dependencies.py           # Dependency injection (FastAPI)
├── examples.py              # Usage examples
├── test_repositories.py     # Test suite
└── USAGE_GUIDE.md          # Detailed usage guide
```

## Quick Start

### 1. Define Protocol (base.py)

```python
from typing import Protocol, Optional

class ProductRepository(Protocol):
    async def get(self, id: str) -> Optional[dict]: ...
    async def list(self, **filters) -> list[dict]: ...
    async def create(self, data: dict) -> dict: ...
    # ... more methods
```

### 2. Implement Adapter (adapters/supabase.py)

```python
class SupabaseProductRepository:
    def __init__(self, client):
        self.client = client

    async def get(self, id: str) -> Optional[dict]:
        response = self.client.table("products").select("*").eq("id", id).single().execute()
        return response.data if response.data else None

    # ... implement all protocol methods
```

### 3. Use in FastAPI (dependencies.py)

```python
from fastapi import Depends

async def get_product_repo():
    # Return Supabase adapter, or mock based on env var
    if os.getenv("REPOSITORY_ADAPTER") == "mock":
        return MockProductRepository()
    else:
        client = get_supabase_client()
        return SupabaseProductRepository(client)

@app.get("/products/{product_id}")
async def get_product(
    product_id: str,
    repo = Depends(get_product_repo)
):
    product = await repo.get(product_id)
    return product
```

## Repository Interfaces

### BaseRepository (All Repositories)

Standard CRUD operations:

```python
await repo.get(id)                          # Get by ID
await repo.get_all(skip=0, limit=100)      # List with pagination
await repo.list(**filters)                  # Filter by criteria
await repo.create(data)                     # Create new
await repo.update(id, data)                 # Update existing
await repo.delete(id)                       # Delete
await repo.exists(id)                       # Check existence
```

### ProductRepository

```python
await repo.get_by_sku(sku)                  # Get by SKU
await repo.list_by_category(category)       # List by category
await repo.search(query)                    # Full-text search
await repo.update_inventory(id, change)     # Adjust stock
await repo.get_low_stock(threshold)         # Get reorder candidates
```

### CartRepository

```python
await repo.get_by_customer(customer_id)     # Get active cart
await repo.add_item(cart_id, product_id, qty, price)
await repo.remove_item(cart_id, item_id)
await repo.update_item(cart_id, item_id, qty)
await repo.clear(cart_id)
await repo.calculate_total(cart_id)         # Get totals
```

### OrderRepository

```python
await repo.get_by_customer(customer_id)
await repo.get_by_status(status)
await repo.get_line_items(order_id)
await repo.update_status(order_id, status, notes)
await repo.add_shipment(order_id, tracking, carrier)
await repo.get_pending_fulfillment()
```

### CustomerRepository

```python
await repo.get_by_email(email)
await repo.list_by_status(status)
await repo.update_profile(customer_id, data)
await repo.add_address(customer_id, address)
await repo.get_addresses(customer_id)
await repo.set_default_address(customer_id, address_id)
```

### ShippingRepository

```python
await repo.get_rates(origin, destination, weight)
await repo.get_by_carrier(carrier)
await repo.track(tracking_number, carrier)
await repo.create_shipment(order_id, carrier, service)
await repo.estimate_delivery(carrier, destination, service)
```

### RFQRepository

```python
await repo.get_by_customer(customer_id)
await repo.get_by_status(status)
await repo.get_items(rfq_id)
await repo.add_quote(rfq_id, quote_data)
await repo.get_quote(rfq_id)
await repo.accept_quote(rfq_id)
await repo.get_pending_quotes()
```

## Adapters

### Supabase Adapter (Production)

Full implementation using Supabase PostgreSQL client.

- **Location**: `adapters/supabase.py`
- **Classes**: `SupabaseProductRepository`, `SupabaseCartRepository`, etc.
- **Dependencies**: `supabase-py` library
- **Configuration**: `SUPABASE_URL`, `SUPABASE_KEY` env vars
- **Usage**: Default adapter, used in production

```bash
export REPOSITORY_ADAPTER=supabase
export SUPABASE_URL=https://xxx.supabase.co
export SUPABASE_KEY=eyJxxx...
```

### Mock Adapter (Testing)

In-memory implementation for unit tests.

- **Location**: `adapters/mock.py`
- **Classes**: `MockProductRepository`, `MockCartRepository`, etc.
- **Dependencies**: None
- **Configuration**: `REPOSITORY_ADAPTER=mock` env var
- **Usage**: Enabled automatically in tests

```bash
export REPOSITORY_ADAPTER=mock
```

**Benefits**:
- No database setup needed
- Fast test execution
- Deterministic behavior
- Easy to debug

## Dependency Injection

FastAPI's `Depends()` pattern for automatic repository injection:

```python
from repositories.dependencies import get_product_repo

@app.get("/products/{product_id}")
async def get_product(
    product_id: str,
    repo = Depends(get_product_repo)  # Automatic injection
):
    return await repo.get(product_id)
```

**How it works**:
1. FastAPI calls `get_product_repo()` when handling request
2. Function checks `REPOSITORY_ADAPTER` env var
3. Returns appropriate adapter instance (Supabase or Mock)
4. Repository is passed to route handler
5. Handler doesn't know or care which adapter is used

## Environment Configuration

### Adapter Selection

```bash
# Use Supabase (default)
export REPOSITORY_ADAPTER=supabase

# Use mock (for testing)
export REPOSITORY_ADAPTER=mock
```

### Supabase Configuration

Required only when using Supabase adapter:

```bash
export SUPABASE_URL=https://project.supabase.co
export SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...
export SQL_ECHO=false  # Set to "true" for SQL logging
```

## Testing

### Run All Tests

```bash
pytest repositories/test_repositories.py -v
```

### Run Specific Test

```bash
pytest repositories/test_repositories.py::test_product_create -v
```

### With Coverage

```bash
pytest repositories/test_repositories.py --cov=repositories --cov-report=html
```

### Test Database (Mock)

Tests use `MockProductRepository`, `MockCartRepository`, etc. automatically when:
- `REPOSITORY_ADAPTER=mock` is set, or
- No environment is set (tests default to mock)

No database setup required.

## Adding Custom Adapters

To add a new backend (Oracle, SAP, MongoDB, etc.):

### 1. Create adapter file

```python
# repositories/adapters/oracle.py

import cx_Oracle

class OracleProductRepository:
    def __init__(self, connection):
        self.conn = connection

    async def get(self, id: str) -> Optional[dict]:
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM products WHERE id = :id", {"id": id})
        row = cursor.fetchone()
        return dict(row) if row else None

    # Implement all protocol methods...
```

### 2. Update dependencies.py

```python
async def get_product_repo():
    if ADAPTER == "mock":
        from repositories.adapters.mock import MockProductRepository
        return MockProductRepository()
    elif ADAPTER == "oracle":
        from repositories.adapters.oracle import OracleProductRepository
        conn = get_oracle_connection()
        return OracleProductRepository(conn)
    else:
        # Default to Supabase
        from repositories.adapters.supabase import SupabaseProductRepository
        client = get_supabase_client()
        return SupabaseProductRepository(client)
```

### 3. Test with environment variable

```bash
export REPOSITORY_ADAPTER=oracle
export ORACLE_CONNECTION_STRING=...
python -m pytest repositories/test_repositories.py
```

## Performance Considerations

### Caching

Repositories don't implement caching. Add in services:

```python
class ProductService:
    def __init__(self, repo):
        self.repo = repo
        self._cache = {}

    async def get_product(self, id: str):
        if id in self._cache:
            return self._cache[id]
        product = await self.repo.get(id)
        self._cache[id] = product
        return product
```

### N+1 Queries

Use repository methods that load related data:

```python
# Good: Gets cart with items in one call
cart = await repo.get(cart_id)
items = cart["cart_items"]  # Already loaded

# Avoid: Would require separate calls
items = await item_repo.list(cart_id=cart_id)
```

### Async All the Way

All repository methods are async. Use `await`:

```python
# Correct
product = await repo.get(id)

# Wrong - will fail
product = repo.get(id)  # Returns coroutine, not data
```

## Best Practices

1. **Use dependency injection**: Always use `Depends(get_*_repo)` in routes
2. **Create services**: Encapsulate business logic in service classes
3. **Handle errors**: Catch repository exceptions and return appropriate HTTP status codes
4. **Test with mocks**: Use mock adapter for unit tests
5. **Don't leak adapters**: Services and routes should use protocols, not concrete classes
6. **Keep protocols simple**: One responsibility per repository
7. **Use proper typing**: Type hints for all parameters and returns
8. **Log operations**: Include logging for debugging

## Migration Guide

### From Direct DB Access to Repository Pattern

**Before:**
```python
@app.get("/products/{product_id}")
async def get_product(product_id: str):
    from sqlalchemy.orm import Session
    db = Session()
    product = db.query(Product).filter(Product.id == product_id).first()
    db.close()
    return product
```

**After:**
```python
@app.get("/products/{product_id}")
async def get_product(
    product_id: str,
    repo = Depends(get_product_repo)
):
    product = await repo.get(product_id)
    return product
```

**Benefits:**
- No database imports in routes
- Testable with mock adapter
- Easy backend swapping
- Consistent error handling
- Better separation of concerns

## File Structure Summary

| File | Purpose |
|------|---------|
| `base.py` | Protocol definitions (contracts) |
| `product.py`, `cart.py`, etc. | Protocol re-exports |
| `adapters/supabase.py` | Supabase implementations |
| `adapters/mock.py` | In-memory implementations for testing |
| `adapters/__init__.py` | Adapter exports |
| `dependencies.py` | FastAPI dependency injection |
| `examples.py` | Usage examples with FastAPI routes |
| `test_repositories.py` | Complete test suite with fixtures |
| `USAGE_GUIDE.md` | Detailed usage guide |
| `README.md` | This file |

## Troubleshooting

### "ModuleNotFoundError: No module named 'supabase'"

Solution: Install supabase library
```bash
pip install supabase
```

### "SUPABASE_URL and SUPABASE_KEY environment variables required"

Solution: Set environment variables
```bash
export SUPABASE_URL=https://xxx.supabase.co
export SUPABASE_KEY=eyJxxx...
```

### Tests failing with database errors

Solution: Set mock adapter for tests
```bash
export REPOSITORY_ADAPTER=mock
pytest repositories/test_repositories.py -v
```

### Async/await issues

Remember: All repository methods are async. Always use `await`:
```python
# Correct
product = await repo.get(id)

# Wrong
product = repo.get(id)  # This won't work!
```

## Future Enhancements

- [ ] Add caching layer adapter
- [ ] Implement query builders for complex filters
- [ ] Add transaction support
- [ ] Create async context managers for operations
- [ ] Add bulk operations (create_many, update_many)
- [ ] Implement soft deletes
- [ ] Add audit logging
- [ ] Create migration tools for schema changes
