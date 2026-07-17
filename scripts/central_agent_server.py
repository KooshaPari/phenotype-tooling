#!/usr/bin/env python3
"""
Central Agent Management Server - FastMCP-based server for agent management.

This server provides tools for managing agents with a central registry,
including creation, retrieval, updating, and deletion of agents.
"""

import os
import sys
import json
import uuid
import time
import logging
import asyncio
import threading
import subprocess
import platform
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("central-agent-server")

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastmcp import FastMCP, Context

    logger.info("Successfully imported FastMCP")
except ImportError:
    logger.error(
        "Failed to import FastMCP. Please install it with 'pip install fastmcp'"
    )
    sys.exit(1)

# Import agent registry
try:
    from agent_registry import get_registry

    logger.info("Successfully imported agent registry")
except ImportError:
    logger.error("Failed to import agent registry")
    sys.exit(1)

# Import agent logger
try:
    from agent_logger import (
        setup_agent_logging,
        launch_log_viewer,
        close_log_viewer,
        log_to_agent,
        get_log_viewer_status,
        get_agent_log_path,
    )

    logger.info("Successfully imported agent logger")
except ImportError:
    logger.error("Failed to import agent logger")
    sys.exit(1)


# Agent status enum
class AgentStatus(str, Enum):
    INITIALIZING = "initializing"
    ACTIVE = "active"
    BUSY = "busy"
    ERROR = "error"
    INACTIVE = "inactive"
    TERMINATED = "terminated"


# Initialize agent registry
registry = get_registry()

# In-memory storage for prompts
prompts_storage = {
    "default": {
        "id": "default",
        "name": "Default Prompt",
        "content": "You are a helpful AI assistant.",
        "description": "The default system prompt for the agent.",
        "created_at": "2025-05-20T00:00:00Z",
        "updated_at": "2025-05-20T00:00:00Z",
    },
    "developer": {
        "id": "developer",
        "name": "Developer Prompt",
        "content": "You are a helpful AI assistant specialized in software development.",
        "description": "A system prompt for software development tasks.",
        "created_at": "2025-05-20T00:00:00Z",
        "updated_at": "2025-05-20T00:00:00Z",
    },
}

# In-memory storage for conversation history
conversation_history = {}

# In-memory storage for message queues
message_queues = {}

# In-memory storage for health status
health_status = {}

# Create the FastMCP server
mcp = FastMCP(
    name="Central Agent Management",
    description="Tools for managing agents with a central registry",
)


# Helper function to perform a health check
def perform_health_check(agent_id):
    """Perform a health check on an agent.

    Args:
        agent_id: The agent ID

    Returns:
        Health check results
    """
    # Simulate a health check
    agent = registry.get_agent(agent_id)
    if not agent:
        return {"status": "error", "message": "Agent not found"}

    # Check if agent is active
    if agent["status"] != AgentStatus.ACTIVE:
        return {
            "status": "error",
            "message": f"Agent is not active (status: {agent['status']})",
        }

    # Store health status
    health_status[agent_id] = {
        "status": "healthy",
        "last_check": datetime.now(timezone.utc).isoformat(),
        "message": "Agent is healthy",
    }

    return health_status[agent_id]


# Agent Management Tools


