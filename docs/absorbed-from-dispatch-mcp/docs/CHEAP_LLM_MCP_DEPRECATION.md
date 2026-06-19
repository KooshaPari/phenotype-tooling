# cheap-llm-mcp Deprecation Notice (effective 2026-06-15)

**Status:** DEPRECATED. Use `dispatch-mcp` instead.

## Why
Per ADR-008 (docs/adr/2026-06-15/ADR-008-dispatch-mcp-sole-mcp-server.md), the Phenotype fleet consolidates MCP servers into `dispatch-mcp` as the sole MCP server. `cheap-llm-mcp` is folded in as an adapter pattern.

## Migration
- All Tier 1.0-T1.5 features are in `dispatch-mcp` (see `src/dispatch_mcp/server.py`)
- The `fireworks` provider (last added to cheap-llm-mcp) is now a first-class tier in `dispatch-mcp` (commit `3c92eeb` on 2026-06-11)
- The OpenAI-compat provider pattern in cheap-llm-mcp becomes a `provider.py` module in dispatch-mcp
- Reference: FLEET_100TASK_DAG_V3.md W1 wave, plan ID `W1-1`

## Removal timeline
- 2026-06-15: This deprecation notice published
- 2026-07-15: cheap-llm-mcp moves to archive/ directory
- 2026-09-15: cheap-llm-mcp GitHub repo archived (read-only)

## Pointers
- `dispatch-mcp` source: /Users/kooshapari/CodeProjects/Phenotype/repos/dispatch-mcp
- `cheap-llm-mcp` source (to be archived): /Users/kooshapari/CodeProjects/Phenotype/repos/cheap-llm-mcp
- V5 plan: /Users/kooshapari/CodeProjects/Phenotype/repos/plans/2026-06-15-CONSOLIDATED-DAG-V5.md
