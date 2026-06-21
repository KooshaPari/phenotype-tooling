# Journey Traceability

Implements the [phenotype-infra journey-traceability standard](https://github.com/kooshapari/phenotype-infra/blob/main/docs/governance/journey-traceability-standard.md).

## Traceability Model

Every user-facing flow should be traceable across:

1. **FR/NFR** — requirement ID and user story.
2. **Spec** — acceptance criteria and non-regression constraints.
3. **Docs** — operator/user documentation and rich media placeholders.
4. **Code** — frontend, MCP, agent, or commerce integration surface implementing the flow.
5. **Tests/Gates** — unit, integration, BDD, lint, and journey verification acting as autograders.
6. **Evidence** — journey manifest, recording/keyframes, and evaluation verdict.

## User-Facing Flows

| Flow | Requirement | Implementation surface | Autograder gates | Evidence status |
| --- | --- | --- | --- | --- |
| Shopper asks the chat UI for product guidance | FR-4SGM-CHAT-001, NFR-4SGM-LATENCY-001 | Next.js Chat UI, MCP FastMCP server, Router/ReAct agent | chat component tests, MCP tool contract tests, BDD journey, eval verdict | Stubbed |
| Shopper discovers and compares product cards | FR-4SGM-PRODUCT-001, NFR-4SGM-ACCESSIBILITY-001 | Next.js product cards, API/product data adapters | UI snapshot/a11y tests, product fixture tests, journey manifest | Stubbed |
| Admin reviews dashboard health and commerce signals | FR-4SGM-ADMIN-001, NFR-4SGM-OBSERVABILITY-001 | Admin Dashboard, MCP Tool Registry, observability hooks | dashboard smoke tests, metric/log assertions, journey eval | Stubbed |
| OAuth-backed MCP tool call completes safely | FR-4SGM-MCP-001, NFR-4SGM-SECURITY-001 | OAuth/Auth handler, FastMCP server, tool registry, scope checks | OAuth contract tests, MCP tool tests, security fixture tests, journey manifest | Stubbed |

## Rich Media Stubs

<!-- RICH-MEDIA-STUB type="animated-gif" subject="Shopper chat guidance and product comparison" journey="chat-product-comparison" status="TODO" -->
![QuadSGM shopper chat — user prompt, agent reasoning, product cards, and comparison result](../assets/rich-media/quadsgm/chat-product-comparison.gif)

*Expected capture: send a shopper prompt, follow the ReAct agent through reasoning, view matched product cards, and confirm the comparison result is rendered with accessibility cues.*

<!-- RICH-MEDIA-STUB type="annotated-screenshot" subject="Admin dashboard health and commerce signals" journey="admin-dashboard-health" status="TODO" -->
![QuadSGM admin dashboard — health, tool registry, commerce signals, and operator action](../assets/rich-media/quadsgm/admin-dashboard-health.png)

*Expected capture: open the admin dashboard, annotate health/tool-registry/commerce signals, and verify operator actions affect downstream tool state.*

<!-- RICH-MEDIA-STUB type="journey-eval" subject="OAuth-backed MCP tool call verdict" journey="oauth-mcp-tool-call" status="TODO" -->
![QuadSGM OAuth MCP — token, scope check, tool call, response, and eval verdict](../assets/rich-media/quadsgm/oauth-mcp-tool-call.png)

*Expected capture: acquire a scoped OAuth token, call a representative MCP tool, validate request/response schema, and attach a pass/fail security and contract verdict.*

## Journey Manifests

Journey manifests should live in `docs/journeys/manifests/` and include:

- FR/NFR IDs covered by the journey;
- API endpoint, UI route, or MCP tool entrypoint used to reproduce the flow;
- fixture product/cart data needed for deterministic replay;
- expected screenshots/GIFs/keyframes;
- tests and gates that must pass before the journey is accepted;
- eval verdict schema and pass/fail criteria.

## Autograder Gates

Minimum gates before marking a journey complete:

- UI component and a11y tests for shopper and admin surfaces;
- MCP tool contract tests for chat, product, and admin flows;
- OAuth/scope contract tests and security fixture tests;
- observability/trace assertions for admin signals;
- BDD journey replay for user-visible flows;
- doc link validation for every referenced rich media asset;
- journey manifest validation via `phenotype-journey verify` when available;
- eval verdict linked to the FR/NFR IDs in the manifest.

## Status

- [x] Identify initial shopper and admin user-facing flows
- [x] Stub rich media embeds for expected screenshots/GIFs/evals
- [ ] Author manifests in `docs/journeys/manifests/`
- [ ] Record journey captures for each flow
- [ ] Run `phenotype-journey verify` in CI
