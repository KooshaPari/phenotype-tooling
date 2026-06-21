# Extending the DeepAgent Architecture

This guide shows how to add new workflows, customize existing ones, and extend the system.

## Adding a New Workflow

### Step 1: Create the Workflow File

Create `subagents/new_workflow.py`:

```python
"""New domain workflow StateGraph subagent."""

import logging
from typing import TypedDict, Annotated

from langgraph.graph import StateGraph, END
from langchain_core.messages import AnyMessage

logger = logging.getLogger(__name__)


class NewWorkflowState(TypedDict):
    """State for new workflow."""
    messages: Annotated[list[AnyMessage], "Chat messages"]
    status: Annotated[str, "Workflow status"]
    # Add domain-specific fields here


def create_graph() -> StateGraph:
    """Create NewWorkflow StateGraph."""

    def step_one(state: NewWorkflowState) -> NewWorkflowState:
        """First step of workflow."""
        logger.info("Executing step one")
        state["status"] = "step_one_complete"
        return state

    def step_two(state: NewWorkflowState) -> NewWorkflowState:
        """Second step of workflow."""
        logger.info("Executing step two")
        state["status"] = "step_two_complete"
        return state

    # Build graph
    graph = StateGraph(NewWorkflowState)

    # Add nodes
    graph.add_node("step_one", step_one)
    graph.add_node("step_two", step_two)

    # Define edges
    graph.set_entry_point("step_one")
    graph.add_edge("step_one", "step_two")
    graph.add_edge("step_two", END)

    return graph


def compile() -> object:
    """Compile and return ready-to-run workflow."""
    graph = create_graph()
    return graph.compile()
```

### Step 2: Update Subagents Init

Edit `subagents/__init__.py`:

```python
"""Specialized StateGraph subagents for domain-specific workflows."""

from . import (
    order_workflow,
    shipping_workflow,
    rfq_workflow,
    new_workflow,  # Add this
)

__all__ = [
    "order_workflow",
    "shipping_workflow",
    "rfq_workflow",
    "new_workflow",  # Add this
]
```

### Step 3: Register in Deep Agent

Edit `deep_agent.py`:

```python
# In imports:
from .subagents import order_workflow, shipping_workflow, rfq_workflow, new_workflow

# In create_4sgm_agent(), after agent creation:
agent._subagents = {
    "order": order_workflow.compile(),
    "shipping": shipping_workflow.compile(),
    "rfq": rfq_workflow.compile(),
    "new_domain": new_workflow.compile(),  # Add this
}

# In should_use_subagent(), add:
new_keywords = ["keyword1", "keyword2", "keyword3"]
if any(kw in message_lower for kw in new_keywords):
    return "new_domain"
```

### Step 4: Add Routing Logic

Edit `deep_agent.py` in `route_to_subagent()`:

```python
elif subagent_name == "new_domain":
    state = {
        "messages": [message],
        "status": "pending",
        # Initialize domain-specific fields
    }
```

### Step 5: Test

```bash
# Start the server
uvicorn app:app --reload

# Test with your keywords
curl -X POST http://localhost:8000/chat \
  -H "Content-Type: application/json" \
  -d '{"text": "Your test message with keyword1"}'
```

## Customizing Existing Workflows

### Example: Add Validation to Order Workflow

Edit `subagents/order_workflow.py`:

```python
def validate_items(state: OrderState) -> OrderState:
    """Validate order items - now with custom logic."""
    items = state.get("items", [])
    logger.info(f"Validating {len(items)} items")

    for item in items:
        # Enhanced validation
        if not item.get("sku"):
            state["status"] = "validation_failed"
            return state

        if not item.get("quantity") or item["quantity"] <= 0:
            state["status"] = "validation_failed"
            return state

        # NEW: Check inventory system
        if not check_inventory(item.get("sku"), item.get("quantity")):
            state["status"] = "out_of_stock"
            return state

    state["status"] = "items_validated"
    return state


def check_inventory(sku: str, qty: int) -> bool:
    """Check actual inventory (integrate with your system)."""
    # TODO: Call your inventory API
    return True
```

### Example: Add Dynamic Pricing to RFQ Workflow

Edit `subagents/rfq_workflow.py`:

