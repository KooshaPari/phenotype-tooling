# Repository Pattern Usage Guide

## Overview

The repository pattern in 4SGM provides a clean, testable way to access data. All repositories follow protocol-based contracts that allow swapping between different backends (Supabase, Oracle, SAP, etc.) without changing application code.

## Quick Start

### 1. Using Repositories in FastAPI Routes

```python
from fastapi import FastAPI, Depends
from repositories.dependencies import get_product_repo

app = FastAPI()

@app.get("/products/{product_id}")
async def get_product(
    product_id: str,
    product_repo = Depends(get_product_repo)
):
    """Get product by ID using injected repository."""
    product = await product_repo.get(product_id)
    if not product:
        raise HTTPException(status_code=404, detail="Product not found")
    return product
```

### 2. Using Repositories in Services

```python
from repositories.dependencies import get_product_repo

class ProductService:
    def __init__(self, repo):
        self.repo = repo

    async def get_product(self, product_id: str):
        """Get product by ID."""
        product = await self.repo.get(product_id)
        return product

    async def search_products(self, query: str):
        """Search products."""
        return await self.repo.search(query)

    async def get_low_stock(self):
        """Get low stock products for reorder."""
        return await self.repo.get_low_stock(threshold=10)
```

### 3. Testing with Mock Repositories

```python
import pytest
from repositories.adapters.mock import MockProductRepository

@pytest.fixture
def product_repo():
    """Provide mock product repository for tests."""
    return MockProductRepository()

@pytest.mark.asyncio
async def test_get_product(product_repo):
    """Test getting a product."""
    # Create test product
    product = await product_repo.create({
        "sku": "TEST-001",
        "name": "Test Product",
        "price": 99.99,
        "quantity_on_hand": 10
    })

    # Retrieve and verify
    retrieved = await product_repo.get(product["id"])
    assert retrieved["name"] == "Test Product"
    assert retrieved["price"] == 99.99
```

## Repository Methods

### Common CRUD Operations (All Repositories)

```python
# Read operations
product = await repo.get(id)                    # Get by ID
all_products = await repo.get_all(skip=0, limit=100)  # List all
filtered = await repo.list(category="shoes")   # Filter

# Write operations
created = await repo.create({"name": "Shoes", "price": 99})
updated = await repo.update(id, {"price": 89})
deleted = await repo.delete(id)

# Check existence
exists = await repo.exists(id)
```

### Product Repository

```python
# Get by SKU
product = await product_repo.get_by_sku("SHOE-001")

# List by category
shoes = await product_repo.list_by_category("shoes")

# Full-text search
results = await product_repo.search("red shoe")

# Inventory management
await product_repo.update_inventory(product_id, quantity_change=5)
low_stock = await product_repo.get_low_stock(threshold=10)
```

### Cart Repository

```python
# Get customer's active cart
cart = await cart_repo.get_by_customer(customer_id)

# Manage items
cart = await cart_repo.add_item(cart_id, product_id, quantity=2, price=99)
cart = await cart_repo.remove_item(cart_id, item_id)
cart = await cart_repo.update_item(cart_id, item_id, quantity=3)

# Cart operations
cart = await cart_repo.clear(cart_id)
totals = await cart_repo.calculate_total(cart_id)
# Returns: {subtotal, tax, shipping, total}
```

### Order Repository

```python
# Get orders
customer_orders = await order_repo.get_by_customer(customer_id)
pending = await order_repo.get_by_status("pending")

# Line items
items = await order_repo.get_line_items(order_id)

# Status management
await order_repo.update_status(order_id, "shipped", notes="Sent via FedEx")

# Shipping
await order_repo.add_shipment(order_id, tracking_number="1Z...", carrier="FedEx")

# Fulfillment
pending_orders = await order_repo.get_pending_fulfillment()
```

### Customer Repository

```python
# Get by email
customer = await customer_repo.get_by_email("user@example.com")

# Status filtering
active = await customer_repo.list_by_status("active")

# Profile management
await customer_repo.update_profile(customer_id, {"phone": "555-1234"})

# Address management
address = await customer_repo.add_address(customer_id, {
    "street": "123 Main St",
    "city": "Portland",
    "state": "OR",
    "zip": "97201"
})
addresses = await customer_repo.get_addresses(customer_id)
await customer_repo.set_default_address(customer_id, address_id)
```

### Shipping Repository

```python
# Get rates
rates = await shipping_repo.get_rates(
    origin="97201",
    destination="94105",
    weight=5.5
)

# Methods by carrier
usps_methods = await shipping_repo.get_by_carrier("USPS")

# Tracking
tracking = await shipping_repo.track("1Z...", "FedEx")

# Create shipment
shipment = await shipping_repo.create_shipment(
    order_id, carrier="FedEx", service="express"
)

# Delivery estimation
estimated = await shipping_repo.estimate_delivery(
    carrier="FedEx",
    destination="97201",
    service="express"
)
```

### RFQ Repository

```python
# Get by customer
rfqs = await rfq_repo.get_by_customer(customer_id)

# Status filtering
open_rfqs = await rfq_repo.get_by_status("open")

# RFQ items
items = await rfq_repo.get_items(rfq_id)

# Quote management
quote = await rfq_repo.add_quote(rfq_id, {
    "pricing": [...],
    "expiry": "2024-12-31"
})
quote = await rfq_repo.get_quote(rfq_id)
order = await rfq_repo.accept_quote(rfq_id)

# Pending
pending = await rfq_repo.get_pending_quotes()
```

