# Quick Reference Guide - 4SGM Requirements

## For Other Agents: How to Use This Documentation

### Overview
This directory contains complete requirements documentation extracted from E2E tests. All user stories are mapped to epics, implementation files, and acceptance criteria.

### Starting Points by Role

#### Agent 2: Architecture & Technical Design
Start with: `epics/` directory
1. Read all EPIC-*.md files for system scope
2. Review TRACEABILITY_MATRIX.md for implementation files
3. Focus on: Integration patterns, API contracts, data models

Key Epics:
- EPIC-001: RAG pipeline (embeddings, vector search)
- EPIC-002: Query routing (intent detection, tool selection)
- EPIC-005: Business tool integration (shipping, inventory)

#### Agent 3: UI/UX Design
Start with: `user-stories/US-009.md` through `US-013.md`
1. Read responsive design requirements (US-009)
2. Read accessibility requirements (US-011)
3. Review message display requirements (US-010, US-012)
4. Review confidence indicator requirements (US-013)

Key Stories:
- US-009: Responsive Design (mobile, tablet, desktop)
- US-010: Special Characters (emoji, symbols, accents)
- US-011: Keyboard Accessibility (Enter to send)
- US-012: Message Timestamps
- US-013: Confidence Indicators

#### Agent 4: Backend Development
Start with: `TRACEABILITY_MATRIX.md` implementation section
1. Identify your assigned backend files
2. Read the user stories that depend on those files
3. Check acceptance criteria for each story

Core Backend Files:
- `backend/embeddings.py` - OpenAI embedding generation
- `backend/vector_search.py` - Supabase pgvector search
- `backend/confidence.py` - Confidence scoring
- `backend/routing.py` - Query intent detection
- `backend/main.py` - FastAPI + MCP endpoints

#### Agent 5: Frontend Development
Start with: `TRACEABILITY_MATRIX.md` implementation section
1. Identify your assigned frontend files
2. Read the user stories that depend on those files
3. Review acceptance criteria and test cases

Core Frontend Files:
- `frontend/components/chat-widget.tsx` - Main chat UI
- `frontend/hooks/useChat.ts` - State management
- `frontend/lib/chat-client.ts` - API client
- `frontend/lib/storage.ts` - Session persistence

#### Agents 6-10: Testing & QA
Start with: `REQUIREMENTS_EXTRACTION_REPORT.md`
1. Review all 13 user stories
2. Note each story's acceptance criteria
3. Map test cases to criteria
4. Check E2E test file references

Source E2E Tests: `frontend/e2e/chat-flow.spec.ts`

---

## Quick Story Lookup

### By Feature Area

**Knowledge Base & Search:**
- US-001: Search knowledge base and get answers
- US-002: See source citations

**Query Routing:**
- US-003: Automatic tool selection for shipping queries
- US-006: Tool coordination - KB + Shipping

**Escalation:**
- US-004: Escalation button appears and works

**Conversation:**
- US-005: Multi-turn conversation maintains context
- US-008: Session persistence across page reload

**Error Handling:**
- US-007: Error handling for invalid input

**UX/Accessibility:**
- US-009: Chat widget responsive design
- US-010: Message rendering with special characters
- US-011: Keyboard accessibility - Enter key
- US-012: Message timestamps are displayed
- US-013: Confidence indicator or visual feedback

### By Epic

**EPIC-001: Knowledge Base RAG**
- US-001, US-002

**EPIC-002: Intelligent Routing**
- US-003, US-006

**EPIC-003: Human Escalation**
- US-004

**EPIC-004: Multi-Turn Context**
- US-005, US-008

**EPIC-005: Business Tools**
- US-006

**EPIC-006: Error Handling**
- US-007

**EPIC-007: Responsive Design**
- US-009

**EPIC-008: Special Characters**
- US-010

**EPIC-009: Accessibility**
- US-011

**EPIC-010: Message Metadata**
- US-012

**EPIC-011: Quality Indicators**
- US-013

---

## Understanding the Documentation Format

### Epic Files

Each epic contains:
- Description: What this feature area covers
- User Stories: List of stories in this epic
- Acceptance Criteria: High-level epic success metrics

Example: `EPIC-001-knowledge-base-rag.md`
```markdown
# EPIC-001: Knowledge Base RAG Pipeline

## Description
[What this covers]

## User Stories
- US-001: [Story title]
- US-002: [Story title]

## Acceptance Criteria
- [ ] Criterion 1
- [ ] Criterion 2
```

### User Story Files

Each story contains:
- User Story statement: "As a [user], I want to [action] so that [benefit]"
- Acceptance Criteria: 5-7 BDD-style Given-When-Then scenarios
- Implementation: Code and test file references
- Test Reference: Link to E2E test specification

Example: `US-001-search-kb.md`
```markdown
# US-001: Search Knowledge Base and Get Answers

## User Story
As a customer, I want to search the knowledge base for answers
so that I can quickly find information.

## Acceptance Criteria
- [ ] Given [context], when [action], then [result]
- [ ] Given [context], when [action], then [result]

## Implementation
- Code Files: [backend files]
- Test Files: [test files]
```

---

## Key Mappings

### Test to Story Mapping

| Test Lines | Story | Description |
|-----------|-------|-------------|
| 27-44 | US-001 | Search KB and get answers |
| 46-63 | US-002 | See source citations |
| 65-82 | US-003 | Automatic shipping tool selection |
| 84-101 | US-004 | Escalation button |
| 103-126 | US-005 | Multi-turn conversation |
| 128-146 | US-006 | Tool coordination |
| 148-170 | US-007 | Error handling |
| 172-201 | US-008 | Session persistence |
| 203-221 | US-009 | Responsive design |
| 223-241 | US-010 | Special characters |
| 243-261 | US-011 | Keyboard accessibility |
| 263-281 | US-012 | Message timestamps |
| 283-301 | US-013 | Confidence indicator |