```python
def apply_discounts(state: RFQState) -> RFQState:
    """Apply volume and customer discounts - now dynamic."""
    quotes = state.get("quotes", [])
    customer_id = state.get("customer_id", "")

    logger.info(f"Applying discounts for customer {customer_id}")

    total = sum(q.get("subtotal", 0) for q in quotes)

    # Get customer tier from database
    customer_tier = get_customer_tier(customer_id)  # NEW

    # Apply tier-based discount
    if customer_tier == "gold":
        discount_rate = 0.20
    elif customer_tier == "silver":
        discount_rate = 0.15
    elif total > 1000:
        discount_rate = 0.15
    elif total > 500:
        discount_rate = 0.10
    else:
        discount_rate = 0.05

    for quote in quotes:
        quote["discount"] = discount_rate
        quote["final_price"] = quote.get("subtotal", 0) * (1 - discount_rate)

    state["status"] = "discounts_applied"
    return state


def get_customer_tier(customer_id: str) -> str:
    """Get customer tier from database."""
    # TODO: Query your customer database
    return "standard"
```

## Adding Node Conditions

### Example: Add Decision Branch

Edit a workflow (e.g., `shipping_workflow.py`):

```python
def create_graph() -> StateGraph:
    """Create ShippingWorkflow StateGraph."""

    def validate_address(state: ShippingState) -> ShippingState:
        """Validate shipping address."""
        # ... validation logic ...
        return state

    # NEW: Add decision node
    def should_require_signature(state: ShippingState) -> str:
        """Decide if signature required."""
        cost = state.get("cost", 0)

        if cost > 500:  # High-value shipment
            return "add_signature"
        else:
            return "continue"

    def add_signature(state: ShippingState) -> ShippingState:
        """Add signature requirement."""
        state["require_signature"] = True
        return state

    # Build graph
    graph = StateGraph(ShippingState)

    graph.add_node("validate", validate_address)
    graph.add_node("check_value", should_require_signature)  # Decision node
    graph.add_node("signature", add_signature)

    graph.set_entry_point("validate")
    graph.add_edge("validate", "check_value")

    # NEW: Conditional edges
    graph.add_conditional_edges(
        "check_value",
        lambda x: "add_signature" if x["cost"] > 500 else "continue",
        {
            "add_signature": "signature",
            "continue": "select_carrier"
        }
    )

    graph.add_edge("signature", "select_carrier")
    # ... rest of workflow ...
```

## Integrating with External Systems

### Example: Connect to Inventory API

Create `integrations/inventory.py`:

```python
"""Integration with inventory management system."""

import httpx
import os
import logging

logger = logging.getLogger(__name__)


async def check_inventory(sku: str, qty: int) -> dict:
    """
    Check inventory availability from external system.

    Args:
        sku: Product SKU
        qty: Requested quantity

    Returns:
        {"available": True, "qty": 100, "warehouse": "main"}
    """
    inventory_api = os.getenv("INVENTORY_API_URL")

    if not inventory_api:
        logger.warning("INVENTORY_API_URL not configured")
        return {"available": True, "qty": qty, "warehouse": "unknown"}

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post(
                f"{inventory_api}/check",
                json={"sku": sku, "qty": qty},
                timeout=5.0
            )

            if response.status_code == 200:
                return response.json()
            else:
                logger.error(f"Inventory check failed: {response.status_code}")
                return {"available": False, "error": "API error"}

    except Exception as e:
        logger.error(f"Inventory check error: {e}")
        return {"available": True, "qty": qty}  # Fail open


async def get_price(sku: str) -> float:
    """Get current price from inventory system."""
    inventory_api = os.getenv("INVENTORY_API_URL")

    if not inventory_api:
        return 0.0

    try:
        async with httpx.AsyncClient() as client:
            response = await client.get(
                f"{inventory_api}/price/{sku}",
                timeout=5.0
            )

            if response.status_code == 200:
                return float(response.json()["price"])
            else:
                return 0.0

    except Exception as e:
        logger.error(f"Price lookup error: {e}")
        return 0.0
```

### Use in Workflow

Edit `subagents/rfq_workflow.py`:

```python
import asyncio
from integrations.inventory import check_inventory, get_price

def generate_quotes(state: RFQState) -> RFQState:
    """Generate pricing quotes with real inventory data."""
    items = state.get("items", [])

    quotes = []
    total_price = 0

    for item in items:
        sku = item.get("sku")
        qty = item.get("quantity", 0)

        # NEW: Get real price and check inventory
        price = asyncio.run(get_price(sku))  # Note: In production, use proper async handling
        inventory = asyncio.run(check_inventory(sku, qty))

        if not inventory["available"]:
            state["status"] = "out_of_stock"
            return state

        unit_price = price * (1 - 0.1)  # 10% bulk discount
        item_total = unit_price * qty
        total_price += item_total

        quotes.append({
            "sku": sku,
            "unit_price": unit_price,
            "quantity": qty,
            "subtotal": item_total,
        })

    state["quotes"] = quotes
    state["status"] = "quotes_generated"
    return state
```

## Enhancing Logging and Monitoring

### Add Custom Metrics

Edit any workflow:

