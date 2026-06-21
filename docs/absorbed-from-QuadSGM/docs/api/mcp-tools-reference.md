# MCP Tools Reference

Complete documentation of all 25 MCP tools available in the 4SGM Wholesale Chatbot.

## Overview

The 4SGM MCP Server provides a comprehensive set of tools organized into six categories:

- **Product Tools** (6): Product information, search, and inventory management
- **Cart Tools** (6): Shopping cart and order management
- **Shipping Tools** (4): Shipping costs and tracking
- **Pricing Tools** (4): Bulk pricing and promotions
- **Customer Tools** (3): Customer history and preferences
- **RFQ Tools** (3): Request for Quote management

## Product Tools

### get_product

**Description**: Get detailed product information including name, description, price, SKU, category, and rating.

**Parameters**:
- `product_id` (string, required): Unique product identifier

**Returns**:
```json
{
  "id": "string",
  "name": "string",
  "description": "string",
  "price": 99.99,
  "sku": "string",
  "category": "string",
  "rating": 4.5,
  "reviews": 128
}
```

**Example Usage**:
```python
result = await get_product("PROD-001")
# Returns detailed product info
```

**Response Example**:
```json
{
  "id": "PROD-001",
  "name": "Premium Widget",
  "description": "High-quality product",
  "price": 99.99,
  "sku": "SKU-PROD-001",
  "category": "Electronics",
  "rating": 4.5,
  "reviews": 128
}
```

---

### search_products

**Description**: Search the product catalog with optional result limiting.

**Parameters**:
- `query` (string, required): Search query term
- `limit` (integer, optional): Maximum results to return (default: 10, max: 10)

**Returns**:
```json
[
  {
    "id": "string",
    "name": "string",
    "price": 50.0,
    "rating": 4.0
  }
]
```

**Example Usage**:
```python
results = await search_products("laptop", limit=5)
# Returns list of matching products
```

**Response Example**:
```json
[
  {
    "id": "prod-0",
    "name": "laptop Product 0",
    "price": 50.0,
    "rating": 4.0
  },
  {
    "id": "prod-1",
    "name": "laptop Product 1",
    "price": 60.0,
    "rating": 4.1
  }
]
```

---

### get_inventory

**Description**: Check current inventory levels for a product including stock, reserved, and available quantities.

**Parameters**:
- `product_id` (string, required): Product identifier

**Returns**:
```json
{
  "product_id": "string",
  "in_stock": 150,
  "reserved": 20,
  "available": 130,
  "warehouse_locations": ["string"]
}
```

**Example Usage**:
```python
inventory = await get_inventory("PROD-001")
# Returns inventory details
```

**Response Example**:
```json
{
  "product_id": "PROD-001",
  "in_stock": 150,
  "reserved": 20,
  "available": 130,
  "warehouse_locations": ["WH-A", "WH-B"]
}
```

---

### update_inventory

**Description**: Update product inventory quantities.

**Parameters**:
- `product_id` (string, required): Product identifier
- `quantity` (integer, required): Quantity to add/subtract

**Returns**:
```json
{
  "product_id": "string",
  "quantity_updated": 10,
  "new_total": 160,
  "timestamp": "2025-01-15T10:30:00Z"
}
```

**Example Usage**:
```python
result = await update_inventory("PROD-001", 50)
# Adds 50 units to inventory
```

**Response Example**:
```json
{
  "product_id": "PROD-001",
  "quantity_updated": 50,
  "new_total": 200,
  "timestamp": "2025-01-15T10:30:00Z"
}
```

---

### get_pricing

**Description**: Get product pricing with automatic bulk discount calculation based on quantity.

Bulk discounts:
- 1000+ units: 20% off
- 500-999 units: 15% off
- 100-499 units: 10% off
- 20-99 units: 5% off

**Parameters**:
- `product_id` (string, required): Product identifier
- `quantity` (integer, optional): Quantity for bulk pricing (default: 1)

**Returns**:
```json
{
  "product_id": "string",
  "quantity": 100,
  "base_price": 99.99,
  "discount_rate": 0.10,
  "unit_price": 89.99,
  "total": 8999.00
}
```

**Example Usage**:
```python
pricing = await get_pricing("PROD-001", quantity=100)
# Returns pricing with 10% bulk discount
```

**Response Example**:
```json
{
  "product_id": "PROD-001",
  "quantity": 100,
  "base_price": 99.99,
  "discount_rate": 0.10,
  "unit_price": 89.99,
  "total": 8999.00
}
```

---

### apply_discount

**Description**: Apply a promotional discount code to a product.

