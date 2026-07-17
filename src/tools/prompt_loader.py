"""
Extensible tool loader that converts MCP tools to system prompt entries.

This module provides a flexible system for loading tools into the system prompt
instead of the tools array, enabling sophisticated tool selection logic and
better extensibility for future enhancements.
"""

import json
import time
from typing import List, Dict, Any, Optional, Callable
from abc import ABC, abstractmethod

from ..mcp.client import get_mcp_tools


class ToolSelector(ABC):
    """Abstract base class for tool selection strategies."""
    
    @abstractmethod
    def select_tools(self, tools: List[Any], max_tools: Optional[int] = None) -> List[Any]:
        """
        Select tools based on the strategy.
        
        Args:
            tools: List of available tools
            max_tools: Maximum number of tools to select
            
        Returns:
            List of selected tools
        """
        pass


class PriorityToolSelector(ToolSelector):
    """Tool selector that prioritizes specific tools."""
    
    def __init__(self, priority_tool_names: List[str]):
        """
        Initialize with priority tool names.
        
        Args:
            priority_tool_names: List of tool names to prioritize
        """
        self.priority_tool_names = priority_tool_names
    
    def select_tools(self, tools: List[Any], max_tools: Optional[int] = None) -> List[Any]:
        """Select tools with priority-based filtering."""
        if max_tools is None or len(tools) <= max_tools:
            return tools
        
        # Separate priority tools from other tools
        priority_tools = []
        other_tools = []
        
        for tool in tools:
            if tool.name in self.priority_tool_names:
                priority_tools.append(tool)
            else:
                other_tools.append(tool)
        
        # Sort each group by name for consistency
        priority_tools = sorted(priority_tools, key=lambda x: x.name)
        other_tools = sorted(other_tools, key=lambda x: x.name)
        
        # Combine priority tools first, then fill with other tools
        combined_tools = priority_tools + other_tools
        return combined_tools[:max_tools]


class AllToolsSelector(ToolSelector):
    """Tool selector that selects all tools (no filtering)."""
    
    def select_tools(self, tools: List[Any], max_tools: Optional[int] = None) -> List[Any]:
        """Select all tools without filtering."""
        return tools


class ToolPromptFormatter:
    """Formats tools as system prompt entries."""
    
    @staticmethod
    def format_tool_as_prompt_entry(tool: Any) -> str:
        """
        Convert a tool to a system prompt entry.
        
        Args:
            tool: The tool to format
            
        Returns:
            Formatted prompt entry string
        """
        # Get tool schema
        schema = None
        if hasattr(tool, 'args_schema') and tool.args_schema:
            if hasattr(tool.args_schema, 'model_json_schema'):
                schema = tool.args_schema.model_json_schema()
            elif isinstance(tool.args_schema, dict):
                schema = tool.args_schema
        
        # Format parameters
        parameters_text = ""
        if schema and 'properties' in schema:
            parameters = []
            required_fields = schema.get('required', [])
            
            for param_name, param_info in schema['properties'].items():
                param_type = param_info.get('type', 'string')
                param_desc = param_info.get('description', 'No description available')
                required_marker = " (required)" if param_name in required_fields else " (optional)"
                
                parameters.append(f"- {param_name}: {param_type}{required_marker} - {param_desc}")
            
            if parameters:
                parameters_text = f"\nParameters:\n" + "\n".join(parameters)
        
        # Format the tool entry
        tool_entry = f"""
## {tool.name}
Description: {getattr(tool, 'description', 'No description available')}{parameters_text}
Usage:
<{tool.name}>
{_generate_parameter_template(schema)}
</{tool.name}>
"""
        return tool_entry.strip()
    
    @staticmethod
    def format_tools_section(tools: List[Any]) -> str:
        """
        Format multiple tools as a complete tools section.
        
        Args:
            tools: List of tools to format
            
        Returns:
            Complete tools section for system prompt
        """
        if not tools:
            return "# Available Tools\n\nNo tools are currently available."
        
        tool_entries = []
        for tool in tools:
            try:
                entry = ToolPromptFormatter.format_tool_as_prompt_entry(tool)
                tool_entries.append(entry)
            except Exception as e:
                print(f"Warning: Failed to format tool '{getattr(tool, 'name', 'unknown')}': {e}")
                continue
        
        tools_section = "# Available Tools\n\n" + "\n\n".join(tool_entries)
        return tools_section


