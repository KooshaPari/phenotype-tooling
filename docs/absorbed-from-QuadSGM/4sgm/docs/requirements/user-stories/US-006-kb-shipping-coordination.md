# US-006: Tool Coordination - KB + Shipping

## Epic
EPIC-005: Real-Time Business Tool Integration

## User Story
As a customer, when I ask a question that requires both product information and shipping cost, I want the system to coordinate multiple tools so I get a complete answer.

## Acceptance Criteria
- [ ] Given a query about shipping policy and cost, when the system analyzes it, then both KB and Shipping tools should be identified
- [ ] Given the query "What is your shipping policy and how much to send a package to 10001?", when processed, then policy info and shipping cost should both be returned
- [ ] Given multiple tools are invoked, when they complete, then results should be synthesized into a single response
- [ ] Given tools run in parallel, when one fails, then available results should still be used
- [ ] Given tool coordination, when the response is generated, then both source types should be cited appropriately
- [ ] Given multiple tool results, when the message displays, then the input should be cleared successfully

## Implementation
- **Code Files**: `backend/tool_orchestrator.py`, `backend/tools/shipping.py`, `backend/main.py`
- **Test Files**: `backend/tests/test_tool_coordination.py`, `frontend/e2e/chat-flow.spec.ts` (US-4.1)

## Test Reference
From `frontend/e2e/chat-flow.spec.ts`:
- Test: "US-4.1: Tool coordination - KB + Shipping"
- Lines: 128-146
