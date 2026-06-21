# EPIC-002: Intelligent Query Routing

## Description
Implement intelligent query routing that automatically detects query types and routes them to the appropriate tools (shipping calculator, knowledge base, product catalog, etc.). The system should analyze query intent and coordinate multiple tools when needed.

## User Stories
- US-003: Automatic tool selection for shipping queries
- US-005: Tool coordination - KB + Shipping

## Acceptance Criteria
- [ ] System identifies shipping-related queries
- [ ] Shipping tool is invoked for shipping queries
- [ ] System can coordinate multiple tools in single query
- [ ] Results from multiple tools are synthesized
- [ ] Query intent detection is accurate (>85%)
- [ ] Tool selection is transparent to user
