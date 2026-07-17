"""
MCP server for agent management.

This module provides a MCP server for creating, retrieving, updating, and deleting agents,
as well as for agent communication.
"""

import asyncio
import json
import os
import sys
from typing import Dict, List, Optional, Any, Union, Callable

from src.mcp_api_client import MCPServer, Tool, ToolCall, ToolResponse

# Add the parent directory to the path
sys.path.append(
    os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
)

from ..tools.agent_management_tools import (
    create_agent_tool,
    create_independent_agent_tool,
    create_swarm_team_tool,
    invoke_agent_http_tool,
    view_agent_console_tool,
    get_agent_tool,
    list_agents_tool,
    update_agent_tool,
    delete_agent_tool,
    invoke_agent_tool,
    send_message_tool,
    broadcast_message_tool,
    get_messages_tool,
    receive_messages_tool,
)
from ...utils.logging import logger


class AgentManagementServer:
    """
    MCP server for agent management.
    """

    def __init__(self, host: str = "localhost", port: int = 8080):
        """
        Initialize the agent management server.

        Args:
            host: The host to bind to.
            port: The port to bind to.
        """
        self.host = host
        self.port = port
        self.server = MCPServer(name="agent-management", host=host, port=port)
        self.logger = logger

        # Register tools
        self._register_tools()

    def _register_tools(self):
        """Register the agent management tools."""
        # Agent CRUD tools
        self.server.register_tool(
            Tool(
                name="create_agent",
                description="Create a new agent",
                parameters={
                    "type": "object",
                    "properties": {
                        "name": {
                            "type": "string",
                            "description": "The name of the agent",
                        },
                        "model_name": {
                            "type": "string",
                            "description": "The name of the model to use",
                        },
                        "system_prompt": {
                            "type": "string",
                            "description": "Optional custom system prompt to use",
                        },
                        "mcp_tools_config_path": {
                            "type": "string",
                            "description": "Optional path to MCP tools configuration",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional description of the agent",
                        },
                        "temperature": {
                            "type": "number",
                            "description": "The temperature to use for generation",
                            "default": 0.7,
                        },
                        "max_tools": {
                            "type": "integer",
                            "description": "Maximum number of tools to use",
                            "default": 128,
                        },
                    },
                    "required": ["name", "model_name"],
                },
                handler=self._handle_create_agent,
            )
        )

        self.server.register_tool(
            Tool(
                name="get_agent",
                description="Get an agent by ID",
                parameters={
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "The agent ID",
                        },
                    },
                    "required": ["agent_id"],
                },
                handler=self._handle_get_agent,
            )
        )

        self.server.register_tool(
            Tool(
                name="list_agents",
                description="List all agents",
                parameters={
                    "type": "object",
                    "properties": {},
                },
                handler=self._handle_list_agents,
            )
        )

        self.server.register_tool(
            Tool(
                name="update_agent",
                description="Update an agent",
                parameters={
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "The agent ID",
                        },
                        "name": {
                            "type": "string",
                            "description": "Optional new name for the agent",
                        },
                        "model_name": {
                            "type": "string",
                            "description": "Optional new model name for the agent",
                        },
                        "system_prompt": {
                            "type": "string",
                            "description": "Optional new system prompt for the agent",
                        },
                        "mcp_tools_config_path": {
                            "type": "string",
                            "description": "Optional new MCP tools configuration path for the agent",
                        },
                        "description": {
                            "type": "string",
                            "description": "Optional new description for the agent",
                        },
                        "temperature": {
                            "type": "number",
                            "description": "Optional new temperature for the agent",
                        },
                        "max_tools": {
                            "type": "integer",
                            "description": "Optional new maximum number of tools for the agent",
                        },
                        "status": {
                            "type": "string",
                            "description": "Optional new status for the agent",
                        },
                    },
                    "required": ["agent_id"],
                },
                handler=self._handle_update_agent,
            )
        )

        self.server.register_tool(
            Tool(
                name="delete_agent",
                description="Delete an agent",
                parameters={
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "The agent ID",
                        },
                    },
                    "required": ["agent_id"],
                },
                handler=self._handle_delete_agent,
            )
        )

        # Agent invocation tool
        self.server.register_tool(
            Tool(
                name="invoke_agent",
                description="Invoke an agent",
                parameters={
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "The agent ID",
                        },
                        "message": {
                            "type": "string",
                            "description": "The message to send to the agent",
                        },
                        "temperature": {
                            "type": "number",
                            "description": "Optional temperature override",
                        },
                        "max_tokens": {
                            "type": "integer",
                            "description": "Optional max tokens override",
                        },
                    },
                    "required": ["agent_id", "message"],
                },
                handler=self._handle_invoke_agent,
            )
        )

        # Agent communication tools
        self.server.register_tool(
            Tool(
                name="send_message",
                description="Send a message from one agent to another",
                parameters={
                    "type": "object",
                    "properties": {
                        "sender_id": {
                            "type": "string",
                            "description": "The sender agent ID",
                        },
                        "recipient_id": {
                            "type": "string",
                            "description": "The recipient agent ID",
                        },
                        "content": {
                            "type": "string",
                            "description": "The message content",
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Optional message metadata",
                        },
                    },
                    "required": ["sender_id", "recipient_id", "content"],
                },
                handler=self._handle_send_message,
            )
        )

        self.server.register_tool(
            Tool(
                name="broadcast_message",
                description="Broadcast a message to multiple agents",
                parameters={
                    "type": "object",
                    "properties": {
                        "sender_id": {
                            "type": "string",
                            "description": "The sender agent ID",
                        },
                        "content": {
                            "type": "string",
                            "description": "The message content",
                        },
                        "recipient_ids": {
                            "type": "array",
                            "items": {"type": "string"},
                            "description": "Optional list of recipient agent IDs",
                        },
                        "metadata": {
                            "type": "object",
                            "description": "Optional message metadata",
                        },
                    },
                    "required": ["sender_id", "content"],
                },
                handler=self._handle_broadcast_message,
            )
        )

        self.server.register_tool(
            Tool(
                name="get_messages",
                description="Get messages for an agent",
                parameters={
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "The agent ID",
                        },
                        "other_agent_id": {
                            "type": "string",
                            "description": "Optional other agent ID to filter messages",
                        },
                        "limit": {
                            "type": "integer",
                            "description": "Optional limit on the number of messages to return",
                        },
                    },
                    "required": ["agent_id"],
                },
                handler=self._handle_get_messages,
            )
        )

        self.server.register_tool(
            Tool(
                name="receive_messages",
                description="Receive messages for an agent",
                parameters={
                    "type": "object",
                    "properties": {
                        "agent_id": {
                            "type": "string",
                            "description": "The agent ID",
                        },
                        "other_agent_id": {
                            "type": "string",
                            "description": "Optional other agent ID to filter messages",
                        },
                        "timeout": {
                            "type": "number",
                            "description": "Optional timeout in seconds",
                        },
                    },
                    "required": ["agent_id"],
                },
                handler=self._handle_receive_messages,
            )
        )

    async def _handle_create_agent(self, tool_call: ToolCall) -> ToolResponse:
        """
        Handle the create_agent tool call.

        Args:
            tool_call: The tool call.

        Returns:
            The tool response.
        """
        try:
            # Extract the arguments
            args = tool_call.arguments

            # Call the tool
            result = await create_agent_tool(
                name=args.get("name"),
                model_name=args.get("model_name"),
                system_prompt=args.get("system_prompt"),
                mcp_tools_config_path=args.get("mcp_tools_config_path"),
                description=args.get("description"),
                temperature=args.get("temperature", 0.7),
                max_tools=args.get("max_tools", 128),
            )

            return ToolResponse(result=result)
        except Exception as e:
            self.logger.error(f"Error handling create_agent tool call: {e}")
            return ToolResponse(result={"error": str(e)})

    async def _handle_get_agent(self, tool_call: ToolCall) -> ToolResponse:
        """
        Handle the get_agent tool call.

        Args:
            tool_call: The tool call.

        Returns:
            The tool response.
        """
        try:
            # Extract the arguments
            args = tool_call.arguments

            # Call the tool
            result = await get_agent_tool(agent_id=args.get("agent_id"))

            return ToolResponse(result=result)
        except Exception as e:
            self.logger.error(f"Error handling get_agent tool call: {e}")
            return ToolResponse(result={"error": str(e)})

    async def _handle_list_agents(self, tool_call: ToolCall) -> ToolResponse:
        """
        Handle the list_agents tool call.

        Args:
            tool_call: The tool call.

        Returns:
            The tool response.
        """
        try:
            # Call the tool
            result = await list_agents_tool()

            return ToolResponse(result=result)
        except Exception as e:
            self.logger.error(f"Error handling list_agents tool call: {e}")
            return ToolResponse(result={"error": str(e)})

    async def _handle_update_agent(self, tool_call: ToolCall) -> ToolResponse:
        """
        Handle the update_agent tool call.

        Args:
            tool_call: The tool call.

        Returns:
            The tool response.
        """
        try:
            # Extract the arguments
            args = tool_call.arguments

            # Call the tool
            result = await update_agent_tool(
                agent_id=args.get("agent_id"),
                name=args.get("name"),
                model_name=args.get("model_name"),
                system_prompt=args.get("system_prompt"),
                mcp_tools_config_path=args.get("mcp_tools_config_path"),
                description=args.get("description"),
                temperature=args.get("temperature"),
                max_tools=args.get("max_tools"),
                status=args.get("status"),
            )

            return ToolResponse(result=result)
        except Exception as e:
            self.logger.error(f"Error handling update_agent tool call: {e}")
            return ToolResponse(result={"error": str(e)})

    async def _handle_delete_agent(self, tool_call: ToolCall) -> ToolResponse:
        """
        Handle the delete_agent tool call.

        Args:
            tool_call: The tool call.

        Returns:
            The tool response.
        """
        try:
            # Extract the arguments
            args = tool_call.arguments

            # Call the tool
            result = await delete_agent_tool(agent_id=args.get("agent_id"))

            return ToolResponse(result=result)
        except Exception as e:
            self.logger.error(f"Error handling delete_agent tool call: {e}")
            return ToolResponse(result={"error": str(e)})

    async def _handle_invoke_agent(self, tool_call: ToolCall) -> ToolResponse:
        """
        Handle the invoke_agent tool call.

        Args:
            tool_call: The tool call.

        Returns:
            The tool response.
        """
        try:
            # Extract the arguments
            args = tool_call.arguments

            # Call the tool
            result = await invoke_agent_tool(
                agent_id=args.get("agent_id"),
                message=args.get("message"),
                temperature=args.get("temperature"),
                max_tokens=args.get("max_tokens"),
            )

            return ToolResponse(result=result)
        except Exception as e:
            self.logger.error(f"Error handling invoke_agent tool call: {e}")
            return ToolResponse(result={"error": str(e)})

    async def _handle_send_message(self, tool_call: ToolCall) -> ToolResponse:
        """
        Handle the send_message tool call.

        Args:
            tool_call: The tool call.

        Returns:
            The tool response.
        """
        try:
            # Extract the arguments
            args = tool_call.arguments

            # Call the tool
            result = await send_message_tool(
                sender_id=args.get("sender_id"),
                recipient_id=args.get("recipient_id"),
                content=args.get("content"),
                metadata=args.get("metadata"),
            )

            return ToolResponse(result=result)
        except Exception as e:
            self.logger.error(f"Error handling send_message tool call: {e}")
            return ToolResponse(result={"error": str(e)})

    async def _handle_broadcast_message(self, tool_call: ToolCall) -> ToolResponse:
        """
        Handle the broadcast_message tool call.

        Args:
            tool_call: The tool call.

        Returns:
            The tool response.
        """
        try:
            # Extract the arguments
            args = tool_call.arguments

            # Call the tool
            result = await broadcast_message_tool(
                sender_id=args.get("sender_id"),
                content=args.get("content"),
                recipient_ids=args.get("recipient_ids"),
                metadata=args.get("metadata"),
            )

            return ToolResponse(result=result)
        except Exception as e:
            self.logger.error(f"Error handling broadcast_message tool call: {e}")
            return ToolResponse(result={"error": str(e)})

    async def _handle_get_messages(self, tool_call: ToolCall) -> ToolResponse:
        """
        Handle the get_messages tool call.

        Args:
            tool_call: The tool call.

        Returns:
            The tool response.
        """
        try:
            # Extract the arguments
            args = tool_call.arguments

            # Call the tool
            result = await get_messages_tool(
                agent_id=args.get("agent_id"),
                other_agent_id=args.get("other_agent_id"),
                limit=args.get("limit"),
            )

            return ToolResponse(result=result)
        except Exception as e:
            self.logger.error(f"Error handling get_messages tool call: {e}")
            return ToolResponse(result={"error": str(e)})

    async def _handle_receive_messages(self, tool_call: ToolCall) -> ToolResponse:
        """
        Handle the receive_messages tool call.

        Args:
            tool_call: The tool call.

        Returns:
            The tool response.
        """
        try:
            # Extract the arguments
            args = tool_call.arguments

            # Call the tool
            result = await receive_messages_tool(
                agent_id=args.get("agent_id"),
                other_agent_id=args.get("other_agent_id"),
                timeout=args.get("timeout"),
            )

            return ToolResponse(result=result)
        except Exception as e:
            self.logger.error(f"Error handling receive_messages tool call: {e}")
            return ToolResponse(result={"error": str(e)})

    def start_sync(self):
        """Start the server synchronously."""
        self.server.start_sync(host=self.host, port=self.port)
        self.logger.info(
            f"Agent management MCP server started on {self.host}:{self.port}"
        )

    async def start(self):
        """Start the server asynchronously."""
        await self.server.start(host=self.host, port=self.port)
        self.logger.info(
            f"Agent management MCP server started on {self.host}:{self.port}"
        )

    async def stop(self):
        """Stop the server."""
        await self.server.stop()
        self.logger.info("Agent management MCP server stopped")


async def main():
    """Main entry point for the server."""
    # Parse command-line arguments
    import argparse

    parser = argparse.ArgumentParser(description="Agent Management MCP Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")

    args = parser.parse_args()

    # Create and start the server
    server = AgentManagementServer(host=args.host, port=args.port)

    try:
        await server.start()

        # Keep the server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        # Stop the server on keyboard interrupt
        await server.stop()
    except Exception as e:
        logger.error(f"Error running agent management MCP server: {e}")
        await server.stop()


if __name__ == "__main__":
    asyncio.run(main())
