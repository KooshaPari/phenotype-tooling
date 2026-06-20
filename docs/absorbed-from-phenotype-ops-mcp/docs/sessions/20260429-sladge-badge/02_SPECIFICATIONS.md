# Specifications

## Acceptance Criteria

- README includes exactly one `sladge.net` badge reference.
- The change is documentation-only.
- Canonical dirty checkout remains untouched.
- The commit includes the required Codex co-author trailer.

## Assumptions, Risks, Uncertainties

- Assumption: An MCP server configured for Claude agent access is in scope.
- Risk: The canonical checkout's active dependency/doc work may be based on a
  branch newer than `main`.
- Mitigation: Commit only to an isolated prepared branch and record merge status
  in projects-landing.
