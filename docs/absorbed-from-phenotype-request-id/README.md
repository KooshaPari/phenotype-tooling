# phenotype-request-id

Zero-dependency request-ID propagation for Python ASGI services.

Most Python web stacks (FastAPI, Starlette, aiohttp) re-implement the same
`X-Request-Id` middleware pattern. `phenotype-request-id` provides the
shared core: a `contextvars`-backed store, an ASGI middleware, and
lazy optional integrations for FastAPI and structlog.

## Install

```bash
pip install phenotype-request-id              # core only (no deps)
pip install "phenotype-request-id[fastapi]"   # + FastAPI/Starlette
pip install "phenotype-request-id[structlog]" # + structlog binder
```

## Core (zero deps)

```python
from phenotype_request_id.context import (
    get_request_id,
    set_request_id,
    with_request_id,
)

with with_request_id("abc-123"):
    assert get_request_id() == "abc-123"
assert get_request_id() is None
```

## FastAPI / Starlette

```python
from fastapi import FastAPI
from phenotype_request_id.fastapi import RequestIdMiddleware

app = FastAPI()
app.add_middleware(RequestIdMiddleware)
```

The middleware reads `X-Request-Id` from the incoming request (or
generates a UUID4), stores it in a `ContextVar`, and echoes it on the
response.

## structlog

```python
import structlog
from phenotype_request_id.logging import bind_request_id

log = bind_request_id(structlog.get_logger())
log.info("hello")  # automatically includes request_id when in scope
```

If `structlog` is not installed, `bind_request_id` returns the logger
unchanged (lazy import, no crash).

## Documentation

This repository includes the following cross-cutting documents:

- [`AGENTS.md`](AGENTS.md) — operating instructions for AI agents and human contributors

