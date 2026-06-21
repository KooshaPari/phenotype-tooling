# 4SGM API Documentation

Complete API documentation for the 4SGM Wholesale Chatbot platform.

## Overview

This directory contains comprehensive documentation for the 4SGM API, which provides a robust interface for wholesale product management, shopping cart operations, shipping, pricing, customer management, and request-for-quote functionality.

**API Version**: 1.0.0
**Last Updated**: January 15, 2025

## Documentation Files

### 1. mcp-tools-reference.md (1,179 lines)
Complete reference for all 25 MCP tools organized by category.

**Contents**:
- Product Tools (6): Product search, inventory, pricing
- Cart Tools (6): Shopping cart and order management
- Shipping Tools (4): Shipping costs and tracking
- Pricing Tools (4): Bulk pricing and promotions
- Customer Tools (3): Customer history and preferences
- RFQ Tools (3): Request for Quote management

**Use this for**:
- Understanding individual tool functionality
- Parameter specifications and data types
- Response schemas and examples
- Error handling procedures

**Key Features**:
- Complete parameter documentation
- JSON response examples for all 25 tools
- Usage examples in Python
- Error handling guidelines

### 2. openapi.yaml (393 lines)
OpenAPI 3.0 specification for the 4SGM REST API.

**Contents**:
- RESTful endpoint definitions
- Request/response schemas
- Authentication configuration
- Error response definitions
- Data model definitions

**Use this for**:
- API endpoint discovery
- Integration testing
- Code generation (Swagger Codegen, OpenAPI Generator)
- API documentation rendering (Swagger UI, ReDoc)

**Supported Endpoints**:
- `GET /health` - Health check
- `GET /tools` - List MCP tools
- `POST /chat` - Chat with agent
- `POST /chat/stream` - Streaming chat
- `POST /api/session` - Create session
- `GET /api/session/{session_id}` - Get session

### 3. api-usage-guide.md (655 lines)
Practical guide with examples and best practices.

**Contents**:
- Quick start guide
- Authentication setup
- 8 core workflow examples:
  1. Product Search & Details
  2. Inventory Management
  3. Shopping Cart & Checkout
  4. Bulk Pricing
  5. Promotions & Discounts
  6. Shipping & Delivery
  7. Customer Management
  8. Request for Quote
- Client integration examples (Python, JavaScript, cURL)
- Error handling and recovery
- Rate limiting information
- Best practices and troubleshooting

**Use this for**:
- Getting started with the API
- Learning by example
- Integration implementation
- Troubleshooting common issues

**Client Examples Included**:
- Python (requests library)
- TypeScript (fetch API)
- cURL (shell)

## Quick Reference

### Base URLs
```
Production: https://api.4sgm.com
Development: http://localhost:8000
```

### MCP Tools by Category

#### Product Tools (6)
- `get_product` - Get product details
- `search_products` - Search catalog
- `get_inventory` - Check stock levels
- `update_inventory` - Modify inventory
- `get_pricing` - Get prices with bulk discounts
- `apply_discount` - Apply promotional codes

#### Cart Tools (6)
- `create_cart` - Create shopping cart
- `add_to_cart` - Add items to cart
- `remove_from_cart` - Remove items from cart
- `calculate_cart_total` - Calculate total with tax/shipping
- `validate_cart` - Validate cart contents
- `create_order` - Create order from cart

#### Shipping Tools (4)
- `calculate_shipping` - Calculate shipping costs
- `get_shipping_methods` - Get available methods
- `track_shipment` - Track delivery
- `estimate_delivery` - Estimate delivery date

#### Pricing Tools (4)
- `get_bulk_pricing` - Get bulk order pricing
- `apply_coupon` - Apply coupon codes
- `get_promotions` - Get active promotions
- `calculate_savings` - Calculate savings amounts

#### Customer Tools (3)
- `get_customer_history` - Get order history
- `get_customer_preferences` - Get preferences
- `save_customer_preferences` - Update preferences

#### RFQ Tools (3)
- `create_rfq` - Create request for quote
- `get_rfq_status` - Check RFQ status
- `accept_rfq` - Accept RFQ and create order

## Authentication

