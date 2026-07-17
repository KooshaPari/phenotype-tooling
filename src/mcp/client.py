"""
MCP Client implementation for loading and executing tools from MCP servers.
"""

import asyncio
import json
import time
from pathlib import Path
from typing import List, Optional, Dict, Any

from langchain_mcp_adapters.client import MultiServerMCPClient
from langchain_mcp_adapters.tools import load_mcp_tools
from langchain_core.tools import BaseTool

from ..utils.config import get_mcp_servers_config, get_mcp_tools_config


async def load_mcp_config() -> Dict[str, Any]:
    """
    Load the MCP configuration from the config file.
    """
    # Try the new config path first
    config_path = Path(__file__).parent.parent.parent.parent / "new" / "config.json"
    if not config_path.exists():
        # Fall back to the old config path
        config_path = (
            Path(__file__).parent.parent.parent.parent / "config" / "config.json"
        )
        if not config_path.exists():
            print(f"Config file not found at {config_path}")
            return {}

    with open(config_path, "r") as f:
        config = json.load(f)

    # Check if the config has the mcpServers key
    if "mcpServers" in config:
        # Extract the mcpServers section
        servers_config = {}

        # Process each server configuration
        for server_name, server_config in config["mcpServers"].items():
            # Skip disabled servers
            if server_config.get("disabled", False):
                continue

            # Create a new config with the correct keys
            new_config = server_config.copy()

            # Update transportType to transport if needed
            if "transportType" in new_config:
                new_config["transport"] = new_config.pop("transportType")
                print(f"Updated transportType to transport for {server_name}")
            # If neither transport nor transportType exists, default to stdio
            elif "transport" not in new_config:
                new_config["transport"] = "stdio"

            # Add the server config to the result
            servers_config[server_name] = new_config

        return servers_config
    else:
        # If no mcpServers key, assume the config is already in the correct format
        servers_config = {}

        # Process each server configuration
        for server_name, server_config in config.items():
            # Skip disabled servers
            if server_config.get("disabled", False):
                continue

            # Create a new config with the correct keys
            new_config = server_config.copy()

            # Update transportType to transport if needed
            if "transportType" in new_config:
                new_config["transport"] = new_config.pop("transportType")
                print(f"Updated transportType to transport for {server_name}")
            # If neither transport nor transportType exists, default to stdio
            elif "transport" not in new_config:
                new_config["transport"] = "stdio"

            # Add the server config to the result
            servers_config[server_name] = new_config

        return servers_config


