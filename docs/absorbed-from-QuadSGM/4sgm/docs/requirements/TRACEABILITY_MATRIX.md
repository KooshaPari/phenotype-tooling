# Requirements Traceability Matrix

## Overview
This matrix maps User Stories to their E2E tests, implementation files, and acceptance criteria coverage.

## Story to Test Mapping

| Story ID | Story Title | Test File | Test Name | Test Lines | Status |
|----------|------------|-----------|-----------|-----------|--------|
| US-001 | Search Knowledge Base and Get Answers | `frontend/e2e/chat-flow.spec.ts` | US-1.1: Customer can search knowledge base and get answers | 27-44 | Pending |
| US-002 | See Source Citations | `frontend/e2e/chat-flow.spec.ts` | US-1.2: Customer can see source citations | 46-63 | Pending |
| US-003 | Automatic Tool Selection for Shipping Queries | `frontend/e2e/chat-flow.spec.ts` | US-2.1: Automatic tool selection for shipping queries | 65-82 | Pending |
| US-004 | Escalation Button Appears and Works | `frontend/e2e/chat-flow.spec.ts` | US-2.2: Escalation button appears and works | 84-101 | Pending |
| US-005 | Multi-Turn Conversation Maintains Context | `frontend/e2e/chat-flow.spec.ts` | US-3.1: Multi-turn conversation maintains context | 103-126 | Pending |
| US-006 | Tool Coordination - KB + Shipping | `frontend/e2e/chat-flow.spec.ts` | US-4.1: Tool coordination - KB + Shipping | 128-146 | Pending |
| US-007 | Error Handling for Invalid Input | `frontend/e2e/chat-flow.spec.ts` | US-6.1: Error handling for invalid input | 148-170 | Pending |
| US-008 | Session Persistence Across Page Reload | `frontend/e2e/chat-flow.spec.ts` | Session persistence across page reload | 172-201 | Pending |
| US-009 | Chat Widget Responsive Design | `frontend/e2e/chat-flow.spec.ts` | Chat widget is responsive on different screen sizes | 203-221 | Pending |
| US-010 | Message Rendering with Special Characters | `frontend/e2e/chat-flow.spec.ts` | Message rendering with special characters | 223-241 | Pending |
| US-011 | Keyboard Accessibility - Send Message with Enter Key | `frontend/e2e/chat-flow.spec.ts` | Keyboard accessibility - send message with Enter key | 243-261 | Pending |
| US-012 | Message Timestamps are Displayed | `frontend/e2e/chat-flow.spec.ts` | Message timestamps are displayed | 263-281 | Pending |
| US-013 | Confidence Indicator or Visual Feedback Provided | `frontend/e2e/chat-flow.spec.ts` | Confidence indicator or visual feedback provided | 283-301 | Pending |

## Implementation File Mapping

### Backend Implementation Files

| File | Stories | Reason |
|------|---------|--------|
| `backend/embeddings.py` | US-001, US-002 | Generate embeddings for vector search |
| `backend/vector_search.py` | US-001, US-002, US-006 | Search knowledge base for relevant documents |
| `backend/confidence.py` | US-002, US-004, US-013 | Calculate confidence scores for responses |
| `backend/routing.py` | US-003, US-006 | Route queries to appropriate tools |
| `backend/tools/shipping.py` | US-003, US-006 | Shipping cost calculation API |
| `backend/tool_orchestrator.py` | US-006 | Coordinate multiple tools |
| `backend/session_manager.py` | US-005, US-008 | Manage chat sessions and history |
| `backend/validation.py` | US-007 | Input validation and sanitization |
| `backend/main.py` | All stories | Main FastAPI application and MCP server |
| `backend/models.py` | All stories | Pydantic data models |

### Frontend Implementation Files

| File | Stories | Reason |
|------|---------|--------|
| `frontend/components/chat-widget.tsx` | US-001, US-007, US-009, US-011 | Main chat widget component |
| `frontend/components/message.tsx` | US-002, US-010, US-012, US-013 | Individual message display |
| `frontend/components/escalation-banner.tsx` | US-004 | Escalation UI |
| `frontend/components/confidence-badge.tsx` | US-013 | Confidence indicator display |
| `frontend/hooks/useChat.ts` | US-001, US-005, US-008, US-011 | Chat state management hook |
| `frontend/lib/chat-client.ts` | US-001, US-006 | API client for chat endpoint |
| `frontend/lib/storage.ts` | US-008 | Local storage for session persistence |
| `frontend/lib/formatting.ts` | US-010, US-012 | Text formatting utilities |
| `frontend/styles/globals.css` | US-009, US-010 | Responsive design and styling |

