# US-001: Search Knowledge Base and Get Answers

## Epic
EPIC-001: Knowledge Base RAG Pipeline

## User Story
As a customer, I want to search the knowledge base for answers so that I can quickly find information about products and services.

## Acceptance Criteria
- [ ] Given the chat widget is open, when I type a query about shipping rates, then the system should accept my input
- [ ] Given I submit a message, when the system processes it, then it should generate an embedding for the query
- [ ] Given the query is embedded, when the system searches the knowledge base, then it should return relevant documents
- [ ] Given relevant documents are found, when the LLM processes them, then it should generate a coherent response
- [ ] Given the response is generated, when the system displays it, then the message input should be cleared
- [ ] Given a customer asks "What are your shipping rates to California?", then the response should address shipping costs to that region

## Implementation
- **Code Files**: `backend/vector_search.py`, `backend/embeddings.py`, `frontend/components/chat-widget.tsx`
- **Test Files**: `backend/tests/test_rag.py`, `frontend/e2e/chat-flow.spec.ts` (US-1.1)

## Test Reference
From `frontend/e2e/chat-flow.spec.ts`:
- Test: "US-1.1: Customer can search knowledge base and get answers"
- Lines: 27-44