class MCPClientManager:
    """
    Manager for MCP clients that handles loading tools from config.json
    and provides a unified interface for tool execution.
    Implements a singleton pattern with caching to prevent unnecessary reinitializations.
    """

    def __init__(self, config_path: Optional[str] = None):
        """
        Initialize the MCP client manager.

        Args:
            config_path: Path to the config file. If None, uses the default config.json.
        """
        self.mcp_servers_config = get_mcp_servers_config()
        self.mcp_tools_config = get_mcp_tools_config()
        self.multi_client: Optional[MultiServerMCPClient] = None
        self.tools: List[BaseTool] = []

        # Add caching and locking
        self.last_initialization_time = 0
        self.initialization_lock = asyncio.Lock()
        self.initialization_in_progress = False
        self.cache_ttl = 300  # 5 minutes cache TTL

    async def initialize(self) -> None:
        """
        Initialize the MCP client and load tools.
        Uses caching and locking to prevent unnecessary reinitializations.
        """
        # Check if initialization was done recently
        current_time = time.time()
        if self.tools and (
            current_time - self.last_initialization_time < self.cache_ttl
        ):
            # Tools are already loaded and cache is fresh
            print(
                f"Using cached MCP tools ({len(self.tools)} tools, cache age: {int(current_time - self.last_initialization_time)}s)"
            )
            return

        # Use a lock to prevent multiple concurrent initializations
        async with self.initialization_lock:
            # Check again in case another task acquired the lock first
            if self.tools and (
                current_time - self.last_initialization_time < self.cache_ttl
            ):
                print(
                    f"Using cached MCP tools ({len(self.tools)} tools, cache age: {int(current_time - self.last_initialization_time)}s)"
                )
                return

            # Set flag to indicate initialization is in progress
            self.initialization_in_progress = True

            try:
                if not self.mcp_servers_config:
                    print(
                        "Warning: No MCP servers configured. Skipping MCP client initialization."
                    )
                    return

                # Initialize the MultiServerMCPClient directly with the server configs
                print(
                    f"Initializing MCP client with {len(self.mcp_servers_config)} servers"
                )
                for name in self.mcp_servers_config:
                    print(f"Initializing MCP server: {name}")

                # Close existing client if it exists
                if self.multi_client:
                    try:
                        await self.close()
                    except Exception as e:
                        print(f"Error closing existing MCP client: {e}")

                # Create the MultiServerMCPClient
                self.multi_client = MultiServerMCPClient(self.mcp_servers_config)

                self.tools = await self.multi_client.get_tools()
                print(
                    f"Loaded {len(self.tools)} MCP tools from {len(self.mcp_servers_config)} servers."
                )

                # Update the last initialization time
                self.last_initialization_time = time.time()

            except Exception as e:
                print(f"Error initializing MCP client: {e}")
                import traceback

                print(traceback.format_exc())
                self.multi_client = None
                self.tools = []
            finally:
                self.initialization_in_progress = False

    def _ensure_async_support(self):
        """
        Ensure all tools have proper async support.
        This method converts StructuredTools to proper Tools with async support.
        """
        from langchain_core.tools import StructuredTool, BaseTool, Tool
        import asyncio
        import inspect
        import types

        # Separate Canvas tools from other tools
        canvas_tools = []
        other_tools = []

        for tool in self.tools:
            if tool.name.startswith("canvas_"):
                canvas_tools.append(tool)
            else:
                other_tools.append(tool)

        # Process Canvas tools - convert them to proper Tools with async support
        wrapped_canvas_tools = []
        for tool in canvas_tools:
            print(f"Processing Canvas tool: {tool.name}")

            # Create a proper async function for Canvas tools that takes no arguments
            async def _async_run_no_args():
                """Async implementation that runs the tool with no arguments."""
                tool_name = tool.name

                try:
                    print(f"CANVAS TOOL: Calling {tool_name} with no arguments")

                    # Determine the best method to call
                    if hasattr(tool, "_run"):
                        method_name = "_run"
                        method = tool._run
                    elif hasattr(tool, "func"):
                        method_name = "func"
                        method = tool.func
                    elif hasattr(tool, "run"):
                        method_name = "run"
                        method = tool.run
                    elif hasattr(tool, "invoke"):
                        method_name = "invoke"
                        method = tool.invoke
                    else:
                        raise NotImplementedError(
                            f"Canvas tool {tool_name} has no compatible method"
                        )

                    print(f"CANVAS TOOL: Using {method_name} method for {tool_name}")

                    # Try different ways to call the method
                    try:
                        # First try with no arguments
                        result = await asyncio.to_thread(method)
                        print(
                            f"CANVAS TOOL: {tool_name} called with no arguments successfully"
                        )
                    except Exception as e1:
                        print(
                            f"CANVAS TOOL: Error calling {tool_name} with no arguments: {str(e1)}"
                        )
                        try:
                            # Then try with empty string
                            result = await asyncio.to_thread(method, "")
                            print(
                                f"CANVAS TOOL: {tool_name} called with empty string successfully"
                            )
                        except Exception as e2:
                            print(
                                f"CANVAS TOOL: Error calling {tool_name} with empty string: {str(e2)}"
                            )
                            # Finally try with empty dict
                            result = await asyncio.to_thread(method, {})
                            print(
                                f"CANVAS TOOL: {tool_name} called with empty dict successfully"
                            )

                    print(f"CANVAS TOOL: {tool_name} returned: {result}")
                    return result
                except Exception as e:
                    print(f"CANVAS TOOL ERROR: {str(e)}")
                    print(f"CANVAS TOOL ERROR TYPE: {type(e).__name__}")
                    import traceback

                    print(f"CANVAS TOOL TRACEBACK: {traceback.format_exc()}")
                    raise

            # Create a sync function that returns a friendly message with the correct tool name
            # We need to create a closure to capture the current tool name
            tool_name_for_closure = tool.name

            def _sync_run(tool_input=None):
                """Sync implementation that returns a friendly message."""
                # Use the captured tool name from the closure
                print(
                    f"SYNC_RUN: Using tool name from closure: {tool_name_for_closure}"
                )
                return f"I'm sorry, but I couldn't access the Canvas tool '{tool_name_for_closure}' at this time. Please try again later or contact support if the issue persists."

            # Create a new Tool with proper async support
            # For Canvas tools, we need to handle the args_schema differently
            # We'll create a simple function that takes a single string argument
            from pydantic import BaseModel, Field
            from typing import Optional

            class EmptySchema(BaseModel):
                """Empty schema for Canvas tools."""

                input: Optional[str] = None

            new_tool = Tool(
                name=tool.name,
                description=tool.description,
                func=_sync_run,  # Sync function that raises an error
                coroutine=_async_run_no_args,  # Async function that works with no args
                args_schema=EmptySchema,  # Use an empty schema to avoid argument issues
                return_direct=getattr(tool, "return_direct", False),
            )

            print(f"Created new Tool for Canvas tool: {tool.name}")
            wrapped_canvas_tools.append(new_tool)

        # Process other tools - add async support if needed
        wrapped_other_tools = []
        for tool in other_tools:
            if isinstance(tool, StructuredTool) and not hasattr(tool, "ainvoke"):
                print(
                    f"Converting StructuredTool to Tool with async support: {tool.name}"
                )

                # Create a new Tool with proper async support
                async def _async_run(tool_input, original_tool=tool):
                    """Async implementation that runs the tool in a thread."""
                    print(f"Async wrapper for {original_tool.name}")

                    if hasattr(original_tool, "_run"):
                        if isinstance(tool_input, dict):
                            return await asyncio.to_thread(
                                original_tool._run, **tool_input
                            )
                        else:
                            return await asyncio.to_thread(
                                original_tool._run, tool_input
                            )
                    elif hasattr(original_tool, "func"):
                        if isinstance(tool_input, dict):
                            return await asyncio.to_thread(
                                original_tool.func, **tool_input
                            )
                        else:
                            return await asyncio.to_thread(
                                original_tool.func, tool_input
                            )
                    elif hasattr(original_tool, "run"):
                        if isinstance(tool_input, dict):
                            return await asyncio.to_thread(
                                original_tool.run, **tool_input
                            )
                        else:
                            return await asyncio.to_thread(
                                original_tool.run, tool_input
                            )
                    elif hasattr(original_tool, "invoke"):
                        return await asyncio.to_thread(original_tool.invoke, tool_input)
                    else:
                        raise NotImplementedError(
                            f"Tool {original_tool.name} has no compatible method"
                        )

                # Create a sync function that works properly
                def _sync_run(tool_input):
                    """Sync implementation that calls the appropriate method."""
                    print(f"Sync wrapper for {tool.name}")

                    if hasattr(tool, "_run"):
                        if isinstance(tool_input, dict):
                            return tool._run(**tool_input)
                        else:
                            return tool._run(tool_input)
                    elif hasattr(tool, "func"):
                        if isinstance(tool_input, dict):
                            return tool.func(**tool_input)
                        else:
                            return tool.func(tool_input)
                    elif hasattr(tool, "run"):
                        if isinstance(tool_input, dict):
                            return tool.run(**tool_input)
                        else:
                            return tool.run(tool_input)
                    elif hasattr(tool, "invoke"):
                        return tool.invoke(tool_input)
                    else:
                        raise NotImplementedError(
                            f"Tool {tool.name} has no compatible method"
                        )

                # Create a new Tool with proper async support
                new_tool = Tool(
                    name=tool.name,
                    description=tool.description,
                    func=_sync_run,
                    coroutine=_async_run,
                    args_schema=getattr(tool, "args_schema", None),
                    return_direct=getattr(tool, "return_direct", False),
                )

                print(f"Converted StructuredTool to Tool: {tool.name}")
                wrapped_other_tools.append(new_tool)
            else:
                wrapped_other_tools.append(tool)

        # Combine all tools
        self.tools = wrapped_canvas_tools + wrapped_other_tools
        print(f"Total tools after processing: {len(self.tools)}")
        print(f"Canvas tools: {len(wrapped_canvas_tools)}")
        print(f"Other tools: {len(wrapped_other_tools)}")

    def get_tools(self) -> List[BaseTool]:
        """
        Get the loaded MCP tools.

        Returns:
            List of LangChain tools loaded from MCP servers.
        """
        return self.tools

    async def close(self) -> None:
        """
        Close the MCP client connections.
        """
        if self.multi_client:
            # Check if the client has an aclose method, otherwise use close
            if hasattr(self.multi_client, "aclose"):
                await self.multi_client.aclose()
            elif hasattr(self.multi_client, "close"):
                await self.multi_client.close()
            print("Successfully closed MCP server connections")

        # Reset state
        self.multi_client = None
        self.tools = []