@mcp.tool(
    annotations={
        "title": "Create Agent",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False,
    }
)
async def create_agent(
    name: str,
    model_name: str,
    system_prompt: Optional[str] = None,
    description: Optional[str] = None,
    temperature: float = 0.7,
    max_tools: int = 128,
    auto_healthcheck: bool = True,
    port: Optional[int] = None,
    uri: Optional[str] = None,
) -> Dict[str, Any]:
    """Create a new agent with the specified parameters.

    Args:
        name: The name of the agent
        model_name: The name of the model to use
        system_prompt: Optional custom system prompt to use
        description: Optional description of the agent
        temperature: The temperature to use for generation
        max_tools: Maximum number of tools to use
        auto_healthcheck: Whether to automatically perform a health check after creation
        port: Optional port number for the agent
        uri: Optional URI for the agent

    Returns:
        The created agent configuration
    """
    logger.info(f"Creating agent: {name} with model: {model_name}")

    try:
        # Generate a unique ID for the agent
        agent_id = f"agent-{uuid.uuid4().hex}"

        # Use the default prompt if none is provided
        if system_prompt is None and "default" in prompts_storage:
            system_prompt = prompts_storage["default"]["content"]

        # Create the agent config
        agent_config = {
            "agent_id": agent_id,
            "name": name,
            "description": description or f"Agent created with model {model_name}",
            "llm_model_id": model_name,
            "initial_prompt": system_prompt,
            "status": AgentStatus.INITIALIZING,  # Start in initializing state
            "config": {
                "temperature": temperature,
                "max_tools": max_tools,
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "port": port,
            "uri": uri,
        }

        # Register agent in the central registry
        registry.register_agent(agent_config)

        # Initialize conversation history
        conversation_history[agent_id] = []

        # Initialize message queue
        message_queues[agent_id] = []

        logger.info(f"Agent created: {agent_id}")

        # Simulate agent initialization
        await asyncio.sleep(0.5)

        # Update agent status to active
        agent_config["status"] = AgentStatus.ACTIVE
        agent_config["updated_at"] = datetime.now(timezone.utc).isoformat()

        # Update in registry
        registry.update_agent(
            agent_id,
            {
                "status": agent_config["status"],
                "updated_at": agent_config["updated_at"],
            },
        )

        # Perform health check if requested
        health_result = None
        if auto_healthcheck:
            health_result = perform_health_check(agent_id)

        # Set up logging for the agent
        log_path = setup_agent_logging(agent_id, name)

        # Log agent creation
        log_to_agent(agent_id, f"Agent created with model: {model_name}")
        log_to_agent(agent_id, f"Status: {agent_config['status']}")
        if system_prompt:
            log_to_agent(
                agent_id,
                (
                    f"System prompt: {system_prompt[:100]}..."
                    if len(system_prompt) > 100
                    else system_prompt
                ),
            )

        # Launch a log viewer for the agent if auto_console is enabled
        log_viewer_launched = False
        auto_console = os.environ.get("AUTO_CONSOLE", "true").lower() == "true"

        if auto_console:
            try:
                # Launch a log viewer for the agent
                log_viewer_launched = launch_log_viewer(agent_id, name)
                logger.info(
                    f"Log viewer {'launched' if log_viewer_launched else 'failed to launch'} for agent {agent_id}"
                )
                log_to_agent(agent_id, "Log viewer launched")
            except Exception as e:
                logger.error(f"Error launching log viewer for agent {agent_id}: {e}")
                log_to_agent(agent_id, f"Error launching log viewer: {e}", "ERROR")

        # Return the agent config with health check results
        result = {
            "agent": agent_config,
            "health_check": health_result,
            "log_viewer_launched": log_viewer_launched,
            "log_path": log_path,
            "message": "Agent created successfully and is now active",
        }

        return result
    except Exception as e:
        logger.error(f"Error creating agent: {e}")
        return {"error": str(e), "status": "error"}


@mcp.tool(
    annotations={"title": "Get Agent", "readOnlyHint": True, "openWorldHint": False}
)
async def get_agent(agent_id: str) -> Dict[str, Any]:
    """Get agent information by ID.

    Args:
        agent_id: The agent ID

    Returns:
        The agent configuration
    """
    logger.info(f"Getting agent: {agent_id}")

    try:
        agent = registry.get_agent(agent_id)
        if not agent:
            return {"error": f"Agent with ID '{agent_id}' not found"}

        return {"agent": agent}
    except Exception as e:
        logger.error(f"Error getting agent: {e}")
        return {"error": str(e)}


@mcp.tool(
    annotations={"title": "List Agents", "readOnlyHint": True, "openWorldHint": False}
)
async def list_agents(status: Optional[str] = None) -> Dict[str, Any]:
    """List all agents with optional filtering.

    Args:
        status: Optional status to filter by

    Returns:
        List of agent configurations
    """
    logger.info("Listing agents")

    try:
        filters = {}
        if status:
            filters["status"] = status

        agents = registry.list_agents(filters)
        return {"agents": agents}
    except Exception as e:
        logger.error(f"Error listing agents: {e}")
        return {"error": str(e)}


@mcp.tool(
    annotations={
        "title": "Update Agent",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False,
    }
)
async def update_agent(
    agent_id: str,
    name: Optional[str] = None,
    description: Optional[str] = None,
    system_prompt: Optional[str] = None,
    status: Optional[str] = None,
    temperature: Optional[float] = None,
    max_tools: Optional[int] = None,
    port: Optional[int] = None,
    uri: Optional[str] = None,
) -> Dict[str, Any]:
    """Update agent information.

    Args:
        agent_id: The agent ID
        name: Optional new name
        description: Optional new description
        system_prompt: Optional new system prompt
        status: Optional new status
        temperature: Optional new temperature
        max_tools: Optional new maximum number of tools
        port: Optional new port number
        uri: Optional new URI

    Returns:
        The updated agent configuration
    """
    logger.info(f"Updating agent: {agent_id}")

    try:
        # Check if agent exists
        agent = registry.get_agent(agent_id)
        if not agent:
            return {"error": f"Agent with ID '{agent_id}' not found"}

        # Prepare update data
        update_data = {}
        if name is not None:
            update_data["name"] = name
        if description is not None:
            update_data["description"] = description
        if system_prompt is not None:
            update_data["system_prompt"] = system_prompt
        if status is not None:
            update_data["status"] = status
        if port is not None:
            update_data["port"] = port
        if uri is not None:
            update_data["uri"] = uri

        # Update config if temperature or max_tools is provided
        if temperature is not None or max_tools is not None:
            config = agent.get("config", {})
            if temperature is not None:
                config["temperature"] = temperature
            if max_tools is not None:
                config["max_tools"] = max_tools
            update_data["config"] = config

        # Update agent
        updated_agent = registry.update_agent(agent_id, update_data)

        return {"agent": updated_agent}
    except Exception as e:
        logger.error(f"Error updating agent: {e}")
        return {"error": str(e)}


@mcp.tool(
    annotations={
        "title": "Delete Agent",
        "readOnlyHint": False,
        "destructiveHint": True,
        "openWorldHint": False,
    }
)
async def delete_agent(agent_id: str) -> Dict[str, Any]:
    """Delete an agent.

    Args:
        agent_id: The agent ID

    Returns:
        Success message
    """
    logger.info(f"Deleting agent: {agent_id}")

    try:
        # Delete agent from registry
        success = registry.delete_agent(agent_id)
        if not success:
            return {"error": f"Agent with ID '{agent_id}' not found"}

        # Clean up in-memory storage
        if agent_id in conversation_history:
            del conversation_history[agent_id]
        if agent_id in message_queues:
            del message_queues[agent_id]
        if agent_id in health_status:
            del health_status[agent_id]

        return {"success": True, "message": f"Agent '{agent_id}' deleted successfully"}
    except Exception as e:
        logger.error(f"Error deleting agent: {e}")
        return {"error": str(e)}


@mcp.tool(
    annotations={
        "title": "Check Agent Health",
        "readOnlyHint": True,
        "openWorldHint": False,
    }
)
async def check_agent_health(agent_id: str) -> Dict[str, Any]:
    """Check the health of an agent.

    Args:
        agent_id: The agent ID

    Returns:
        Health check results
    """
    logger.info(f"Checking health of agent: {agent_id}")

    try:
        result = perform_health_check(agent_id)
        return result
    except Exception as e:
        logger.error(f"Error checking agent health: {e}")
        return {"status": "error", "message": str(e)}


@mcp.tool(
    annotations={
        "title": "View Agent Console",
        "readOnlyHint": True,
        "openWorldHint": False,
    }
)
async def view_agent_console(agent_id: str) -> Dict[str, Any]:
    """Launch a console viewer for an agent to see its output.

    Args:
        agent_id: The agent ID

    Returns:
        Status of the console viewer launch
    """
    logger.info(f"Launching console viewer for agent: {agent_id}")

    try:
        # Check if agent exists
        agent = registry.get_agent(agent_id)
        if not agent:
            return {"error": f"Agent with ID '{agent_id}' not found"}

        # Get agent name
        agent_name = agent.get("name", "Unknown Agent")

        # Launch log viewer
        log_viewer_launched = launch_log_viewer(agent_id, agent_name)

        # Log the action
        log_to_agent(agent_id, "Console viewer launched by user")

        if log_viewer_launched:
            return {
                "success": True,
                "message": f"Console viewer launched for agent '{agent_name}' ({agent_id})",
                "log_path": (
                    get_agent_log_path(agent_id)
                    if "get_agent_log_path" in globals()
                    else None
                ),
            }
        else:
            return {
                "success": False,
                "message": f"Failed to launch console viewer for agent '{agent_name}' ({agent_id})",
            }
    except Exception as e:
        logger.error(f"Error launching console viewer for agent {agent_id}: {e}")
        return {"status": "error", "message": str(e)}


# Start the TUI in a separate thread
def start_tui():
    """Start the TUI in a separate process."""
    try:
        # Get the path to the TUI script
        tui_script = os.path.join(
            os.path.dirname(os.path.abspath(__file__)), "agent_manager_tui.py"
        )

        # Check if TUI_ENABLED environment variable is set
        tui_enabled = os.environ.get("TUI_ENABLED", "true").lower() == "true"

        if tui_enabled:
            # Start the TUI in a separate process with proper redirection
            with open(os.devnull, "w") as devnull:
                subprocess.Popen(
                    [sys.executable, tui_script],
                    stdout=devnull,
                    stderr=devnull,
                    env=dict(os.environ, PYTHONUNBUFFERED="1", TERM="xterm-256color"),
                )
            logger.info("Started TUI in a separate process")
        else:
            logger.info("TUI disabled by environment variable")
    except Exception as e:
        logger.error(f"Error starting TUI: {e}")


# Main entry point
if __name__ == "__main__":
    # Start the TUI if not running in API mode
    if os.environ.get("API_MODE", "false").lower() != "true":
        start_tui()

    # Run the server
    logger.info("Starting central agent management server")
    mcp.run(transport="stdio")
