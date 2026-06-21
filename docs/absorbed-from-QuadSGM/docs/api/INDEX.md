# 4SGM API Documentation Index

**Total Documentation**: 2,888 lines across 5 files
**API Version**: 1.0.0
**Last Updated**: January 15, 2025

## Navigation Guide

### For First-Time Users
Start here if you're new to the 4SGM API:
1. Read [README.md](./README.md) - Overview and introduction
2. Review [QUICK-REFERENCE.md](./QUICK-REFERENCE.md) - Quick lookup
3. Follow [api-usage-guide.md](./api-usage-guide.md) - Step-by-step examples

### For Developers
Reference these documents during implementation:
- [openapi.yaml](./openapi.yaml) - OpenAPI 3.0 specification
- [mcp-tools-reference.md](./mcp-tools-reference.md) - Tool details
- [api-usage-guide.md](./api-usage-guide.md) - Integration examples

### For Operations/Support
Reference these for troubleshooting:
- [QUICK-REFERENCE.md](./QUICK-REFERENCE.md) - Status codes and common issues
- [README.md](./README.md) - Support channels and resources

## Document Overview

### 1. README.md (286 lines)
**Purpose**: Navigation hub and overview

**Sections**:
- Overview and document guide
- Quick reference for all 25 tools
- Base URLs and authentication
- Rate limiting information
- Getting started steps
- Integration examples
- Key features and statistics
- Support resources

**Best for**: Understanding the API landscape, finding resources

### 2. QUICK-REFERENCE.md (245 lines)
**Purpose**: Developer quick lookup

**Sections**:
- Endpoints overview (table)
- Quick start commands
- All tools organized by category
- Common request patterns
- Response structure
- Status codes
- Bulk discounts and promotions
- Shipping options
- Code snippets (Python, JavaScript)
- Troubleshooting table

**Best for**: Fast lookups during development, command reference

### 3. openapi.yaml (393 lines)
**Purpose**: Machine-readable API specification

**Sections**:
- OpenAPI 3.0 metadata
- 6 REST endpoint definitions
- Request/response schemas
- Security schemes
- Data models (Product, Order, Cart, etc.)
- Error definitions

**Best for**: Code generation, testing frameworks, API documentation tools

### 4. mcp-tools-reference.md (1,179 lines)
**Purpose**: Complete tool documentation

**Structure** (25 tools documented):
- Product Tools (6): Lines 16-180
- Cart Tools (6): Lines 181-345
- Shipping Tools (4): Lines 346-487
- Pricing Tools (4): Lines 488-657
- Customer Tools (3): Lines 658-747
- RFQ Tools (3): Lines 748-833

**Each tool includes**:
- Description
- Parameters (with types)
- Returns (JSON schema)
- Example usage
- Response example

**Best for**: Understanding tool functionality, parameter specs, examples

### 5. api-usage-guide.md (655 lines)
**Purpose**: Practical integration guide

**Sections**:
- Quick start (health check)
- Authentication setup
- 8 workflow examples with curl commands
- Client integration examples (Python, TypeScript, cURL)
- Session management
- Streaming responses
- Error handling and recovery
- Rate limiting details
- Best practices
- Testing procedures
- Troubleshooting guide

**Best for**: Learning by example, troubleshooting, implementation

## Tool Categorization

### By Count
- **25 Total MCP Tools** across 6 categories
- **6 REST API Endpoints**
- **3 Workflow Categories** (Product, Order, Support)

### By Category

#### Product Management (6 tools)
```
get_product → search_products
get_inventory ↔ update_inventory
get_pricing → apply_discount
```

#### Shopping (6 tools)
```
create_cart → add_to_cart → remove_from_cart
           ↓
      validate_cart → calculate_cart_total
           ↓
      create_order
```

#### Fulfillment (4 tools)
```
calculate_shipping → get_shipping_methods
        ↓
estimate_delivery → track_shipment
```

#### Pricing (4 tools)
```
get_bulk_pricing
apply_coupon → get_promotions
calculate_savings
```

#### Customer (3 tools)
```
get_customer_history
get_customer_preferences ↔ save_customer_preferences
```

#### RFQ (3 tools)
```
create_rfq → get_rfq_status → accept_rfq
```

## Common Workflows

