# MCP Tools Reference - Product, Cart, Order

Quick reference for all 13 upgraded tools with signatures, validation rules, and error codes.

## Product Tools

### 1. get_product(product_id: str)
Retrieve full product details.

**Input Validation**
- `product_id`: string, required

**Output**
```python
{
    "id": str,
    "sku": str,
    "name": str,
    "price": float,
    "description": str | null,
    "category": str | null,
    "rating": float | null,
    "reviews": int | null,
    "quantity_on_hand": int,
    "created_at": datetime | null,
    "updated_at": datetime | null
}
```

**Errors**
- `ProductNotFoundError` - Product not in catalog
- `ProductSearchError` - Database query failed

---

### 2. search_products(query: str, limit: int = 10)
Full-text search across product catalog.

**Input Validation**
- `query`: string, required, min_length=1
- `limit`: int, default=10, range=1-100

**Output**
```python
{
    "products": [ProductResponse],
    "total_results": int,
    "query": str
}
```

**Errors**
- `ProductSearchError` - Search operation failed

---

### 3. get_inventory(product_id: str)
Check current stock levels and warehouse locations.

**Input Validation**
- `product_id`: string, required

**Output**
```python
{
    "product_id": str,
    "in_stock": int,
    "reserved": int,
    "available": int,
    "warehouse_locations": [str]
}
```

**Errors**
- `InventoryNotFoundError` - No inventory record for product
- `InventoryError` - Database query failed

---

### 4. update_inventory(product_id: str, quantity: int)
Add or remove inventory (positive/negative quantities).

**Input Validation**
- `product_id`: string, required
- `quantity`: int, required, non-zero

**Output**
```python
{
    "product_id": str,
    "quantity_updated": int,
    "new_total": int,
    "timestamp": datetime
}
```

**Errors**
- `InventoryNotFoundError` - Product not found
- `InsufficientInventoryError` - Reducing below zero
- `InventoryError` - Update failed

---

### 5. get_pricing(product_id: str, quantity: int = 1)
Calculate pricing with automatic bulk discounts.

**Input Validation**
- `product_id`: string, required
- `quantity`: int, default=1, min=1

**Bulk Discount Table**
| Quantity | Discount |
|----------|----------|
| 1-19     | 0%       |
| 20-99    | 5%       |
| 100-499  | 10%      |
| 500-999  | 15%      |
| 1000+    | 20%      |

**Output**
```python
{
    "product_id": str,
    "quantity": int,
    "base_price": float,
    "discount_rate": float,
    "unit_price": float,
    "total": float
}
```

**Errors**
- `PricingError` - Pricing calculation failed

---

### 6. apply_discount(product_id: str, discount_code: str)
Apply promotional discount code.

**Input Validation**
- `product_id`: string, required
- `discount_code`: string, required, min_length=1

**Valid Codes**
| Code    | Discount |
|---------|----------|
| SAVE10  | 10%      |
| SAVE20  | 20%      |
| BULK15  | 15%      |

**Output**
```python
{
    "product_id": str,
    "code": str,
    "discount_rate": float,
    "valid": bool
}
```

**Errors**
- `InvalidDiscountCodeError` - Code not valid
- `PricingError` - Operation failed

---

## Cart Tools

### 7. create_cart(user_id: str)
Create new shopping cart for user.

**Input Validation**
- `user_id`: string, required, min_length=1

**Output**
```python
{
    "cart_id": str,
    "user_id": str,
    "items": [],
    "total": 0.0,
    "created_at": datetime
}
```

**Errors**
- `CartError` - Creation failed

---

### 8. add_to_cart(cart_id: str, product_id: str, quantity: int)
Add product to cart (or update quantity).

**Input Validation**
- `cart_id`: string, required, min_length=1
- `product_id`: string, required, min_length=1
- `quantity`: int, required, min=1

**Output**
```python
{
    "cart_id": str,
    "product_id": str,
    "quantity": int,
    "unit_price": float,
    "line_total": float,
    "status": "added"
}
```

**Notes**
- Automatically fetches current unit price from pricing repo
- Applies bulk discounts based on quantity

**Errors**
- `CartNotFoundError` - Cart doesn't exist
- `CartError` - Add operation failed

---

### 9. remove_from_cart(cart_id: str, product_id: str)
Remove product from cart completely.

**Input Validation**
- `cart_id`: string, required, min_length=1
- `product_id`: string, required, min_length=1

**Output**
```python
{
    "cart_id": str,
    "product_id": str,
    "status": "removed"
}
```

**Errors**
- `CartNotFoundError` - Cart doesn't exist
- `CartError` - Remove operation failed

---

### 10. calculate_cart_total(cart_id: str, items: list[dict])
Calculate cart total with tax and shipping.

**Input Validation**
- `cart_id`: string, required, min_length=1
- `items`: list, required, min_length=1
  - Each item: `{"product_id": str, "quantity": int >= 1, "price": float >= 0}`