# Singleton instance for application-wide use
mcp_client_manager = MCPClientManager()


async def initialize_mcp_client() -> None:
    """
    Initialize the MCP client manager.
    """
    await mcp_client_manager.initialize()


# Cache for filtered tools to avoid repeated filtering
_tools_cache = {}
_tools_cache_timestamp = 0
_tools_cache_ttl = 300  # 5 minutes cache TTL


async def get_mcp_tools(
    max_tools: Optional[int] = None, include_canvas_tools: bool = False
) -> List[BaseTool]:
    """
    Get the MCP tools, optionally limiting the number of tools returned.
    Uses caching to avoid repeated filtering and initialization.

    Args:
        max_tools: Optional maximum number of tools to return. If None, returns all tools.
                  If specified, returns at most this many tools.
                  If set to 0, returns an empty list (no tools).
        include_canvas_tools: Whether to include Canvas tools in the result. Default is False.

    Returns:
        List of LangChain tools loaded from MCP servers, limited to max_tools if specified.
    """
    global _tools_cache, _tools_cache_timestamp

    # If max_tools is 0, return an empty list (no tools)
    if max_tools == 0:
        print("Tools disabled: max_tools is set to 0")
        return []

    # Create a cache key based on the parameters (include version for cache invalidation)
    cache_key = f"{max_tools}_{include_canvas_tools}_v6"

    # Check if we have a valid cache entry
    current_time = time.time()
    if (
        cache_key in _tools_cache
        and (current_time - _tools_cache_timestamp < _tools_cache_ttl)
        and _tools_cache[cache_key]
    ):
        print(
            f"Using cached filtered tools for key {cache_key} (cache age: {int(current_time - _tools_cache_timestamp)}s)"
        )
        return _tools_cache[cache_key]

    # Initialize MCP client if tools are not loaded yet
    if not mcp_client_manager.tools:
        print("MCP tools not loaded yet, initializing client...")
        await initialize_mcp_client()

    # If still no tools after initialization, return empty list
    if not mcp_client_manager.tools:
        print("No MCP tools available after initialization")
        return []

    # Filter out Canvas tools if include_canvas_tools is False
    if not include_canvas_tools:
        tools = [
            tool
            for tool in mcp_client_manager.tools
            if not tool.name.startswith("canvas_")
        ]
        print(
            f"Filtered out Canvas tools: {len(mcp_client_manager.tools) - len(tools)} tools removed"
        )
    else:
        tools = (
            mcp_client_manager.tools.copy()
        )  # Create a copy to avoid modifying the original

    # Limit the number of tools if max_tools is specified and less than the total
    if max_tools is not None and len(tools) > max_tools:
        print(
            f"Warning: Limiting tools from {len(tools)} to {max_tools} due to API constraints."
        )

        # Prioritize agent management tools
        priority_tool_names = [
            "create_agent",
            "list_agents",
            "get_agent",
            "update_agent",
            "delete_agent",
            "check_agent_health",
            "view_agent_console",
            "register_agent",
            "send_message",
            "get_messages",
            "broadcast_message",
            "create_task",
            "list_tasks",
            "get_task",
            "update_task",
            "delete_task",
            "assign_task",
            "complete_task",
        ]

        # Debug: Print all available tool names
        all_tool_names = [tool.name for tool in tools]
        print(f"DEBUG: All available tools: {sorted(all_tool_names)}")

        # Separate priority tools from other tools
        priority_tools = []
        other_tools = []

        for tool in tools:
            if tool.name in priority_tool_names:
                priority_tools.append(tool)
                print(f"DEBUG: Found priority tool: {tool.name}")
            else:
                other_tools.append(tool)

        # Sort each group by name for consistency
        priority_tools = sorted(priority_tools, key=lambda x: x.name)
        other_tools = sorted(other_tools, key=lambda x: x.name)

        # Combine priority tools first, then fill with other tools
        combined_tools = priority_tools + other_tools

        # Filter out tools with invalid schemas for OpenAI API
        valid_tools = []
        for tool in combined_tools:
            # Check if this tool has a problematic schema
            skip_tool = False

            if hasattr(tool, "args_schema") and tool.args_schema:
                try:
                    # Handle both Pydantic models and dictionaries
                    if hasattr(tool.args_schema, "model_json_schema"):
                        # Pydantic model
                        schema = tool.args_schema.model_json_schema()
                    elif isinstance(tool.args_schema, dict):
                        # Dictionary schema (from MCP tools)
                        schema = tool.args_schema
                    else:
                        # Unknown schema type, skip validation
                        schema = None

                    if schema:
                        # Check if the schema has invalid top-level properties for OpenAI
                        if any(
                            key in schema
                            for key in ["oneOf", "anyOf", "allOf", "enum", "not"]
                        ):
                            print(
                                f"DEBUG: Skipping tool '{tool.name}' due to invalid schema (contains {[key for key in ['oneOf', 'anyOf', 'allOf', 'enum', 'not'] if key in schema]})"
                            )
                            skip_tool = True

                        # Check if the schema type is 'object'
                        elif schema.get("type") != "object":
                            print(
                                f"DEBUG: Skipping tool '{tool.name}' due to invalid schema (type is '{schema.get('type')}', not 'object')"
                            )
                            skip_tool = True

                except Exception as e:
                    print(
                        f"DEBUG: Skipping tool '{tool.name}' due to schema validation error: {e}"
                    )
                    skip_tool = True

            if not skip_tool:
                valid_tools.append(tool)

        result = valid_tools[:max_tools]
        print(
            f"DEBUG: Filtered out {len(combined_tools) - len(valid_tools)} tools with invalid schemas"
        )

        print(
            f"DEBUG: Selected {len(priority_tools)} priority tools and {len(result) - len(priority_tools)} other tools"
        )
        print(
            f"DEBUG: Priority tools selected: {[tool.name for tool in priority_tools]}"
        )
        print(
            f"DEBUG: First 10 tools in final selection: {[tool.name for tool in result[:10]]}"
        )
    else:
        result = tools

    # Update the cache
    _tools_cache[cache_key] = result
    _tools_cache_timestamp = current_time

    print(f"Cached filtered tools for key {cache_key} ({len(result)} tools)")
    return result


async def close_mcp_client() -> None:
    """
    Close the MCP client connections.
    """
    await mcp_client_manager.close()
