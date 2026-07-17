from fastapi import FastAPI, HTTPException, Request, Depends
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel
from core.orchestrator import AIOrchestrator
from core.openai_compat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    convert_to_orchestration_request,
    convert_to_openai_response,
)
import uvicorn
import os
import logging
import time
import uuid
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
        response = orchestrator.process_request(request.dict())
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


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=9000)