Valid discount codes:
- `SAVE10`: 10% off
- `SAVE20`: 20% off
- `BULK15`: 15% off

**Parameters**:
- `product_id` (string, required): Product identifier
- `discount_code` (string, required): Promotional code

**Returns**:
```json
{
  "product_id": "string",
  "code": "string",
  "discount_rate": 0.10,
  "valid": true
}
```

**Example Usage**:
```python
discount = await apply_discount("PROD-001", "SAVE10")
# Validates and applies discount code
```

**Response Example**:
```json
{
  "product_id": "PROD-001",
  "code": "SAVE10",
  "discount_rate": 0.10,
  "valid": true
}
```

---

## Cart Tools

### create_cart

**Description**: Create a new shopping cart for a user.

**Parameters**:
- `user_id` (string, required): Customer user identifier

**Returns**:
```json
{
  "cart_id": "string",
  "user_id": "string",
  "created_at": "2025-01-15T10:30:00Z",
  "items": [],
  "total": 0.0
}
```

**Example Usage**:
```python
cart = await create_cart("USER-001")
# Returns new cart
```

**Response Example**:
```json
{
  "cart_id": "CART-A1B2C3D4",
  "user_id": "USER-001",
  "created_at": "2025-01-15T10:30:00Z",
  "items": [],
  "total": 0.0
}
```

---

### add_to_cart

**Description**: Add an item to the shopping cart.

**Parameters**:
- `cart_id` (string, required): Cart identifier
- `product_id` (string, required): Product identifier
- `quantity` (integer, required): Quantity to add

**Returns**:
```json
{
  "cart_id": "string",
  "product_id": "string",
  "quantity": 5,
  "unit_price": 99.99,
  "line_total": 499.95,
  "status": "added"
}
```

**Example Usage**:
```python
item = await add_to_cart("CART-A1B2C3D4", "PROD-001", 5)
# Adds product to cart
```

**Response Example**:
```json
{
  "cart_id": "CART-A1B2C3D4",
  "product_id": "PROD-001",
  "quantity": 5,
  "unit_price": 99.99,
  "line_total": 499.95,
  "status": "added"
}
```

---

### remove_from_cart

**Description**: Remove an item from the shopping cart.

**Parameters**:
- `cart_id` (string, required): Cart identifier
- `product_id` (string, required): Product identifier to remove

**Returns**:
```json
{
  "cart_id": "string",
  "product_id": "string",
  "status": "removed"
}
```

**Example Usage**:
```python
result = await remove_from_cart("CART-A1B2C3D4", "PROD-001")
# Removes product from cart
```

**Response Example**:
```json
{
  "cart_id": "CART-A1B2C3D4",
  "product_id": "PROD-001",
  "status": "removed"
}
```

---

### calculate_cart_total

**Description**: Calculate cart total including subtotal, tax (8%), and shipping ($50 flat).

**Parameters**:
- `cart_id` (string, required): Cart identifier
- `items` (array, required): Array of item objects with `quantity` and `price`

**Returns**:
```json
{
  "cart_id": "string",
  "subtotal": 499.95,
  "tax": 39.99,
  "shipping": 50.0,
  "total": 589.94
}
```

**Example Usage**:
```python
total = await calculate_cart_total("CART-A1B2C3D4", [
  {"product_id": "PROD-001", "quantity": 5, "price": 99.99}
])
# Calculates total with tax and shipping
```

**Response Example**:
```json
{
  "cart_id": "CART-A1B2C3D4",
  "subtotal": 499.95,
  "tax": 39.99,
  "shipping": 50.0,
  "total": 589.94
}
```

---

### validate_cart

**Description**: Validate cart contents to ensure it's ready for checkout.

**Parameters**:
- `cart_id` (string, required): Cart identifier
- `items` (array, required): Array of items to validate

**Returns**:
```json
{
  "cart_id": "string",
  "valid": true,
  "item_count": 1,
  "errors": []
}
```

**Example Usage**:
```python
validation = await validate_cart("CART-A1B2C3D4", items)
# Validates cart for checkout
```

**Response Example**:
```json
{
  "cart_id": "CART-A1B2C3D4",
  "valid": true,
  "item_count": 1,
  "errors": []
}
```

---

### create_order

**Description**: Create an order from the shopping cart.

**Parameters**:
- `cart_id` (string, required): Cart identifier
- `user_id` (string, required): Customer user identifier
- `shipping_address` (string, required): Full shipping address

**Returns**:
```json
{
  "order_id": "string",
  "cart_id": "string",
  "user_id": "string",
  "status": "confirmed",
  "created_at": "2025-01-15T10:30:00Z",
  "shipping_address": "string",
  "tracking_number": "string"
}
```

