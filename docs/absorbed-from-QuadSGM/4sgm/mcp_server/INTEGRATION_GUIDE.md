# Integration Guide for Agent 5 - Repository Implementation

This guide explains how to implement the repository interfaces and inject them into the MCP server.

## Overview

Agent 6 has defined:
1. **Abstract repository interfaces** in `repositories.py`
2. **Pydantic models** in `models/` for validation
3. **13 async tools** in `server.py` that use repositories
4. **Exception hierarchy** in `exceptions.py` for error handling

Your job (Agent 5) is to implement the repository interfaces and connect them to the database.

## Repository Interfaces to Implement

### 1. ProductRepository

```python
from repositories import ProductRepository, Product

class ProductRepositoryImpl(ProductRepository):
    def __init__(self, db_session):
        self.db = db_session

    async def get(self, product_id: str) -> Optional[Product]:
        """Fetch single product from database.

        Args:
            product_id: Product ID or SKU

        Returns:
            Product object with all details, or None if not found
        """
        # Query: SELECT * FROM products WHERE id = ? OR sku = ?
        # Return: Product(id, sku, name, price, description, category, rating, reviews, quantity_on_hand, created_at, updated_at)
        pass

    async def search(self, query: str, limit: int = 10) -> list[Product]:
        """Full-text search across products.

        Args:
            query: Search string (product name, description, category)
            limit: Max results to return (1-100)

        Returns:
            List of matching Product objects
        """
        # Query: SELECT * FROM products WHERE name ILIKE ? OR description ILIKE ? LIMIT ?
        # Return: [Product(...), ...]
        pass
```

### 2. InventoryRepository

```python
from repositories import InventoryRepository, Inventory

class InventoryRepositoryImpl(InventoryRepository):
    def __init__(self, db_session):
        self.db = db_session

    async def get_inventory(self, product_id: str) -> Optional[Inventory]:
        """Get stock levels for product.

        Args:
            product_id: Product ID

        Returns:
            Inventory object with in_stock, reserved, available counts
        """
        # Query: SELECT * FROM inventory WHERE product_id = ?
        # Return: Inventory(product_id, in_stock, reserved, available, warehouse_locations)
        pass

    async def update_inventory(self, product_id: str, quantity_change: int) -> Optional[Inventory]:
        """Update inventory quantity.

        Args:
            product_id: Product ID
            quantity_change: Positive (add) or negative (reduce)

        Returns:
            Updated Inventory object, or None if product not found

        Note:
            Must prevent inventory from going below reserved quantity
            Update should be atomic
        """
        # Query: UPDATE inventory SET in_stock = in_stock + ? WHERE product_id = ?
        # Return: Updated Inventory object
        pass

    async def check_availability(self, product_id: str, quantity: int) -> bool:
        """Check if quantity is available.

        Args:
            product_id: Product ID
            quantity: Quantity needed

        Returns:
            True if (available >= quantity), False otherwise
        """
        # Query: SELECT available FROM inventory WHERE product_id = ?
        # Return: bool
        pass
```

### 3. PricingRepository

```python
from repositories import PricingRepository

class PricingRepositoryImpl(PricingRepository):
    def __init__(self, db_session):
        self.db = db_session

    async def get_pricing(self, product_id: str, quantity: int = 1) -> dict:
        """Get pricing with bulk discounts.

        Args:
            product_id: Product ID
            quantity: Quantity for calculation

        Returns:
            Dict with keys:
                - base_price: float (product base price)
                - discount_rate: float (0.0-1.0)
                - unit_price: float (price after discount)
                - total: float (unit_price * quantity)

        Discount Table:
            1-19:     0%
            20-99:    5%
            100-499:  10%
            500-999:  15%
            1000+:    20%
        """
        # Query: SELECT price FROM products WHERE id = ?
        # Calculate bulk discount based on quantity
        # Return: {"base_price": 99.99, "discount_rate": 0.15, "unit_price": 84.99, "total": 8499.0}
        pass

    async def validate_discount_code(self, code: str) -> float:
        """Validate discount code and return rate.

        Args:
            code: Discount code (e.g., "SAVE10")

        Returns:
            Discount rate 0.0-1.0, or 0.0 if invalid
        """
        # Query: SELECT rate FROM discount_codes WHERE code = ? AND expired_at > NOW()
        # Return: 0.10 for valid code, 0.0 for invalid
        pass
```

