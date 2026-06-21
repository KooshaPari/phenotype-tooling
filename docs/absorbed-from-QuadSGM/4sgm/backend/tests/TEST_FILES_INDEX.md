# Test Files Index - 4SGM Backend Unit Tests

## Directory Structure

```
backend/tests/
├── __init__.py
├── conftest.py                          # Pytest configuration and shared fixtures
├── TEST_FILES_INDEX.md                  # This file
├── unit/
│   ├── __init__.py
│   ├── test_models.py                   # SQLAlchemy model tests (355 lines, 19 tests)
│   ├── test_database.py                 # Database configuration tests (185 lines, 14 tests)
│   ├── test_exceptions.py               # Exception handling tests (375 lines, 21 tests)
│   ├── test_repositories/
│   │   ├── __init__.py
│   │   └── test_base_repo.py            # Repository interface tests (345 lines, 23 tests)
│   └── test_mcp_tools/
│       ├── __init__.py
│       ├── test_product_tools.py        # Product MCP tools (240 lines, 20 tests)
│       ├── test_cart_tools.py           # Cart MCP tools (290 lines, 20 tests)
│       ├── test_shipping_tools.py       # Shipping MCP tools (255 lines, 18 tests)
│       ├── test_pricing_tools.py        # Pricing MCP tools (260 lines, 20 tests)
│       ├── test_customer_tools.py       # Customer MCP tools (310 lines, 23 tests)
│       ├── test_rfq_tools.py            # RFQ MCP tools (380 lines, 23 tests)
│       └── test_order_tools.py          # Order MCP tools (320 lines, 24 tests)
```

## Test Files Summary

### Core Testing Infrastructure

#### `/tests/conftest.py` (310 lines)
**Purpose**: Pytest configuration and shared test fixtures

**Fixtures Provided**:
- `test_database_url`: SQLite in-memory database URL
- `engine`: SQLAlchemy engine with auto-created tables
- `db_session`: Transactional test session with rollback
- `test_db`: Async database session
- `async_client`: HTTP client for API testing
- `event_loop`: Async event loop for async tests
- `mock_product_repo`: Mock product repository
- `mock_chat_session_repo`: Mock chat session repository
- `mock_document_repo`: Mock document repository
- `mock_user_auth`: Mock authentication data
- `mock_jwt_token`: Mock JWT token
- `auth_headers`: Authorization headers
- `mock_llm_service`: Mock LLM service
- `mock_vector_db`: Mock vector database
- `mock_cache`: Mock cache service

#### `/tests/__init__.py`
**Purpose**: Package initialization

### Unit Tests

#### `/tests/unit/test_models.py` (355 lines, 19 tests)
**Purpose**: Test SQLAlchemy ORM models

**Test Classes**:
- `TestProductModel` (7 tests): Product model CRUD and validation
- `TestChatSessionModel` (5 tests): Chat session model operations
- `TestDocumentModel` (7 tests): Document model with embeddings

**Coverage**:
- Table creation and indexes
- Column constraints (unique, not null)
- Default values
- JSON data persistence
- String representations
- Metadata handling

#### `/tests/unit/test_database.py` (185 lines, 14 tests)
**Purpose**: Test database configuration and connectivity

**Test Classes**:
- `TestDatabaseConfiguration` (3 tests): Session lifecycle
- `TestDatabaseURL` (3 tests): URL configuration
- `TestDatabaseEngine` (3 tests): Engine setup
- `TestSessionLocal` (3 tests): Session factory
- `TestDatabaseConnectivity` (2 tests): Connection establishment

**Coverage**:
- Database URL from environment
- Session creation and cleanup
- Engine pooling (NullPool for serverless)
- Query execution
- Table initialization

#### `/tests/unit/test_exceptions.py` (375 lines, 21 tests)
**Purpose**: Test error handling and exception scenarios

**Test Classes**:
- `TestDatabaseExceptions` (4 tests): Database-level errors
- `TestMockServiceExceptions` (4 tests): Mock service errors
- `TestErrorMessages` (4 tests): Error message formatting
- `TestErrorHandlingPatterns` (4 tests): Common patterns
- `TestExceptionEdgeCases` (5 tests): Edge cases

