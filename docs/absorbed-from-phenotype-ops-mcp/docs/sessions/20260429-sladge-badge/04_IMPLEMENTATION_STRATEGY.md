# Implementation Strategy

## Approach

Use a narrow prepared rollout:

- Add a visible README badge.
- Store session evidence under `docs/sessions/`.
- Avoid merging into the dirty canonical checkout.

## Rationale

The badge identifies an agent-facing MCP server while preserving unrelated local
dependency and documentation work.
