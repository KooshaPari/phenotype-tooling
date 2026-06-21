# US-002: See Source Citations

## Epic
EPIC-001: Knowledge Base RAG Pipeline

## User Story
As a customer, I want to see the sources for the answers provided so that I can verify the information and access the original documentation.

## Acceptance Criteria
- [ ] Given a response is generated from the knowledge base, when it is displayed, then citations should be included
- [ ] Given multiple documents are used, when the response is generated, then all source documents should be cited
- [ ] Given a citation is displayed, when I click on it, then I should access the source document
- [ ] Given a customer asks "Tell me about your return policy", then the response should cite the policy document
- [ ] Given sources are available, when the response is formatted, then sources should be visible in the UI
- [ ] Given different confidence levels, when citations are displayed, then high-confidence sources should be highlighted

## Implementation
- **Code Files**: `backend/confidence.py`, `frontend/components/message.tsx`, `backend/main.py`
- **Test Files**: `backend/tests/test_rag.py`, `frontend/e2e/chat-flow.spec.ts` (US-1.2)

## Test Reference
From `frontend/e2e/chat-flow.spec.ts`:
- Test: "US-1.2: Customer can see source citations"
- Lines: 46-63
