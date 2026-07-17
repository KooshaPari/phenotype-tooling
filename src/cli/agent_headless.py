"""
Headless script for agent management.

This script provides a headless interface for creating, retrieving, updating, and deleting agents,
as well as for agent communication. It returns parsable information for programmatic use.
"""

import argparse
import asyncio
import json
import os
import sys
import uuid
from typing import Dict, List, Optional, Any, Union

import httpx

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..utils.logging import logger

# Constants
DEFAULT_API_URL = "http://localhost:8000"


async def create_agent(args):
    """
    Create a new agent.
    
    Args:
        args: Command-line arguments.
        
    Returns:
        The agent ID and API URL.
    """
    # Prepare the request data
    data = {
        "name": args.name,
        "llm_model_id": args.model,
        "description": args.description,
        "mcp_tools_config_path": args.mcp_tools_config,
        "initial_prompt": args.system_prompt,
    }
    
    # Remove None values
    data = {k: v for k, v in data.items() if v is not None}
    
    # Make the request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{args.api_url}/v1/agents",
            json=data,
            timeout=args.timeout,
        )
    
    # Check for errors
    if response.status_code >= 400:
        error_data = {
            "error": f"Error creating agent: {response.status_code} {response.text}",
            "status": "error",
        }
        print(json.dumps(error_data))
        return
    
    # Parse the response
    agent = response.json()
    
    # Output the result
    result = {
        "agent_id": agent["agent_id"],
        "api_url": args.api_url,
        "status": "success",
    }
    print(json.dumps(result))


async def list_agents(args):
    """
    List all agents.
    
    Args:
        args: Command-line arguments.
        
    Returns:
        A list of agent IDs.
    """
    # Make the request
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{args.api_url}/v1/agents",
            timeout=args.timeout,
        )
    
    # Check for errors
    if response.status_code >= 400:
        error_data = {
            "error": f"Error listing agents: {response.status_code} {response.text}",
            "status": "error",
        }
        print(json.dumps(error_data))
        return
    
    # Parse the response
    agents = response.json()["data"]
    
    # Output the result
    result = {
        "agent_ids": [agent["agent_id"] for agent in agents],
        "api_url": args.api_url,
        "status": "success",
    }
    print(json.dumps(result))


async def get_agent(args):
    """
    Get an agent by ID.
    
    Args:
        args: Command-line arguments.
        
    Returns:
        The agent details.
    """
    # Make the request
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{args.api_url}/v1/agents/{args.agent_id}",
            timeout=args.timeout,
        )
    
    # Check for errors
    if response.status_code >= 400:
        error_data = {
            "error": f"Error getting agent: {response.status_code} {response.text}",
            "status": "error",
        }
        print(json.dumps(error_data))
        return
    
    # Parse the response
    agent = response.json()
    
    # Output the result
    result = {
        "agent_id": agent["agent_id"],
        "name": agent["name"],
        "description": agent["description"],
        "llm_model_id": agent["llm_model_id"],
        "mcp_tools_config_path": agent["mcp_tools_config_path"],
        "initial_prompt": agent["initial_prompt"],
        "status": agent["status"],
        "api_url": args.api_url,
        "result_status": "success",
    }
    print(json.dumps(result))


async def update_agent(args):
    """
    Update an agent.
    
    Args:
        args: Command-line arguments.
        
    Returns:
        The updated agent details.
    """
    # Prepare the request data
    data = {
        "name": args.name,
        "llm_model_id": args.model,
        "description": args.description,
        "mcp_tools_config_path": args.mcp_tools_config,
        "initial_prompt": args.system_prompt,
        "status": args.status,
    }
    
    # Remove None values
    data = {k: v for k, v in data.items() if v is not None}
    
    # Make the request
    async with httpx.AsyncClient() as client:
        response = await client.put(
            f"{args.api_url}/v1/agents/{args.agent_id}",
            json=data,
            timeout=args.timeout,
        )
    
    # Check for errors
    if response.status_code >= 400:
        error_data = {
            "error": f"Error updating agent: {response.status_code} {response.text}",
            "status": "error",
        }
        print(json.dumps(error_data))
        return
    
    # Parse the response
    agent = response.json()
    
    # Output the result
    result = {
        "agent_id": agent["agent_id"],
        "name": agent["name"],
        "description": agent["description"],
        "llm_model_id": agent["llm_model_id"],
        "mcp_tools_config_path": agent["mcp_tools_config_path"],
        "initial_prompt": agent["initial_prompt"],
        "status": agent["status"],
        "api_url": args.api_url,
        "result_status": "success",
    }
    print(json.dumps(result))


