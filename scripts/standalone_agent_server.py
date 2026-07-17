#!/usr/bin/env python3
"""
Standalone FastMCP-based agent management server.

This server provides tools for managing agents and their prompts,
without relying on importing from the main project.

Features:
- Agent CRUD operations
- Prompt management (create, push, pull)
- Agent lifecycle management (health checks, status)
- Agent communication (direct messaging, broadcast)
- Conversation history tracking
"""

import os
import sys
import json
import uuid
import time
import logging
import asyncio
import requests
import threading
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timedelta, timezone
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("agent-management-server")

try:
    from fastmcp import FastMCP, Context

    logger.info("Successfully imported FastMCP")
except ImportError:
    logger.error(
        "Failed to import FastMCP. Please install it with 'pip install fastmcp'"
    )
    sys.exit(1)


# Define agent status enum
class AgentStatus(str, Enum):
    CREATING = "creating"
    INITIALIZING = "initializing"
    ACTIVE = "active"
    IDLE = "idle"
    BUSY = "busy"
    ERROR = "error"
    TERMINATED = "terminated"


# Create the FastMCP server
mcp = FastMCP(
    name="Agent Management",
    description="Tools for managing agents and their communication",
)

# In-memory storage for agents and prompts
agents_storage = {}
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

# Message storage for agent communication
message_queues = {}
message_history = {}

# Conversation history storage
conversation_history = {}

# Agent health check status
health_status = {}