## Acceptance Criteria Coverage

### US-001: Search Knowledge Base and Get Answers
- [ ] Chat widget accepts customer queries
- [ ] System generates embeddings for queries
- [ ] Vector search retrieves relevant documents
- [ ] LLM generates response based on context
- [ ] Input is cleared after message submission

**Implementation Path:**
1. Frontend: Collect user input in chat widget
2. Backend: Generate embedding using OpenAI API
3. Backend: Search vector database using Supabase pgvector
4. Backend: Format context and call LLM
5. Frontend: Display response and clear input

---

### US-002: See Source Citations
- [ ] Response includes document source citations
- [ ] All source documents are cited
- [ ] Citations are clickable/actionable
- [ ] Sources are visible in UI

**Implementation Path:**
1. Backend: Return source metadata with search results
2. Frontend: Format and display citations with response
3. Frontend: Add click handlers for source links

---

### US-003: Automatic Tool Selection for Shipping Queries
- [ ] System identifies shipping-related queries
- [ ] Shipping tool is invoked for shipping queries
- [ ] Tool results are synthesized into response
- [ ] Query intent detection is accurate (>85%)

**Implementation Path:**
1. Backend: Implement intent classification
2. Backend: Route to shipping tool based on intent
3. Backend: Call shipping API with parameters
4. Backend: Synthesize results with LLM

---

### US-004: Escalation Button Appears and Works
- [ ] Escalation button appears when confidence < 60%
- [ ] Button is visible and clickable
- [ ] Escalation transfers context to human agent
- [ ] Visual indicator shows escalation is available

**Implementation Path:**
1. Backend: Calculate confidence score
2. Frontend: Show escalation button when confidence low
3. Frontend: Handle escalation click event
4. Backend: Transfer session to human agent queue

---

### US-005: Multi-Turn Conversation Maintains Context
- [ ] Chat system maintains session history
- [ ] Previous messages are available for context
- [ ] System understands pronouns in follow-up messages
- [ ] LLM can reference previous messages

**Implementation Path:**
1. Frontend: Store message history in state
2. Backend: Include conversation history in LLM prompt
3. Backend: Manage session context window (last 5-10 messages)

---

### US-006: Tool Coordination - KB + Shipping
- [ ] Both KB and Shipping tools are identified
- [ ] Multiple tools run in parallel
- [ ] Results are synthesized into single response
- [ ] Both source types are cited

**Implementation Path:**
1. Backend: Identify need for multiple tools
2. Backend: Run tools concurrently
3. Backend: Aggregate results
4. Backend: Synthesize with LLM
5. Frontend: Display combined response with citations

---

### US-007: Error Handling for Invalid Input
- [ ] System validates input before processing
- [ ] Long inputs are rejected gracefully
- [ ] Error messages are helpful and clear
- [ ] User can retry after errors

**Implementation Path:**
1. Frontend: Validate input length and format
2. Backend: Validate all inputs with Zod
3. Frontend: Display helpful error messages

---

### US-008: Session Persistence Across Page Reload
- [ ] Chat session is stored
- [ ] Previous messages are visible after reload
- [ ] Conversation history is preserved
- [ ] Session data is retrieved on load

**Implementation Path:**
1. Frontend: Store session data in localStorage
2. Frontend: Load session on component mount
3. Backend: Persist session in database
4. Frontend: Restore UI state on reload

---

### US-009: Chat Widget Responsive Design
- [ ] Widget adapts to mobile (375x667)
- [ ] Widget adapts to tablet (768x1024)
- [ ] Widget adapts to desktop
- [ ] No horizontal scrolling on small screens
- [ ] All buttons are clickable on all sizes

**Implementation Path:**
1. Frontend: Use CSS media queries
2. Frontend: Use Tailwind responsive utilities
3. Frontend: Test on multiple viewport sizes

---

### US-010: Message Rendering with Special Characters
- [ ] Emoji render correctly
- [ ] Symbols (&, %, $) don't escape
- [ ] Accents (é, ñ, ü) display correctly
- [ ] Mixed-language content renders
- [ ] Encoding is consistent

**Implementation Path:**
1. Frontend: Ensure UTF-8 encoding
2. Backend: Handle Unicode in models
3. Backend: Preserve character encoding in storage

