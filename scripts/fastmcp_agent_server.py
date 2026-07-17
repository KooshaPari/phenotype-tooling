#!/usr/bin/env python3
"""
FastMCP-based agent management server.
This server provides tools for managing agents and their prompts.
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

try:
    from fastmcp import FastMCP, Context
    logger.info("Successfully imported FastMCP")
except ImportError:
    logger.error("Failed to import FastMCP. Please install it with 'pip install fastmcp'")
    sys.exit(1)

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

# Create the FastMCP server
mcp = FastMCP(
    name="Agent Management",
    description="Tools for managing agents and their prompts"
)

# Echo tool
@mcp.tool(
    annotations={
        "title": "Echo Message",
        "readOnlyHint": True,
        "openWorldHint": False
    }
)
async def echo(message: str) -> str:
    """Echo a message back to the client.
    
    Args:
        message: The message to echo
        
    Returns:
        The same message
    """
    logger.info(f"Echo tool called with message: {message}")
    return f"Echo: {message}"

# Prompt management tools
@mcp.tool(
    annotations={
        "title": "List Prompts",
        "readOnlyHint": True,
        "openWorldHint": False
    }
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
    annotations={
        "title": "Get Prompt",
        "readOnlyHint": True,
        "openWorldHint": False
    }
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
        "openWorldHint": False
    }
)
async def create_prompt(
    name: str, 
    content: str, 
    description: Optional[str] = None
) -> Dict[str, Union[Dict[str, Any], str]]:
    """Create a new prompt.
    
    Args:
        name: The name of the prompt
        content: The content of the prompt
        description: Optional description of the prompt
        
    Returns:
        The created prompt data
    """
    import time
    import uuid
    
    logger.info(f"Create prompt tool called with name: {name}")
    
    # Generate a unique ID
    prompt_id = str(uuid.uuid4())
    
    # Get current timestamp
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    # Create the prompt
    prompt = {
        "id": prompt_id,
        "name": name,
        "content": content,
        "description": description or "",
        "created_at": timestamp,
        "updated_at": timestamp
    }
    
    # Store the prompt
    prompts_storage[prompt_id] = prompt
    
    return {"prompt": prompt}

@mcp.tool(
    annotations={
        "title": "Update Prompt",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False
    }
)
async def update_prompt(
    prompt_id: str,
    name: Optional[str] = None,
    content: Optional[str] = None,
    description: Optional[str] = None
) -> Dict[str, Union[Dict[str, Any], str]]:
    """Update an existing prompt.
    
    Args:
        prompt_id: The ID of the prompt to update
        name: Optional new name for the prompt
        content: Optional new content for the prompt
        description: Optional new description for the prompt
        
    Returns:
        The updated prompt data or an error message
    """
    logger.info(f"Update prompt tool called with ID: {prompt_id}")
    
    if prompt_id not in prompts_storage:
        return {"error": f"Prompt with ID '{prompt_id}' not found"}
    
    import time
    
    # Get current timestamp
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
    
    # Update the prompt
    prompt = prompts_storage[prompt_id]
    if name is not None:
        prompt["name"] = name
    if content is not None:
        prompt["content"] = content
    if description is not None:
        prompt["description"] = description
    prompt["updated_at"] = timestamp
    
    # Store the updated prompt
    prompts_storage[prompt_id] = prompt
    
    return {"prompt": prompt}

@mcp.tool(
    annotations={
        "title": "Delete Prompt",
        "readOnlyHint": False,
        "destructiveHint": True,
        "idempotentHint": True,
        "openWorldHint": False
    }
)
async def delete_prompt(prompt_id: str) -> Dict[str, bool]:
    """Delete a prompt.
    
    Args:
        prompt_id: The ID of the prompt to delete
        
    Returns:
        A success indicator
    """
    logger.info(f"Delete prompt tool called with ID: {prompt_id}")
    
    if prompt_id not in prompts_storage:
        return {"success": False}
    
    # Delete the prompt
    del prompts_storage[prompt_id]
    
    return {"success": True}

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
