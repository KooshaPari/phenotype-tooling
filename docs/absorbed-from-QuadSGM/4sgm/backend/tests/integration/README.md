# Integration Tests - MCP Chain Workflows

This directory contains comprehensive integration tests for multi-tool MCP workflow chains in the 4SGM Wholesale Chatbot system.

## Overview

Integration tests validate complete workflows that span multiple MCP tools working together to accomplish real business scenarios. Each test simulates how the tools interact in production workflows.

## Test Suites

### 1. Product → Cart → Order Chain (`test_product_cart_order_chain.py`)

Tests the complete order workflow from product discovery to checkout.

**Workflows Tested:**
- Product search and retrieval
- Cart creation and item management
- Cart validation and total calculation
- Order creation and confirmation

**Test Cases:**
- `test_complete_order_workflow`: Full workflow with multiple products
- `test_cart_workflow_with_multiple_products`: Multiple items in cart
- `test_insufficient_inventory_in_workflow`: Inventory constraint handling
- `test_product_not_found_in_workflow`: Missing product error handling
- `test_remove_item_from_cart_workflow`: Item removal and total recalculation
- `test_cart_persistence_across_operations`: State persistence
- `test_order_creation_captures_cart_state`: Order snapshot of cart
- `test_sequential_cart_operations`: Add/remove sequences
- `test_bulk_order_workflow`: Large quantity orders

**Key Validations:**
- Products found in search are retrievable with get_product
- Inventory checks pass for available items
- Cart totals are calculated correctly
- Orders capture exact cart state
- Sequential operations maintain consistency

### 2. Shipping Calculation Chain (`test_shipping_chain.py`)

Tests shipping cost calculations and method selection.

**Workflows Tested:**
- Shipping cost calculation between locations
- Available shipping method retrieval
- Carrier option comparison
- Delivery time estimation
- Shipment tracking

**Test Cases:**
- `test_shipping_calculation_workflow`: Basic cost calculation
- `test_shipping_cost_scales_with_weight`: Weight-based pricing
- `test_shipping_methods_availability`: Method enumeration
- `test_complete_shipping_workflow`: Calculate → select → estimate
- `test_carrier_options_structure`: Option validation
- `test_shipping_dimension_impact`: Dimensional weight
- `test_delivery_estimate_consistency`: Estimate accuracy
- `test_tracking_shipment_workflow`: Tracking flow
- `test_multiple_shipping_locations`: Various location pairs
- `test_expedited_vs_standard_shipping`: Cost/time tradeoff
- `test_shipping_method_selection_strategy`: Different selection logic

**Key Validations:**
- Shipping costs > 0
- Weight impacts cost proportionally
- Multiple carriers available
- Faster options typically cost more
- Delivery estimates reasonable
- Cost consistency within location pairs

### 3. Pricing & Discount Chain (`test_pricing_discount_chain.py`)

Tests pricing tiers, bulk discounts, and coupon application.

**Workflows Tested:**
- Base product pricing
- Bulk quantity discounts
- Coupon code application
- Savings calculations
- Discount stacking

**Test Cases:**
- `test_bulk_pricing_workflow`: Tiered discount structure
- `test_coupon_application_workflow`: Coupon validation and application
- `test_invalid_coupon_handling`: Error handling for invalid codes
- `test_complete_pricing_workflow`: Full discount sequence
- `test_promotional_offers_retrieval`: Active promotions list
- `test_savings_calculation_accuracy`: Exact savings math
- `test_tiered_discount_structure`: Monotonic discount improvement
- `test_coupon_stacking_policy`: Multiple discount application
- `test_negative_discount_prevention`: Price floor validation
- `test_bulk_pricing_with_coupon_combination`: Stacking discounts
- `test_customer_specific_pricing`: VIP/loyalty pricing
- `test_price_consistency_across_quantities`: Unit price consistency

**Key Validations:**
- Discounts increase with quantity
- Coupons properly reduce totals
- Invalid coupons handled gracefully
- Prices never go negative
- Unit prices consistent
- Bulk discounts stack correctly

### 4. RFQ Creation & Acceptance Chain (`test_rfq_chain.py`)

Tests wholesale request for quote workflows.

**Workflows Tested:**
- RFQ creation with multiple items
- Quote status tracking
- RFQ acceptance and PO linkage
- Price guarantee