def _generate_parameter_template(schema: Optional[Dict[str, Any]]) -> str:
    """Generate parameter template for tool usage example."""
    if not schema or 'properties' not in schema:
        return "<parameter_name>parameter_value</parameter_name>"
    
    template_parts = []
    for param_name, param_info in schema['properties'].items():
        param_type = param_info.get('type', 'string')
        
        if param_type == 'object':
            template_parts.append(f"<{param_name}>{{\n  \"key\": \"value\"\n}}</{param_name}>")
        elif param_type == 'array':
            template_parts.append(f"<{param_name}>[\"item1\", \"item2\"]</{param_name}>")
        elif param_type == 'boolean':
            template_parts.append(f"<{param_name}>true</{param_name}>")
        elif param_type == 'number' or param_type == 'integer':
            template_parts.append(f"<{param_name}>123</{param_name}>")
        else:
            template_parts.append(f"<{param_name}>value</{param_name}>")
    
    return "\n".join(template_parts) if template_parts else "<parameter_name>parameter_value</parameter_name>"


class ExtensibleToolLoader:
    """
    Extensible tool loader that converts MCP tools to system prompt entries.
    
    This class provides hooks for future smart tool selection logic and
    maintains flexibility for different tool selection strategies.
    """
    
    def __init__(self, tool_selector: Optional[ToolSelector] = None):
        """
        Initialize the tool loader.
        
        Args:
            tool_selector: Strategy for selecting tools. Defaults to AllToolsSelector.
        """
        self.tool_selector = tool_selector or AllToolsSelector()
        self.formatter = ToolPromptFormatter()
        self._cache = {}
        self._cache_ttl = 300  # 5 minutes
    
    def set_tool_selector(self, tool_selector: ToolSelector):
        """
        Set a new tool selection strategy.
        
        Args:
            tool_selector: New tool selection strategy
        """
        self.tool_selector = tool_selector
        # Clear cache when selector changes
        self._cache.clear()
    
    async def load_tools_as_prompt_section(
        self, 
        max_tools: Optional[int] = None,
        include_canvas_tools: bool = True,
        cache_key: Optional[str] = None
    ) -> str:
        """
        Load MCP tools and format them as a system prompt section.
        
        Args:
            max_tools: Maximum number of tools to include
            include_canvas_tools: Whether to include Canvas tools
            cache_key: Optional cache key for caching results
            
        Returns:
            Formatted tools section for system prompt
        """
        # Generate cache key if not provided
        if cache_key is None:
            cache_key = f"{max_tools}_{include_canvas_tools}_{type(self.tool_selector).__name__}"
        
        # Check cache
        current_time = time.time()
        if cache_key in self._cache:
            cached_result, timestamp = self._cache[cache_key]
            if current_time - timestamp < self._cache_ttl:
                print(f"Using cached tools section for key {cache_key}")
                return cached_result
        
        print(f"Loading tools for prompt section with key {cache_key}")
        
        # Get all available tools
        all_tools = await get_mcp_tools(
            max_tools=None,  # Get all tools first
            include_canvas_tools=include_canvas_tools
        )
        
        print(f"Retrieved {len(all_tools)} tools from MCP client")
        
        # Apply tool selection strategy
        selected_tools = self.tool_selector.select_tools(all_tools, max_tools)
        
        print(f"Selected {len(selected_tools)} tools using {type(self.tool_selector).__name__}")
        
        # Format tools as prompt section
        tools_section = self.formatter.format_tools_section(selected_tools)
        
        # Cache the result
        self._cache[cache_key] = (tools_section, current_time)
        
        return tools_section
    
    def clear_cache(self):
        """Clear the tool cache."""
        self._cache.clear()


# Pre-configured tool selectors for common use cases
def create_agent_management_selector() -> PriorityToolSelector:
    """Create a tool selector that prioritizes agent management tools."""
    priority_tools = [
        'create_agent', 'list_agents', 'get_agent', 'update_agent', 'delete_agent',
        'check_agent_health', 'view_agent_console', 'register_agent',
        'send_message', 'get_messages', 'broadcast_message',
        'create_task', 'list_tasks', 'get_task', 'update_task', 'delete_task',
        'assign_task', 'complete_task'
    ]
    return PriorityToolSelector(priority_tools)


def create_development_selector() -> PriorityToolSelector:
    """Create a tool selector that prioritizes development tools."""
    priority_tools = [
        'git_status', 'git_add', 'git_commit', 'git_push', 'git_pull',
        'create_or_update_file', 'read_file', 'search_code',
        'bash_tool', 'echo', 'fetch'
    ]
    return PriorityToolSelector(priority_tools)