## Switching Adapters

### Environment Variable

Set `REPOSITORY_ADAPTER` to choose the backend:

```bash
# Use Supabase (default)
export REPOSITORY_ADAPTER=supabase
export SUPABASE_URL=https://xxx.supabase.co
export SUPABASE_KEY=eyJxxx...

# Use mock (in-memory, for testing)
export REPOSITORY_ADAPTER=mock
```

### In Tests

```python
import os
import pytest

@pytest.fixture(autouse=True)
def use_mock_adapter():
    """Use mock adapter for all tests."""
    os.environ["REPOSITORY_ADAPTER"] = "mock"
    yield
    # Cleanup if needed
```

### Creating Custom Adapters

To add a new backend (Oracle, SAP, MongoDB, etc.):

1. Create a new file in `repositories/adapters/`:
```python
# repositories/adapters/oracle.py

class OracleProductRepository:
    def __init__(self, connection):
        self.connection = connection

    async def get(self, id: str) -> Optional[dict]:
        # Implementation
        pass

    # Implement all protocol methods...
```

2. Update `repositories/dependencies.py`:
```python
ADAPTER = os.getenv("REPOSITORY_ADAPTER", "supabase").lower()

async def get_product_repo():
    if ADAPTER == "mock":
        from repositories.adapters.mock import MockProductRepository
        return MockProductRepository()
    elif ADAPTER == "oracle":
        from repositories.adapters.oracle import OracleProductRepository
        connection = get_oracle_connection()
        return OracleProductRepository(connection)
    else:
        from repositories.adapters.supabase import SupabaseProductRepository
        client = get_supabase_client()
        return SupabaseProductRepository(client)
```

## Architecture Benefits

### 1. Testability
- Mock adapter provides in-memory implementation
- No database setup needed for tests
- Fast, isolated test execution

### 2. Flexibility
- Swap backends by environment variable
- Add new backends without changing application code
- Protocol-based contracts ensure compatibility

### 3. Clean Code
- Business logic separated from data access
- Routes don't know about database details
- Services depend on abstractions, not implementations

### 4. Scalability
- Easy to add caching layer
- Can optimize per-adapter
- Future support for distributed systems

## Common Patterns

### Pagination

```python
async def list_products(
    page: int = 1,
    per_page: int = 20,
    repo = Depends(get_product_repo)
):
    skip = (page - 1) * per_page
    products = await repo.get_all(skip=skip, limit=per_page)
    return products
```

### Filtering

```python
async def search_products(
    category: str = None,
    min_price: float = None,
    max_price: float = None,
    repo = Depends(get_product_repo)
):
    filters = {}
    if category:
        filters["category"] = category
    # Note: Price filtering may require custom logic

    products = await repo.list(**filters)
    if min_price or max_price:
        products = [p for p in products
                   if (min_price is None or p["price"] >= min_price)
                   and (max_price is None or p["price"] <= max_price)]
    return products
```

### Error Handling

```python
async def get_product_safe(
    product_id: str,
    repo = Depends(get_product_repo)
):
    try:
        product = await repo.get(product_id)
        if not product:
            raise HTTPException(status_code=404)
        return product
    except Exception as e:
        logger.error(f"Error getting product: {e}")
        raise HTTPException(status_code=500, detail="Database error")
```

### Transactions/Batch Operations

```python
async def create_order_from_cart(
    customer_id: str,
    cart_repo = Depends(get_cart_repo),
    order_repo = Depends(get_order_repo)
):
    # Get cart
    cart = await cart_repo.get_by_customer(customer_id)
    if not cart or not cart.get("cart_items"):
        raise HTTPException(status_code=400, detail="Cart is empty")

    # Create order
    order = await order_repo.create({
        "customer_id": customer_id,
        "items": cart["cart_items"],
        "total": cart["total"]
    })

    # Clear cart
    await cart_repo.clear(cart["id"])

    return order
```

## Performance Considerations

### Caching
Repositories don't implement caching, but you can add it in services:

```python
from functools import lru_cache

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

### Connection Pooling
Supabase client handles connection pooling automatically.

### N+1 Queries
Repository methods load related data explicitly:

```python
# Good: Gets cart with items in one call
cart = await cart_repo.get(cart_id)
# cart["cart_items"] already loaded

# Bad: Would require separate calls
items = await item_repo.list(cart_id=cart_id)
```

## Migration Guide

### From Direct Database Access

Before (without repository pattern):
```python
@app.get("/products/{product_id}")
async def get_product(product_id: str):
    from database import SessionLocal
    db = SessionLocal()
    product = db.query(Product).filter(Product.id == product_id).first()
    db.close()
    return product
```

After (with repository pattern):
```python
@app.get("/products/{product_id}")
async def get_product(
    product_id: str,
    repo = Depends(get_product_repo)
):
    product = await repo.get(product_id)
    return product
```

Benefits:
- No database import in route
- Easy to test with mock
- Easy to switch backends
- Consistent error handling