**Test Cases:**
- `test_create_rfq_workflow`: RFQ creation with items
- `test_rfq_pricing_calculation`: Quote calculation accuracy
- `test_rfq_status_tracking`: Status lifecycle
- `test_complete_rfq_workflow`: Create → review → accept
- `test_rfq_with_bulk_discount_expectation`: Bulk quote pricing
- `test_rfq_expiration_handling`: Quote expiration
- `test_rfq_rejection_workflow`: RFQ rejection
- `test_multiple_rfqs_for_same_customer`: Multiple quotes per customer
- `test_rfq_with_custom_notes`: Special handling notes
- `test_rfq_price_guarantee`: Price lock-in
- `test_rfq_item_availability_verification`: Stock verification
- `test_rfq_vs_regular_order_pricing`: Wholesale vs retail
- `test_rfq_acceptance_creates_order_reference`: PO linking
- `test_rfq_multi_item_status_tracking`: Multi-line tracking

**Key Validations:**
- RFQs created with all items
- Pricing calculated correctly
- Status transitions properly
- Price locked when accepted
- Item availability verified
- PO numbers tracked

### 5. Error Recovery & Data Consistency (`test_error_recovery_consistency.py`)

Tests system resilience and data integrity across failures.

**Workflows Tested:**
- Error handling for missing products
- Inventory constraint violations
- Cart state recovery after errors
- Price consistency across tools
- Transaction safety

**Test Cases:**
- `test_product_not_found_error_handling`: Missing product errors
- `test_search_empty_results_handling`: No results handling
- `test_cart_add_nonexistent_product_error`: Invalid item error
- `test_insufficient_inventory_error_recovery`: Stock constraint
- `test_cart_state_after_failed_add`: State recovery
- `test_order_creation_with_empty_cart`: Empty order prevention
- `test_price_consistency_get_vs_search`: Price agreement
- `test_inventory_consistency_after_failed_update`: Rollback
- `test_concurrent_cart_modifications_consistency`: Concurrent safety
- `test_invalid_quantity_handling`: Quantity validation
- `test_invalid_price_handling`: Price validation
- `test_order_total_validation`: Total verification
- `test_invalid_shipping_address_handling`: Address validation
- `test_pricing_consistency_bulk_vs_single`: Price consistency
- `test_coupon_validation_before_application`: Coupon validation
- `test_transaction_rollback_on_order_failure`: Transaction safety
- `test_duplicate_add_idempotency`: Idempotent operations
- `test_error_message_clarity`: Clear error messages

**Key Validations:**
- Errors handled gracefully
- Cart state consistent after failures
- Prices agree across tools
- Inventory stays valid
- No negative prices/quantities
- Transactions atomic
- Error messages clear

## Running Tests

### Run all integration tests:
```bash
pytest 4sgm/backend/tests/integration/ -v
```

### Run specific test file:
```bash
pytest 4sgm/backend/tests/integration/test_product_cart_order_chain.py -v
```

### Run specific test:
```bash
pytest 4sgm/backend/tests/integration/test_product_cart_order_chain.py::test_complete_order_workflow -v
```

### Run with coverage:
```bash
pytest 4sgm/backend/tests/integration/ --cov=backend --cov-report=html
```

## Test Structure

All tests follow a consistent pattern:

```python
@pytest.mark.asyncio
async def test_workflow_name(fixtures):
    """Test description."""

    # Step 1: Setup/Create
    # Step 2: Execute main workflow
    # Step 3: Validate results
    # Step 4: Verify consistency

    assert result is not None
```

## Integration Points

Tests verify data consistency at these critical junctures:

1. **Product Data**: Price, SKU, inventory match between search and get
2. **Cart State**: Items, totals persist across operations
3. **Inventory**: Updated correctly after cart operations
4. **Shipping**: Location-based cost scales properly
5. **Pricing**: Discounts stack without conflicts
6. **Orders**: Capture exact cart state and prices
7. **RFQs**: Quote prices locked when accepted

## Error Scenarios

Tests cover these error cases:

- Product not found (404)
- Insufficient inventory
- Invalid cart items
- Empty carts
- Invalid coupon codes
- Negative quantities/prices
- Invalid shipping addresses
- Missing required fields
- Concurrent modification safety

## Performance

Tests use mock repositories for fast execution:
- No database calls
- No network requests
- In-memory operations only
- Average test execution: <100ms

## Coverage Goals

- All workflows should have >90% line coverage
- Error paths should have 100% coverage
- Data consistency checks in every test
- At least 2-3 variants of each workflow
- Both success and failure cases