# Helper functions for agent lifecycle management
def perform_health_check(agent_id: str) -> Dict[str, Any]:
    """Perform a health check on an agent.

    Args:
        agent_id: The agent ID

    Returns:
        The health check result
    """
    if agent_id not in agents_storage:
        return {
            "status": "error",
            "message": f"Agent with ID '{agent_id}' not found",
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }

    agent = agents_storage[agent_id]

    # Simulate a health check
    # In a real implementation, this would make an API call to the agent
    is_healthy = agent["status"] not in [AgentStatus.ERROR, AgentStatus.TERMINATED]

    result = {
        "agent_id": agent_id,
        "status": "healthy" if is_healthy else "unhealthy",
        "message": (
            "Agent is responding normally" if is_healthy else "Agent is not responding"
        ),
        "last_activity": agent.get("last_activity", agent["updated_at"]),
        "timestamp": datetime.now(timezone.utc).isoformat(),
    }

    # Store the health check result
    health_status[agent_id] = result

    return result


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

    Returns:
        The created agent configuration with health check results
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
        }

        # Store the agent
        agents_storage[agent_id] = agent_config

        # Initialize conversation history
        conversation_history[agent_id] = []

        # Initialize message queue
        message_queues[agent_id] = []

        logger.info(f"Agent created: {agent_id}")

        # Simulate agent initialization (in a real implementation, this would start the agent)
        # Wait a short time to simulate initialization
        await asyncio.sleep(0.5)

        # Update agent status to active
        agent_config["status"] = AgentStatus.ACTIVE
        agent_config["updated_at"] = datetime.now(timezone.utc).isoformat()
        agents_storage[agent_id] = agent_config

        # Perform health check if requested
        health_result = None
        if auto_healthcheck:
            health_result = perform_health_check(agent_id)

        # Return the agent config with health check results
        result = {
            "agent": agent_config,
            "health_check": health_result,
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
    """Get an agent by ID.

    Args:
        agent_id: The agent ID

    Returns:
        The agent configuration
    """
    logger.info(f"Getting agent: {agent_id}")

    try:
        if agent_id in agents_storage:
            return agents_storage[agent_id]
        else:
            return {"error": f"Agent with ID '{agent_id}' not found"}
    except Exception as e:
        logger.error(f"Error getting agent: {e}")
        return {"error": str(e)}


@mcp.tool(
    annotations={"title": "List Agents", "readOnlyHint": True, "openWorldHint": False}
)
async def list_agents() -> Dict[str, List[Dict[str, Any]]]:
    """List all agents.

    Returns:
        A list of agent configurations
    """
    logger.info("Listing agents")

    try:
        agents = list(agents_storage.values())
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
    system_prompt: Optional[str] = None,
    description: Optional[str] = None,
    status: Optional[str] = None,
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
        if agent_id not in agents_storage:
            return {"error": f"Agent with ID '{agent_id}' not found"}

        # Get the agent
        agent = agents_storage[agent_id]

        # Update the agent
        if name is not None:
            agent["name"] = name
        if system_prompt is not None:
            agent["initial_prompt"] = system_prompt
        if description is not None:
            agent["description"] = description
        if status is not None:
            agent["status"] = status

        # Update the timestamp
        agent["updated_at"] = datetime.now(timezone.utc).isoformat()
        agent["last_activity"] = datetime.now(timezone.utc).isoformat()

        # Store the updated agent
        agents_storage[agent_id] = agent

        logger.info(f"Agent updated: {agent_id}")

        return agent
    except Exception as e:
        logger.error(f"Error updating agent: {e}")
        return {"error": str(e)}


@mcp.tool(
    annotations={
        "title": "Delete Agent",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False,
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
        if agent_id not in agents_storage:
            return {"success": False, "error": f"Agent with ID '{agent_id}' not found"}

        # Update agent status to terminated
        agents_storage[agent_id]["status"] = AgentStatus.TERMINATED
        agents_storage[agent_id]["updated_at"] = datetime.now(timezone.utc).isoformat()

        # In a real implementation, this would shut down the agent process
        await asyncio.sleep(0.5)

        # Delete the agent
        del agents_storage[agent_id]

        # Clean up related data
        if agent_id in conversation_history:
            del conversation_history[agent_id]
        if agent_id in message_queues:
            del message_queues[agent_id]
        if agent_id in health_status:
            del health_status[agent_id]

        logger.info(f"Agent deleted: {agent_id}")

        return {"success": True, "message": f"Agent {agent_id} successfully deleted"}
    except Exception as e:
        logger.error(f"Error deleting agent: {e}")
        return {"success": False, "error": str(e)}


# Agent Health and Conversation Tools


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
        The health check result
    """
    logger.info(f"Checking health of agent: {agent_id}")

    try:
        result = perform_health_check(agent_id)
        return result
    except Exception as e:
        logger.error(f"Error checking agent health: {e}")
        return {
            "status": "error",
            "message": str(e),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }


@mcp.tool(
    annotations={
        "title": "Get Agent Conversation History",
        "readOnlyHint": True,
        "openWorldHint": False,
    }
)
async def get_conversation_history(
    agent_id: str, limit: Optional[int] = None, include_system_messages: bool = False
) -> Dict[str, Any]:
    """Get the conversation history for an agent.

    Args:
        agent_id: The agent ID
        limit: Optional limit on the number of messages to return (most recent first)
        include_system_messages: Whether to include system messages in the history

    Returns:
        The conversation history
    """
    logger.info(f"Getting conversation history for agent: {agent_id}")

    try:
        if agent_id not in agents_storage:
            return {"error": f"Agent with ID '{agent_id}' not found"}

        if agent_id not in conversation_history:
            return {"messages": [], "agent_id": agent_id}

        # Get the conversation history
        history = conversation_history[agent_id]

        # Filter out system messages if requested
        if not include_system_messages:
            history = [msg for msg in history if msg.get("role") != "system"]

        # Apply limit if specified
        if limit is not None and limit > 0:
            history = history[-limit:]

        return {
            "messages": history,
            "agent_id": agent_id,
            "total_messages": len(history),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting conversation history: {e}")
        return {"error": str(e)}


# Prompt Management Tools


@mcp.tool(
    annotations={"title": "List Prompts", "readOnlyHint": True, "openWorldHint": False}
)
async def list_prompts() -> Dict[str, List[Dict[str, Any]]]:
    """List all available prompts.

    Returns:
        A dictionary containing the list of prompts
    """
    logger.info("List prompts tool called")
    prompts = list(prompts_storage.values())
    return {"prompts": prompts}


@mcp.tool(
    annotations={"title": "Get Prompt", "readOnlyHint": True, "openWorldHint": False}
)
async def get_prompt(prompt_id: str) -> Dict[str, Union[Dict[str, Any], str]]:
    """Get a prompt by ID.

    Args:
        prompt_id: The ID of the prompt to retrieve

    Returns:
        The prompt data or an error message
    """
    logger.info(f"Get prompt tool called with ID: {prompt_id}")
    if prompt_id in prompts_storage:
        return {"prompt": prompts_storage[prompt_id]}
    else:
        return {"error": f"Prompt with ID '{prompt_id}' not found"}


@mcp.tool(
    annotations={
        "title": "Create Prompt",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False,
    }
)
async def create_prompt(
    name: str, content: str, description: Optional[str] = None
) -> Dict[str, Union[Dict[str, Any], str]]:
    """Create a new prompt.

    Args:
        name: The name of the prompt
        content: The content of the prompt
        description: Optional description of the prompt

    Returns:
        The created prompt data
    """
    logger.info(f"Create prompt tool called with name: {name}")

    # Generate a unique ID
    prompt_id = str(uuid.uuid4())

    # Get current timestamp
    timestamp = datetime.now(timezone.utc).isoformat()

    # Create the prompt
    prompt = {
        "id": prompt_id,
        "name": name,
        "content": content,
        "description": description or "",
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    # Store the prompt
    prompts_storage[prompt_id] = prompt

    return {"prompt": prompt}


@mcp.tool(
    annotations={
        "title": "Push Prompt To Agent",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False,
    }
)
async def push_prompt_to_agent(
    agent_id: str, prompt_id: str, replace_existing: bool = True
) -> Dict[str, Any]:
    """Push a prompt to an agent.

    Args:
        agent_id: The agent ID
        prompt_id: The prompt ID
        replace_existing: Whether to replace the existing prompt

    Returns:
        The result of the operation
    """
    logger.info(f"Pushing prompt {prompt_id} to agent {agent_id}")

    try:
        # Check if agent exists
        if agent_id not in agents_storage:
            return {"error": f"Agent with ID '{agent_id}' not found"}

        # Check if prompt exists
        if prompt_id not in prompts_storage:
            return {"error": f"Prompt with ID '{prompt_id}' not found"}

        # Get the agent and prompt
        agent = agents_storage[agent_id]
        prompt = prompts_storage[prompt_id]

        # Check if agent is in a state where the prompt can be updated
        if agent["status"] in [AgentStatus.ERROR, AgentStatus.TERMINATED]:
            return {
                "error": f"Agent is in {agent['status']} state and cannot receive prompts"
            }

        # Store the previous prompt if it exists
        previous_prompt = None
        if "initial_prompt" in agent and agent["initial_prompt"] is not None:
            previous_prompt = agent["initial_prompt"]

        # Update the agent's prompt
        if replace_existing or previous_prompt is None:
            agent["initial_prompt"] = prompt["content"]
            agent["updated_at"] = datetime.now(timezone.utc).isoformat()
            agent["last_activity"] = datetime.now(timezone.utc).isoformat()
            agents_storage[agent_id] = agent

            # Add a system message to the conversation history
            if agent_id in conversation_history:
                conversation_history[agent_id].append(
                    {
                        "role": "system",
                        "content": prompt["content"],
                        "timestamp": datetime.now(timezone.utc).isoformat(),
                        "prompt_id": prompt_id,
                        "prompt_name": prompt["name"],
                    }
                )

            return {
                "success": True,
                "agent_id": agent_id,
                "prompt_id": prompt_id,
                "prompt_name": prompt["name"],
                "previous_prompt": previous_prompt,
                "message": f"Prompt '{prompt['name']}' successfully pushed to agent '{agent['name']}'",
            }
        else:
            return {
                "success": False,
                "error": "Agent already has a prompt and replace_existing is False",
            }
    except Exception as e:
        logger.error(f"Error pushing prompt to agent: {e}")
        return {"error": str(e)}


# Agent Communication Tools


@mcp.tool(
    annotations={
        "title": "Send Message To Agent",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False,
    }
)
async def send_message_to_agent(
    sender_id: str,
    recipient_id: str,
    content: str,
    message_type: str = "text",
    metadata: Optional[Dict[str, Any]] = None,
) -> Dict[str, Any]:
    """Send a message from one agent to another.

    Args:
        sender_id: The sender agent ID
        recipient_id: The recipient agent ID
        content: The message content
        message_type: The type of message (text, command, etc.)
        metadata: Optional message metadata

    Returns:
        The result of the operation
    """
    logger.info(f"Sending message from {sender_id} to {recipient_id}")

    try:
        # Check if sender exists
        if sender_id not in agents_storage:
            return {"error": f"Sender agent with ID '{sender_id}' not found"}

        # Check if recipient exists
        if recipient_id not in agents_storage:
            return {"error": f"Recipient agent with ID '{recipient_id}' not found"}

        # Check if recipient is in a state where it can receive messages
        recipient = agents_storage[recipient_id]
        if recipient["status"] in [AgentStatus.ERROR, AgentStatus.TERMINATED]:
            return {
                "error": f"Recipient agent is in {recipient['status']} state and cannot receive messages"
            }

        # Create the message
        message_id = f"msg-{uuid.uuid4().hex}"
        timestamp = datetime.now(timezone.utc).isoformat()

        message = {
            "message_id": message_id,
            "sender_id": sender_id,
            "recipient_id": recipient_id,
            "content": content,
            "type": message_type,
            "metadata": metadata or {},
            "timestamp": timestamp,
            "status": "delivered",
        }

        # Add the message to the recipient's queue
        if recipient_id not in message_queues:
            message_queues[recipient_id] = []
        message_queues[recipient_id].append(message)

        # Add the message to the conversation history
        if recipient_id not in conversation_history:
            conversation_history[recipient_id] = []
        conversation_history[recipient_id].append(
            {
                "role": "user",
                "content": content,
                "timestamp": timestamp,
                "sender_id": sender_id,
                "message_id": message_id,
            }
        )

        # Update the recipient's last activity
        recipient["last_activity"] = timestamp
        agents_storage[recipient_id] = recipient

        return {
            "success": True,
            "message_id": message_id,
            "timestamp": timestamp,
            "status": "delivered",
        }
    except Exception as e:
        logger.error(f"Error sending message: {e}")
        return {"error": str(e)}


@mcp.tool(
    annotations={
        "title": "Get Agent Messages",
        "readOnlyHint": True,
        "openWorldHint": False,
    }
)
async def get_agent_messages(
    agent_id: str, limit: Optional[int] = None, include_processed: bool = False
) -> Dict[str, Any]:
    """Get messages for an agent.

    Args:
        agent_id: The agent ID
        limit: Optional limit on the number of messages to return
        include_processed: Whether to include processed messages

    Returns:
        The agent's messages
    """
    logger.info(f"Getting messages for agent: {agent_id}")

    try:
        # Check if agent exists
        if agent_id not in agents_storage:
            return {"error": f"Agent with ID '{agent_id}' not found"}

        # Get the agent's message queue
        if agent_id not in message_queues:
            return {"messages": [], "agent_id": agent_id}

        messages = message_queues[agent_id]

        # Filter out processed messages if requested
        if not include_processed:
            messages = [msg for msg in messages if msg.get("status") != "processed"]

        # Apply limit if specified
        if limit is not None and limit > 0:
            messages = messages[:limit]

        return {
            "messages": messages,
            "agent_id": agent_id,
            "total_messages": len(messages),
            "timestamp": datetime.now(timezone.utc).isoformat(),
        }
    except Exception as e:
        logger.error(f"Error getting messages: {e}")
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