---

### US-011: Keyboard Accessibility - Send Message with Enter Key
- [ ] Enter key sends message
- [ ] Input clears after Enter
- [ ] Tab navigation works
- [ ] All interactive elements are reachable

**Implementation Path:**
1. Frontend: Add keyboard event handlers
2. Frontend: Manage focus states
3. Frontend: Implement ARIA labels
4. Frontend: Test keyboard navigation

---

### US-012: Message Timestamps are Displayed
- [ ] Each message has visible timestamp
- [ ] Format is consistent (HH:MM or relative)
- [ ] Timestamps are accurate
- [ ] Old messages retain timestamps

**Implementation Path:**
1. Backend: Add timestamp to message model
2. Frontend: Format and display timestamp
3. Frontend: Use relative or absolute time format

---

### US-013: Confidence Indicator or Visual Feedback Provided
- [ ] High confidence (>80%) shows positive indicator
- [ ] Medium confidence (60-80%) shows neutral indicator
- [ ] Low confidence (<60%) shows warning indicator
- [ ] Indicator is clearly visible

**Implementation Path:**
1. Backend: Calculate confidence score for each response
2. Frontend: Create confidence badge component
3. Frontend: Display badge color based on score
4. Frontend: Show escalation option for low confidence

---

## Epic to Story Mapping

### EPIC-001: Knowledge Base RAG Pipeline
- US-001: Search Knowledge Base and Get Answers
- US-002: See Source Citations

### EPIC-002: Intelligent Query Routing
- US-003: Automatic Tool Selection for Shipping Queries
- US-006: Tool Coordination - KB + Shipping

### EPIC-003: Human Escalation
- US-004: Escalation Button Appears and Works

### EPIC-004: Multi-Turn Conversation Context
- US-005: Multi-Turn Conversation Maintains Context
- US-008: Session Persistence Across Page Reload

### EPIC-005: Real-Time Business Tool Integration
- US-006: Tool Coordination - KB + Shipping

### EPIC-006: Robust Error Handling
- US-007: Error Handling for Invalid Input

### EPIC-007: Responsive Design
- US-009: Chat Widget Responsive Design

### EPIC-008: Unicode and Special Character Support
- US-010: Message Rendering with Special Characters

### EPIC-009: Accessibility
- US-011: Keyboard Accessibility - Send Message with Enter Key

### EPIC-010: Message Metadata
- US-012: Message Timestamps are Displayed

### EPIC-011: Response Quality Indicators
- US-013: Confidence Indicator or Visual Feedback Provided

---

## Test Execution Strategy

### Phase 1: Unit Tests
- Backend: RAG pipeline components (embedding, search, confidence)
- Frontend: Individual components (message, input, badges)
- Backend: Input validation and error handling
- Backend: Session management

### Phase 2: Integration Tests
- Backend: Tool routing and coordination
- Backend: MCP tool endpoints
- Frontend-Backend: Chat API integration
- Backend: Database interactions

### Phase 3: E2E Tests
- Complete user journeys from test file
- Cross-browser compatibility (Chrome, Firefox, Safari)
- Mobile responsiveness testing
- Accessibility testing (keyboard, screen readers)

### Phase 4: Performance Tests
- Embedding generation latency
- Vector search performance
- Message throughput
- Session persistence speed

## Coverage Targets

| Layer | Target | Current |
|-------|--------|---------|
| Backend Unit Tests | 90% | 0% |
| Frontend Unit Tests | 80% | 0% |
| E2E Test Coverage | 100% | 13 tests |
| Acceptance Criteria | 100% | 0% |

## Known Dependencies

### Cross-Story Dependencies
- **US-005 → US-001, US-002**: Multi-turn context requires RAG pipeline
- **US-006 → US-003**: Tool coordination requires routing
- **US-004 ↔ US-002**: Escalation depends on confidence scores from RAG
- **US-008 → US-005**: Session persistence enables multi-turn

### External Dependencies
- OpenAI API for embeddings and LLM
- Supabase for vector database and session storage
- Shipping API for cost calculations
- Knowledge base documents for initial ingestion

## Sign-off Checklist

- [ ] All 13 user stories documented with acceptance criteria
- [ ] All 6 main epics defined with success metrics
- [ ] Traceability matrix complete with test mapping
- [ ] Implementation files identified for each story
- [ ] All E2E tests referenced and mapped
- [ ] Dependencies documented
- [ ] Coverage targets defined
- [ ] Ready for development team
