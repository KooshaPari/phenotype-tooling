# phenotype-request-id

Zero-dep request-ID propagation (contextvars) for Python ASGI services,
with optional FastAPI/Starlette middleware and structlog binder.

## Layout
- `src/phenotype_request_id/context.py` — `ContextVar` store (zero deps)
- `src/phenotype_request_id/fastapi.py` — ASGI middleware (lazy import of starlette)
- `src/phenotype_request_id/logging.py` — structlog binder (lazy import)
- `tests/test_context.py` — stdlib-only tests
- `tests/test_middleware.py` — auto-skips when fastapi/httpx absent

## Conventions
- Core must remain zero-dep. All optional integrations via lazy import.
- No class larger than 50 lines.
- Use `contextvars` (stdlib), not `threading.local`.
