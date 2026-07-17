from fastapi import FastAPI, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from core.orchestrator import AIOrchestrator
from core.openai_compat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    convert_to_orchestration_request,
    convert_to_openai_response,
    stream_openai_response,
)
from sse_starlette.sse import EventSourceResponse
import uvicorn
import os
import logging
import time
import uuid
import json
import json
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

# Configure logging
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)

# Initialize FastAPI app
app = FastAPI(title="AI Orchestration API")

# Initialize orchestrator
orchestrator = AIOrchestrator("config/config.yaml")

# Mount static files
app.mount("/static", StaticFiles(directory="static"), name="static")


# Define request models
class AIRequest(BaseModel):
    prompt: str
    routing_policy: str = "default"
    max_tokens: int = 1000
    temperature: float = 0.7
    plugins: list = []


class PluginRequest(BaseModel):
    name: str
    endpoint: str
    capabilities: list
    description: str = None


# API routes
@app.get("/", response_class=HTMLResponse)
async def read_root(request: Request):
    with open("static/index.html", "r") as f:
        html_content = f.read()
    return HTMLResponse(content=html_content)


@app.post("/api/generate")
async def generate(request: AIRequest):
    try:
        response = orchestrator.process_request(request.model_dump())
        return response
    except Exception as e:
        logging.error(f"Error processing request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


@app.get("/api/plugins")
async def list_plugins():
    plugins = orchestrator.get_available_plugins()
    return {"plugins": plugins}


@app.post("/api/plugins/register")
async def register_plugin(plugin: PluginRequest):
    try:
        plugin_data = {
            "id": plugin.name.lower().replace(" ", "_"),
            "name": plugin.name,
            "endpoint": plugin.endpoint,
            "capabilities": plugin.capabilities,
            "description": plugin.description or f"{plugin.name} plugin",
        }

        # Register plugin
        plugin_id = orchestrator.mcp_registry.register_plugin(plugin_data)

        return {"status": "registered", "plugin_id": plugin_id}
    except Exception as e:
        logging.error(f"Error registering plugin: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


# OpenAI-compatible API routes
@app.post("/v1/chat/completions")
async def openai_chat_completions(request: ChatCompletionRequest):
    try:
        # Check if streaming is requested
        if request.stream:
            # For streaming responses, we need to use EventSourceResponse
            return EventSourceResponse(
                stream_response(request), media_type="text/event-stream"
            )
        else:
            # For regular responses, process normally
            # Convert the OpenAI request to our format
            orchestration_request = convert_to_orchestration_request(request)

            # Process the request
            orchestration_response = orchestrator.process_request(orchestration_request)

            # Convert the response back to OpenAI format
            openai_response = convert_to_openai_response(
                orchestration_response, request
            )

            return openai_response
    except Exception as e:
        logging.error(f"Error processing OpenAI-compatible request: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


async def stream_response(request: ChatCompletionRequest):
    """
    Stream a response for the OpenAI-compatible API.

    Args:
        request: The OpenAI API request.

    Yields:
        SSE formatted data chunks.
    """
    try:
        # Convert the OpenAI request to our format
        orchestration_request = convert_to_orchestration_request(request)

        # Process the request
        orchestration_response = orchestrator.process_request(orchestration_request)

        # Stream the response
        async for chunk in stream_openai_response(orchestration_response, request):
            yield chunk
    except Exception as e:
        logging.error(f"Error streaming response: {str(e)}")
        # Send an error message in SSE format
        error_message = {
            "error": {"message": str(e), "type": "server_error", "code": 500}
        }
        yield f"data: {json.dumps(error_message)}\n\n"
        yield "data: [DONE]\n\n"


@app.get("/v1/models")
async def openai_list_models():
    """List available models in OpenAI format."""
    try:
        # Get all available models from providers
        models = []
        seen_model_ids = set()  # Track seen model IDs to avoid duplicates

        # Add cloud provider models
        if hasattr(orchestrator.oblix_router, "cloud_providers"):
            for (
                provider_name,
                provider,
            ) in orchestrator.oblix_router.cloud_providers.items():
                provider_models = provider.get_models()
                if "models" in provider_models:
                    for model_name in provider_models["models"]:
                        # Handle OpenRouter models specially
                        if provider_name == "openrouter":
                            # OpenRouter models already have provider prefixes like "openai/gpt-4"
                            # We need to add "openrouter/" prefix for internal routing but remove it for display
                            # Extract the original model ID without the provider prefix
                            if "/" in model_name:
                                original_provider, model_id = model_name.split("/", 1)
                                # Check if this model ID already exists from a native provider
                                if model_id in seen_model_ids:
                                    # Use the OpenRouter version with a prefix to avoid collision
                                    display_id = f"openrouter/{model_name}"
                                else:
                                    # Use the original model ID if no collision
                                    display_id = model_id
                                    # For internal routing, we'll prepend "openrouter/" when needed
                            else:
                                # If no provider prefix, use as is
                                display_id = model_name
                        else:
                            # For non-OpenRouter providers, use the model name as is
                            display_id = model_name

                        # Skip if we've already seen this model ID
                        if display_id in seen_model_ids:
                            continue

                        # Add the model to the list
                        models.append(
                            {
                                "id": display_id,
                                "object": "model",
                                "created": int(time.time()),
                                "owned_by": (
                                    provider_name
                                    if provider_name != "openrouter"
                                    else "openai"
                                ),
                            }
                        )
                        seen_model_ids.add(display_id)

        # Add edge provider models
        if hasattr(orchestrator.oblix_router, "edge_providers"):
            for (
                provider_name,
                provider,
            ) in orchestrator.oblix_router.edge_providers.items():
                provider_models = provider.get_models()
                if "models" in provider_models:
                    for model_name in provider_models["models"]:
                        # Skip if we've already seen this model ID
                        if model_name in seen_model_ids:
                            continue

                        models.append(
                            {
                                "id": model_name,
                                "object": "model",
                                "created": int(time.time()),
                                "owned_by": provider_name,
                            }
                        )
                        seen_model_ids.add(model_name)

        return {"object": "list", "data": models}
    except Exception as e:
        logging.error(f"Error listing models: {str(e)}")
        raise HTTPException(status_code=500, detail=str(e))


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
