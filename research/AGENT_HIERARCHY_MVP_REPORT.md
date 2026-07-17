# Research Report: Agent Hierarchy & Maximal MVP

> **WORK_STREAM IDs**:
> - research-agent-hierarchy-mvp ✅ Research Complete
> **Date**: 2026-02-19

## Executive Summary

The transition to a hierarchical agent architecture is essential for managing the complexity of `thegent` platform. This report outlines the design for "SmolGents" (lightweight, task-specific agents) coordinated by a central harness, leveraging the `codex`, `cc` (Compute Control), and `droid` (Direct Remote Orchestration & Interaction) layers.

## Key Research Findings

1. **SmolGents Architecture**: Specialized agents (e.g., `smol-fix`, `smol-search`, `smol-audit`) with minimal context and high efficiency.
2. **Harness Layer (`codex/cc/droid`)**:
   - **`codex`**: Shared knowledge base for agent coordination.
   - **`cc` (Compute Control)**: Resource allocation and sandboxing for SmolGents.
   - **`droid`**: Direct interface for remote execution and interaction.
3. **Maximal MVP**: A baseline implementation that integrates these layers to perform a complex, multi-step task (e.g., "Full-stack feature implementation with automated testing and documentation").

## Implementation Status

- **Architecture**: The hierarchical model is designed.
- **Integration**: Initial hooks for `cc` and `droid` exist in `src/thegent/`.

## Next Steps

1. Develop the `SmolGents` base class in `src/thegent/agents/`.
2. Implement the `codex` synchronization loop for shared state.
3. Prototype the `Maximal MVP` task flow using `LangGraph` for state management.

## Reference

Detailed design available in `SMOLGENTS_MVP_AND_LANGGRAPH_CC_VISION.md`.