### 4. CartRepository

```python
from repositories import CartRepository

class CartRepositoryImpl(CartRepository):
    def __init__(self, db_session):
        self.db = db_session

    async def create_cart(self, user_id: str) -> dict:
        """Create new shopping cart.

        Args:
            user_id: User identifier

        Returns:
            Dict with keys:
                - cart_id: str (unique identifier)
                - user_id: str
                - created_at: datetime
                - items: list (empty)
                - total: float (0.0)
        """
        # Insert: INSERT INTO carts (id, user_id, created_at) VALUES (?, ?, NOW())
        # Return: {"cart_id": "CART-...", "user_id": "...", "created_at": datetime, "items": [], "total": 0.0}
        pass

    async def get_cart(self, cart_id: str) -> Optional[dict]:
        """Get cart details.

        Args:
            cart_id: Cart identifier

        Returns:
            Cart dict, or None if not found
        """
        # Query: SELECT * FROM carts WHERE id = ?
        # Include: items, total
        pass

    async def add_item(self, cart_id: str, product_id: str, quantity: int,
                      unit_price: float) -> dict:
        """Add item to cart.

        Args:
            cart_id: Cart identifier
            product_id: Product to add
            quantity: Quantity
            unit_price: Price per unit

        Returns:
            Dict with keys:
                - product_id: str
                - quantity: int
                - unit_price: float
                - line_total: float
        """
        # Upsert: INSERT INTO cart_items (...) VALUES (...) ON CONFLICT (...) UPDATE ...
        # Return: {"product_id": "...", "quantity": 5, "unit_price": 50.0, "line_total": 250.0}
        pass

    async def remove_item(self, cart_id: str, product_id: str) -> bool:
        """Remove item from cart.

        Args:
            cart_id: Cart identifier
            product_id: Product to remove

        Returns:
            True if removed, False if not found
        """
        # Delete: DELETE FROM cart_items WHERE cart_id = ? AND product_id = ?
        # Return: True if deleted, False if not found
        pass

    async def get_items(self, cart_id: str) -> list[dict]:
        """Get all items in cart.

        Args:
            cart_id: Cart identifier

        Returns:
            List of item dicts with product_id, quantity, unit_price, line_total
        """
        # Query: SELECT product_id, quantity, unit_price, line_total FROM cart_items WHERE cart_id = ?
        # Return: [{"product_id": "...", "quantity": 5, "unit_price": 50.0, "line_total": 250.0}, ...]
        pass
```

### 5. OrderRepository

```python
from repositories import OrderRepository

class OrderRepositoryImpl(OrderRepository):
    def __init__(self, db_session):
        self.db = db_session

    async def create_order(self, cart_id: str, user_id: str, shipping_address: str,
                          items: Optional[list[dict]] = None, subtotal: Optional[float] = None,
                          tax: Optional[float] = None, shipping_cost: Optional[float] = None,
                          total: Optional[float] = None) -> dict:
        """Create order from cart.

        Args:
            cart_id: Cart ID to convert
            user_id: User identifier
            shipping_address: Delivery address
            items: Order items (optional, for record)
            subtotal: Order subtotal (optional, for record)
            tax: Tax amount (optional, for record)
            shipping_cost: Shipping cost (optional, for record)
            total: Order total (optional, for record)

        Returns:
            Dict with keys:
                - order_id: str (unique)
                - cart_id: str
                - user_id: str
                - status: str ("confirmed")
                - created_at: datetime
                - shipping_address: str
                - tracking_number: str (unique)
        """
        # Transaction:
        # 1. INSERT INTO orders (...) VALUES (...)
        # 2. INSERT INTO order_items (SELECT ... FROM cart_items WHERE cart_id = ?)
        # 3. DELETE FROM carts WHERE id = ? OR UPDATE carts SET status = "converted"
        # 4. Return order details
        pass

    async def get_order(self, order_id: str) -> Optional[dict]:
        """Get order details.

        Args:
            order_id: Order identifier

        Returns:
            Order dict with all details, or None if not found
        """
        # Query: SELECT * FROM orders WHERE id = ?
        # Include: items, subtotal, tax, shipping_cost, total
        pass
```

