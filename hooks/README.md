# Claude Code Observability Hooks

Wires `anthropic-usage-poll`, `agent-forecast`, and `temporal-grounding` into
Claude Code via a PreToolUse hook.

## Installing hooks

```bash
cargo install --path bin/hook-entry
```

Then copy (or merge) `hooks/settings.local.json` into `~/.claude/settings.local.json`.

## How it works

On every tool use, `hook-entry` reads `~/.claude/usage.json` (written by the
`anthropic-usage-poll` daemon) and injects a one-line budget summary:

```
[observability] daily_remaining=50000 monthly_remaining=1200000 | forecast=p50:3200 p90:8100 | elapsed=23s | updated=2024-01-01T12:00:00Z
```

Run `anthropic-usage-poll` as a background daemon and call `agent-start-stamp`
at the start of each session for full triad coverage.
