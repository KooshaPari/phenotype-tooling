# API Design Best Practices Reference

## 1. REST API Design

### 1.1 Resource Naming

| Pattern | Example |
|---------|---------|
| Collections | `/users`, `/orders` |
| Single resource | `/users/123` |
| Nested | `/users/123/orders` |
| Filtering | `/products?category=electronics` |
| Sorting | `/users?sort=created_at desc` |

### 1.2 HTTP Methods

| Method | Idempotent | Usage |
|--------|------------|-------|
| GET | Yes | Retrieve resources |
| POST | No | Create new resource |
| PUT | Yes | Replace resource |
| PATCH | No | Partial update |
| DELETE | Yes | Remove resource |

### 1.3 Status Codes

```python
# Success
200 OK, 201 Created, 204 No Content

# Client Errors
400 Bad Request, 401 Unauthorized, 403 Forbidden
404 Not Found, 409 Conflict, 422 Unprocessable Entity
429 Too Many Requests

# Server Errors
500 Internal Error, 502 Bad Gateway, 503 Unavailable
```

### 1.4 Response Envelope

```python
# Success response
{
    "data": {"id": "usr_123", "email": "user@example.com"},
    "meta": {"request_id": "req_abc", "timestamp": "2026-02-15T10:00:00Z"}
}

# Error response
{
    "error": {
        "code": "VALIDATION_ERROR",
        "message": "Invalid input",
        "details": [{"field": "email", "message": "Invalid format"}]
    }
}
```

### 1.5 Pagination

```python
# Cursor-based (recommended)
GET /users?limit=20&cursor=eyJpZCI6MTAwfQ

# Response
{
    "data": [...],
    "pagination": {
        "next_cursor": "eyJpZCI6MTIwfQ",
        "has_more": true,
        "total_count": 150
    }
}
```

---

## 2. GraphQL API Design

### 2.1 Schema Structure

```graphql
type User {
  id: ID!
  email: String!
  orders: [Order!]!  # Resolver-based (lazy)
}

type Query {
  user(id: ID!): User
  users(filter: UserFilter, limit: Int): UserConnection!
}

type Mutation {
  createUser(input: CreateUserInput!): CreateUserPayload!
}
```

### 2.2 N+1 Prevention

```python
# Use DataLoader for batching
class UserOrdersLoader:
    async def batch_load_fn(self, user_ids: List[str]) -> Dict[str, List[Order]]:
        orders = await self.order_service.get_by_user_ids(user_ids)
        return {uid: [o for o in orders if o.user_id == uid] for uid in user_ids}
```

---

## 3. gRPC API Design

### 3.1 Proto3 Service

```protobuf
service UserService {
  rpc GetUser(GetUserRequest) returns (User);
  rpc ListUsers(ListUsersRequest) returns (stream User);
  rpc StreamUserEvents(stream UserEvent) returns (stream UserEvent);
}
```

### 3.2 Message Definition

```protobuf
message User {
  string id = 1;
  string email = 2 [(google.api.field_behavior) = REQUIRED];
  UserStatus status = 3;
  google.protobuf.Timestamp created_at = 4;
}

enum UserStatus {
  USER_STATUS_UNSPECIFIED = 0;
  USER_STATUS_ACTIVE = 1;
}
```

---

## 4. Webhook Design

### 4.1 Security

```python
import hmac, hashlib

def verify_signature(payload: bytes, signature: str, secret: str) -> bool:
    expected = f"sha256={hmac.new(secret.encode(), payload, hashlib.sha256).hexdigest()}"
    return hmac.compare_digest(expected, signature)
```

### 4.2 Retry Strategy

```python
# Exponential backoff
async def deliver_with_retry(endpoint: str, payload: dict, max_retries: int = 5):
    delay = 1.0
    for attempt in range(max_retries):
        try:
            async with httpx.AsyncClient() as client:
                r = await client.post(endpoint, json=payload)
                if r.status_code < 400:
                    return True
        except Exception:
            pass
        await asyncio.sleep(delay)
        delay = min(delay * 2, 60)  # Max 60s
    return False
```

---

## 5. API Versioning

| Strategy | Pros | Cons |
|----------|------|------|
| URL Path (`/v1/`) | Explicit, cacheable | URL pollution |
| Header | Clean URLs | Less discoverable |
| Query Param | Simple | Caching issues |

**Recommended:** URL path versioning

---

## 6. Rate Limiting

### 6.1 Headers

```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
Retry-After: 60
```

### 6.2 Algorithm

```python
# Token bucket algorithm
class TokenBucket:
    def __init__(self, capacity: int, refill_rate: float):
        self.capacity = capacity
        self.tokens = capacity
        self.refill_rate = refill_rate

    def consume(self, tokens: int = 1) -> bool:
        self._refill()
        if self.tokens >= tokens:
            self.tokens -= tokens
            return True
        return False
```

---

## 7. OpenAPI/Swagger

```yaml
openapi: 3.1.0
info:
  title: User API
  version: 1.0.0
paths:
  /users:
    get:
      summary: List users
      responses:
        '200':
          content:
            application/json:
              schema:
                type: array
                items:
                  $ref: '#/components/schemas/User'
```

---

## Quick Reference

| Need | Use | NOT |
|------|-----|-----|
| REST | FastAPI, Flask | Raw socket HTTP |
| GraphQL | strawberry-graphql, ariadne | Manual schema |
| gRPC | grpcio, protobuf | JSON over HTTP |
| Validation | pydantic | Manual if/else |
| Rate limiting | slowapi | Custom class |
| Docs | OpenAPI/swagger-ui | Custom docs |

---

*For detailed examples and patterns, see full API design research document.*