### Story Dependencies

**Critical Path (build in order):**
1. US-001: RAG search (foundation)
2. US-003: Tool routing (enables multi-tool)
3. US-005: Multi-turn context (enables conversations)

**Dependent Stories:**
- US-002 depends on: US-001 (uses RAG results)
- US-004 depends on: US-002 (uses confidence scores)
- US-006 depends on: US-001 and US-003 (combines features)
- US-008 depends on: US-005 (persists context)

---

## Implementation File Quick Reference

### Backend Files by Function

| File | Purpose | Stories |
|------|---------|---------|
| embeddings.py | Generate query embeddings | US-001, US-002, US-006 |
| vector_search.py | Search vector database | US-001, US-002, US-006 |
| confidence.py | Calculate confidence scores | US-002, US-004, US-013 |
| routing.py | Detect query intent | US-003, US-006 |
| tools/shipping.py | Shipping cost API | US-003, US-006 |
| tool_orchestrator.py | Coordinate tools | US-006 |
| session_manager.py | Manage chat sessions | US-005, US-008 |
| validation.py | Validate inputs | US-007 |
| main.py | FastAPI + MCP server | All stories |

### Frontend Files by Function

| File | Purpose | Stories |
|------|---------|---------|
| chat-widget.tsx | Main chat UI | US-001, US-009, US-011 |
| message.tsx | Display messages | US-002, US-010, US-012, US-013 |
| escalation-banner.tsx | Escalation UI | US-004 |
| confidence-badge.tsx | Show confidence | US-013 |
| useChat.ts | State management | US-001, US-005, US-008 |
| chat-client.ts | API client | US-001, US-006 |
| storage.ts | Session storage | US-008 |
| formatting.ts | Format text | US-010, US-012 |
| styles/globals.css | Responsive styling | US-009 |

---

## Acceptance Criteria Quick Lookup

### US-001: Search Knowledge Base
- Chat widget accepts queries
- System generates embeddings
- Vector search retrieves documents
- LLM generates response
- Input clears after submission

### US-002: Source Citations
- Response includes citations
- Sources are visible and clickable
- All relevant sources are cited

### US-003: Shipping Tool Routing
- System identifies shipping queries
- Shipping tool is invoked
- Results are synthesized into response

### US-004: Escalation Button
- Button appears when confidence < 60%
- Button is clickable
- Context transfers to human agent

### US-005: Multi-Turn Context
- Session history is maintained
- System understands pronouns
- Previous messages are available

### US-006: Tool Coordination
- Multiple tools identified and run
- Results synthesized into single response
- Both source types cited

### US-007: Error Handling
- Invalid inputs rejected gracefully
- Helpful error messages shown
- User can retry after error

### US-008: Session Persistence
- Session data stored locally/server
- Previous messages visible after reload
- Conversation history preserved

### US-009: Responsive Design
- Works on mobile (375x667)
- Works on tablet (768x1024)
- Works on desktop
- No horizontal scrolling

### US-010: Special Characters
- Emoji render correctly
- Symbols don't escape
- Accents display correctly
- Mixed languages supported

### US-011: Keyboard Accessibility
- Enter key sends message
- Tab navigation works
- Interactive elements reachable

### US-012: Message Timestamps
- Each message has timestamp
- Format is consistent
- Timestamps are accurate

### US-013: Confidence Indicator
- High confidence shows positive indicator
- Medium confidence shows neutral
- Low confidence shows warning
- Indicator is visible

---

## Common Questions

### Q: Where do I find the test for my story?
A: Check the story file's "Test Reference" section. It lists the line numbers in `frontend/e2e/chat-flow.spec.ts`.

### Q: How do I know which stories depend on mine?
A: Check TRACEABILITY_MATRIX.md under "Cross-Story Dependencies".

### Q: What files should I modify for my feature?
A: Check TRACEABILITY_MATRIX.md "Implementation File Mapping" section. Look for your story ID.

### Q: How many acceptance criteria should I test?
A: Each story has 5-7 criteria. All must be tested. See the story file for the complete list.

### Q: What's the acceptance criteria format?
A: BDD-style Given-When-Then format. Example:
```
Given the chat widget is open, when I send a message, then the input clears
```

### Q: How do I trace my implementation to requirements?
A: Use the story file's "Implementation" section to see which code files are relevant.

### Q: Where's the source E2E test?
A: `frontend/e2e/chat-flow.spec.ts`. Each story references specific line numbers.

---

## Document Index

| Document | Purpose | For Whom |
|----------|---------|----------|
| README.md | Overview and index | Everyone |
| EPIC-00X.md | Feature area definitions | Architects, PMs |
| US-00X.md | Detailed requirements | Developers, QA |
| TRACEABILITY_MATRIX.md | Complete mapping | Project leads, QA |
| REQUIREMENTS_EXTRACTION_REPORT.md | Executive summary | Managers, team leads |
| QUICK_REFERENCE.md | This guide | Everyone |

---

## Next Steps

1. **Identify your role above**
2. **Go to the "Starting Points" section**
3. **Follow the recommended reading order**
4. **Reference the Quick Lookup sections as needed**
5. **Use TRACEABILITY_MATRIX.md for detailed mappings**
6. **Check individual story files for acceptance criteria**

All documentation is interconnected. Use cross-references to navigate between files.

---

Generated: December 19, 2025
Source: frontend/e2e/chat-flow.spec.ts
Status: Complete and ready for use
