# 4SGM API Usage Guide

Comprehensive guide for integrating with the 4SGM Wholesale Chatbot API.

## Quick Start

### Base URL
```
Production: https://api.4sgm.com
Development: http://localhost:8000
```

### Health Check
```bash
curl http://localhost:8000/health
```

Response:
```json
{
  "status": "ok",
  "mcp": true,
  "tools": 25
}
```

## Authentication

The 4SGM API uses bearer token authentication via JWT. Include the token in the Authorization header:

```bash
curl -H "Authorization: Bearer YOUR_JWT_TOKEN" \
  http://localhost:8000/chat
```

## Core Workflows

### 1. Product Search & Details

**Find products matching a search query:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Find me laptop products under $1000",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

The agent will use `search_products` tool to find matching items.

**Get detailed product information:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Show me details for product PROD-001",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

The agent will use `get_product` tool to retrieve full details.

---

### 2. Inventory Management

**Check stock availability:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "How many units of PROD-001 do we have in stock?",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

The agent will:
1. Call `get_inventory` to check current stock
2. Return availability and warehouse locations

**Update inventory:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Add 50 units of PROD-001 to inventory",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

The agent will call `update_inventory` and return confirmation.

---

### 3. Shopping Cart & Checkout

**Create a new cart:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Create a new cart for user USER-001",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

Response will include cart ID: `CART-A1B2C3D4`

**Add items to cart:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Add 5 units of PROD-001 to cart CART-A1B2C3D4",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Get cart total:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Calculate total for cart CART-A1B2C3D4 with items",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Create order from cart:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Create order from cart CART-A1B2C3D4 for user USER-001 shipping to 123 Main St, New York, NY 10001",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

Response will include:
- Order ID: `ORD-X1Y2Z3W4`
- Tracking number: `TRK-A1B2C3D4`

---

### 4. Bulk Pricing

**Get bulk pricing quotes:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What is the bulk price for 100 units of PROD-001?",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

Response:
```json
{
  "text": "For 100 units of PROD-001: Unit Price: $89.99 (10% bulk discount), Total: $8,999.00, Savings: $999.90",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Get pricing at different quantities:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Compare pricing for 50, 100, 500, and 1000 units of PROD-001",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

The agent will call `get_bulk_pricing` for each quantity and compare.

---

### 5. Promotions & Discounts

**Check available promotions:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What promotions are currently available?",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

Response lists all active promotional codes:
- SAVE10: 10% off
- SAVE20: 20% off orders over $500
- BULK15: 15% off bulk orders

**Apply coupon code:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Apply coupon SAVE10 to order total of 589.95",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

Response:
```json
{
  "text": "Coupon SAVE10 applied successfully: 10% discount = $58.99 savings. New total: $530.96",
  "session_id": "550e8400-e29b-41d4-a716-446655440000"
}
```

**Calculate savings:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Show me savings if I apply 20% discount to 5000 dollar order",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

---

### 6. Shipping & Delivery

**Calculate shipping costs:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Calculate shipping from CA to NY for 10.5 pound package",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

Response includes available carriers:
- Standard: 5 days
- Express: 2 days

**Get shipping methods:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What shipping methods are available?",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Estimate delivery:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "When will my order arrive if shipped standard to NY?",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Track shipment:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Track my shipment TRK-A1B2C3D4",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

---

### 7. Customer Management

**Get customer history:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Show me order history for user USER-001",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

Response shows:
- Total orders
- Total spent
- Recent order details

**Get customer preferences:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What are USER-001 preferences?",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Save customer preferences:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Set USER-001 preferred shipping to express and enable newsletter",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

---

### 8. Request for Quote (RFQ)

**Create RFQ:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Create RFQ for 1000 units of PROD-001 and PROD-002 for Acme Corp",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

Response includes:
- RFQ ID: `RFQ-X1Y2Z3W4`
- Valid until: 30 days from creation

**Check RFQ status:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What is the status of RFQ RFQ-X1Y2Z3W4?",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

**Accept RFQ:**

```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Accept RFQ RFQ-X1Y2Z3W4",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

Response includes generated order ID.

---

## Session Management

### Create Session

```bash
curl -X POST http://localhost:8000/api/session
```

Response:
```json
{
  "sessionId": "550e8400-e29b-41d4-a716-446655440000",
  "createdAt": "2025-01-15T10:30:00Z",
  "messages": []
}
```

### Get Session

```bash
curl http://localhost:8000/api/session/550e8400-e29b-41d4-a716-446655440000
```

---

## Streaming Responses

For long-running operations, use the streaming endpoint:

