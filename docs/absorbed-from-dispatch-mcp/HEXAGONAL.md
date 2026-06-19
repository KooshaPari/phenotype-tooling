# Hexagonal Architecture

This repository is moving toward a strict three-layer split inside
`src/dispatch_mcp`.

The intent is to keep domain and orchestration logic independent from transport
details and composition code.

The target package layout is:

- `dispatch_mcp/core` for domain rules, dispatch policies, validation, and
  use-case logic.
- `dispatch_mcp/adapters` for OmniRoute HTTP clients, environment-backed
  configuration readers, and other infrastructure-facing implementations.
- `dispatch_mcp/server` for FastMCP registration, process startup, signal
  handling, and wiring the application together.

The import direction is deliberately narrow.

Core is the innermost layer and must not import from adapters or server.
That keeps business logic testable and reusable without the MCP runtime.

Adapters may depend on core contracts and types, but adapters must not import
from server.
They should expose infrastructure capabilities without reaching into the
composition layer.

Server is the outer composition layer.
It is allowed to import from both core and adapters because it is responsible
for assembling the running application and exposing MCP tools.

No reverse dependency from inner layers to outer layers is allowed.
If a change requires core to call infrastructure code, introduce an interface or
data contract in core and implement it in adapters.

The repository enforces these rules with Import Linter through the
`.import-linter` file at the project root.
That contract is intended to fail fast when a refactor accidentally introduces a
cross-layer import.

As the codebase is decomposed from the current single-file server module,
new modules should be placed into one of these three layers instead of adding
more responsibilities to the composition entrypoint.
