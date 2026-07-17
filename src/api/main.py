"""
Main FastAPI application for the SWE Agent.
"""

# Import Pydantic compatibility layer first to ensure patches are applied
# before any other imports that might use Pydantic
from ..utils.pydantic_compat import apply_pydantic_patches

apply_pydantic_patches()

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import time
import uuid
from prometheus_client import Counter, Histogram, generate_latest, CONTENT_TYPE_LATEST
from fastapi.responses import Response as FastAPIResponse

# Import routers
from . import models_api
from . import chat_api
from . import agents_api
from . import cache_api

# Import MCP client for initialization
from ..mcp.client import initialize_mcp_client, close_mcp_client

# Import logging
from ..utils.logging import logger, request_logger

# Prometheus metrics
REQUEST_COUNT = Counter(
    "http_requests_total", "Total HTTP Requests Count", ["method", "endpoint", "status"]
)
REQUEST_LATENCY = Histogram(
    "http_request_duration_seconds", "HTTP Request Latency", ["method", "endpoint"]
)

# Prompt cache metrics
CACHE_HIT_COUNT = Counter(
    "prompt_cache_hits_total", "Total Prompt Cache Hits", ["model"]
)
CACHE_MISS_COUNT = Counter(
    "prompt_cache_misses_total", "Total Prompt Cache Misses", ["model"]
)
CACHE_HIT_TOKENS = Counter(
    "prompt_cache_hit_tokens_total", "Total Tokens Read from Cache", ["model"]
)
CACHE_WRITE_TOKENS = Counter(
    "prompt_cache_write_tokens_total", "Total Tokens Written to Cache", ["model"]
)
CACHE_COST_SAVED = Counter(
    "prompt_cache_cost_saved_dollars", "Total Cost Saved by Cache in Dollars", ["model"]
)


# Lifespan for FastAPI application
@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for the FastAPI application.

    Args:
        app: The FastAPI application.
    """
    # Initialize resources
    logger.info("Starting up the SWE Agent API...")
    await initialize_mcp_client()

    yield

    # Clean up resources
    logger.info("Shutting down the SWE Agent API...")
    await close_mcp_client()


# Create the FastAPI application
app = FastAPI(
    title="SWE Agent API",
    description="API for interacting with the SWE Agent, compliant with OpenAI standards and providing agent management.",
    version="0.1.0",
    lifespan=lifespan,
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify the allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Add middleware for request timing and logging
@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    """
    Middleware to add process time header and log requests.

    Args:
        request: The request.
        call_next: The next middleware or route handler.

    Returns:
        The response.
    """
    # Generate a request ID
    request_id = str(uuid.uuid4())

    # Extract request details
    method = request.method
    url = str(request.url)
    endpoint = request.url.path

    # Start timer
    start_time = time.time()

    # Log the request
    logger.info(f"Request {request_id}: {method} {url}")

    # Start the latency timer
    with REQUEST_LATENCY.labels(method=method, endpoint=endpoint).time():
        # Process the request
        try:
            response = await call_next(request)

            # Log the response
            process_time = time.time() - start_time
            status_code = response.status_code
            logger.info(f"Response {request_id}: {status_code} in {process_time:.4f}s")

            # Update metrics
            REQUEST_COUNT.labels(
                method=method, endpoint=endpoint, status=status_code
            ).inc()

            # Add custom headers
            response.headers["X-Process-Time"] = str(process_time)
            response.headers["X-Request-ID"] = request_id

            return response
        except Exception as e:
            # Log the error
            process_time = time.time() - start_time
            logger.error(f"Error {request_id}: {str(e)} in {process_time:.4f}s")

            # Update metrics
            REQUEST_COUNT.labels(method=method, endpoint=endpoint, status=500).inc()

            # Re-raise the exception
            raise


# Include routers with /api prefix (for backward compatibility)
app.include_router(models_api.router, prefix="/api")
app.include_router(chat_api.router, prefix="/api")
app.include_router(agents_api.router, prefix="/api")
app.include_router(cache_api.router, prefix="/api")

# Include routers without prefix for direct OpenAI-compatible access
app.include_router(models_api.router)  # For /v1/models
app.include_router(chat_api.router)  # For /v1/chat/completions
app.include_router(agents_api.router)  # For /v1/agents
app.include_router(cache_api.router)  # For /v1/cache


# Add metrics endpoint
@app.get("/metrics", tags=["Monitoring"])
async def metrics():
    """
    Endpoint for Prometheus metrics.

    Returns:
        Prometheus metrics.
    """
    return FastAPIResponse(content=generate_latest(), media_type=CONTENT_TYPE_LATEST)


@app.get("/", tags=["General"])
async def read_root():
    """
    Root endpoint that returns a welcome message.

    Returns:
        A welcome message.
    """
    return {
        "message": "Welcome to the SWE Agent API. See /docs or /api/docs for API documentation."
    }


if __name__ == "__main__":
    import uvicorn

    # This is for local development. For deployment, use a proper ASGI server like Uvicorn or Hypercorn.
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
    )
