# US-004: Escalation Button Appears and Works

## Epic
EPIC-003: Human Escalation

## User Story
As a customer, when the AI cannot confidently answer my question, I want an escalation button to appear so that I can connect with a human support agent.

## Acceptance Criteria
- [ ] Given the system processes a query, when confidence is below 60%, then an escalation button should appear
- [ ] Given a vague or unclear query, when the system evaluates confidence, then escalation should be triggered
- [ ] Given the escalation button is visible, when I click it, then the system should initiate human transfer
- [ ] Given I send the query "xyzabc123", when processed, then escalation UI should appear
- [ ] Given escalation is initiated, when the transfer occurs, then chat context should be preserved
- [ ] Given an escalation request, when processed, then the message input should still clear
- [ ] Given escalation context, when transferred, then the human agent should see previous messages

## Implementation
- **Code Files**: `frontend/components/escalation-banner.tsx`, `backend/confidence.py`, `backend/main.py`
- **Test Files**: `frontend/e2e/chat-flow.spec.ts` (US-2.2), `frontend/tests/escalation-banner.test.tsx`

## Test Reference
From `frontend/e2e/chat-flow.spec.ts`:
- Test: "US-2.2: Escalation button appears and works"
- Lines: 84-101