**Example Usage**:
```python
order = await create_order(
  "CART-A1B2C3D4",
  "USER-001",
  "123 Main St, New York, NY 10001"
)
# Creates order and generates tracking number
```

**Response Example**:
```json
{
  "order_id": "ORD-X1Y2Z3W4",
  "cart_id": "CART-A1B2C3D4",
  "user_id": "USER-001",
  "status": "confirmed",
  "created_at": "2025-01-15T10:30:00Z",
  "shipping_address": "123 Main St, New York, NY 10001",
  "tracking_number": "TRK-A1B2C3D4"
}
```

---

## Shipping Tools

### calculate_shipping

**Description**: Calculate shipping costs and available carrier options based on origin, destination, and weight.

**Parameters**:
- `origin` (string, required): Origin location (e.g., "CA")
- `destination` (string, required): Destination location (e.g., "NY")
- `weight_lbs` (number, required): Package weight in pounds

**Returns**:
```json
{
  "origin": "string",
  "destination": "string",
  "weight_lbs": 10.5,
  "cost": 15.75,
  "estimated_days": 5,
  "carriers": [
    {
      "name": "Standard",
      "cost": 15.75,
      "days": 5
    },
    {
      "name": "Express",
      "cost": 23.63,
      "days": 2
    }
  ]
}
```

**Example Usage**:
```python
shipping = await calculate_shipping("CA", "NY", 10.5)
# Returns shipping options
```

**Response Example**:
```json
{
  "origin": "CA",
  "destination": "NY",
  "weight_lbs": 10.5,
  "cost": 15.75,
  "estimated_days": 5,
  "carriers": [
    {
      "name": "Standard",
      "cost": 15.75,
      "days": 5
    },
    {
      "name": "Express",
      "cost": 23.63,
      "days": 2
    }
  ]
}
```

---

### get_shipping_methods

**Description**: Get available shipping method options.

**Parameters**: None

**Returns**:
```json
[
  {
    "id": "string",
    "name": "string",
    "days": 5,
    "cost": 50
  }
]
```

**Example Usage**:
```python
methods = await get_shipping_methods()
# Returns all available shipping methods
```

**Response Example**:
```json
[
  {
    "id": "standard",
    "name": "Standard",
    "days": 5,
    "cost": 50
  },
  {
    "id": "express",
    "name": "Express",
    "days": 2,
    "cost": 75
  },
  {
    "id": "overnight",
    "name": "Overnight",
    "days": 1,
    "cost": 150
  }
]
```

---

### track_shipment

**Description**: Track shipment status and delivery progress.

**Parameters**:
- `tracking_number` (string, required): Shipment tracking number

**Returns**:
```json
{
  "tracking_number": "string",
  "status": "in_transit",
  "current_location": "string",
  "estimated_delivery": "2025-01-18T00:00:00Z",
  "events": [
    {
      "timestamp": "2025-01-15T10:30:00Z",
      "status": "picked_up",
      "location": "string"
    }
  ]
}
```

**Example Usage**:
```python
tracking = await track_shipment("TRK-A1B2C3D4")
# Returns tracking status
```

**Response Example**:
```json
{
  "tracking_number": "TRK-A1B2C3D4",
  "status": "in_transit",
  "current_location": "Distribution Center",
  "estimated_delivery": "2025-01-18T10:30:00Z",
  "events": [
    {
      "timestamp": "2025-01-15T10:30:00Z",
      "status": "picked_up",
      "location": "Warehouse"
    }
  ]
}
```

---

### estimate_delivery

**Description**: Estimate delivery date based on destination and shipping method.

**Parameters**:
- `destination` (string, required): Destination location
- `shipping_method` (string, required): Shipping method (standard/express/overnight)

**Returns**:
```json
{
  "destination": "string",
  "shipping_method": "string",
  "estimated_days": 5,
  "estimated_delivery_date": "2025-01-20T00:00:00Z"
}
```

**Example Usage**:
```python
estimate = await estimate_delivery("NY", "standard")
# Returns estimated delivery date
```

**Response Example**:
```json
{
  "destination": "NY",
  "shipping_method": "standard",
  "estimated_days": 5,
  "estimated_delivery_date": "2025-01-20T10:30:00Z"
}
```

---

## Pricing Tools

### get_bulk_pricing

**Description**: Get bulk order pricing with automatic discounts based on quantity ordered.

Discount tiers:
- 1000+ units: 20% off
- 500-999 units: 15% off
- 100-499 units: 10% off

