# EPIC-001: Knowledge Base RAG Pipeline

## Description
Implement a Retrieval-Augmented Generation (RAG) pipeline that allows customers to search the knowledge base and receive AI-generated answers with proper source citations. This epic covers embedding generation, vector search, and response synthesis with cited sources.

## User Stories
- US-001: Customer can search knowledge base and get answers
- US-002: Customer can see source citations

## Acceptance Criteria
- [ ] Chat widget accepts customer queries
- [ ] System generates embeddings for queries
- [ ] Vector search retrieves relevant documents
- [ ] LLM generates response based on context
- [ ] Response includes document source citations
- [ ] Input is cleared after message submission
- [ ] System handles edge cases (empty, very long inputs)
