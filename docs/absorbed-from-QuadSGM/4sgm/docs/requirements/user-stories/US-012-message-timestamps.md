# US-012: Message Timestamps are Displayed

## Epic
EPIC-009: Message Metadata

## User Story
As a customer, I want each message in the chat to display a timestamp so that I can see when messages were sent.

## Acceptance Criteria
- [ ] Given a message is sent, when it appears in the chat, then a timestamp should be visible
- [ ] Given the query "Test timestamp message", when sent, then time should display next to the message
- [ ] Given multiple messages, when viewed, then each should have its own timestamp
- [ ] Given a conversation, when timestamps are displayed, then format should be consistent (e.g., HH:MM or relative time)
- [ ] Given older messages, when scrolling up, then timestamps should remain visible
- [ ] Given a chat history, when messages are retrieved, then timestamps should be restored accurately

## Implementation
- **Code Files**: `frontend/components/message.tsx`, `backend/models.py`, `frontend/lib/formatting.ts`
- **Test Files**: `frontend/e2e/chat-flow.spec.ts` (Message timestamps), `frontend/tests/message.test.tsx`

## Test Reference
From `frontend/e2e/chat-flow.spec.ts`:
- Test: "Message timestamps are displayed"
- Lines: 263-281
