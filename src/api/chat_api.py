"""
API Endpoints for Chat Completions, compliant with OpenAI specification.
"""

import time
import uuid
import json

# Streaming implementation is now directly in this file
from fastapi import APIRouter, HTTPException, Request
from fastapi.responses import StreamingResponse
from typing import List, Optional, Dict, Any, Union

from ..agent import SWEAgent
from ..agent_prompt_based import PromptBasedSWEAgent
from langgraph.errors import GraphRecursionError
from langchain_core.agents import AgentAction
from langchain_core.messages import ToolMessage, AIMessage, HumanMessage
from ..llm.models import (
    ChatMessage,
    ChatCompletionRequest,
    ChatCompletionChoiceMessage,
    ChatCompletionChoice,
    ChatCompletionUsage,
    ChatCompletion,
    ToolCall,
    ToolCallFunction,
)
from ..llm.services import determine_model_provider
from ..mcp.client import get_mcp_tools

router = APIRouter()

# Cache for agent instances (now using Union type for both agent types)
agent_cache: Dict[str, Union[SWEAgent, PromptBasedSWEAgent]] = {}


async def get_agent(
    model: str, tool_choice: Optional[Union[str, Dict[str, Any]]] = None
) -> Union[SWEAgent, PromptBasedSWEAgent]:
    """
    Get or create an agent for the specified model.
    Now uses the new prompt-based agent implementation.
    """
    if isinstance(tool_choice, dict):
        tool_choice_str = json.dumps(tool_choice, sort_keys=True)
    else:
        tool_choice_str = str(tool_choice)
    cache_key = f"{model}_{tool_choice_str}_prompt_based"

    if cache_key not in agent_cache:
        provider = determine_model_provider(model)
        if tool_choice == "none":
            max_tools = 0
        elif provider == "openai":
            max_tools = 80  # Reduced for prompt-based approach
        else:
            max_tools = None

        # Create the new prompt-based agent
        # This loads tools into the system prompt instead of the tools array
        agent = PromptBasedSWEAgent(
            model_name=model,
            temperature=0.7,
            max_tools=max_tools,
            use_agent_management_priority=True,  # Prioritize agent management tools
        )

        # Initialize the agent
        await agent.initialize()

        # Store the agent in the cache
        agent_cache[cache_key] = agent

    return agent_cache[cache_key]


def convert_to_langchain_format(messages: List[ChatMessage]) -> List[Dict[str, Any]]:
    """
    Convert OpenAI API messages to LangChain format.
    """
    return [
        {
            "role": msg.role,
            "content": msg.content,
            **({"name": msg.name} if msg.name else {}),
            **({"tool_call_id": msg.tool_call_id} if msg.tool_call_id else {}),
        }
        for msg in messages
    ]


def format_model_id_for_response(model: str) -> str:
    """
    Format the model ID for the response.

    For OpenRouter models, we need to add the 'openrouter/' prefix if it's not already there.
    This ensures clients can properly identify the model provider.

    Args:
        model: The model ID from the request

    Returns:
        The formatted model ID for the response
    """
    # If the model already has a provider prefix, return it as is
    if "/" in model:
        return model

    # Determine the provider
    provider = determine_model_provider(model)

    # For OpenRouter models, add the prefix
    if provider == "openrouter":
        return f"openrouter/{model}"

    # For other providers, return as is
    return model