**Calculation**
```
subtotal = sum(item.quantity * item.price for item in items)
tax = subtotal * 0.08
shipping = 50.0
total = subtotal + tax + shipping
```

**Output**
```python
{
    "cart_id": str,
    "subtotal": float,
    "tax": float,
    "shipping": 50.0,
    "total": float
}
```

**Errors**
- `CartValidationError` - Invalid items
- `CartError` - Calculation failed

---

### 11. validate_cart(cart_id: str, items: list[dict])
Validate cart contents without calculating totals.

**Input Validation**
- `cart_id`: string, required, min_length=1
- `items`: list, required
  - Each item: `{"product_id": str, "quantity": int, "price": float | optional}`

**Validation Rules**
- Cart must not be empty
- Each item must have quantity > 0
- Each item must have product_id
- Price (if provided) must be >= 0

**Output**
```python
{
    "cart_id": str,
    "valid": bool,
    "item_count": int,
    "errors": [str]  # List of validation errors
}
```

**Errors**
- `CartError` - Validation operation failed

---

## Order Tools

### 12. create_order(cart_id: str, user_id: str, shipping_address: str, items: list[dict] = None, subtotal: float = None, tax: float = None, shipping_cost: float = None, total: float = None)
Convert cart to confirmed order.

**Input Validation**
- `cart_id`: string, required, min_length=1
- `user_id`: string, required, min_length=1
- `shipping_address`: string, required, min_length=10
- `items`: list[dict], optional
- `subtotal`: float, optional
- `tax`: float, optional
- `shipping_cost`: float, optional
- `total`: float, optional

**Output**
```python
{
    "order_id": str,
    "cart_id": str,
    "user_id": str,
    "status": "confirmed",
    "created_at": datetime,
    "shipping_address": str,
    "tracking_number": str,
    "items": [CartItem] | null,
    "subtotal": float | null,
    "tax": float | null,
    "shipping_cost": float | null,
    "total": float | null
}
```

**Notes**
- Generates unique order_id (ORD-XXXXXXXX)
- Generates tracking_number (TRK-XXXXXXXX)
- All optional financial fields echo back in response for record-keeping

**Errors**
- `InvalidOrderDataError` - Required fields invalid
- `OrderCreationError` - Order creation failed

---

## Integration Guide

### Repository Injection
```python
from mcp_server.server import set_repositories
from mcp_server.repositories import (
    ProductRepository, InventoryRepository, PricingRepository,
    CartRepository, OrderRepository
)

# Implement repositories
product_repo = MyProductRepository()
inventory_repo = MyInventoryRepository()
pricing_repo = MyPricingRepository()
cart_repo = MyCartRepository()
order_repo = MyOrderRepository()

# Inject
set_repositories(
    product_repo,
    inventory_repo,
    pricing_repo,
    cart_repo,
    order_repo
)
```

### Exception Handling
```python
from mcp_server.exceptions import (
    ProductNotFoundError, CartError, OrderCreationError
)

try:
    result = await get_product("prod-123")
except ProductNotFoundError:
    # Handle missing product
    pass
except Exception as e:
    # Log unexpected errors
    logger.error(f"Unexpected error: {e}")
```

### Pydantic Integration
```python
from mcp_server.models import ProductResponse

# Response models auto-validate
response = ProductResponse(id="123", name="Widget", sku="SKU-123", price=99.99)
response_dict = response.model_dump()
response_json = response.model_dump_json()
```

---

## Common Workflows

### Product Search + Inventory + Pricing
```python
# 1. Search for products
search_result = await search_products("widget", limit=5)

# 2. Get inventory for selected product
inventory = await get_inventory(search_result["products"][0]["id"])

# 3. Get bulk pricing
pricing = await get_pricing(product_id, quantity=100)
```

### Shopping Workflow
```python
# 1. Create cart
cart = await create_cart("user-123")
cart_id = cart["cart_id"]

# 2. Add items
await add_to_cart(cart_id, "prod-1", 5)
await add_to_cart(cart_id, "prod-2", 10)

# 3. Calculate total
items = [
    {"product_id": "prod-1", "quantity": 5, "price": 50.0},
    {"product_id": "prod-2", "quantity": 10, "price": 30.0}
]
total = await calculate_cart_total(cart_id, items)

# 4. Validate
validation = await validate_cart(cart_id, items)
if not validation["valid"]:
    raise CartValidationError(validation["errors"])

# 5. Create order
order = await create_order(cart_id, "user-123", "123 Main St, City, State 12345")
```

### Discount Application
```python
# Check discount code validity
discount = await apply_discount("prod-123", "SAVE10")
if discount["valid"]:
    # Apply to cart calculation
    discounted_price = product_price * (1 - discount["discount_rate"])
```

---

## Performance Notes

- All operations are async (non-blocking)
- Bulk operations (search) support limit parameter for pagination
- Cart operations are stateless (queries include full item list)
- Order creation is transactional (atomic operation)
- Recommend caching product pricing for frequently requested items
