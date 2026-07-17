"""
Prompt-based agent implementation using extensible tool loading.

This agent loads tools into the system prompt instead of the tools array,
providing more flexibility and enabling sophisticated tool selection logic.
"""

import json
import asyncio
import operator
from pathlib import Path
from typing import (
    Dict,
    List,
    Any,
    Optional,
    TypedDict,
    Sequence,
    Annotated,
)

from langchain_core.agents import AgentAction, AgentFinish
from langchain_core.messages import (
    BaseMessage,
    AIMessage,
    HumanMessage,
    SystemMessage,
    ToolMessage,
)
from langgraph.graph import StateGraph, END, MessagesState, START

from .tools.prompt_loader import (
    ExtensibleToolLoader,
    create_agent_management_selector,
    AllToolsSelector,
)
from .mcp.client import get_mcp_tools


def determine_model_provider(model_name: str) -> str:
    """
    Determine the model provider based on the model name.

    Args:
        model_name: The name of the model.

    Returns:
        The provider name (e.g., "openai", "anthropic", etc.).
    """
    if model_name.startswith(("gpt-", "text-", "dall-e")):
        return "openai"
    elif model_name.startswith(("claude-")):
        return "anthropic"
    elif model_name.startswith(("llama-", "meta/")):
        return "meta"
    else:
        # Default to OpenAI for unknown models
        return "openai"


# Define the agent state
class AgentState(TypedDict):
    """
    State for the agent graph.
    """

    messages: Annotated[Sequence[BaseMessage], operator.add]
    agent_id: Optional[str]
    agent_config: Optional[Dict[str, Any]]


