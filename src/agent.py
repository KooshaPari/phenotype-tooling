"""
Core agent implementation using LangChain and LangGraph.
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
from langchain_core.tools import BaseTool
from langgraph.graph import StateGraph, END, MessagesState, START
from langgraph.prebuilt import ToolNode

from src.mcp.client import get_mcp_tools


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


class SWEAgent:
    """
    Software Engineering agent using LangGraph.
    """

    def __init__(
        self,
        model_name: str = "gpt-4",
        temperature: float = 0.7,
        tools: Optional[List[BaseTool]] = None,
        system_prompt: Optional[str] = None,
        max_tools: Optional[int] = 128,  # OpenAI API limit is 128 tools
    ):
        """
        Initialize the SWE agent.

        Args:
            model_name: The name of the model to use.
            temperature: The temperature to use for generation.
            tools: Optional list of tools to use. If None, MCP tools will be loaded.
            system_prompt: Optional system prompt to use.
            max_tools: Maximum number of tools to use. Default is 128 (OpenAI API limit).
                      Set to None to use all available tools.
        """
        self.model_name = model_name
        self.temperature = temperature
        self.tools = tools
        self.max_tools = max_tools
        if system_prompt:
            self.system_prompt = system_prompt
        else:
            # Load the main system prompt
            prompt_path = (
                Path(__file__).parent.parent.parent / "config" / "system_prompt.txt"
            )

            if prompt_path.exists():
                self.system_prompt = prompt_path.read_text()

            else:
                # Fallback to a very basic default if the file is missing
                self.system_prompt = "You are a helpful assistant."
        self.graph = None

    async def initialize(self) -> None:
        """
        Initialize the agent by loading tools and creating the graph.
        """
        if self.tools is None:
            # Use the singleton MCP client manager to get tools
            # This avoids creating a new client for each agent
            print("Getting tools from global MCP client manager...")

            # Determine the model provider
            provider = determine_model_provider(self.model_name)

            # Calculate the actual max_tools to request
            if provider == "openai":
                # Limit to 80 tools to stay under the context limit for OpenAI models
                actual_max_tools = min(
                    80, self.max_tools if self.max_tools is not None else 80
                )
            else:
                # For other providers, use the specified max_tools
                actual_max_tools = self.max_tools

            # Get tools with proper filtering applied in get_mcp_tools
            all_tools = await get_mcp_tools(
                max_tools=actual_max_tools,  # Pass the actual limit to get_mcp_tools for proper prioritization
                include_canvas_tools=True,  # Include all tools, we'll handle Canvas tools specially
            )
            print(f"Retrieved {len(all_tools)} tools from global MCP client manager")

            # If max_tools is 0, no tools will be loaded
            if actual_max_tools == 0:
                self.tools = []
                print(f"Tools disabled for {self.model_name} agent")
            else:
                self.tools = all_tools
                print(f"Limited to {len(self.tools)} tools for {self.model_name} agent")

            # If no tools were loaded, use an empty list
            if not self.tools:
                print("No tools loaded, using empty tools list")
                self.tools = []

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

        # Create the graph directly
        self.graph = self._create_graph(None)

    def _create_graph(self, _) -> StateGraph:
        """
        Create the LangGraph agent graph.

        Args:
            _: Unused parameter (kept for backward compatibility).

        Returns:
            The compiled StateGraph.
        """
        # Create the graph using MessagesState
        workflow = StateGraph(MessagesState)

        # Define the call_model node
        def call_model(state: MessagesState):
            """Call the model with the current state."""
            # Use bind_tools to attach tools to the model
            # This ensures tools are properly formatted for the model
            # and avoids the 'functions' and 'tools' conflict
            response = self.model.bind_tools(self.tools).invoke(state["messages"])
            return {"messages": state["messages"] + [response]}

        # Add nodes
        workflow.add_node("call_model", call_model)
        workflow.add_node("tools", ToolNode(self.tools))

        # Set the entry point
        workflow.add_edge(START, "call_model")

        # Add conditional edges
        def route_to_tool_or_end(state):
            """Route to tool or end based on the last message."""
            last_message = state["messages"][-1]
            if hasattr(last_message, "tool_calls") and last_message.tool_calls:
                return "tools"
            return END

        workflow.add_conditional_edges(
            "call_model",
            route_to_tool_or_end,
        )

        # Add edge from tools back to call_model
        workflow.add_edge("tools", "call_model")

        # Compile the graph
        return workflow.compile()

    def _agent_node(self, agent):
        """
        Create the agent node function.

        Args:
            agent: The agent to use.

        Returns:
            A function that processes the agent state.
        """

        def agent_node(state: AgentState) -> Dict[str, Any]:
            """
            Process the agent state and invoke the agent.

            Args:
                state: The current agent state.

            Returns:
                The updated state.
            """
            # Get the agent configuration from the state
            # The agent configuration is passed to the state when invoking the agent
            # and can contain parameters like tool_choice, temperature, etc.
            # We don't need to explicitly use it here as the LLM is already configured
            # with the appropriate tool_choice setting

            # Invoke the agent
            result = agent.invoke(state)

            # Handle different result types
            if isinstance(result, AgentFinish):
                # Normal completion without tool calls
                return {
                    "messages": state["messages"]
                    + [
                        AIMessage(
                            content=str(result.return_values.get("output", result.log))
                        )
                    ]
                }
            elif isinstance(result, AgentAction):
                # Tool call action
                return {"messages": state["messages"] + [result]}
            elif isinstance(result, dict) and "messages" in result:
                # Result already contains messages
                return {"messages": state["messages"] + result["messages"]}
            else:
                # Fallback for unexpected result types
                return {
                    "messages": state["messages"] + [AIMessage(content=str(result))]
                }

        return agent_node

    async def _tool_node(self, state: AgentState) -> Dict[str, Any]:
        """
        Process tool invocations.

        Args:
            state: The current agent state.

        Returns:
            The updated state with tool results.
        """
        print("\n==== TOOL NODE EXECUTION START ====")
        print(f"Messages in state: {len(state['messages'])}")

        # Get the most recent AgentAction message
        agent_action = None
        for message in reversed(state["messages"]):
            if isinstance(message, AgentAction):
                agent_action = message
                print(
                    f"Found AgentAction: {agent_action.tool} with input: {agent_action.tool_input}"
                )
                break

        if not agent_action:
            # No AgentAction found, return an error
            print("ERROR: No tool action found in messages")
            return {
                "messages": state["messages"]
                + [
                    ToolMessage(
                        content="No tool action found in messages.",
                        tool_call_id="error",
                    )
                ]
            }

        # Find the tool
        tool_name = agent_action.tool

        # Special handling for Canvas tools
        if tool_name.startswith("canvas_"):
            print(f"CANVAS TOOL: Special handling for {tool_name}")
            # Return a friendly message for Canvas tools
            friendly_message = f"I'm sorry, but I couldn't access the Canvas tool '{tool_name}' at this time. Please try again later or contact support if the issue persists."
            return {
                "messages": state["messages"]
                + [
                    ToolMessage(
                        content=friendly_message,
                        tool_call_id=getattr(agent_action, "id", None)
                        or agent_action.tool,
                    )
                ]
            }

        # Find the tool for non-Canvas tools
        tool = None
        for t in self.tools:
            if t.name == tool_name:
                tool = t
                break

        if not tool:
            # Tool not found, return an error
            return {
                "messages": state["messages"]
                + [
                    ToolMessage(
                        content=f"Tool '{tool_name}' not found. Available tools: {', '.join(t.name for t in self.tools)}",
                        tool_call_id=getattr(agent_action, "id", None)
                        or agent_action.tool,
                    )
                ]
            }

        try:
            # Prepare the tool input
            tool_input = agent_action.tool_input
            if isinstance(tool_input, str):
                try:
                    tool_input = json.loads(tool_input)
                except json.JSONDecodeError:
                    # If it's not JSON, pass as is
                    pass

            # Invoke the tool
            # Check if it's a Canvas tool (special handling)
            is_canvas_tool = tool_name.startswith("canvas_")

            print(f"TOOL INVOCATION: Invoking tool: {tool_name}")

            # Special handling for Canvas tools and other problematic tools
            if is_canvas_tool or tool_name in [
                "get_web_content",
                "playwright_navigate",
                "ai_web_search",
            ]:
                print(f"PROBLEMATIC TOOL: Special handling for {tool_name}")
                print(f"PROBLEMATIC TOOL: Tool type: {type(tool)}")
                print(f"PROBLEMATIC TOOL: Tool dir: {dir(tool)}")

                # Create a friendly message for problematic tools
                if is_canvas_tool:
                    observation = f"I'm sorry, but I couldn't access the Canvas tool '{tool_name}' at this time. Please try again later or contact support if the issue persists."
                elif tool_name == "get_web_content":
                    observation = f"I'm sorry, but I cannot directly access external websites. If you need information from a specific website, please visit it directly."
                elif tool_name == "playwright_navigate":
                    observation = f"I'm sorry, but I cannot directly navigate to external websites. If you need to visit a website, please open it in your browser."
                else:
                    observation = f"I'm sorry, but I couldn't access the {tool_name} tool at this time. Please try again later or contact support if the issue persists."

                print(f"PROBLEMATIC TOOL: Returning friendly message for {tool_name}")

                # Try to fix the tool for future use
                try:
                    # Create a completely new Tool instance
                    from langchain_core.tools import Tool

                    # Create a proper async function
                    async def emergency_async_wrapper(input_data=None):
                        """Async implementation that returns a friendly message."""
                        print(f"CANVAS TOOL: Emergency async wrapper for {tool_name}")
                        return f"I'm sorry, but I couldn't access the Canvas tool '{tool_name}' at this time. Please try again later or contact support if the issue persists."

                    # Create a sync function that returns a friendly message
                    def emergency_sync_run(input_data=None):
                        """Sync implementation that returns a friendly message."""
                        print(f"CANVAS TOOL: Emergency sync function for {tool_name}")
                        return f"I'm sorry, but I couldn't access the Canvas tool '{tool_name}' at this time. Please try again later or contact support if the issue persists."

                    # Create a new Tool with proper async support
                    from typing import Optional
                    from pydantic import BaseModel

                    class EmptySchema(BaseModel):
                        """Empty schema for Canvas tools."""

                        input: Optional[str] = None

                    new_tool = Tool(
                        name=tool.name,
                        description=tool.description,
                        func=emergency_sync_run,
                        coroutine=emergency_async_wrapper,
                        args_schema=EmptySchema,
                        return_direct=False,
                    )

                    # Replace the tool in the tools list for future invocations
                    for i, t in enumerate(self.tools):
                        if t.name == tool.name:
                            self.tools[i] = new_tool
                            print(
                                f"CANVAS TOOL: Replaced {tool_name} with emergency version"
                            )
                            break

                except Exception as e:
                    print(
                        f"CANVAS TOOL ERROR: Failed to create emergency tool: {str(e)}"
                    )
                    import traceback

                    print(f"CANVAS TOOL TRACEBACK: {traceback.format_exc()}")
            else:
                # For non-Canvas tools, use the standard approach
                # The preferred order is: coroutine > ainvoke > _arun > invoke > _run > run > func
                if hasattr(tool, "coroutine"):
                    # This is the proper way to invoke a Tool with async support
                    print(f"Using coroutine for {tool_name}")
                    observation = await tool.coroutine(tool_input)
                elif hasattr(tool, "ainvoke"):
                    # This is for tools that have been patched with ainvoke
                    print(f"Using ainvoke for {tool_name}")
                    observation = await tool.ainvoke(tool_input)
                elif hasattr(tool, "_arun"):
                    # This is for BaseTool subclasses that implement _arun
                    print(f"Using _arun for {tool_name}")
                    observation = await tool._arun(tool_input)
                elif hasattr(tool, "invoke"):
                    # For tools that only support sync invocation
                    print(f"Using invoke for {tool_name}")
                    observation = await asyncio.to_thread(tool.invoke, tool_input)
                elif hasattr(tool, "_run"):
                    # For tools that have a _run method
                    print(f"Using _run for {tool_name}")
                    if isinstance(tool_input, dict):
                        observation = await asyncio.to_thread(tool._run, **tool_input)
                    else:
                        observation = await asyncio.to_thread(tool._run, tool_input)
                elif hasattr(tool, "run"):
                    # For tools that have a run method
                    print(f"Using run for {tool_name}")
                    if isinstance(tool_input, dict):
                        observation = await asyncio.to_thread(tool.run, **tool_input)
                    else:
                        observation = await asyncio.to_thread(tool.run, tool_input)
                elif hasattr(tool, "func"):
                    # For tools that have a func method
                    print(f"Using func for {tool_name}")
                    if isinstance(tool_input, dict):
                        observation = await asyncio.to_thread(tool.func, **tool_input)
                    else:
                        observation = await asyncio.to_thread(tool.func, tool_input)
                else:
                    # No compatible method found
                    raise AttributeError(
                        f"Tool {tool_name} has no compatible invocation method"
                    )

            # Return the result
            tool_call_id = getattr(agent_action, "id", None) or agent_action.tool

            # Log detailed information about the tool call and response
            print("\n==== TOOL CALL SUCCESS DETAILS ====")
            print(f"Tool Name: {tool_name}")
            print(f"Tool Call ID: {tool_call_id}")
            print(f"Tool Input: {json.dumps(tool_input, default=str)}")
            print(
                f"Tool Response: {str(observation)[:500]}{'...' if len(str(observation)) > 500 else ''}"
            )
            print("==== TOOL CALL SUCCESS END ====\n")

            result = {
                "messages": state["messages"]
                + [ToolMessage(content=str(observation), tool_call_id=tool_call_id)]
            }

            print(f"Returning result with {len(result['messages'])} messages")
            return result
        except Exception as e:
            # Handle tool execution errors
            tool_call_id = getattr(agent_action, "id", None) or agent_action.tool

            # Log the error for debugging
            print(f"ERROR: Exception when executing tool {tool_name}: {str(e)}")
            print(f"ERROR: Exception type: {type(e).__name__}")
            import traceback

            print(f"ERROR: Traceback: {traceback.format_exc()}")

            # Provide more detailed error messages for common issues
            error_message = str(e)
            is_canvas_tool = tool_name.startswith("canvas_")

            # Handle specific error types
            if "StructuredTool does not support sync invocation" in error_message or (
                is_canvas_tool and "NotImplementedError" in error_message
            ):
                # For Canvas tools or problematic tools, just return a friendly message
                if is_canvas_tool or tool_name in [
                    "get_web_content",
                    "playwright_navigate",
                    "ai_web_search",
                ]:
                    print(f"PROBLEMATIC TOOL ERROR: {error_message}")
                    friendly_message = f"I'm sorry, but I couldn't access the {tool_name} tool at this time. Please try again later or contact support if the issue persists."

                    return {
                        "messages": state["messages"]
                        + [
                            ToolMessage(
                                content=friendly_message,
                                tool_call_id=tool_call_id,
                            )
                        ]
                    }

                # For other tools, try to fix them on the fly
                print(f"RECOVERY: Attempting to fix tool {tool_name}")

                # Try to fix the tool on the fly
                try:
                    # Create a completely new Tool instance
                    from langchain_core.tools import Tool

                    # Create a proper async function
                    async def emergency_async_wrapper(input_data):
                        """Async implementation that runs the tool in a thread."""
                        print(f"RECOVERY: Async wrapper for {tool_name}")

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
                                f"Tool {tool_name} has no compatible method"
                            )

                        print(f"RECOVERY: Using {method_name} method for {tool_name}")

                        # Handle different input types
                        if isinstance(input_data, dict) and method_name != "invoke":
                            return await asyncio.to_thread(method, **input_data)
                        else:
                            return await asyncio.to_thread(method, input_data)

                    # Create a sync function that raises an error
                    def emergency_sync_run(input_data):
                        """Sync implementation that raises an error."""
                        raise NotImplementedError(
                            "This tool only supports async invocation. Please use the async version."
                        )

                    # Create a new Tool with proper async support
                    new_tool = Tool(
                        name=tool.name,
                        description=tool.description,
                        func=emergency_sync_run,  # Sync function that raises an error
                        coroutine=emergency_async_wrapper,  # Async function that works
                        args_schema=getattr(tool, "args_schema", None),
                        return_direct=getattr(tool, "return_direct", False),
                    )

                    # Replace the tool in the tools list for future invocations
                    for i, t in enumerate(self.tools):
                        if t.name == tool.name:
                            self.tools[i] = new_tool
                            break

                    # Use the new tool
                    print(f"RECOVERY: Created new Tool for {tool_name}")
                    observation = await new_tool.coroutine(tool_input)

                    # If we get here, the recovery was successful
                    print(f"RECOVERY: Successfully recovered {tool_name}")
                    return {
                        "messages": state["messages"]
                        + [
                            ToolMessage(
                                content=str(observation), tool_call_id=tool_call_id
                            )
                        ]
                    }
                except Exception as recovery_e:
                    # Recovery failed
                    print(
                        f"RECOVERY FAILED: Could not recover {tool_name}: {str(recovery_e)}"
                    )
                    error_message = (
                        f"Error executing tool {tool_name}: This tool requires asynchronous invocation. "
                        "Recovery attempt failed. Please try again with a different tool."
                    )
            elif is_canvas_tool:
                # Special handling for Canvas tool errors
                error_message = (
                    f"Error executing Canvas tool {tool_name}: {error_message}. "
                    "There might be an issue with the Canvas API connection. "
                    "Please try again later or check your Canvas credentials."
                )
            else:
                error_message = f"Error executing tool {tool_name}: {error_message}"

            # Log detailed information about the failed tool call
            print("\n==== TOOL CALL ERROR DETAILS ====")
            print(f"Tool Name: {tool_name}")
            print(f"Tool Call ID: {tool_call_id}")
            print(f"Tool Input: {json.dumps(tool_input, default=str)}")
            print(f"Error Message: {error_message}")
            print("==== TOOL CALL ERROR END ====\n")

            result = {
                "messages": state["messages"]
                + [
                    ToolMessage(
                        content=error_message,
                        tool_call_id=tool_call_id,
                    )
                ]
            }

            print(f"Returning error result with {len(result['messages'])} messages")
            return result

    def _should_continue(self, state: AgentState) -> str:
        """
        Determine whether to continue to tools or end the conversation.

        Args:
            state: The current agent state.

        Returns:
            The next node to route to.
        """
        last_message = state["messages"][-1]
        if isinstance(last_message, AgentAction):
            return "continue_to_tools"
        else:
            return "end_conversation"

    async def invoke(self, input_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Invoke the agent with the given input.

        Args:
            input_data: The input data, which should contain a "messages" key.

        Returns:
            The agent's response.
        """
        if self.graph is None:
            await self.initialize()

        # Ensure the input has the expected format
        if "messages" not in input_data:
            raise ValueError("Input must contain a 'messages' key")

        # Convert messages to the expected format if needed
        messages = input_data["messages"]
        if isinstance(messages, str):
            # If messages is a string, convert it to a HumanMessage
            messages = [HumanMessage(content=messages)]
        elif isinstance(messages, list) and all(isinstance(m, dict) for m in messages):
            # If messages is a list of dicts, convert to BaseMessage objects
            converted_messages = []
            for m in messages:
                if m.get("role") == "user":
                    converted_messages.append(
                        HumanMessage(content=m.get("content", ""))
                    )
                elif m.get("role") == "assistant":
                    converted_messages.append(AIMessage(content=m.get("content", "")))
                elif m.get("role") == "system":
                    converted_messages.append(
                        SystemMessage(content=m.get("content", ""))
                    )
                elif m.get("role") == "tool":
                    converted_messages.append(
                        ToolMessage(
                            content=m.get("content", ""),
                            tool_call_id=m.get("tool_call_id", "unknown"),
                        )
                    )
            messages = converted_messages

        # Prepare the input state
        input_state = AgentState(
            messages=messages,
            agent_id=input_data.get("agent_id"),
            agent_config=input_data.get("agent_config", {}),
        )

        # Invoke the graph with increased recursion limit
        return await self.graph.ainvoke(input_state, {"recursion_limit": 100})

    async def stream(self, input_data: Dict[str, Any]):
        """
        Stream the agent's response.

        Args:
            input_data: The input data, which should contain a "messages" key.

        Yields:
            The agent's response chunks.
        """
        if self.graph is None:
            await self.initialize()

        # Ensure the input has the expected format
        if "messages" not in input_data:
            raise ValueError("Input must contain a 'messages' key")

        # Convert messages to the expected format if needed
        messages = input_data["messages"]
        if isinstance(messages, str):
            # If messages is a string, convert it to a HumanMessage
            messages = [HumanMessage(content=messages)]
        elif isinstance(messages, list) and all(isinstance(m, dict) for m in messages):
            # If messages is a list of dicts, convert to BaseMessage objects
            converted_messages = []
            for m in messages:
                if m.get("role") == "user":
                    converted_messages.append(
                        HumanMessage(content=m.get("content", ""))
                    )
                elif m.get("role") == "assistant":
                    converted_messages.append(AIMessage(content=m.get("content", "")))
                elif m.get("role") == "system":
                    converted_messages.append(
                        SystemMessage(content=m.get("content", ""))
                    )
                elif m.get("role") == "tool":
                    converted_messages.append(
                        ToolMessage(
                            content=m.get("content", ""),
                            tool_call_id=m.get("tool_call_id", "unknown"),
                        )
                    )
            messages = converted_messages

        # Prepare the input state
        input_state = AgentState(
            messages=messages,
            agent_id=input_data.get("agent_id"),
            agent_config=input_data.get("agent_config", {}),
        )

        # Stream the graph execution with increased recursion limit
        async for chunk in self.graph.astream(input_state, {"recursion_limit": 100}):
            yield chunk
