"""
Command-line interface for agent management.

This module provides a CLI for creating, retrieving, updating, and deleting agents,
as well as for agent communication.
"""

import argparse
import asyncio
import json
import os
import sys
import uuid
from typing import Dict, List, Optional, Any, Union

import httpx
from rich.console import Console
from rich.table import Table

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from ..utils.logging import logger

# Constants
DEFAULT_API_URL = "http://localhost:8000"
DEFAULT_OUTPUT_FORMAT = "human"

# Initialize console
console = Console()


async def create_agent(args):
    """
    Create a new agent.
    
    Args:
        args: Command-line arguments.
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
        error_message = f"Error creating agent: {response.status_code} {response.text}"
        if args.output_format == "json":
            print(json.dumps({"error": error_message}))
        else:
            console.print(f"[bold red]{error_message}[/bold red]")
        return
    
    # Parse the response
    agent = response.json()
    
    # Output the result
    if args.output_format == "json":
        print(json.dumps(agent))
    else:
        console.print("[bold green]Agent created successfully![/bold green]")
        console.print(f"Agent ID: [bold]{agent['agent_id']}[/bold]")
        console.print(f"Name: {agent['name']}")
        console.print(f"Model: {agent['llm_model_id']}")
        console.print(f"Status: {agent['status']}")


async def list_agents(args):
    """
    List all agents.
    
    Args:
        args: Command-line arguments.
    """
    # Make the request
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{args.api_url}/v1/agents",
            timeout=args.timeout,
        )
    
    # Check for errors
    if response.status_code >= 400:
        error_message = f"Error listing agents: {response.status_code} {response.text}"
        if args.output_format == "json":
            print(json.dumps({"error": error_message}))
        else:
            console.print(f"[bold red]{error_message}[/bold red]")
        return
    
    # Parse the response
    agents = response.json()["data"]
    
    # Output the result
    if args.output_format == "json":
        print(json.dumps(agents))
    else:
        if not agents:
            console.print("[bold yellow]No agents found.[/bold yellow]")
            return
        
        table = Table(title="Agents")
        table.add_column("ID", style="cyan")
        table.add_column("Name", style="green")
        table.add_column("Model", style="blue")
        table.add_column("Status", style="magenta")
        
        for agent in agents:
            table.add_row(
                agent["agent_id"],
                agent["name"],
                agent["llm_model_id"],
                agent["status"],
            )
        
        console.print(table)


async def get_agent(args):
    """
    Get an agent by ID.
    
    Args:
        args: Command-line arguments.
    """
    # Make the request
    async with httpx.AsyncClient() as client:
        response = await client.get(
            f"{args.api_url}/v1/agents/{args.agent_id}",
            timeout=args.timeout,
        )
    
    # Check for errors
    if response.status_code >= 400:
        error_message = f"Error getting agent: {response.status_code} {response.text}"
        if args.output_format == "json":
            print(json.dumps({"error": error_message}))
        else:
            console.print(f"[bold red]{error_message}[/bold red]")
        return
    
    # Parse the response
    agent = response.json()
    
    # Output the result
    if args.output_format == "json":
        print(json.dumps(agent))
    else:
        console.print(f"Agent ID: [bold]{agent['agent_id']}[/bold]")
        console.print(f"Name: {agent['name']}")
        console.print(f"Description: {agent['description']}")
        console.print(f"Model: {agent['llm_model_id']}")
        console.print(f"MCP Tools Config: {agent['mcp_tools_config_path']}")
        console.print(f"System Prompt: {agent['initial_prompt']}")
        console.print(f"Status: {agent['status']}")


async def update_agent(args):
    """
    Update an agent.
    
    Args:
        args: Command-line arguments.
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
        error_message = f"Error updating agent: {response.status_code} {response.text}"
        if args.output_format == "json":
            print(json.dumps({"error": error_message}))
        else:
            console.print(f"[bold red]{error_message}[/bold red]")
        return
    
    # Parse the response
    agent = response.json()
    
    # Output the result
    if args.output_format == "json":
        print(json.dumps(agent))
    else:
        console.print("[bold green]Agent updated successfully![/bold green]")
        console.print(f"Agent ID: [bold]{agent['agent_id']}[/bold]")
        console.print(f"Name: {agent['name']}")
        console.print(f"Model: {agent['llm_model_id']}")
        console.print(f"Status: {agent['status']}")