@router.post("/v1/chat/completions", response_model=ChatCompletion, tags=["Chat"])
async def create_chat_completion(request: Request):
    """
    Creates a model response for the given chat conversation.
    """
    raw_body = await request.body()
    try:
        body = json.loads(raw_body.decode("utf-8"))
    except json.JSONDecodeError as e:
        raise HTTPException(status_code=400, detail=f"Invalid JSON: {e}")

    # Print detailed request information
    print("\n==== CHAT API REQUEST DETAILS ====")
    print(f"Request Body: {json.dumps(body, indent=2)}")
    print("==== CHAT API REQUEST END ====\n")

    # Process the model ID - remove provider prefix if present
    if "model" in body and body["model"] and "/" in body["model"]:
        # Store the original model ID for the response
        original_model_id = body["model"]

        # For requests, we want to keep the provider prefix for proper routing
        print(f"Request contains prefixed model ID: {original_model_id}")

    chat_request = ChatCompletionRequest(**body)

    # Handle MCP tool-listing queries in OpenAI-compatible interface
    last_user = next(
        (m for m in reversed(chat_request.messages) if m.role == "user"), None
    )
    if last_user and "MCP tools" in last_user.content:
        tools = await get_mcp_tools()
        names = [t.name for t in tools]
        content = "I have access to: " + (", ".join(names) if names else "no tools.")
        # Format the model ID for the response
        response_model_id = format_model_id_for_response(chat_request.model)

        return ChatCompletion(
            id=f"chatcmpl-{uuid.uuid4().hex}",
            created=int(time.time()),
            model=response_model_id,  # Use the formatted model ID
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=ChatCompletionChoiceMessage(
                        role="assistant", content=content
                    ),
                    finish_reason="stop",
                )
            ],
            usage=ChatCompletionUsage(
                prompt_tokens=0, completion_tokens=0, total_tokens=0
            ),
        )

    if chat_request.stream:
        # Stream with full COT (Chain of Thought) from agent
        agent = await get_agent(chat_request.model, chat_request.tool_choice)
        messages = convert_to_langchain_format(chat_request.messages)
        agent_input = {
            "messages": messages,
            "agent_config": {
                "temperature": chat_request.temperature,
                "max_tokens": chat_request.max_tokens,
                "user": chat_request.user,
                "tool_choice": chat_request.tool_choice,
            },
        }
        completion_id = f"chatcmpl-{uuid.uuid4().hex}"
        created_ts = int(time.time())

        # Format the model ID for the response
        response_model_id = format_model_id_for_response(chat_request.model)

        return StreamingResponse(
            sse_from_agent(
                agent.stream(agent_input), completion_id, created_ts, response_model_id
            ),
            media_type="text/event-stream",
        )
    if chat_request.n and chat_request.n > 1:
        raise HTTPException(status_code=400, detail="n > 1 not supported")
    agent = await get_agent(chat_request.model, chat_request.tool_choice)
    messages = convert_to_langchain_format(chat_request.messages)
    agent_input = {
        "messages": messages,
        "agent_config": {
            "temperature": chat_request.temperature,
            "max_tokens": chat_request.max_tokens,
            "user": chat_request.user,
            "tool_choice": chat_request.tool_choice,
        },
    }
    try:
        print("\n==== AGENT INVOKE START ====")
        print(f"Agent Input: {json.dumps(agent_input, default=str)}")
        agent_response = await agent.invoke(agent_input)
        print(f"Agent Response: {json.dumps(agent_response, default=str)}")
        print("==== AGENT INVOKE END ====\n")
    except GraphRecursionError:
        print("ERROR: Agent recursion limit reached")
        raise HTTPException(status_code=500, detail="Agent recursion limit reached")
    # Determine messages from the current turn, excluding prior history
    # 'messages' is the input to agent.invoke (already in LangChain format)
    num_prior_messages = len(messages)
    current_turn_messages = agent_response.get("messages", [])[num_prior_messages:]

    print(f"Number of prior messages: {num_prior_messages}")
    print(f"Number of current turn messages: {len(current_turn_messages)}")

    # Extract the chain of thought from the current turn
    final_content_parts: List[str] = []
    final_tool_calls: Optional[List[ToolCall]] = None  # For the final response message
    final_finish_reason: str = "stop"  # Default

    # Extract only the chain of thought for the current message
    # We'll build a list of thought processes, tool calls, and observations
    # that occurred during this turn

    # First, find all the thought processes, tool calls, and observations
    thoughts = []
    tool_calls = []
    observations = []
    final_response = None

    # Iterate through messages of the current turn to extract the chain of thought
    for m_obj in current_turn_messages:
        if isinstance(m_obj, HumanMessage):
            # This should ideally not occur if current_turn_messages is sliced correctly,
            # but skip if it does.
            continue

        if isinstance(m_obj, AgentAction):
            thought = getattr(m_obj, "log", "").strip()
            if thought:
                thoughts.append(f"Thought: {thought}")

            tool_input_str = ""
            if isinstance(m_obj.tool_input, str):
                tool_input_str = m_obj.tool_input
            elif isinstance(m_obj.tool_input, dict):
                try:
                    tool_input_str = json.dumps(m_obj.tool_input)
                except TypeError:  # pragma: no cover
                    tool_input_str = str(
                        m_obj.tool_input
                    )  # Fallback for non-serializable dicts
            else:
                tool_input_str = str(m_obj.tool_input)  # Fallback for other types
            tool_call_id = f"call_{uuid.uuid4().hex[:8]}"
            tool_calls.append(
                f'<tool-call name="{m_obj.tool}" id="{tool_call_id}">\n{tool_input_str}\n</tool-call>'
            )

        elif isinstance(m_obj, ToolMessage):
            tool_call_id = getattr(m_obj, "tool_call_id", "unknown")
            observations.append(
                f"<tool-response id=\"{tool_call_id}\">\n{json.dumps({'result': str(m_obj.content)}, indent=2)}\n</tool-response>"
            )

        elif isinstance(m_obj, AIMessage):
            # Check if this is the final response (last AIMessage in the turn)
            if m_obj == current_turn_messages[-1]:
                # This is the final response
                if isinstance(m_obj.content, str) and m_obj.content:
                    final_response = m_obj.content
                elif isinstance(m_obj.content, list):
                    # Handle list content (e.g., for multimodal)
                    final_response_parts = []
                    for content_item in m_obj.content:
                        if (
                            isinstance(content_item, dict)
                            and content_item.get("type") == "text"
                        ):
                            final_response_parts.append(content_item.get("text", ""))
                        elif isinstance(content_item, str):
                            final_response_parts.append(content_item)
                    final_response = "\n".join(final_response_parts)

                # If this AIMessage itself requested tool calls, represent them textually
                # and set them as the final tool calls
                if m_obj.tool_calls:
                    parsed_tool_calls = []
                    for tc_data in m_obj.tool_calls:
                        tool_call_id = tc_data.get("id")
                        tool_call_name = tc_data.get("name")
                        if not tool_call_id or not tool_call_name:
                            continue

                        args_value = tc_data.get("args", {})
                        arguments_str = (
                            json.dumps(args_value)
                            if isinstance(args_value, dict)
                            else str(args_value)
                        )

                        parsed_tool_calls.append(
                            ToolCall(
                                id=tool_call_id,
                                type="function",
                                function=ToolCallFunction(
                                    name=tool_call_name, arguments=arguments_str
                                ),
                            )
                        )

                    if parsed_tool_calls:
                        final_tool_calls = parsed_tool_calls
                        final_finish_reason = "tool_calls"
                        final_response = None  # OpenAI spec: content is null if tool_calls are present
            else:
                # This is an intermediate AI message, add it to the thoughts
                if isinstance(m_obj.content, str) and m_obj.content:
                    thoughts.append(m_obj.content)

                # If this AIMessage requested tool calls, add them to the tool calls
                if m_obj.tool_calls:
                    tc_parts = []
                    for tc_data in m_obj.tool_calls:
                        args_value = tc_data.get("args", {})
                        args_str = (
                            json.dumps(args_value)
                            if isinstance(args_value, dict)
                            else str(args_value)
                        )
                        tc_parts.append(f"Tool Call: {tc_data.get('name')}({args_str})")
                    tool_calls.extend(tc_parts)

    # Now combine all the chain of thought elements
    # Start with thoughts, then tool calls, then observations
    final_content_parts = thoughts + tool_calls + observations

    # If we have a final response, add it at the end
    if final_response:
        final_content_parts.append(final_response)

    # Determine the final message structure for the ChatCompletionChoice
    # We've already processed the messages and extracted the chain of thought
    # Now we just need to format the final response

    # Join the final content parts with newlines
    final_content_str = "\n".join(filter(None, final_content_parts)) or ""

    # If we have tool calls, set the finish reason to "tool_calls"
    if final_tool_calls:
        final_finish_reason = "tool_calls"
        # OpenAI spec: content is null if tool_calls are present
        final_content_str = None
    else:
        final_finish_reason = "stop"
        # Ensure content is a string (e.g., "") if finish_reason is 'stop' and content ended up None
        if final_content_str is None:
            final_content_str = ""

    # Build the assistant message, preferring function_call for tool invocations
    choice_message = ChatCompletionChoiceMessage(
        role="assistant",
        content=final_content_str,
    )
    if final_tool_calls:
        # Use the first tool call as the function_call for OpenAI-compatible API
        choice_message.function_call = final_tool_calls[0].function

    choice = ChatCompletionChoice(
        index=0,
        message=choice_message,
        finish_reason=final_finish_reason,
    )
    usage = ChatCompletionUsage(prompt_tokens=0, completion_tokens=0, total_tokens=0)
    # Format the model ID for the response
    response_model_id = format_model_id_for_response(chat_request.model)

    return ChatCompletion(
        id=f"chatcmpl-{uuid.uuid4().hex}",
        created=int(time.time()),
        model=response_model_id,  # Use the formatted model ID
        choices=[choice],
        usage=usage,
    )


