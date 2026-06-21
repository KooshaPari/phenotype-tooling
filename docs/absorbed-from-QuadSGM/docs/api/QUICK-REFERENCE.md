# 4SGM API Quick Reference Card

## Endpoints Overview

| Method | Endpoint | Description | Auth |
|--------|----------|-------------|------|
| GET | `/health` | Health check | No |
| GET | `/tools` | List MCP tools | No |
| POST | `/chat` | Chat with agent | Optional |
| POST | `/chat/stream` | Streaming chat | Optional |
| POST | `/api/session` | Create session | No |
| GET | `/api/session/{id}` | Get session | No |

## Base URLs
```
Local:  http://localhost:8000
Prod:   https://api.4sgm.com
```

## Quick Start Commands

### Health Check
```bash
curl http://localhost:8000/health
```

### List Tools
```bash
curl http://localhost:8000/tools
```

### Create Session
```bash
curl -X POST http://localhost:8000/api/session
```

### Chat Request
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What products do you have?",
    "session_id": "SESSION_ID"
  }'
```

## MCP Tools (25 Total)

### Product (6)
| Tool | Purpose |
|------|---------|
| `get_product` | Product details |
| `search_products` | Search catalog |
| `get_inventory` | Check stock |
| `update_inventory` | Modify stock |
| `get_pricing` | Get prices |
| `apply_discount` | Apply coupon |

### Cart (6)
| Tool | Purpose |
|------|---------|
| `create_cart` | New cart |
| `add_to_cart` | Add item |
| `remove_from_cart` | Remove item |
| `calculate_cart_total` | Calculate total |
| `validate_cart` | Validate cart |
| `create_order` | Finalize order |

### Shipping (4)
| Tool | Purpose |
|------|---------|
| `calculate_shipping` | Shipping cost |
| `get_shipping_methods` | Available methods |
| `track_shipment` | Track order |
| `estimate_delivery` | Delivery date |

### Pricing (4)
| Tool | Purpose |
|------|---------|
| `get_bulk_pricing` | Bulk prices |
| `apply_coupon` | Apply code |
| `get_promotions` | Active promos |
| `calculate_savings` | Savings calc |

### Customer (3)
| Tool | Purpose |
|------|---------|
| `get_customer_history` | Order history |
| `get_customer_preferences` | User prefs |
| `save_customer_preferences` | Update prefs |

### RFQ (3)
| Tool | Purpose |
|------|---------|
| `create_rfq` | New quote req |
| `get_rfq_status` | RFQ status |
| `accept_rfq` | Accept quote |

## Common Request Patterns

### Search Products
```json
{
  "text": "Find laptop products",
  "session_id": "uuid"
}
```

### Check Pricing
```json
{
  "text": "What is the bulk price for 100 units of PROD-001?",
  "session_id": "uuid"
}
```

### Place Order
```json
{
  "text": "Create order from cart CART-ID for user USER-ID shipping to ADDRESS",
  "session_id": "uuid"
}
```

### Track Shipment
```json
{
  "text": "Track my shipment TRK-ID",
  "session_id": "uuid"
}
```

## Response Structure

### Success (200)
```json
{
  "text": "Response from agent",
  "session_id": "uuid"
}
```

### Error (4xx/5xx)
```json
{
  "detail": "Error description"
}
```

## Status Codes

| Code | Meaning |
|------|---------|
| 200 | OK |
| 400 | Bad request |
| 401 | Unauthorized |
| 429 | Rate limited |
| 500 | Server error |
| 503 | Service unavailable |

## Rate Limits

- **10 requests/minute** per user
- Headers: `X-RateLimit-Limit`, `X-RateLimit-Remaining`

## Authentication

```bash
curl -H "Authorization: Bearer TOKEN" \
  https://api.4sgm.com/endpoint
```

## Bulk Discounts

| Qty | Discount |
|-----|----------|
| 1-19 | 0% |
| 20-99 | 5% |
| 100-499 | 10% |
| 500-999 | 15% |
| 1000+ | 20% |

## Active Promotions

| Code | Discount |
|------|----------|
| SAVE10 | 10% off |
| SAVE20 | 20% off |
| BULK15 | 15% off |

## Shipping Options

| Method | Days | Cost |
|--------|------|------|
| Standard | 5 | $50 |
| Express | 2 | $75 |
| Overnight | 1 | $150 |

## Example: Complete Checkout Flow

```bash
# 1. Create session
SESSION=$(curl -s -X POST http://localhost:8000/api/session | jq -r '.sessionId')

# 2. Create cart
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": \"Create cart for USER-001\",
    \"session_id\": \"$SESSION\"
  }"

# 3. Add item to cart (returns CART-ID)
# 4. Calculate total
# 5. Create order
```

## Example: Bulk Quote Flow

```bash
# 1. Create RFQ
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Create RFQ for 1000 units of PROD-001 for Acme Corp",
    "session_id": "SESSION_ID"
  }'

# 2. Check status
# 3. Accept RFQ
```

## Python Client Snippet

```python
import requests
import uuid

BASE = "http://localhost:8000"
sid = str(uuid.uuid4())

# Create session
r = requests.post(f"{BASE}/api/session")
sid = r.json()["sessionId"]

# Send message
r = requests.post(f"{BASE}/chat", json={
  "text": "Find PROD-001",
  "session_id": sid
})
print(r.json()["text"])
```

## JavaScript Client Snippet

```javascript
const BASE = "http://localhost:8000";
let sessionId;

// Create session
const s = await fetch(`${BASE}/api/session`, {method: "POST"});
const {sessionId} = await s.json();

// Send message
const r = await fetch(`${BASE}/chat`, {
  method: "POST",
  headers: {"Content-Type": "application/json"},
  body: JSON.stringify({
    text: "Find PROD-001",
    session_id: sessionId
  })
});
const {text} = await r.json();
console.log(text);
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| 503 error | Start MCP: `python -m mcp_server.server` |
| Rate limited | Wait 60 seconds or create new session |
| Invalid session | Create new session |
| Slow response | Use `/chat/stream` endpoint |
| Auth error | Check JWT token validity |

## Documentation Files

- **mcp-tools-reference.md** - Complete tool documentation
- **openapi.yaml** - OpenAPI 3.0 specification
- **api-usage-guide.md** - Full usage guide with examples
- **README.md** - Overview and guide navigation

## Links

- Docs: https://4sgm.com/docs
- GitHub: https://github.com/4sgm/api
- Issues: https://github.com/4sgm/api/issues
- Support: support@4sgm.com

## Key Numbers

- **Total Endpoints**: 6
- **Total Tools**: 25
- **Rate Limit**: 10 req/min
- **Response Time**: <2s avg
- **Uptime SLA**: 99.9%

## Version

API v1.0.0 | Docs Updated: Jan 15, 2025
