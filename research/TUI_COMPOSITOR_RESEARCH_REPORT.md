# Research Report: TUI Compositor & Multiplexer

> **WORK_STREAM ID**: research-tui-compositor
> **Status**: ✅ Research Phase Complete
> **Date**: 2026-02-19

## Executive Summary

The research for a TUI compositor and multiplexer for "Sitback" and enhanced UX is complete. The recommended architecture combines robust multiplexing (Zellij/tmux) with a GUI-like Python TUI layer (Textual).

## Key Findings

1. **Multiplexers**: Zellij is the primary recommendation due to its plugin architecture and floating pane support. tmux is the secondary fallback.
2. **GUI Layer**: Textual (Python) is selected for the high-level menu system, status bars, and dialogs.
3. **Integration**: A Textual application will host the compositor or run as a Zellij plugin to provide a unified "Terminal App" experience.
4. **Basic Implementation**: Initial patterns exist in `ux/compositor.py`.

## Implementation Status

- **Compositor**: Zellij integration verified.
- **TUI Framework**: Textual selected and basic components designed.
- **Layout**: Layered model (GUI menu -> Compositor -> PTY) defined.

## Next Steps

1. Implement the `CompositorManager` in `src/thegent/ux/compositor.py`.
2. Develop the Textual-based menu system.
3. Create Zellij layout templates for different agent modes.

## Reference

Detailed research available in [CONVERSATION_DUMP_2026-02-16.md](./CONVERSATION_DUMP_2026-02-16.md) and [UNIFIED_SYSTEM_APPLICATION_PLAN.md](../plans/UNIFIED_SYSTEM_APPLICATION_PLAN.md).