```bash
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{
    "text": "Process bulk order for 1000 units",
    "session_id": "550e8400-e29b-41d4-a716-446655440000"
  }'
```

The response will be Server-Sent Events (SSE) format:
```
data: {"event": "processing", "message": "Calculating pricing..."}

data: {"event": "result", "message": "Order total: $89,990.00"}
```

---

## Error Handling

### Common Error Responses

**503 - Service Unavailable (MCP not connected)**
```json
{
  "detail": "Tools not loaded - start MCP server with: 4sgm mcp"
}
```

**500 - Internal Server Error**
```json
{
  "detail": "Chat error: [error details]"
}
```

**400 - Bad Request**
```json
{
  "detail": "Invalid request format"
}
```

### Error Recovery

1. Check MCP server status: `curl http://localhost:8000/health`
2. If tools unavailable, start MCP: `python -m mcp_server.server`
3. Retry request after 5 seconds

---

## Client Integration Examples

### Python

```python
import requests
import uuid

BASE_URL = "http://localhost:8000"
SESSION_ID = str(uuid.uuid4())

# Create session
session_response = requests.post(f"{BASE_URL}/api/session")
SESSION_ID = session_response.json()["sessionId"]

# Send chat message
response = requests.post(
    f"{BASE_URL}/chat",
    json={
        "text": "What is the bulk price for 100 units of PROD-001?",
        "session_id": SESSION_ID
    }
)

print(response.json()["text"])
```

### JavaScript/TypeScript

```typescript
const BASE_URL = "http://localhost:8000";
let sessionId: string;

// Create session
const sessionResponse = await fetch(`${BASE_URL}/api/session`, {
  method: "POST"
});
const session = await sessionResponse.json();
sessionId = session.sessionId;

// Send chat message
const response = await fetch(`${BASE_URL}/chat`, {
  method: "POST",
  headers: { "Content-Type": "application/json" },
  body: JSON.stringify({
    text: "What is the bulk price for 100 units of PROD-001?",
    session_id: sessionId
  })
});

const result = await response.json();
console.log(result.text);
```

### cURL

```bash
# Create session
SESSION=$(curl -X POST http://localhost:8000/api/session | jq -r '.sessionId')

# Send message
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d "{
    \"text\": \"What is the bulk price for 100 units of PROD-001?\",
    \"session_id\": \"$SESSION\"
  }"
```

---

## Rate Limiting

The API implements rate limiting of **10 requests per minute per user**.

Rate limit headers:
```
X-RateLimit-Limit: 10
X-RateLimit-Remaining: 9
X-RateLimit-Reset: 1705308600
```

When rate limit exceeded (429 Too Many Requests):
```json
{
  "detail": "Rate limit exceeded. Try again in 60 seconds."
}
```

---

## Best Practices

### 1. Session Management
- Reuse session IDs for related requests
- Include session_id in all chat requests
- Create new session for each user/conversation

### 2. Error Handling
- Check health endpoint before making requests
- Implement exponential backoff for retries
- Log error responses for debugging

### 3. Performance
- Use streaming endpoint for long operations
- Batch related requests when possible
- Cache product data where appropriate

### 4. Security
- Always use HTTPS in production
- Store JWT tokens securely
- Never expose tokens in logs
- Validate all user input

### 5. Monitoring
- Track response times
- Monitor error rates
- Log all API interactions
- Set up alerts for service degradation

---

## Testing

### Health Check
```bash
curl http://localhost:8000/health
```

### List Available Tools
```bash
curl http://localhost:8000/tools
```

### Test Chat
```bash
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{
    "text": "What products do you have?",
    "session_id": "test-session"
  }'
```

---

## Troubleshooting

### MCP Server Not Connected

**Problem**: Tools endpoint returns 503
```json
{"detail": "Tools not loaded"}
```

**Solution**:
1. Start MCP server: `python -m mcp_server.server`
2. Wait 2-3 seconds for connection
3. Retry request

### Slow Response Times

**Problem**: Requests take >5 seconds

**Causes**:
- MCP server overloaded
- Database query slow
- LLM model inference slow

**Solutions**:
- Check server logs: `docker logs 4sgm-mcp`
- Monitor resource usage
- Use streaming endpoint for long operations

### Invalid Session

**Problem**: Session ID not recognized

**Solution**:
- Create new session: `POST /api/session`
- Use returned sessionId in requests

---

## API Versions

Current version: **1.0.0**

### Version History
- **1.0.0** (2025-01-15): Initial release with 25 MCP tools

---

## Support

For issues or questions:
- Documentation: https://4sgm.com/docs
- Issues: https://github.com/4sgm/api/issues
- Email: support@4sgm.com
