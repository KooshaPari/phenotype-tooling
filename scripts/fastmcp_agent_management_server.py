#!/usr/bin/env python3
"""
FastMCP-based agent management server.

This server provides tools for managing agents and their prompts,
integrating with the existing agent management system.
"""

import os
import sys
import json
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("agent-management-server")

# Add the parent directory to the path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

try:
    from fastmcp import FastMCP, Context
    logger.info("Successfully imported FastMCP")
except ImportError:
    logger.error("Failed to import FastMCP. Please install it with 'pip install fastmcp'")
    sys.exit(1)

# Import agent management services
try:
    from src.services.agent_manager import agent_manager
    from src.services.agent_communication import communication_hub
    logger.info("Successfully imported agent management services")
except ImportError:
    logger.error("Failed to import agent management services")
    sys.exit(1)

# Create the FastMCP server
mcp = FastMCP(
    name="Agent Management",
    description="Tools for managing agents and their communication"
)

# In-memory storage for prompts
prompts_storage = {
    "default": {
        "id": "default",
        "name": "Default Prompt",
        "content": "You are a helpful AI assistant.",
        "description": "The default system prompt for the agent.",
        "created_at": "2025-05-20T00:00:00Z",
        "updated_at": "2025-05-20T00:00:00Z"
    },
    "developer": {
        "id": "developer",
        "name": "Developer Prompt",
        "content": "You are a helpful AI assistant specialized in software development.",
        "description": "A system prompt for software development tasks.",
        "created_at": "2025-05-20T00:00:00Z",
        "updated_at": "2025-05-20T00:00:00Z"
    }
}

# Agent Management Tools

@mcp.tool(
    annotations={
        "title": "Create Agent",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False
    }
)
async def create_agent(
    name: str,
    model_name: str,
    system_prompt: Optional[str] = None,
    description: Optional[str] = None,
    temperature: float = 0.7,
    max_tools: int = 128
) -> Dict[str, Any]:
    """Create a new agent with the specified parameters.
    
    Args:
        name: The name of the agent
        model_name: The name of the model to use
        system_prompt: Optional custom system prompt to use
        description: Optional description of the agent
        temperature: The temperature to use for generation
        max_tools: Maximum number of tools to use
        
    Returns:
        The created agent configuration
    """
    logger.info(f"Creating agent: {name} with model: {model_name}")
    
    try:
        result = await agent_manager.create_agent(
            name=name,
            model_name=model_name,
            system_prompt=system_prompt,
            description=description,
            temperature=temperature,
            max_tools=max_tools
        )
        
        return result
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        return {"error": str(e)}

@mcp.tool(
    annotations={
        "title": "Get Agent",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
async def get_agent(agent_id: str) -> Dict[str, Any]:
    """Get an agent by ID.
    
    Args:
        agent_id: The agent ID
        
    Returns:
        The agent configuration
    """
    logger.info(f"Getting agent: {agent_id}")
    
    try:
        result = await agent_manager.get_agent(agent_id)
        
        if result:
            return result
        else:
            return {"error": f"Agent with ID '{agent_id}' not found"}
    except Exception as e:
        logger.error(f"Error getting agent: {e}")
        return {"error": str(e)}

@mcp.tool(
    annotations={
        "title": "List Agents",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
async def list_agents() -> Dict[str, List[Dict[str, Any]]]:
    """List all agents.
    
    Returns:
        A list of agent configurations
    """
    logger.info("Listing agents")
    
    try:
        result = await agent_manager.list_agents()
        
        return {"agents": result}
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        return {"error": str(e)}

@mcp.tool(
    annotations={
        "title": "Update Agent",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False
    }
)
async def update_agent(
    agent_id: str,
    name: Optional[str] = None,
    system_prompt: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None
) -> Dict[str, Any]:
    """Update an existing agent.
    
    Args:
        agent_id: The agent ID
        name: Optional new name for the agent
        system_prompt: Optional new system prompt for the agent
        description: Optional new description for the agent
        status: Optional new status for the agent
        
    Returns:
        The updated agent configuration
    """
    logger.info(f"Updating agent: {agent_id}")
    
    try:
        # Prepare the update data
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if system_prompt is not None:
            update_data["initial_prompt"] = system_prompt
        if description is not None:
            update_data["description"] = description
        if status is not None:
            update_data["status"] = status
        
        result = await agent_manager.update_agent(agent_id, update_data)
        
        if result:
            return result
        else:
            return {"error": f"Agent with ID '{agent_id}' not found"}
    except Exception as e:
        logger.error(f"Error updating agent: {e}")
        return {"error": str(e)}

@mcp.tool(
    annotations={
        "title": "Delete Agent",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def delete_agent(agent_id: str) -> Dict[str, bool]:
    """Delete an agent.
    
    Args:
        agent_id: The agent ID
        
    Returns:
        A success indicator
    """
    logger.info(f"Deleting agent: {agent_id}")
    
    try:
        result = await agent_manager.delete_agent(agent_id)
        
        return {"success": result}
    except Exception as e:
        logger.error(f"Error deleting agent: {e}")
        return {"error": str(e)}

# Agent Communication Tools

@mcp.tool(
    annotations={
        "title": "Send Message",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False
    }
)
async def send_message(
    sender_id: str,
    recipient_id: str,
    content: str,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Send a message from one agent to another.
    
    Args:
        sender_id: The sender agent ID
        recipient_id: The recipient agent ID
        content: The message content
        metadata: Optional message metadata
        
    Returns:
        The message that was sent
    """
    logger.info(f"Sending message from {sender_id} to {recipient_id}")
    
    try:
        result = await communication_hub.send_message(
            sender_id=sender_id,
            recipient_id=recipient_id,
            content=content,
            metadata=metadata
        )
        
        return result
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return {"error": str(e)}

@mcp.tool(
    annotations={
        "title": "Broadcast Message",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False
    }
)
async def broadcast_message(
    sender_id: str,
    content: str,
    recipient_ids: Optional[List[str]] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, List[Dict[str, Any]]]:
    """Broadcast a message to multiple agents.
    
    Args:
        sender_id: The sender agent ID
        content: The message content
        recipient_ids: Optional list of recipient agent IDs. If not provided, send to all agents.
        metadata: Optional message metadata
        
    Returns:
        A list of messages that were sent
    """
    logger.info(f"Broadcasting message from {sender_id}")
    
    try:
        result = await communication_hub.broadcast_message(
            sender_id=sender_id,
            content=content,
            recipient_ids=recipient_ids,
            metadata=metadata
        )
        
        return {"messages": result}
    except Exception as e:
        logger.error(f"Error broadcasting message: {e}")
        return {"error": str(e)}

# Main entry point
if __name__ == "__main__":
    # Print environment variables for debugging
    logger.info("Environment variables:")
    for key, value in os.environ.items():
        if key.startswith("MCP") or key.startswith("PYTHON") or key in ["HOME", "PATH"]:
            logger.info(f"  {key}={value}")
    
    # Run the server
    logger.info("Starting FastMCP agent management server")
    mcp.run(transport="stdio")