**Parameters**:
- `product_id` (string, required): Product identifier
- `quantity` (integer, required): Order quantity

**Returns**:
```json
{
  "product_id": "string",
  "quantity": 100,
  "unit_price": 89.99,
  "total": 8999.00,
  "savings": 999.90
}
```

**Example Usage**:
```python
pricing = await get_bulk_pricing("PROD-001", 100)
# Returns bulk pricing with savings
```

**Response Example**:
```json
{
  "product_id": "PROD-001",
  "quantity": 100,
  "unit_price": 89.99,
  "total": 8999.00,
  "savings": 999.90
}
```

---

### apply_coupon

**Description**: Apply coupon code to order for discount.

Valid coupons:
- `SAVE10`: 10% off
- `SAVE20`: 20% off
- `BULK15`: 15% off

**Parameters**:
- `coupon_code` (string, required): Coupon code
- `cart_total` (number, required): Cart total before discount

**Returns**:
```json
{
  "coupon_code": "string",
  "valid": true,
  "discount_rate": 0.10,
  "discount_amount": 59.99,
  "new_total": 529.96
}
```

**Example Usage**:
```python
coupon = await apply_coupon("SAVE10", 589.95)
# Applies coupon and calculates new total
```

**Response Example**:
```json
{
  "coupon_code": "SAVE10",
  "valid": true,
  "discount_rate": 0.10,
  "discount_amount": 58.99,
  "new_total": 530.96
}
```

---

### get_promotions

**Description**: Get list of active promotional campaigns.

**Parameters**: None

**Returns**:
```json
[
  {
    "code": "string",
    "description": "string",
    "valid_until": "2025-12-31"
  }
]
```

**Example Usage**:
```python
promotions = await get_promotions()
# Returns all active promotions
```

**Response Example**:
```json
[
  {
    "code": "SAVE10",
    "description": "10% off",
    "valid_until": "2025-12-31"
  },
  {
    "code": "SAVE20",
    "description": "20% off orders over $500",
    "valid_until": "2025-12-31"
  },
  {
    "code": "BULK15",
    "description": "15% off bulk orders",
    "valid_until": "2025-12-31"
  }
]
```

---

### calculate_savings

**Description**: Calculate potential savings from applying a discount rate.

**Parameters**:
- `original_price` (number, required): Original price before discount
- `discount_rate` (number, required): Discount rate as decimal (0.10 = 10%)

**Returns**:
```json
{
  "original_price": 99.99,
  "discount_rate": 0.10,
  "savings": 9.99,
  "final_price": 90.00
}
```

**Example Usage**:
```python
savings = await calculate_savings(99.99, 0.10)
# Calculates savings amount and final price
```

**Response Example**:
```json
{
  "original_price": 99.99,
  "discount_rate": 0.10,
  "savings": 10.00,
  "final_price": 90.00
}
```

---

## Customer Tools

### get_customer_history

**Description**: Retrieve customer's order history and spending summary.

**Parameters**:
- `user_id` (string, required): Customer user identifier

**Returns**:
```json
{
  "user_id": "string",
  "total_orders": 5,
  "total_spent": 2500.00,
  "orders": [
    {
      "order_id": "string",
      "date": "2025-01-01",
      "total": 500.00
    }
  ]
}
```

**Example Usage**:
```python
history = await get_customer_history("USER-001")
# Returns customer order history
```

**Response Example**:
```json
{
  "user_id": "USER-001",
  "total_orders": 5,
  "total_spent": 2500.00,
  "orders": [
    {
      "order_id": "ORD-0",
      "date": "2025-01-01",
      "total": 500.00
    },
    {
      "order_id": "ORD-1",
      "date": "2025-01-02",
      "total": 500.00
    }
  ]
}
```

---

### get_customer_preferences

**Description**: Get customer's saved preferences and settings.

**Parameters**:
- `user_id` (string, required): Customer user identifier

**Returns**:
```json
{
  "user_id": "string",
  "preferred_shipping": "express",
  "preferred_payment": "credit_card",
  "newsletter_subscribed": true,
  "saved_addresses": 2
}
```

**Example Usage**:
```python
preferences = await get_customer_preferences("USER-001")
# Returns customer preferences
```

**Response Example**:
```json
{
  "user_id": "USER-001",
  "preferred_shipping": "express",
  "preferred_payment": "credit_card",
  "newsletter_subscribed": true,
  "saved_addresses": 2
}
```

---

### save_customer_preferences

**Description**: Save or update customer preferences.

**Parameters**:
- `user_id` (string, required): Customer user identifier
- `preferences` (object, required): Preferences object with user settings