## Implementation Example

Here's a complete example using SQLAlchemy:

```python
from sqlalchemy import select, insert, update, delete
from sqlalchemy.ext.asyncio import AsyncSession
from datetime import datetime
import uuid

from repositories import (
    ProductRepository, Product, Inventory,
    InventoryRepository, PricingRepository,
    CartRepository, OrderRepository
)
from ..backend.models import (
    ProductModel, InventoryModel, DiscountCodeModel,
    CartModel, CartItemModel, OrderModel, OrderItemModel
)

class ProductRepositoryImpl(ProductRepository):
    def __init__(self, db: AsyncSession):
        self.db = db

    async def get(self, product_id: str) -> Optional[Product]:
        # Query by ID or SKU
        query = select(ProductModel).where(
            (ProductModel.id == product_id) | (ProductModel.sku == product_id)
        )
        result = await self.db.execute(query)
        row = result.scalar_one_or_none()

        if not row:
            return None

        return Product(
            id=row.id,
            sku=row.sku,
            name=row.name,
            price=row.price,
            description=row.description,
            category=row.category,
            rating=None,  # Calculate from reviews table
            reviews=None,  # Count from reviews table
            quantity_on_hand=row.quantity_on_hand,
            created_at=row.created_at,
            updated_at=row.updated_at,
        )

    async def search(self, query: str, limit: int = 10) -> list[Product]:
        search_term = f"%{query}%"
        sql_query = select(ProductModel).where(
            (ProductModel.name.ilike(search_term)) |
            (ProductModel.description.ilike(search_term)) |
            (ProductModel.category.ilike(search_term))
        ).limit(limit)

        result = await self.db.execute(sql_query)
        rows = result.scalars().all()

        return [
            Product(
                id=row.id,
                sku=row.sku,
                name=row.name,
                price=row.price,
                description=row.description,
                category=row.category,
                rating=None,
                reviews=None,
                quantity_on_hand=row.quantity_on_hand,
                created_at=row.created_at,
                updated_at=row.updated_at,
            )
            for row in rows
        ]

class PricingRepositoryImpl(PricingRepository):
    async def get_pricing(self, product_id: str, quantity: int = 1) -> dict:
        # Get product price
        query = select(ProductModel.price).where(ProductModel.id == product_id)
        result = await self.db.execute(query)
        base_price = result.scalar_one_or_none()

        if base_price is None:
            raise ProductNotFoundError(f"Product {product_id} not found")

        # Calculate bulk discount
        discount_rate = 0.0
        if quantity >= 1000:
            discount_rate = 0.20
        elif quantity >= 500:
            discount_rate = 0.15
        elif quantity >= 100:
            discount_rate = 0.10
        elif quantity >= 20:
            discount_rate = 0.05

        unit_price = base_price * (1 - discount_rate)
        total = unit_price * quantity

        return {
            "base_price": float(base_price),
            "discount_rate": discount_rate,
            "unit_price": round(float(unit_price), 2),
            "total": round(float(total), 2),
        }

    async def validate_discount_code(self, code: str) -> float:
        query = select(DiscountCodeModel.rate).where(
            (DiscountCodeModel.code == code) &
            (DiscountCodeModel.expires_at > datetime.utcnow())
        )
        result = await self.db.execute(query)
        rate = result.scalar_one_or_none()

        return float(rate) if rate else 0.0
```

## Dependency Injection

Once implemented, inject repositories into the MCP server:

