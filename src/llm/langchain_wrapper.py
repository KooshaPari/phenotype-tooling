"""
LangChain wrapper for our custom LLM routing logic.
This wrapper ensures that all LLM calls go through our provider routing system.
"""

from typing import Any, Dict, List, Optional, Union, Iterator, AsyncIterator, Sequence
from langchain_core.language_models.chat_models import BaseChatModel
from langchain_core.messages import BaseMessage, AIMessage, HumanMessage, SystemMessage
from langchain_core.outputs import ChatGeneration, ChatResult
from langchain_core.callbacks import (
    CallbackManagerForLLMRun,
    AsyncCallbackManagerForLLMRun,
)
from langchain_core.language_models.llms import LLMResult
from langchain_core.tools import BaseTool
from langchain_core.utils.function_calling import convert_to_openai_tool
from pydantic import Field

from .services import get_chat_completion, determine_model_provider


class CustomChatLLM(BaseChatModel):
    """
    Custom LangChain chat model that uses our provider routing logic.
    This ensures all model calls go through our get_chat_completion function.
    """

    model: str = Field(description="The model name to use")
    temperature: float = Field(
        default=0.7, description="The temperature to use for generation"
    )
    streaming: bool = Field(default=False, description="Whether to stream responses")
    max_tokens: Optional[int] = Field(
        default=None, description="Maximum tokens to generate"
    )

    class Config:
        """Configuration for this pydantic object."""

        extra = "forbid"

    @property
    def _llm_type(self) -> str:
        """Return type of chat model."""
        return "custom_chat_llm"

    def bind_tools(
        self,
        tools: List[Any],
        **kwargs: Any,
    ) -> "CustomChatLLM":
        """Bind tools to the model."""
        print(f"DEBUG: CustomChatLLM.bind_tools called with {len(tools)} tools")

        # Convert tools to OpenAI format
        formatted_tools = []
        for tool in tools:
            if hasattr(tool, "name") and hasattr(tool, "description"):
                # This is likely a LangChain tool
                try:
                    # Try to convert using LangChain's utility
                    openai_tool = convert_to_openai_tool(tool)
                    formatted_tools.append(openai_tool)
                except Exception as e:
                    print(
                        f"DEBUG: Error converting tool {getattr(tool, 'name', 'unknown')}: {e}"
                    )
                    # Fallback to manual conversion
                    formatted_tools.append(
                        {
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description,
                                "parameters": getattr(tool, "args_schema", {}) or {},
                            },
                        }
                    )
            else:
                # Assume it's already in the correct format
                formatted_tools.append(tool)

        # Create a new instance with tools bound
        return CustomChatLLMWithTools(
            model=self.model,
            temperature=self.temperature,
            streaming=self.streaming,
            max_tokens=self.max_tokens,
            tools=formatted_tools,
            **kwargs,
        )

    def _convert_messages_to_dict(
        self, messages: List[BaseMessage]
    ) -> List[Dict[str, Any]]:
        """Convert LangChain messages to dictionary format."""
        converted = []
        for message in messages:
            if isinstance(message, HumanMessage):
                converted.append({"role": "user", "content": message.content})
            elif isinstance(message, AIMessage):
                converted.append({"role": "assistant", "content": message.content})
            elif isinstance(message, SystemMessage):
                converted.append({"role": "system", "content": message.content})
            else:
                # For other message types, try to extract role and content
                role = getattr(message, "role", "user")
                content = getattr(message, "content", str(message))
                converted.append({"role": role, "content": content})
        return converted

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a chat response."""
        print(f"DEBUG: CustomChatLLM._generate called with model '{self.model}'")

        # Convert messages to dictionary format
        dict_messages = self._convert_messages_to_dict(messages)

        # Extract tools from kwargs if present
        tools = kwargs.get("tools", None)
        tool_choice = kwargs.get("tool_choice", None)

        try:
            # Use our custom routing logic
            response = get_chat_completion(
                model=self.model,
                messages=dict_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=False,  # Non-streaming for _generate
                tools=tools,
                tool_choice=tool_choice,
            )

            # Extract the response content
            if hasattr(response, "choices") and response.choices:
                # OpenAI-style response
                choice = response.choices[0]
                content = choice.message.content or ""

                # Handle tool calls if present
                tool_calls = getattr(choice.message, "tool_calls", None)
                if tool_calls:
                    # Convert tool calls to LangChain format
                    ai_message = AIMessage(
                        content=content,
                        tool_calls=[
                            {
                                "name": tc.function.name,
                                "args": tc.function.arguments,
                                "id": tc.id,
                            }
                            for tc in tool_calls
                        ],
                    )
                else:
                    ai_message = AIMessage(content=content)
            elif isinstance(response, dict):
                # Dictionary response format
                if "choices" in response and response["choices"]:
                    choice = response["choices"][0]
                    if isinstance(choice, dict) and "message" in choice:
                        content = choice["message"].get("content", "")
                    else:
                        content = str(choice)
                    ai_message = AIMessage(content=content)
                else:
                    # Fallback for other dictionary formats
                    content = response.get("content", str(response))
                    ai_message = AIMessage(content=content)
            else:
                # Fallback for other response types
                ai_message = AIMessage(content=str(response))

            generation = ChatGeneration(message=ai_message)
            return ChatResult(generations=[generation])

        except Exception as e:
            print(f"ERROR: CustomChatLLM._generate failed: {e}")
            # Return an error message
            error_message = AIMessage(content=f"Error generating response: {str(e)}")
            generation = ChatGeneration(message=error_message)
            return ChatResult(generations=[generation])

    async def _agenerate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Async generate a chat response."""
        print(f"DEBUG: CustomChatLLM._agenerate called with model '{self.model}'")

        # For now, just call the sync version
        # In a full implementation, you'd want to make this truly async
        return self._generate(messages, stop, run_manager, **kwargs)

    def _stream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> Iterator[ChatGeneration]:
        """Stream chat responses."""
        print(f"DEBUG: CustomChatLLM._stream called with model '{self.model}'")

        # Convert messages to dictionary format
        dict_messages = self._convert_messages_to_dict(messages)

        # Extract tools from kwargs if present
        tools = kwargs.get("tools", None)
        tool_choice = kwargs.get("tool_choice", None)

        try:
            # Use our custom routing logic with streaming
            response = get_chat_completion(
                model=self.model,
                messages=dict_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=True,  # Enable streaming
                tools=tools,
                tool_choice=tool_choice,
            )

            # Handle streaming response
            accumulated_content = ""

            if hasattr(response, "__iter__"):
                # Streaming response - process SSE format
                for chunk_line in response:
                    # Handle both string and bytes
                    if isinstance(chunk_line, bytes):
                        chunk_str = chunk_line.decode("utf-8")
                    else:
                        chunk_str = str(chunk_line)

                    # Skip empty lines
                    if not chunk_str.strip():
                        continue

                    # Parse SSE format
                    if chunk_str.startswith("data: "):
                        data_str = chunk_str[6:].strip()

                        # Skip empty lines and [DONE] marker
                        if not data_str or data_str == "[DONE]":
                            continue

                        try:
                            import json

                            chunk_data = json.loads(data_str)

                            # Extract content delta
                            if "choices" in chunk_data and chunk_data["choices"]:
                                choice = chunk_data["choices"][0]
                                delta = choice.get("delta", {})
                                content_delta = delta.get("content", "")

                                if content_delta:
                                    accumulated_content += content_delta

                                    # Yield the incremental generation with just the delta
                                    ai_message = AIMessage(content=content_delta)
                                    yield ChatGeneration(message=ai_message)

                        except json.JSONDecodeError:
                            # Skip malformed JSON
                            continue
            else:
                # Non-streaming fallback
                result = self._generate(messages, stop, run_manager, **kwargs)
                for generation in result.generations:
                    yield generation

        except Exception as e:
            print(f"ERROR: CustomChatLLM._stream failed: {e}")
            # Return an error message
            error_message = AIMessage(content=f"Error streaming response: {str(e)}")
            yield ChatGeneration(message=error_message)

    async def _astream(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[AsyncCallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> AsyncIterator[ChatGeneration]:
        """Async stream chat responses."""
        print(f"DEBUG: CustomChatLLM._astream called with model '{self.model}'")

        # For now, just call the sync version
        # In a full implementation, you'd want to make this truly async
        for chunk in self._stream(messages, stop, run_manager, **kwargs):
            yield chunk


class CustomChatLLMWithTools(CustomChatLLM):
    """
    Custom LangChain chat model with tools bound.
    This class handles tool-calling functionality.
    """

    tools: List[Dict[str, Any]] = Field(
        default_factory=list, description="The tools bound to this model"
    )

    class Config:
        """Configuration for this pydantic object."""

        extra = "forbid"

    def _generate(
        self,
        messages: List[BaseMessage],
        stop: Optional[List[str]] = None,
        run_manager: Optional[CallbackManagerForLLMRun] = None,
        **kwargs: Any,
    ) -> ChatResult:
        """Generate a chat response with tools."""
        print(
            f"DEBUG: CustomChatLLMWithTools._generate called with model '{self.model}' and {len(self.tools)} tools"
        )

        # Convert messages to dictionary format
        dict_messages = self._convert_messages_to_dict(messages)

        # Add tools to kwargs
        kwargs["tools"] = self.tools

        # Extract tool_choice from kwargs if present
        tool_choice = kwargs.get("tool_choice", None)

        try:
            # Use our custom routing logic
            response = get_chat_completion(
                model=self.model,
                messages=dict_messages,
                temperature=self.temperature,
                max_tokens=self.max_tokens,
                stream=False,  # Non-streaming for _generate
                tools=self.tools,
                tool_choice=tool_choice,
            )

            # Extract the response content
            if hasattr(response, "choices") and response.choices:
                # OpenAI-style response
                choice = response.choices[0]
                content = choice.message.content or ""

                # Handle tool calls if present
                tool_calls = getattr(choice.message, "tool_calls", None)
                if tool_calls:
                    # Convert tool calls to LangChain format
                    formatted_tool_calls = []
                    for tc in tool_calls:
                        # Parse arguments if they're a JSON string
                        args = tc.function.arguments
                        if isinstance(args, str):
                            try:
                                import json

                                args = json.loads(args)
                            except (json.JSONDecodeError, TypeError):
                                # If parsing fails, use empty dict
                                args = {}
                        elif args is None:
                            args = {}

                        formatted_tool_calls.append(
                            {
                                "name": tc.function.name,
                                "args": args,
                                "id": tc.id,
                            }
                        )

                    ai_message = AIMessage(
                        content=content, tool_calls=formatted_tool_calls
                    )
                else:
                    ai_message = AIMessage(content=content)
            elif isinstance(response, dict):
                # Dictionary response format
                if "choices" in response and response["choices"]:
                    choice = response["choices"][0]
                    if isinstance(choice, dict) and "message" in choice:
                        content = choice["message"].get("content", "")

                        # Handle tool calls in dictionary format
                        tool_calls = choice["message"].get("tool_calls", None)
                        if tool_calls:
                            formatted_tool_calls = []
                            for tc in tool_calls:
                                # Parse arguments if they're a JSON string
                                args = tc.get("function", {}).get("arguments", "{}")
                                if isinstance(args, str):
                                    try:
                                        import json

                                        args = json.loads(args)
                                    except (json.JSONDecodeError, TypeError):
                                        # If parsing fails, use empty dict
                                        args = {}
                                elif args is None:
                                    args = {}

                                formatted_tool_calls.append(
                                    {
                                        "name": tc.get("function", {}).get("name", ""),
                                        "args": args,
                                        "id": tc.get("id", ""),
                                    }
                                )

                            ai_message = AIMessage(
                                content=content, tool_calls=formatted_tool_calls
                            )
                        else:
                            ai_message = AIMessage(content=content)
                    else:
                        content = str(choice)
                        ai_message = AIMessage(content=content)
                else:
                    # Fallback for other dictionary formats
                    content = response.get("content", str(response))
                    ai_message = AIMessage(content=content)
            else:
                # Fallback for other response types
                ai_message = AIMessage(content=str(response))

            generation = ChatGeneration(message=ai_message)
            return ChatResult(generations=[generation])

        except Exception as e:
            print(f"ERROR: CustomChatLLMWithTools._generate failed: {e}")
            # Return an error message
            error_message = AIMessage(content=f"Error generating response: {str(e)}")
            generation = ChatGeneration(message=error_message)
            return ChatResult(generations=[generation])

    def bind_tools(
        self,
        tools: List[Any],
        **kwargs: Any,
    ) -> "CustomChatLLMWithTools":
        """Bind additional tools to the model."""
        print(
            f"DEBUG: CustomChatLLMWithTools.bind_tools called with {len(tools)} additional tools"
        )

        # Convert tools to OpenAI format
        formatted_tools = []
        for tool in tools:
            if hasattr(tool, "name") and hasattr(tool, "description"):
                # This is likely a LangChain tool
                try:
                    # Try to convert using LangChain's utility
                    openai_tool = convert_to_openai_tool(tool)
                    formatted_tools.append(openai_tool)
                except Exception as e:
                    print(
                        f"DEBUG: Error converting tool {getattr(tool, 'name', 'unknown')}: {e}"
                    )
                    # Fallback to manual conversion
                    formatted_tools.append(
                        {
                            "type": "function",
                            "function": {
                                "name": tool.name,
                                "description": tool.description,
                                "parameters": getattr(tool, "args_schema", {}) or {},
                            },
                        }
                    )
            else:
                # Assume it's already in the correct format
                formatted_tools.append(tool)

        # Combine existing tools with new tools
        all_tools = self.tools + formatted_tools

        # Create a new instance with all tools bound
        return CustomChatLLMWithTools(
            model=self.model,
            temperature=self.temperature,
            streaming=self.streaming,
            max_tokens=self.max_tokens,
            tools=all_tools,
            **kwargs,
        )
