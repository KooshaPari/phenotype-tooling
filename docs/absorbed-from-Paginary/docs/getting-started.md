# Paginary Getting Started

## Why Paginary?

Paginary is the knowledge hub of the Phenotype ecosystem: a federated documentation system bringing together **Handbooks** (operational guides), **Specs** (feature designs and ADRs), **X-Driven Dev** (quality governance and test patterns), and **Journeys** (user workflows). As a TypeScript/Vue 3 collection powered by VitePress, Paginary documents not just *what* the collections do, but *how* to use them together—with live examples and event-driven workflows.

**Key problems Paginary solves:**

- **Unified documentation** — No scattered wikis; all knowledge in one searchable hub
- **Workflow documentation** — Document cross-collection event flows (dispatch → automation → tracing → caching)
- **Quality governance** — Centralize test strategy, spec traceability, TDD patterns
- **Developer onboarding** — Quick-start guides, architecture diagrams, runnable examples
- **Integration with collections** — MCP adapters (planned) for Node.js event bus subscriptions

## Install

Paginary uses `bun` package manager:

```bash
bun install
bun run dev
```

Or fine-grained install:

```bash
bun add vitepress vue
bun add typescript
```

Project structure:

```toml
# package.json
{
  "name": "@phenotype/paginary",
  "packageManager": "bun@latest",
  "scripts": {
    "dev": "vitepress dev .",
    "build": "vitepress build .",
    "preview": "vitepress preview ."
  }
}
```

## Quickstart (20 lines)

```bash
# Start the dev server
cd /Users/kooshapari/CodeProjects/Phenotype/repos/Paginary
bun install
bun run dev

# Open in browser
# Handbook: http://localhost:5173/handbook/
# Specs: http://localhost:5174/specs/
# X-Driven Dev: http://localhost:5175/xdd/
# Journeys: http://localhost:5176/journeys/
```

Create a new spec:

```markdown
# Feature: User Status Tracking

## Overview
Sidekick tracks agent presence (online, away, focus, inactive) across distributed systems.

## Events (phenotype-bus)
- `UserStatusChanged` — emitted by sidekick-presence
- Consumed by: Eidolon (triggers automation on online), Observably (traces status changes)

## Workflow
1. Agent comes online → UserStatusChanged published
2. Eidolon listens → triggers automation
3. Observably traces → emits metrics
4. Stashly stores → event log
```

## Common Patterns

### Pattern 1: Document Cross-Collection Workflows

Visualize how collections interact via phenotype-bus:

```markdown
# Workflow: Dispatch → Automation → Caching → Tracing

## Event Flow

```
┌─────────────────────────────────────────────────────┐
│ 1. Sidekick: User status changes                    │
│    → DispatchStarted event published                │
└────────────────────┬────────────────────────────────┘
                     │ phenotype-bus
┌────────────────────▼────────────────────────────────┐
│ 2. Eidolon: Subscribes to DispatchStarted          │
│    → Takes screenshot (before.png)                  │
│    → Clicks button                                  │
│    → Takes screenshot (after.png)                   │
│    → AutomationCompleted event published            │
└────────────────────┬────────────────────────────────┘
                     │ phenotype-bus
┌────────────────────▼────────────────────────────────┐
│ 3. Stashly: Subscribes to AutomationCompleted      │
│    → Caches screenshots (2-tier LRU + TTL)         │
│    → Appends to event log (hash chain)             │
│    → ScreenshotCached event published              │
└────────────────────┬────────────────────────────────┘
                     │ phenotype-bus
┌────────────────────▼────────────────────────────────┐
│ 4. Observably: Subscribes to ScreenshotCached      │
│    → Records distributed trace                      │
│    → PII filtering on metadata                      │
│    → TraceRecorded event published                 │
└────────────────────┬────────────────────────────────┘
                     │ phenotype-bus
┌────────────────────▼────────────────────────────────┐
│ 5. Sidekick: Messaging notifies user                │
│    → "Screenshot cached, trace recorded"            │
└─────────────────────────────────────────────────────┘
```
```

### Pattern 2: Spec Traceability Matrix

Link specifications to tests in each collection:

```markdown
# Spec Traceability: Caching

| Spec ID | Feature | Test (Stashly) | Test (Observably) |
|---------|---------|----------------|--------------------|
| CACHE-001 | LRU eviction | `test_lru_evicts_oldest` | `test_cache_metrics` |
| CACHE-002 | TTL expiration | `test_ttl_expires` | `test_ttl_trace` |
| CACHE-003 | Two-tier persistence | `test_mem_to_disk` | `test_persistence_trace` |
```

### Pattern 3: X-Driven Dev Guidance

Document TDD, BDD, and smart contract patterns:

```markdown
# Test-First Mandate: Sidekick Dispatch

## Smart Contract Pattern

**Contract:** If a dispatch request is sent with provider="minimax", 
the response must be received within 2 seconds and cost < $0.01.

```rust
// tests/dispatch_minimax.rs
#[tokio::test]
async fn test_dispatch_minimax_budget_constraint() {
    let dispatcher = Dispatcher::new();
    let request = DispatchRequest::new("agent", "summarize...")
        .with_provider_hint(Provider::Minimax);
    
    let start = Instant::now();
    let response = dispatcher.dispatch(request).await.unwrap();
    let elapsed = start.elapsed();
    
    assert!(elapsed < Duration::from_secs(2), "Response too slow");
    assert!(response.cost_cents < 1, "Cost exceeded budget");
}
```

## Acceptance Criteria
- [x] Response latency < 2s
- [x] Cost < $0.01
- [x] Fallback to Kimi if Minimax unavailable
- [x] Trace recorded with provider name
```

### Pattern 4: Handbook: Runnable Workflow Examples

Embed runnable examples and screenshots:

```markdown
# Handbook: Desktop Automation Workflow

## Getting Started with Eidolon

1. Install Eidolon:
```bash
cargo add eidolon-desktop
```

2. Take your first screenshot:
```rust
let automator = DesktopClient::new()?;
automator.screenshot("./first-screenshot.png").await?;
```

3. See the result in `./first-screenshot.png`

## Common Gotchas
- Desktop automation requires accessibility permissions (macOS)
- Screenshots are always synchronous; use tokio::spawn for parallel captures
```

## Cross-Collection Integration

Paginary documents and indexes all Phenotype collections via **phenotype-bus**:

- **Documents**: Event schemas, workflows, specifications for Sidekick, Eidolon, Observably, Stashly
- **Produces**: Live examples, architecture diagrams, acceptance criteria
- **Consumes**: None directly (planned: MCP Node.js adapters for event subscription)

See [phenotype-bus](../../phenotype-bus/README.md) for event reference. Paginary is the documentation hub for [Sidekick](../Sidekick/README.md), [Eidolon](../Eidolon/README.md), [Observably](../Observably/README.md), and [Stashly](../Stashly/README.md).

## Next Steps

- Explore the [Handbook](./handbook/)
- Review [Specifications](./specs/)
- Study [X-Driven Dev patterns](./xdd/)
- Follow [User Journeys](./journeys/)
- Check the [cross-collection demo](../../docs/collections/cross_collection_demo.md)