```python
import logging
from datetime import datetime

logger = logging.getLogger(__name__)


def process_order(state: OrderState) -> OrderState:
    """Process order with monitoring."""
    start_time = datetime.now()

    try:
        # Process logic
        state["status"] = "processed"

        # Calculate metrics
        duration = (datetime.now() - start_time).total_seconds()

        # Log with metrics
        logger.info(
            "Order processed",
            extra={
                "order_id": state.get("order_id"),
                "duration_seconds": duration,
                "total": state.get("total"),
                "item_count": len(state.get("items", [])),
            }
        )

        return state

    except Exception as e:
        logger.error(
            "Order processing failed",
            extra={
                "order_id": state.get("order_id"),
                "error": str(e),
            }
        )
        raise
```

## Persistence and State Recovery

### Save Workflow State

Edit a workflow:

```python
import json
import os

async def save_workflow_state(state: OrderState, workflow_name: str):
    """Save workflow state for recovery."""
    state_dir = os.path.join("/tmp", "workflow_states", workflow_name)
    os.makedirs(state_dir, exist_ok=True)

    state_file = os.path.join(
        state_dir,
        f"{state.get('order_id')}.json"
    )

    # Convert state to JSON-serializable format
    json_state = {
        "order_id": state.get("order_id"),
        "status": state.get("status"),
        "total": float(state.get("total", 0)),
        # ... other fields ...
    }

    with open(state_file, "w") as f:
        json.dump(json_state, f)


async def recover_workflow_state(order_id: str, workflow_name: str) -> OrderState:
    """Recover workflow state from file."""
    state_file = os.path.join(
        "/tmp", "workflow_states", workflow_name, f"{order_id}.json"
    )

    if os.path.exists(state_file):
        with open(state_file) as f:
            data = json.load(f)

        return OrderState(**data)  # Or parse accordingly

    return None
```

## Testing Custom Workflows

Create `tests/test_new_workflow.py`:

```python
"""Tests for new workflow."""

import pytest
from agents.subagents import new_workflow


def test_new_workflow_steps():
    """Test workflow progression."""
    workflow = new_workflow.compile()

    initial_state = {
        "messages": [],
        "status": "pending",
    }

    result = workflow.invoke(initial_state)

    assert result["status"] == "step_two_complete"


def test_workflow_error_handling():
    """Test error handling in workflow."""
    workflow = new_workflow.compile()

    invalid_state = {
        "messages": [],
        # Missing required fields
    }

    with pytest.raises(Exception):
        workflow.invoke(invalid_state)


@pytest.mark.asyncio
async def test_async_workflow():
    """Test async workflow execution."""
    workflow = new_workflow.compile()

    state = {"messages": [], "status": "pending"}

    result = await workflow.ainvoke(state)

    assert "status" in result
```

## Performance Optimization

### Add Caching

```python
from functools import lru_cache
import time


@lru_cache(maxsize=128)
def get_shipping_cost(country: str) -> float:
    """Cache shipping costs."""
    # Cost lookup logic
    return 15.0


def select_carrier(state: ShippingState) -> ShippingState:
    """Select carrier with cached costs."""
    address = state.get("address", {})
    country = address.get("country")

    # Use cached function
    cost = get_shipping_cost(country)
    state["cost"] = cost

    return state
```

### Parallel Processing

```python
import asyncio


async def process_items_parallel(items: list) -> list:
    """Process items in parallel."""
    tasks = [process_item(item) for item in items]
    return await asyncio.gather(*tasks)


async def process_item(item: dict) -> dict:
    """Process single item asynchronously."""
    # Item processing logic
    return item
```

## Debugging Workflows

### Enable Debug Logging

```bash
LOG_LEVEL=DEBUG uvicorn app:app --reload
```

### Add Debug Nodes

```python
def debug_state(state: OrderState) -> OrderState:
    """Debug node to inspect state."""
    logger.debug(f"Current state: {state}")
    return state


# Add to graph:
graph.add_node("debug", debug_state)
graph.add_edge("previous_node", "debug")
graph.add_edge("debug", "next_node")
```

## Best Practices

1. **Keep nodes focused** - One responsibility per node
2. **Use meaningful names** - Descriptive node/workflow names
3. **Log everything** - Debug-level logging for flow tracking
4. **Handle errors** - Try/catch with proper error state
5. **Test independently** - Unit test each node
6. **Document state** - Clear TypedDict definitions
7. **Monitor performance** - Add timing metrics
8. **Version workflows** - Track changes over time
9. **Validate inputs** - Check state at entry points
10. **Plan for failure** - Implement recovery logic

## Support

For questions about extending the architecture, refer to:
- `/backend/DEEPAGENT_ARCHITECTURE.md` - Architecture overview
- `/backend/agents/QUICK_START.md` - Quick reference
- Individual workflow files - Implementation examples
