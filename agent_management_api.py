#!/usr/bin/env python3
"""
Agent Management REST API

This provides a REST API for the centralized agent management system,
enabling programmatic control of agents for dashboard integration and automation.
"""

import asyncio
import sys
import os
from pathlib import Path
from typing import Dict, List, Any, Optional
import uvicorn
from fastapi import FastAPI, HTTPException, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import logging

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.centralized_agent_manager import centralized_agent_manager
from src.services.agent_communication import send_message_to_agent

# Logging setup
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# FastAPI app
app = FastAPI(
    title="Agent Management API",
    description="REST API for centralized agent management",
    version="1.0.0"
)

# CORS middleware for dashboard integration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Pydantic models for API requests
class CreateAgentRequest(BaseModel):
    name: str
    role: str
    model_name: str = "gpt-4o-mini"
    description: Optional[str] = None
    system_prompt: Optional[str] = None
    temperature: float = 0.7
    max_tools: int = 128
    capabilities: Optional[List[str]] = None
    launch_process: bool = True

class SendMessageRequest(BaseModel):
    sender_id: str
    recipient_id: str
    content: str
    message_type: str = "text"

class AssignTaskRequest(BaseModel):
    sender_id: str
    recipient_id: str
    task_title: str
    task_description: str
    priority: str = "medium"
    deadline: Optional[str] = None

# API Routes

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "message": "Agent Management API",
        "version": "1.0.0",
        "endpoints": {
            "agents": "/agents",
            "create_agent": "/agents",
            "get_agent": "/agents/{agent_id}",
            "health_check": "/agents/{agent_id}/health",
            "send_message": "/agents/message",
            "assign_task": "/agents/task"
        }
    }

@app.get("/agents")
async def list_agents():
    """List all agents."""
    try:
        agents = centralized_agent_manager.list_agents()
        return {
            "success": True,
            "agents": agents,
            "total_count": len(agents)
        }
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents")
async def create_agent(request: CreateAgentRequest, background_tasks: BackgroundTasks):
    """Create a new agent."""
    try:
        result = await centralized_agent_manager.create_agent(
            name=request.name,
            role=request.role,
            model_name=request.model_name,
            description=request.description,
            system_prompt=request.system_prompt,
            temperature=request.temperature,
            max_tools=request.max_tools,
            capabilities=request.capabilities or [],
            launch_process=request.launch_process
        )
        
        if "error" in result:
            raise HTTPException(status_code=400, detail=result["error"])
        
        return {
            "success": True,
            "agent": result
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_id}")
async def get_agent(agent_id: str):
    """Get details about a specific agent."""
    try:
        agent = await centralized_agent_manager.get_agent(agent_id)
        if agent is None:
            raise HTTPException(status_code=404, detail="Agent not found")
        
        return {
            "success": True,
            "agent": agent
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/agents/{agent_id}/health")
async def check_agent_health(agent_id: str):
    """Check the health of a specific agent."""
    try:
        health = await centralized_agent_manager.health_check(agent_id)
        return {
            "success": True,
            "health": health
        }
    except Exception as e:
        logger.error(f"Error checking health of agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.delete("/agents/{agent_id}")
async def terminate_agent(agent_id: str):
    """Terminate an agent."""
    try:
        result = await centralized_agent_manager.terminate_agent(agent_id)
        return {
            "success": result.get("success", False),
            "message": result.get("message", result.get("error", "Unknown error"))
        }
    except Exception as e:
        logger.error(f"Error terminating agent {agent_id}: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/message")
async def send_message(request: SendMessageRequest):
    """Send a message between agents."""
    try:
        result = await send_message_to_agent(
            sender_id=request.sender_id,
            recipient_id=request.recipient_id,
            content=request.content,
            message_type=request.message_type
        )
        
        return {
            "success": True,
            "message": result
        }
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/agents/task")
async def assign_task(request: AssignTaskRequest):
    """Assign a task to an agent."""
    try:
        # Create task message
        task_content = f"""Task Assignment:
Title: {request.task_title}
Description: {request.task_description}
Priority: {request.priority}
Deadline: {request.deadline or 'Not specified'}

Please acknowledge receipt and provide an estimated completion time."""
        
        result = await send_message_to_agent(
            sender_id=request.sender_id,
            recipient_id=request.recipient_id,
            content=task_content,
            message_type="task"
        )
        
        return {
            "success": True,
            "task_assignment": {
                "message_id": result.get("message_id"),
                "task_title": request.task_title,
                "assigned_to": request.recipient_id,
                "assigned_by": request.sender_id,
                "priority": request.priority,
                "deadline": request.deadline
            }
        }
    except Exception as e:
        logger.error(f"Error assigning task: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/health")
async def api_health():
    """API health check."""
    return {
        "status": "healthy",
        "service": "Agent Management API",
        "version": "1.0.0"
    }

@app.get("/stats")
async def get_stats():
    """Get platform statistics."""
    try:
        agents = centralized_agent_manager.list_agents()
        
        # Count agents by status
        status_counts = {}
        for agent in agents:
            status = agent.get("status", "unknown")
            status_counts[status] = status_counts.get(status, 0) + 1
        
        # Count agents by role
        role_counts = {}
        for agent in agents:
            role = agent.get("config", {}).get("role", "unknown")
            role_counts[role] = role_counts.get(role, 0) + 1
        
        return {
            "success": True,
            "stats": {
                "total_agents": len(agents),
                "status_breakdown": status_counts,
                "role_breakdown": role_counts,
                "platform_status": "operational"
            }
        }
    except Exception as e:
        logger.error(f"Error getting stats: {e}")
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    logger.info("🚀 Starting Agent Management API Server")
    logger.info("📡 API will be available at: http://localhost:8000")
    logger.info("📚 API documentation at: http://localhost:8000/docs")
    logger.info("🔧 Dashboard can connect to this API for agent management")
    
    uvicorn.run(
        "agent_management_api:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