async def delete_agent(args):
    """
    Delete an agent.
    
    Args:
        args: Command-line arguments.
        
    Returns:
        A success message.
    """
    # Make the request
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{args.api_url}/v1/agents/{args.agent_id}",
            timeout=args.timeout,
        )
    
    # Check for errors
    if response.status_code >= 400:
        error_data = {
            "error": f"Error deleting agent: {response.status_code} {response.text}",
            "status": "error",
        }
        print(json.dumps(error_data))
        return
    
    # Output the result
    result = {
        "agent_id": args.agent_id,
        "api_url": args.api_url,
        "status": "success",
    }
    print(json.dumps(result))


async def invoke_agent(args):
    """
    Invoke an agent.
    
    Args:
        args: Command-line arguments.
        
    Returns:
        The agent's response.
    """
    # Prepare the request data
    data = {
        "messages": [{"role": "user", "content": args.message}],
        "stream": False,  # Headless mode doesn't support streaming
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }
    
    # Remove None values
    data = {k: v for k, v in data.items() if v is not None}
    
    # Make the request
    async with httpx.AsyncClient() as client:
        response = await client.post(
            f"{args.api_url}/v1/agents/{args.agent_id}/completions",
            json=data,
            timeout=args.timeout,
        )
    
    # Check for errors
    if response.status_code >= 400:
        error_data = {
            "error": f"Error invoking agent: {response.status_code} {response.text}",
            "status": "error",
        }
        print(json.dumps(error_data))
        return
    
    # Parse the response
    result = response.json()
    
    # Output the result
    output = {
        "agent_id": args.agent_id,
        "api_url": args.api_url,
        "status": "success",
        "response": result,
    }
    print(json.dumps(output))


def main():
    """Main entry point for the headless script."""
    parser = argparse.ArgumentParser(description="Headless Agent Management")
    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help=f"API URL (default: {DEFAULT_API_URL})",
    )
    parser.add_argument(
        "--timeout",
        type=float,
        default=30.0,
        help="Request timeout in seconds (default: 30.0)",
    )
    
    subparsers = parser.add_subparsers(dest="command", help="Command to run")
    
    # Create agent command
    create_parser = subparsers.add_parser("create", help="Create a new agent")
    create_parser.add_argument("--name", required=True, help="Agent name")
    create_parser.add_argument("--model", required=True, help="LLM model ID")
    create_parser.add_argument("--description", help="Agent description")
    create_parser.add_argument("--mcp-tools-config", help="Path to MCP tools configuration")
    create_parser.add_argument("--system-prompt", help="Custom system prompt")
    
    # List agents command
    list_parser = subparsers.add_parser("list", help="List all agents")
    
    # Get agent command
    get_parser = subparsers.add_parser("get", help="Get an agent by ID")
    get_parser.add_argument("agent_id", help="Agent ID")
    
    # Update agent command
    update_parser = subparsers.add_parser("update", help="Update an agent")
    update_parser.add_argument("agent_id", help="Agent ID")
    update_parser.add_argument("--name", help="Agent name")
    update_parser.add_argument("--model", help="LLM model ID")
    update_parser.add_argument("--description", help="Agent description")
    update_parser.add_argument("--mcp-tools-config", help="Path to MCP tools configuration")
    update_parser.add_argument("--system-prompt", help="Custom system prompt")
    update_parser.add_argument("--status", help="Agent status")
    
    # Delete agent command
    delete_parser = subparsers.add_parser("delete", help="Delete an agent")
    delete_parser.add_argument("agent_id", help="Agent ID")
    
    # Invoke agent command
    invoke_parser = subparsers.add_parser("invoke", help="Invoke an agent")
    invoke_parser.add_argument("agent_id", help="Agent ID")
    invoke_parser.add_argument("message", help="Message to send to the agent")
    invoke_parser.add_argument("--temperature", type=float, help="Temperature for generation")
    invoke_parser.add_argument("--max-tokens", type=int, help="Maximum number of tokens to generate")
    
    args = parser.parse_args()
    
    # Run the appropriate command
    if args.command == "create":
        asyncio.run(create_agent(args))
    elif args.command == "list":
        asyncio.run(list_agents(args))
    elif args.command == "get":
        asyncio.run(get_agent(args))
    elif args.command == "update":
        asyncio.run(update_agent(args))
    elif args.command == "delete":
        asyncio.run(delete_agent(args))
    elif args.command == "invoke":
        asyncio.run(invoke_agent(args))
    else:
        parser.print_help()


if __name__ == "__main__":
    main()