async def sse_from_agent(
    agent_stream,
    completion_id: str,
    created_ts: int,
    model: str,
):
    """
    Convert an agent.stream async iterator into SSE events in OpenAI format.

    Yields:
        SSE event strings with 'data: <json_payload>' in OpenAI format.
    """
    # Track the number of prior messages to filter them out
    prior_messages_count = 0
    first_chunk = True

    # Process each step from the agent
    async for step in agent_stream:
        messages = step.get("messages", [])

        # On the first chunk, determine how many messages are from prior history
        if first_chunk:
            # Count the number of HumanMessage objects at the beginning
            for msg in messages:
                if isinstance(msg, HumanMessage):
                    prior_messages_count += 1
                else:
                    break
            first_chunk = False

        # Extract only the new messages from this turn
        current_messages = messages[prior_messages_count:]

        # Process each message in the current turn
        for msg in current_messages:
            if isinstance(msg, AgentAction):
                # Extract thought process and tool call
                thought = getattr(msg, "log", "").strip()
                tool_name = msg.tool
                tool_input = msg.tool_input

                # Format tool input
                if isinstance(tool_input, dict):
                    tool_input_str = json.dumps(tool_input)
                else:
                    tool_input_str = str(tool_input)

                # Create a delta chunk for the thought using <thinking> tags
                if thought:
                    thought_chunk = {
                        "id": completion_id,
                        "object": "chat.completion.chunk",
                        "created": created_ts,
                        "model": model,
                        "choices": [
                            {
                                "index": 0,
                                "delta": {
                                    "content": f"<thinking>\n{thought}\n</thinking>\n"
                                },
                                "finish_reason": None,
                            }
                        ],
                    }
                    yield f"data: {json.dumps(thought_chunk)}\n\n"

                # Create a delta chunk for the tool call using XML-style format
                tool_call_id = f"call_{uuid.uuid4().hex[:8]}"
                tool_call_chunk = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created_ts,
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "content": f'<tool-call name="{tool_name}" id="{tool_call_id}">\n{tool_input_str}\n</tool-call>\n'
                            },
                            "finish_reason": None,
                        }
                    ],
                }
                yield f"data: {json.dumps(tool_call_chunk)}\n\n"

            elif isinstance(msg, ToolMessage):
                # Create a delta chunk for the tool observation using XML-style format
                # Extract the tool_call_id from the message if available
                tool_call_id = getattr(msg, "tool_call_id", "unknown")
                observation_chunk = {
                    "id": completion_id,
                    "object": "chat.completion.chunk",
                    "created": created_ts,
                    "model": model,
                    "choices": [
                        {
                            "index": 0,
                            "delta": {
                                "content": f"<tool-response id=\"{tool_call_id}\">\n{json.dumps({'result': str(msg.content)}, indent=2)}\n</tool-response>\n"
                            },
                            "finish_reason": None,
                        }
                    ],
                }
                yield f"data: {json.dumps(observation_chunk)}\n\n"

            elif isinstance(msg, AIMessage):
                # For AI messages, stream the content in OpenAI format
                content = msg.content or ""

                # Check if this is the final message in the current messages
                is_final = msg == current_messages[-1] if current_messages else True

                if content:
                    # For final AI messages, stream word by word like OpenAI does
                    if is_final:
                        # Split content into words for streaming
                        words = content.split()
                        for word in words:
                            # Send each word as a delta
                            word_chunk = {
                                "id": completion_id,
                                "object": "chat.completion.chunk",
                                "created": created_ts,
                                "model": model,
                                "choices": [
                                    {
                                        "index": 0,
                                        "delta": {"content": word + " "},
                                        "finish_reason": None,
                                    }
                                ],
                            }
                            yield f"data: {json.dumps(word_chunk)}\n\n"

                        # Send final chunk with finish_reason
                        final_chunk = {
                            "id": completion_id,
                            "object": "chat.completion.chunk",
                            "created": created_ts,
                            "model": model,
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {},  # Empty delta
                                    "finish_reason": "stop",
                                }
                            ],
                        }
                        yield f"data: {json.dumps(final_chunk)}\n\n"
                    else:
                        # For intermediate AI messages, send as single chunk
                        ai_chunk = {
                            "id": completion_id,
                            "object": "chat.completion.chunk",
                            "created": created_ts,
                            "model": model,
                            "choices": [
                                {
                                    "index": 0,
                                    "delta": {"content": content},
                                    "finish_reason": None,
                                }
                            ],
                        }
                        yield f"data: {json.dumps(ai_chunk)}\n\n"

    # Final [DONE] event
    yield "data: [DONE]\n\n"