```python
# main.py or app initialization
from mcp_server.server import set_repositories
from my_repositories import (
    ProductRepositoryImpl, InventoryRepositoryImpl,
    PricingRepositoryImpl, CartRepositoryImpl,
    OrderRepositoryImpl
)

async def init_mcp_server(db_session):
    """Initialize MCP server with repository implementations."""

    product_repo = ProductRepositoryImpl(db_session)
    inventory_repo = InventoryRepositoryImpl(db_session)
    pricing_repo = PricingRepositoryImpl(db_session)
    cart_repo = CartRepositoryImpl(db_session)
    order_repo = OrderRepositoryImpl(db_session)

    set_repositories(
        product_repo,
        inventory_repo,
        pricing_repo,
        cart_repo,
        order_repo
    )
```

## Error Handling in Repositories

Raise appropriate exceptions:

```python
from exceptions import (
    ProductNotFoundError, InventoryNotFoundError,
    InsufficientInventoryError
)

async def get(self, product_id: str) -> Optional[Product]:
    # Query...
    if not row:
        raise ProductNotFoundError(f"Product {product_id} not found")
    return Product(...)

async def update_inventory(self, product_id: str, quantity_change: int):
    # Get current inventory
    inventory = await self.get_inventory(product_id)
    if not inventory:
        raise InventoryNotFoundError(f"Inventory for {product_id} not found")

    # Check if reduction would go negative
    if inventory.in_stock + quantity_change < inventory.reserved:
        raise InsufficientInventoryError(
            f"Cannot reduce inventory below reserved quantity"
        )

    # Update...
    return updated_inventory
```

## Testing Your Implementations

Create a test repository using in-memory data:

```python
class MockProductRepository(ProductRepository):
    def __init__(self):
        self.products = {
            "prod-1": Product(id="prod-1", sku="SKU-1", name="Widget", price=99.99, ...),
        }

    async def get(self, product_id: str) -> Optional[Product]:
        return self.products.get(product_id)

    async def search(self, query: str, limit: int = 10) -> list[Product]:
        return [p for p in self.products.values() if query.lower() in p.name.lower()][:limit]
```

Then test the MCP tools:

```python
async def test_get_product():
    mock_product_repo = MockProductRepository()
    set_repositories(mock_product_repo, ...)

    result = await get_product("prod-1")
    assert result["name"] == "Widget"
```

## Database Schema Considerations

Ensure your models support:

**Products Table**
- id (PK)
- sku (unique)
- name
- description
- price
- category
- quantity_on_hand
- created_at
- updated_at

**Inventory Table**
- product_id (FK)
- in_stock
- reserved
- available
- warehouse_locations (JSON)

**Discount Codes Table**
- code (PK)
- rate (0.0-1.0)
- expires_at
- created_at

**Carts Table**
- id (PK)
- user_id
- status
- created_at
- updated_at

**Cart Items Table**
- cart_id (FK)
- product_id (FK)
- quantity
- unit_price
- line_total

**Orders Table**
- id (PK)
- user_id
- cart_id (FK)
- status
- shipping_address
- tracking_number
- subtotal
- tax
- shipping_cost
- total
- created_at

**Order Items Table**
- order_id (FK)
- product_id (FK)
- quantity
- unit_price
- line_total

## Async/Await Patterns

All repository methods must be async:

```python
# ✅ CORRECT
async def get(self, product_id: str) -> Optional[Product]:
    result = await self.db.execute(...)
    return result.scalar_one_or_none()

# ❌ WRONG
def get(self, product_id: str) -> Optional[Product]:
    result = self.db.query(...).first()
    return result
```

## Performance Tips

1. **Index frequently queried columns** (product_id, sku, user_id)
2. **Use connection pooling** for database efficiency
3. **Cache discount codes** (rarely change)
4. **Batch operations** where possible (order creation)
5. **Use database transactions** for critical operations (order creation)

## Success Criteria

Your repository implementations are complete when:
- ✅ All 5 repository interfaces implemented
- ✅ All methods are async/await
- ✅ Appropriate exceptions raised
- ✅ All 13 MCP tools work end-to-end
- ✅ Mock data replaced with real database queries
- ✅ Tests pass for all tool workflows
- ✅ Error handling verified for edge cases

Good luck with the implementation!
