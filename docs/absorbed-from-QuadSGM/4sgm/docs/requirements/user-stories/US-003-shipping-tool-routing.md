# US-003: Automatic Tool Selection for Shipping Queries

## Epic
EPIC-002: Intelligent Query Routing

## User Story
As a customer, I want the system to automatically route my shipping question to the shipping tool so that I get accurate, real-time shipping cost estimates.

## Acceptance Criteria
- [ ] Given I ask a shipping-related question, when the system analyzes the query, then it should identify it as shipping-related
- [ ] Given a shipping query is identified, when the system selects tools, then the shipping tool should be invoked
- [ ] Given the shipping tool is called, when it returns data, then the response should include the cost estimate
- [ ] Given the query "How much will it cost to ship 10 lbs to New York?", when processed, then the shipping calculator should provide a quote
- [ ] Given the shipping tool returns results, when the response is generated, then it should synthesize the data into a natural answer
- [ ] Given different shipping scenarios, when queried, then accuracy should be >95%

## Implementation
- **Code Files**: `backend/routing.py`, `backend/tools/shipping.py`, `backend/main.py`
- **Test Files**: `backend/tests/test_mcp_tools.py`, `frontend/e2e/chat-flow.spec.ts` (US-2.1)

## Test Reference
From `frontend/e2e/chat-flow.spec.ts`:
- Test: "US-2.1: Automatic tool selection for shipping queries"
- Lines: 65-82