### Product Search Workflow
1. `search_products` - Find matching items
2. `get_product` - Get full details
3. `get_inventory` - Check availability
4. `get_pricing` - Check pricing

### Order Placement Workflow
1. `create_cart` - Start cart
2. `add_to_cart` - Add items
3. `validate_cart` - Check validity
4. `calculate_cart_total` - Get final price
5. `create_order` - Place order

### Bulk Quote Workflow
1. `create_rfq` - Request quote
2. `get_rfq_status` - Check status
3. `accept_rfq` - Convert to order

### Shipping Workflow
1. `calculate_shipping` - Get costs
2. `get_shipping_methods` - See options
3. `estimate_delivery` - Get date
4. `track_shipment` - Monitor progress

## Response Formats

### Standard Success Response
```json
{
  "text": "Agent response",
  "session_id": "uuid"
}
```

### Tool-Specific Responses
Each tool returns its own schema (documented in mcp-tools-reference.md)

### Error Response
```json
{
  "detail": "Error description"
}
```

## Quick Command Reference

```bash
# Health check
curl http://localhost:8000/health

# List tools
curl http://localhost:8000/tools

# Create session
curl -X POST http://localhost:8000/api/session

# Send chat
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "...", "session_id": "..."}'

# Stream chat
curl -X POST http://localhost:8000/chat/stream \
  -H "Content-Type: application/json" \
  -d '{"text": "...", "session_id": "..."}'
```

## Key Statistics

| Metric | Value |
|--------|-------|
| Total Documentation | 2,888 lines |
| REST Endpoints | 6 |
| MCP Tools | 25 |
| Tool Categories | 6 |
| Response Format | JSON |
| Rate Limit | 10 req/min |
| Auth Method | JWT Bearer |
| Uptime SLA | 99.9% |

## Performance Metrics

| Operation | Target Time |
|-----------|------------|
| Health check | <100ms |
| Search | <1s |
| Pricing calculation | <500ms |
| Order creation | <2s |
| Shipping estimate | <1s |

## Support Matrix

| Question | Document |
|----------|----------|
| How do I start? | README.md |
| How do I do X? | api-usage-guide.md |
| What does tool Y do? | mcp-tools-reference.md |
| What's the endpoint? | openapi.yaml |
| Need quick lookup? | QUICK-REFERENCE.md |
| Where's everything? | INDEX.md (you are here) |

## External Resources

### Tools & Services
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **Postman**: Import openapi.yaml

### Code Generation
- OpenAPI Generator: https://openapi-generator.tech/
- Swagger Codegen: https://swagger.io/tools/swagger-codegen/

### Testing
- Postman: https://www.postman.com/
- Insomnia: https://insomnia.rest/
- curl: https://curl.se/

## Document Relationships

```
README.md (Start here)
    ↓
QUICK-REFERENCE.md (Quick lookup)
    ↓
api-usage-guide.md (Examples)
    ↓
mcp-tools-reference.md (Details)
    ↓
openapi.yaml (Specification)
    ↓
INDEX.md (Navigation)
```

## Version Information

- **API Version**: 1.0.0
- **Documentation Version**: 1.0.0
- **OpenAPI Spec Version**: 3.0.0
- **Last Updated**: January 15, 2025

## Updates & Changes

### What's New in v1.0.0
- Complete API documentation
- 25 MCP tools documented
- 8 workflow examples
- Client code samples
- OpenAPI specification

### Planned Updates
- More code examples (Go, Ruby)
- Postman collection
- Video tutorials
- Webhook documentation

## Contact & Support

- **Documentation Issues**: GitHub Issues
- **API Support**: support@4sgm.com
- **Feature Requests**: Feature discussion
- **Bugs**: Bug report form

## Document Stats

| File | Lines | Size | Purpose |
|------|-------|------|---------|
| README.md | 286 | 8.3K | Overview |
| QUICK-REFERENCE.md | 245 | 6.0K | Lookup |
| openapi.yaml | 393 | 9.9K | Spec |
| mcp-tools-reference.md | 1,179 | 20K | Details |
| api-usage-guide.md | 655 | 13K | Guide |
| **TOTAL** | **2,888** | **57K** | Complete |

---

**Last Updated**: January 15, 2025
**Created by**: Agent 2 (API Documentation & OpenAPI)
**Status**: Complete and Ready for Use