**Coverage**:
- Integrity constraints
- Session cleanup
- Error messages
- Exception chaining
- Try-except-finally patterns
- Context managers

#### `/tests/unit/test_repositories/test_base_repo.py` (345 lines, 23 tests)
**Purpose**: Test repository interface and implementations

**Test Classes**:
- `TestRepositoryInterface` (2 tests): Interface contracts
- `TestProductRepository` (8 tests): Product CRUD
- `TestChatSessionRepository` (5 tests): Session CRUD
- `TestDocumentRepository` (5 tests): Document CRUD
- `TestRepositoryErrorHandling` (3 tests): Error scenarios

**Coverage**:
- CRUD operations (Create, Read, Update, Delete)
- Search functionality
- List with pagination
- Error handling
- Mock verification

### MCP Tools Tests

#### `/tests/unit/test_mcp_tools/test_product_tools.py` (240 lines, 20 tests)
**Purpose**: Test product-related MCP tools

**Tool Classes Tested**:
- `TestGetProductTool` (4 tests): Retrieve product by ID
- `TestSearchProductsTool` (5 tests): Search products by query
- `TestGetInventoryTool` (4 tests): Get inventory levels
- `TestListCategoriesTool` (3 tests): List product categories
- `TestProductToolErrors` (4 tests): Error handling

#### `/tests/unit/test_mcp_tools/test_cart_tools.py` (290 lines, 20 tests)
**Purpose**: Test shopping cart MCP tools

**Tool Classes Tested**:
- `TestCreateCartTool` (3 tests): Create new cart
- `TestAddToCartTool` (5 tests): Add items to cart
- `TestGetCartTool` (2 tests): Retrieve cart
- `TestRemoveFromCartTool` (3 tests): Remove items
- `TestClearCartTool` (2 tests): Clear entire cart
- `TestCartToolErrors` (5 tests): Error scenarios

#### `/tests/unit/test_mcp_tools/test_shipping_tools.py` (255 lines, 18 tests)
**Purpose**: Test shipping-related MCP tools

**Tool Classes Tested**:
- `TestCalculateShippingTool` (5 tests): Calculate shipping costs
- `TestGetShippingMethodsTool` (2 tests): List shipping methods
- `TestEstimateDeliveryTool` (4 tests): Estimate delivery dates
- `TestTrackingTool` (3 tests): Track shipments
- `TestShippingToolErrors` (4 tests): Error handling

#### `/tests/unit/test_mcp_tools/test_pricing_tools.py` (260 lines, 20 tests)
**Purpose**: Test pricing and discount MCP tools

**Tool Classes Tested**:
- `TestGetPricingTool` (5 tests): Get product pricing
- `TestApplyDiscountTool` (5 tests): Apply discount codes
- `TestGetPromotionsTool` (3 tests): List active promotions
- `TestBulkPricingTool` (2 tests): Bulk order pricing
- `TestPricingToolErrors` (5 tests): Error handling

#### `/tests/unit/test_mcp_tools/test_customer_tools.py` (310 lines, 23 tests)
**Purpose**: Test customer management MCP tools

**Tool Classes Tested**:
- `TestGetCustomerTool` (3 tests): Retrieve customer
- `TestSearchCustomersTool` (4 tests): Search customers
- `TestCreateCustomerTool` (3 tests): Create customer
- `TestUpdateCustomerTool` (3 tests): Update customer
- `TestGetCustomerOrdersTool` (3 tests): Get customer orders
- `TestGetCustomerCreditTool` (2 tests): Get credit info
- `TestApplyCreditTool` (2 tests): Apply customer credit
- `TestCustomerToolErrors` (3 tests): Error handling

#### `/tests/unit/test_mcp_tools/test_rfq_tools.py` (380 lines, 23 tests)
**Purpose**: Test RFQ (Request for Quote) MCP tools

