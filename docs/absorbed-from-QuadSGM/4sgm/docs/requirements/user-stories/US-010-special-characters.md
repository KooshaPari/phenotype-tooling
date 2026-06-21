# US-010: Message Rendering with Special Characters

## Epic
EPIC-007: Unicode and Special Character Support

## User Story
As a customer, when I send messages containing emoji, special symbols, or non-ASCII characters, I want them to render correctly so that I can express myself naturally.

## Acceptance Criteria
- [ ] Given I send a message with emoji (💰), when it displays, then the emoji should render correctly
- [ ] Given I send a message with symbols (&, %, $), when it displays, then symbols should not be escaped
- [ ] Given I send text with accents (é, ñ, ü), when it displays, then they should show correctly
- [ ] Given the query "What about pricing? 💰 10% off! & more...", when processed, then all characters should display correctly
- [ ] Given special characters in both input and output, when displayed, then encoding should be consistent
- [ ] Given mixed-language content, when sent, then all scripts should render properly

## Implementation
- **Code Files**: `frontend/components/message.tsx`, `backend/main.py`, `backend/models.py`
- **Test Files**: `frontend/e2e/chat-flow.spec.ts` (Special characters), `frontend/tests/message.test.tsx`

## Test Reference
From `frontend/e2e/chat-flow.spec.ts`:
- Test: "Message rendering with special characters"
- Lines: 223-241
