# US-011: Keyboard Accessibility - Send Message with Enter Key

## Epic
EPIC-008: Accessibility

## User Story
As a user with keyboard navigation needs, I want to send messages using the Enter key so that I can operate the chat without a mouse.

## Acceptance Criteria
- [ ] Given the message input is focused, when I press Enter, then the message should be sent
- [ ] Given a message is typed, when I press Enter, then the input field should clear
- [ ] Given the chat widget is open, when I navigate with Tab, then all interactive elements should be reachable
- [ ] Given the query "Keyboard test message", when Enter is pressed, then the message should send successfully
- [ ] Given different browsers, when Enter is pressed, then behavior should be consistent
- [ ] Given Shift+Enter, when pressed, then it could optionally add a line break if supported

## Implementation
- **Code Files**: `frontend/components/chat-widget.tsx`, `frontend/hooks/useChat.ts`
- **Test Files**: `frontend/e2e/chat-flow.spec.ts` (Keyboard accessibility), `frontend/tests/chat-widget.test.tsx`

## Test Reference
From `frontend/e2e/chat-flow.spec.ts`:
- Test: "Keyboard accessibility - send message with Enter key"
- Lines: 243-261