**Tool Classes Tested**:
- `TestCreateRFQTool` (3 tests): Create RFQ
- `TestGetRFQTool` (3 tests): Retrieve RFQ
- `TestUpdateRFQTool` (3 tests): Update RFQ
- `TestSearchRFQTool` (3 tests): Search RFQs
- `TestQuoteRFQTool` (3 tests): Generate quote
- `TestAcceptRFQTool` (2 tests): Accept quote
- `TestRejectRFQTool` (2 tests): Reject quote
- `TestRFQToolErrors` (4 tests): Error handling

#### `/tests/unit/test_mcp_tools/test_order_tools.py` (320 lines, 24 tests)
**Purpose**: Test order management MCP tools

**Tool Classes Tested**:
- `TestCreateOrderTool` (4 tests): Create order
- `TestGetOrderTool` (3 tests): Retrieve order
- `TestUpdateOrderTool` (3 tests): Update order
- `TestListOrdersTool` (3 tests): List orders
- `TestCancelOrderTool` (3 tests): Cancel order
- `TestReturnOrderTool` (3 tests): Return order
- `TestOrderToolErrors` (6 tests): Error handling

## Running Tests

### Run All Tests
```bash
cd backend && python -m pytest tests/ -v
```

### Run Specific Category
```bash
# Run model tests
python -m pytest tests/unit/test_models.py -v

# Run database tests
python -m pytest tests/unit/test_database.py -v

# Run all MCP tool tests
python -m pytest tests/unit/test_mcp_tools/ -v

# Run specific MCP tool tests
python -m pytest tests/unit/test_mcp_tools/test_product_tools.py -v
```

### Run With Coverage Report
```bash
python -m pytest tests/ --cov=backend --cov-report=html
```

### Run Specific Test Class
```bash
python -m pytest tests/unit/test_models.py::TestProductModel -v
```

### Run Specific Test Method
```bash
python -m pytest tests/unit/test_models.py::TestProductModel::test_product_creation -v
```

### Run Tests Matching Pattern
```bash
python -m pytest tests/ -k "test_product" -v
```

## Test Statistics

| Component | Files | Tests | Lines |
|-----------|-------|-------|-------|
| Configuration | 1 | - | 310 |
| Models | 1 | 19 | 355 |
| Database | 1 | 14 | 185 |
| Exceptions | 1 | 21 | 375 |
| Repositories | 1 | 23 | 345 |
| Product Tools | 1 | 20 | 240 |
| Cart Tools | 1 | 20 | 290 |
| Shipping Tools | 1 | 18 | 255 |
| Pricing Tools | 1 | 20 | 260 |
| Customer Tools | 1 | 23 | 310 |
| RFQ Tools | 1 | 23 | 380 |
| Order Tools | 1 | 24 | 320 |
| **TOTAL** | **12** | **225** | **3,825** |

## Test Patterns

### Database Testing Pattern
```python
def test_feature(self, db_session: Session):
    # Create test data
    obj = Model(...)
    db_session.add(obj)
    db_session.commit()

    # Test operation
    result = db_session.query(Model).first()

    # Assert
    assert result is not None
```

### Mock Repository Pattern
```python
async def test_feature(self, mock_product_repo):
    mock_product_repo.get.return_value = test_data

    result = await mock_product_repo.get("id")

    assert result == test_data
    mock_product_repo.get.assert_called_once_with("id")
```

### Error Testing Pattern
```python
def test_error(self):
    with pytest.raises(ValueError, match="error message"):
        # Code that should raise
```

## Coverage Goals

- **Models**: 95%+ coverage
- **Database**: 90%+ coverage
- **Repositories**: 85%+ coverage
- **MCP Tools**: 80%+ coverage
- **Exception Handling**: 100% coverage
- **Overall**: 90%+ target

## Notes

1. All tests use in-memory SQLite for fast execution
2. Each test runs in a transaction that rolls back after completion
3. Fixtures provide automatic cleanup
4. Mock objects allow testing without external dependencies
5. Async tests use pytest-asyncio for proper event loop handling
6. Tests follow AAA (Arrange-Act-Assert) pattern
7. Comprehensive edge case and error scenario coverage

---

**Status**: ✅ COMPLETE
**Total Coverage**: 225 test methods across 12 files
**Expected Line Coverage**: >90%