**Returns**:
```json
{
  "user_id": "string",
  "preferences_saved": true,
  "updated_at": "2025-01-15T10:30:00Z"
}
```

**Example Usage**:
```python
result = await save_customer_preferences("USER-001", {
  "preferred_shipping": "express",
  "newsletter_subscribed": True
})
# Saves customer preferences
```

**Response Example**:
```json
{
  "user_id": "USER-001",
  "preferences_saved": true,
  "updated_at": "2025-01-15T10:30:00Z"
}
```

---

## RFQ Tools

### create_rfq

**Description**: Create a Request for Quote for bulk/custom orders.

**Parameters**:
- `items` (array, required): List of items in the RFQ
- `quantity` (integer, required): Total quantity requested
- `customer_name` (string, required): Customer name

**Returns**:
```json
{
  "rfq_id": "string",
  "customer_name": "string",
  "items": [],
  "total_quantity": 1000,
  "status": "pending",
  "created_at": "2025-01-15T10:30:00Z",
  "valid_until": "2025-02-14T10:30:00Z"
}
```

**Example Usage**:
```python
rfq = await create_rfq(
  ["PROD-001", "PROD-002"],
  1000,
  "Acme Corp"
)
# Creates RFQ request
```

**Response Example**:
```json
{
  "rfq_id": "RFQ-X1Y2Z3W4",
  "customer_name": "Acme Corp",
  "items": ["PROD-001", "PROD-002"],
  "total_quantity": 1000,
  "status": "pending",
  "created_at": "2025-01-15T10:30:00Z",
  "valid_until": "2025-02-14T10:30:00Z"
}
```

---

### get_rfq_status

**Description**: Check status of a Request for Quote.

**Parameters**:
- `rfq_id` (string, required): RFQ identifier

**Returns**:
```json
{
  "rfq_id": "string",
  "status": "pending",
  "created_at": "2025-01-15T10:30:00Z",
  "quote_amount": 5000.00
}
```

**Example Usage**:
```python
status = await get_rfq_status("RFQ-X1Y2Z3W4")
# Returns RFQ status
```

**Response Example**:
```json
{
  "rfq_id": "RFQ-X1Y2Z3W4",
  "status": "pending",
  "created_at": "2025-01-15T10:30:00Z",
  "quote_amount": 5000.00
}
```

---

### accept_rfq

**Description**: Accept an RFQ and create an order from it.

**Parameters**:
- `rfq_id` (string, required): RFQ identifier

**Returns**:
```json
{
  "rfq_id": "string",
  "order_id": "string",
  "status": "accepted",
  "created_at": "2025-01-15T10:30:00Z"
}
```

**Example Usage**:
```python
result = await accept_rfq("RFQ-X1Y2Z3W4")
# Accepts RFQ and creates order
```

**Response Example**:
```json
{
  "rfq_id": "RFQ-X1Y2Z3W4",
  "order_id": "ORD-A5B6C7D8",
  "status": "accepted",
  "created_at": "2025-01-15T10:30:00Z"
}
```

---

## Tool Categories Reference

### Product Management
- `get_product` - Retrieve product details
- `search_products` - Search catalog
- `get_inventory` - Check stock levels
- `update_inventory` - Modify inventory
- `get_pricing` - Get prices with bulk discounts
- `apply_discount` - Apply promotional codes

### Shopping & Orders
- `create_cart` - Start new cart
- `add_to_cart` - Add items
- `remove_from_cart` - Remove items
- `calculate_cart_total` - Compute totals
- `validate_cart` - Check cart validity
- `create_order` - Finalize purchase

### Shipping & Delivery
- `calculate_shipping` - Compute shipping costs
- `get_shipping_methods` - View options
- `track_shipment` - Monitor delivery
- `estimate_delivery` - Get delivery date

### Promotions & Pricing
- `get_bulk_pricing` - Bulk order pricing
- `apply_coupon` - Apply codes
- `get_promotions` - View campaigns
- `calculate_savings` - Savings calculator

### Customer Management
- `get_customer_history` - Order history
- `get_customer_preferences` - User settings
- `save_customer_preferences` - Update settings

### Request for Quote
- `create_rfq` - Create quote request
- `get_rfq_status` - Check status
- `accept_rfq` - Convert to order

## Error Handling

All tools return structured responses. If a tool encounters an error, it returns an error object:

```json
{
  "error": "Error description",
  "code": "ERROR_CODE",
  "details": {}
}
```

## Rate Limiting

The MCP server implements rate limiting of 10 requests per minute per user.

## Authentication

Tools are secured through the MCP server's authentication mechanism. Ensure proper client credentials are configured.