async def delete_agent(args):
    """
    Delete an agent.
    
    Args:
        args: Command-line arguments.
    """
    # Make the request
    async with httpx.AsyncClient() as client:
        response = await client.delete(
            f"{args.api_url}/v1/agents/{args.agent_id}",
            timeout=args.timeout,
        )
    
    # Check for errors
    if response.status_code >= 400:
        error_message = f"Error deleting agent: {response.status_code} {response.text}"
        if args.output_format == "json":
            print(json.dumps({"error": error_message}))
        else:
            console.print(f"[bold red]{error_message}[/bold red]")
        return
    
    # Output the result
    if args.output_format == "json":
        print(json.dumps({"success": True}))
    else:
        console.print("[bold green]Agent deleted successfully![/bold green]")


async def invoke_agent(args):
    """
    Invoke an agent.
    
    Args:
        args: Command-line arguments.
    """
    # Prepare the request data
    data = {
        "messages": [{"role": "user", "content": args.message}],
        "stream": args.stream,
        "temperature": args.temperature,
        "max_tokens": args.max_tokens,
    }
    
    # Remove None values
    data = {k: v for k, v in data.items() if v is not None}
    
    # Make the request
    async with httpx.AsyncClient() as client:
        if args.stream:
            async with client.stream(
                "POST",
                f"{args.api_url}/v1/agents/{args.agent_id}/completions",
                json=data,
                timeout=args.timeout,
            ) as response:
                # Check for errors
                if response.status_code >= 400:
                    error_message = f"Error invoking agent: {response.status_code} {response.text}"
                    if args.output_format == "json":
                        print(json.dumps({"error": error_message}))
                    else:
                        console.print(f"[bold red]{error_message}[/bold red]")
                    return
                
                # Stream the response
                async for chunk in response.aiter_text():
                    if chunk.startswith("data: "):
                        chunk = chunk[6:]
                    if chunk.strip() == "[DONE]":
                        break
                    try:
                        chunk_data = json.loads(chunk)
                        if "error" in chunk_data:
                            if args.output_format == "json":
                                print(json.dumps({"error": chunk_data["error"]}))
                            else:
                                console.print(f"[bold red]{chunk_data['error']}[/bold red]")
                            return
                        if args.output_format == "json":
                            print(json.dumps(chunk_data))
                        else:
                            if "choices" in chunk_data and chunk_data["choices"]:
                                choice = chunk_data["choices"][0]
                                if "delta" in choice and "content" in choice["delta"]:
                                    console.print(choice["delta"]["content"], end="")
                    except json.JSONDecodeError:
                        pass
        else:
            response = await client.post(
                f"{args.api_url}/v1/agents/{args.agent_id}/completions",
                json=data,
                timeout=args.timeout,
            )
            
            # Check for errors
            if response.status_code >= 400:
                error_message = f"Error invoking agent: {response.status_code} {response.text}"
                if args.output_format == "json":
                    print(json.dumps({"error": error_message}))
                else:
                    console.print(f"[bold red]{error_message}[/bold red]")
                return
            
            # Parse the response
            result = response.json()
            
            # Output the result
            if args.output_format == "json":
                print(json.dumps(result))
            else:
                if "choices" in result and result["choices"]:
                    choice = result["choices"][0]
                    if "message" in choice and "content" in choice["message"]:
                        console.print(choice["message"]["content"])
                    elif "content" in choice:
                        console.print(choice["content"])
                else:
                    console.print(result)


def main():
    """Main entry point for the CLI."""
    parser = argparse.ArgumentParser(description="Agent Management CLI")
    parser.add_argument(
        "--api-url",
        default=DEFAULT_API_URL,
        help=f"API URL (default: {DEFAULT_API_URL})",
    )
    parser.add_argument(
        "--output-format",
        choices=["human", "json"],
        default=DEFAULT_OUTPUT_FORMAT,
        help=f"Output format (default: {DEFAULT_OUTPUT_FORMAT})",
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
    invoke_parser.add_argument("--stream", action="store_true", help="Stream the response")
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