class PromptBasedSWEAgent:
    """
    Software Engineering agent using prompt-based tool loading.

    This agent loads tools into the system prompt instead of using the tools array,
    providing more flexibility for tool selection and future enhancements.
    """

    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        system_prompt: Optional[str] = None,
        max_tools: Optional[int] = None,
        use_agent_management_priority: bool = True,
    ):
        """
        Initialize the prompt-based SWE agent.

        Args:
            model_name: The name of the model to use.
            temperature: The temperature to use for generation.
            system_prompt: Optional system prompt to use.
            max_tools: Maximum number of tools to include in prompt. None for all tools.
            use_agent_management_priority: Whether to prioritize agent management tools.
        """
        self.model_name = model_name
        self.temperature = temperature
        self.max_tools = max_tools
        self.use_agent_management_priority = use_agent_management_priority

        # Initialize tool loader with appropriate selector
        if use_agent_management_priority:
            tool_selector = create_agent_management_selector()
        else:
            tool_selector = AllToolsSelector()

        self.tool_loader = ExtensibleToolLoader(tool_selector)

        # Load base system prompt
        if system_prompt:
            self.base_system_prompt = system_prompt
        else:
            # Load the MCP-specific system prompt
            prompt_path = (
                Path(__file__).parent.parent / "config" / "system_prompt_mcp.txt"
            )

            if prompt_path.exists():
                self.base_system_prompt = prompt_path.read_text()
            else:
                # Fallback to a very basic default if the file is missing
                self.base_system_prompt = "You are an advanced AI agent with access to MCP tools. Use the tools provided to accomplish tasks and communicate with other agents."

        self.system_prompt = None  # Will be populated during initialization
        self.available_tools = {}  # Map of tool names to tool objects for execution
        self.graph = None

    async def initialize(self) -> None:
        """
        Initialize the agent by loading tools into the system prompt.
        """
        print("Initializing prompt-based SWE agent...")

        # Load tools as prompt section
        tools_section = await self.tool_loader.load_tools_as_prompt_section(
            max_tools=self.max_tools, include_canvas_tools=True
        )

        # Get actual tool objects for execution (load all tools for execution)
        all_tools = await get_mcp_tools(
            max_tools=None, include_canvas_tools=True  # Get all tools for execution
        )

        # Create tool name to tool object mapping
        self.available_tools = {tool.name: tool for tool in all_tools}
        print(f"Loaded {len(self.available_tools)} tools for execution")

        # Combine base system prompt with tools section
        self.system_prompt = f"{self.base_system_prompt}\n\n{tools_section}"

        print(f"System prompt length: {len(self.system_prompt)} characters")

        # Create the LLM using our custom routing logic
        from .llm.services import determine_model_provider as llm_determine_provider

        provider = llm_determine_provider(self.model_name)

        print(
            f"DEBUG: Agent creating LLM for model '{self.model_name}' with provider '{provider}'"
        )

        # Use our custom LLM wrapper that handles provider routing
        from .llm.langchain_wrapper import CustomChatLLM

        self.model = CustomChatLLM(
            model=self.model_name,
            temperature=self.temperature,
            streaming=True,
        )

        # Create the graph
        self.graph = self._create_graph()

    def _create_graph(self) -> StateGraph:
        """
        Create the LangGraph agent graph.

        Returns:
            The compiled StateGraph.
        """
        # Create the graph using MessagesState
        workflow = StateGraph(MessagesState)

        # Define the call_model node
        def call_model(state: MessagesState):
            """Call the model with the current state."""
            # Prepare messages with system prompt
            messages = state["messages"]

            # Add system message if not already present
            if not messages or not isinstance(messages[0], SystemMessage):
                messages = [SystemMessage(content=self.system_prompt)] + list(messages)

            # Call model without tools array (tools are in system prompt)
            response = self.model.invoke(messages)
            return {"messages": state["messages"] + [response]}

        # Add nodes
        workflow.add_node("call_model", call_model)
        workflow.add_node("tools", self._tool_execution_node)

        # Set the entry point
        workflow.add_edge(START, "call_model")

        # Add conditional edges
        def route_to_tool_or_end(state):
            """Route to tool or end based on the last message."""
            last_message = state["messages"][-1]

            # Check if the message contains tool calls in XML format
            if hasattr(last_message, "content") and last_message.content:
                content = last_message.content
                print(
                    f"DEBUG: Checking message content for tool calls: {content[:200]}..."
                )

                # Look for XML-style tool calls
                if "<" in content and ">" in content:
                    # Simple check for XML-style tool calls
                    import re

                    # Match both self-closing and regular XML tags
                    tool_pattern = r"<(\w+)(?:\s[^>]*)?\s*/?>"
                    matches = re.findall(tool_pattern, content)
                    print(f"DEBUG: Found XML matches: {matches}")

                    if matches:
                        # Check if any matches are known tools
                        for match in matches:
                            if match in self.available_tools:
                                print(
                                    f"DEBUG: Found known tool '{match}', routing to tools"
                                )
                                return "tools"
                        print(f"DEBUG: No known tools found in matches: {matches}")
                    else:
                        print("DEBUG: No XML tool patterns found")
                else:
                    print("DEBUG: No XML brackets found in content")
            else:
                print("DEBUG: No content in last message")

            print("DEBUG: Routing to END")
            return END

        workflow.add_conditional_edges(
            "call_model",
            route_to_tool_or_end,
        )

        # Add edge from tools back to call_model
        workflow.add_edge("tools", "call_model")

        # Compile the graph
        return workflow.compile()

    def _tool_execution_node(self, state: MessagesState) -> Dict[str, Any]:
        """
        Execute tools based on XML-style tool calls in the last message.

        Args:
            state: The current state

        Returns:
            Updated state with tool results
        """
        print("\n==== TOOL EXECUTION NODE START ====")

        last_message = state["messages"][-1]
        if not hasattr(last_message, "content") or not last_message.content:
            return {
                "messages": state["messages"]
                + [AIMessage(content="No tool calls found in the message.")]
            }

        content = last_message.content

        # Parse XML-style tool calls
        tool_calls = self._parse_xml_tool_calls(content)

        if not tool_calls:
            return {
                "messages": state["messages"]
                + [AIMessage(content="No valid tool calls found.")]
            }

        # Execute tool calls
        results = []
        for tool_call in tool_calls:
            result = asyncio.run(self._execute_tool_call(tool_call))
            results.append(result)

        # Format results
        results_text = "\n\n".join(results)

        print(f"Tool execution results: {results_text[:500]}...")
        print("==== TOOL EXECUTION NODE END ====\n")

        return {
            "messages": state["messages"]
            + [AIMessage(content=f"Tool execution results:\n\n{results_text}")]
        }

    def _parse_xml_tool_calls(self, content: str) -> List[Dict[str, Any]]:
        """
        Parse XML-style tool calls from message content.

        Args:
            content: Message content to parse

        Returns:
            List of parsed tool calls
        """
        import re
        import xml.etree.ElementTree as ET

        tool_calls = []

        print(f"DEBUG: Parsing XML tool calls from content: {content[:200]}...")

        # Find all XML-style tool calls (both self-closing and regular)
        # Pattern for self-closing tags: <tool_name /> or <tool_name/>
        self_closing_pattern = r"<(\w+)\s*/>"
        self_closing_matches = re.findall(self_closing_pattern, content)

        # Pattern for regular tags: <tool_name>content</tool_name>
        regular_pattern = r"<(\w+)>(.*?)</\1>"
        regular_matches = re.findall(regular_pattern, content, re.DOTALL)

        print(f"DEBUG: Found self-closing matches: {self_closing_matches}")
        print(f"DEBUG: Found regular matches: {regular_matches}")

        # Process self-closing tags
        for tool_name in self_closing_matches:
            if tool_name in self.available_tools:
                print(f"DEBUG: Processing self-closing tool: {tool_name}")
                tool_calls.append({"name": tool_name, "parameters": {}})

        # Process regular tags
        for tool_name, tool_content in regular_matches:
            if tool_name in self.available_tools:
                print(
                    f"DEBUG: Processing regular tool: {tool_name} with content: {tool_content[:100]}..."
                )
                # Parse parameters from XML content
                parameters = {}
                try:
                    if tool_content.strip():
                        # Wrap in a root element for parsing
                        xml_content = f"<root>{tool_content}</root>"
                        root = ET.fromstring(xml_content)

                        for child in root:
                            parameters[child.tag] = child.text or ""

                except ET.ParseError as e:
                    print(f"DEBUG: Failed to parse XML for tool {tool_name}: {e}")
                    continue

                tool_calls.append({"name": tool_name, "parameters": parameters})

        print(
            f"DEBUG: Parsed {len(tool_calls)} tool calls: {[tc['name'] for tc in tool_calls]}"
        )
        return tool_calls

    async def _execute_tool_call(self, tool_call: Dict[str, Any]) -> str:
        """
        Execute a single tool call.

        Args:
            tool_call: Tool call information

        Returns:
            Tool execution result
        """
        tool_name = tool_call["name"]
        parameters = tool_call["parameters"]

        print(f"Executing tool: {tool_name} with parameters: {parameters}")

        if tool_name not in self.available_tools:
            return f"Error: Tool '{tool_name}' not found."

        tool = self.available_tools[tool_name]

        # Debug: Print tool information
        print(f"DEBUG: Tool type: {type(tool)}")
        print(f"DEBUG: Tool attributes: {dir(tool)}")
        print(f"DEBUG: Tool name: {getattr(tool, 'name', 'N/A')}")
        print(f"DEBUG: Tool description: {getattr(tool, 'description', 'N/A')}")

        # Check if this is an MCP tool with a specific calling pattern
        if hasattr(tool, "func"):
            print(f"DEBUG: Tool func value: {tool.func}")
            print(f"DEBUG: Tool func type: {type(tool.func)}")
            if hasattr(tool.func, "__name__"):
                print(f"DEBUG: Tool func name: {tool.func.__name__}")
                if "call_tool" in tool.func.__name__:
                    print("DEBUG: This appears to be an MCP tool wrapper")

            # Check the function signature
            import inspect

            try:
                if tool.func is not None:
                    sig = inspect.signature(tool.func)
                    print(f"DEBUG: Tool func signature: {sig}")
                    print(f"DEBUG: Tool func parameters: {list(sig.parameters.keys())}")
                else:
                    print("DEBUG: Tool func is None")
            except Exception as e:
                print(f"DEBUG: Could not get signature: {e}")
        else:
            print("DEBUG: Tool has no func attribute")

        try:
            # Execute the tool using the same logic as the original agent
            # For MCP tools, we need to handle the parameters correctly

            # Special handling for MCP tools that have func=None or call_tool wrapper function
            is_mcp_tool = False
            if hasattr(tool, "func") and tool.func is None:
                is_mcp_tool = True
                print(f"DEBUG: Tool {tool_name} has func=None, treating as MCP tool")
            elif (
                hasattr(tool, "func")
                and hasattr(tool.func, "__name__")
                and "call_tool" in tool.func.__name__
            ):
                is_mcp_tool = True
                print(
                    f"DEBUG: Tool {tool_name} has call_tool wrapper, treating as MCP tool"
                )

            if is_mcp_tool:
                print(
                    f"DEBUG: Tool {tool_name} is MCP tool, trying alternative methods"
                )
                # This is likely an MCP tool, try _arun first
                if hasattr(tool, "_arun"):
                    try:
                        # Try calling _arun with config parameter (required for StructuredTool)
                        from langchain_core.runnables import RunnableConfig

                        config = RunnableConfig()

                        # Try with parameters and config
                        if parameters:
                            result = await tool._arun(config=config, **parameters)
                            print(
                                f"DEBUG: Successfully called {tool_name}._arun(config=config, **parameters)"
                            )
                        else:
                            result = await tool._arun(config=config)
                            print(
                                f"DEBUG: Successfully called {tool_name}._arun(config=config)"
                            )
                    except Exception as e:
                        print(
                            f"DEBUG: Failed to call {tool_name}._arun() with config: {e}"
                        )
                        return (
                            f"Error: Could not invoke MCP tool '{tool_name}': {str(e)}"
                        )
                elif hasattr(tool, "ainvoke"):
                    try:
                        result = await tool.ainvoke(parameters)
                    except TypeError:
                        result = await tool.ainvoke({})
                else:
                    return f"Error: MCP tool '{tool_name}' has no compatible async invocation method."
            elif hasattr(tool, "coroutine"):
                result = await tool.coroutine(parameters)
            elif hasattr(tool, "ainvoke"):
                result = await tool.ainvoke(parameters)
            elif hasattr(tool, "_arun"):
                # For regular tools, try both with and without parameters
                try:
                    if parameters:
                        result = await tool._arun(**parameters)
                    else:
                        result = await tool._arun()
                except TypeError:
                    # If that fails, try the other way
                    if parameters:
                        result = await tool._arun()
                    else:
                        result = await tool._arun(**parameters)
            elif hasattr(tool, "invoke"):
                try:
                    if parameters:
                        result = await asyncio.to_thread(tool.invoke, **parameters)
                    else:
                        result = await asyncio.to_thread(tool.invoke)
                except TypeError:
                    # If that fails, try the other way
                    if parameters:
                        result = await asyncio.to_thread(tool.invoke)
                    else:
                        result = await asyncio.to_thread(tool.invoke, **parameters)
            elif hasattr(tool, "_run"):
                try:
                    if parameters:
                        result = await asyncio.to_thread(tool._run, **parameters)
                    else:
                        result = await asyncio.to_thread(tool._run)
                except TypeError:
                    # If that fails, try the other way
                    if parameters:
                        result = await asyncio.to_thread(tool._run)
                    else:
                        result = await asyncio.to_thread(tool._run, **parameters)
            elif hasattr(tool, "run"):
                try:
                    if parameters:
                        result = await asyncio.to_thread(tool.run, **parameters)
                    else:
                        result = await asyncio.to_thread(tool.run)
                except TypeError:
                    # If that fails, try the other way
                    if parameters:
                        result = await asyncio.to_thread(tool.run)
                    else:
                        result = await asyncio.to_thread(tool.run, **parameters)
            elif hasattr(tool, "func") and tool.func is not None:
                try:
                    if parameters:
                        result = await asyncio.to_thread(tool.func, **parameters)
                    else:
                        result = await asyncio.to_thread(tool.func)
                except TypeError:
                    # If that fails, try the other way
                    if parameters:
                        result = await asyncio.to_thread(tool.func)
                    else:
                        result = await asyncio.to_thread(tool.func, **parameters)
            else:
                return f"Error: Tool '{tool_name}' has no compatible invocation method."

            return f"Tool '{tool_name}' result: {str(result)}"

        except Exception as e:
            print(f"Error executing tool {tool_name}: {e}")
            return f"Error executing tool '{tool_name}': {str(e)}"

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke the agent with input data.

        Args:
            input_data: Input data containing messages and config

        Returns:
            Agent response
        """
        if self.graph is None:
            await self.initialize()

        return await self.graph.ainvoke(input_data)