The API uses bearer token authentication with JWT tokens.

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  https://api.4sgm.com/health
```

## Rate Limiting

- **Limit**: 10 requests per minute per user
- **Headers**:
  - `X-RateLimit-Limit: 10`
  - `X-RateLimit-Remaining: 9`
  - `X-RateLimit-Reset: 1705308600`

## Common Workflows

### 1. Product Search
```
User Query → Search Products → Get Details → Return Results
```

### 2. Place Order
```
Create Cart → Add Items → Validate → Calculate Total → Create Order
```

### 3. Check Shipping
```
Calculate Shipping → Select Method → Estimate Delivery → Track
```

### 4. Bulk Quote
```
Create RFQ → Get Status → Accept RFQ → Create Order
```

## Response Format

All endpoints return JSON responses:

```json
{
  "status": "success|error",
  "data": {},
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## Error Handling

### HTTP Status Codes
- `200` - Success
- `400` - Bad request
- `401` - Unauthorized
- `429` - Rate limit exceeded
- `500` - Server error
- `503` - Service unavailable (MCP not connected)

### Error Response Format
```json
{
  "detail": "Error description",
  "code": "ERROR_CODE",
  "timestamp": "2025-01-15T10:30:00Z"
}
```

## Getting Started

### Step 1: Health Check
```bash
curl http://localhost:8000/health
```

### Step 2: List Tools
```bash
curl http://localhost:8000/tools
```

### Step 3: Create Session
```bash
curl -X POST http://localhost:8000/api/session
```

### Step 4: Send Chat Message
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Find laptop products",
    "session_id": "YOUR_SESSION_ID"
  }'
```

## Integration Examples

### Python
See api-usage-guide.md section "Client Integration Examples" for complete Python implementation.

### JavaScript/TypeScript
See api-usage-guide.md section "Client Integration Examples" for complete TypeScript implementation.

### cURL
See api-usage-guide.md section "Client Integration Examples" for cURL examples.

## Key Features

### Real-time Chat Interface
- Natural language product queries
- Intelligent agent routing
- Multi-step conversations
- Session management

### Comprehensive Product Management
- Product search and filtering
- Inventory tracking
- Pricing with bulk discounts
- Promotional code management

### Order Management
- Shopping cart operations
- Tax and shipping calculations
- Order confirmation
- Tracking integration

### Customer Management
- Order history
- Preference tracking
- Saved addresses
- Communication preferences

### Request for Quote (RFQ)
- Custom quote requests
- Bulk pricing
- Quote validation
- Order creation from quotes

## Bulk Discount Tiers

| Quantity | Discount | Unit Price | Total |
|----------|----------|-----------|-------|
| 1-19 | 0% | $99.99 | $99.99 |
| 20-99 | 5% | $94.99 | $1,899.80 |
| 100-499 | 10% | $89.99 | $8,999.00 |
| 500-999 | 15% | $84.99 | $42,495.00 |
| 1000+ | 20% | $79.99 | $79,990.00 |

## Available Promotions

| Code | Discount | Details |
|------|----------|---------|
| SAVE10 | 10% off | All products |
| SAVE20 | 20% off | Orders over $500 |
| BULK15 | 15% off | Bulk orders |

## Shipping Methods

| Method | Days | Cost |
|--------|------|------|
| Standard | 5 | $50.00 |
| Express | 2 | $75.00 |
| Overnight | 1 | $150.00 |

## Support & Resources

### Documentation
- **API Reference**: mcp-tools-reference.md
- **Usage Guide**: api-usage-guide.md
- **OpenAPI Spec**: openapi.yaml

### External Tools
- [Swagger UI](http://localhost:8000/docs) - Interactive API explorer
- [ReDoc](http://localhost:8000/redoc) - Beautiful documentation
- [Postman Collection](./postman-collection.json) - Importable tests

### Support Channels
- Documentation: https://4sgm.com/docs
- Issues: https://github.com/4sgm/api/issues
- Email: support@4sgm.com

## API Statistics

- **Total Endpoints**: 6 REST endpoints
- **Total MCP Tools**: 25 tools across 6 categories
- **Documentation**: 2,227 lines across 3 files
- **Response Format**: JSON
- **Authentication**: JWT Bearer Token
- **Rate Limit**: 10 requests/minute per user
- **Uptime SLA**: 99.9%

## Version History

### v1.0.0 (2025-01-15)
- Initial release
- 25 MCP tools implemented
- Complete REST API documentation
- Session management
- Real-time chat interface

## License

The 4SGM API is licensed under the Apache 2.0 License.

---

**Last Updated**: January 15, 2025
**Documentation Version**: 1.0.0
**API Version**: 1.0.0
