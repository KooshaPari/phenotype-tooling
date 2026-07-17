"""
OpenAI API compatibility layer for AI Orchestration.

This module provides compatibility with the OpenAI API format, allowing the AI Orchestration
system to be used as a drop-in replacement for OpenAI's API.
"""

import json
import time
import uuid
import asyncio
from typing import Dict, List, Any, Optional, Union, Literal, AsyncGenerator
from pydantic import BaseModel, Field, root_validator
from fastapi import Response
from sse_starlette.sse import EventSourceResponse


class ChatCompletionRequestMessage(BaseModel):
    """
    A message in a chat completion request.
    """

    role: str
    content: str
    name: Optional[str] = None


class ChatCompletionResponseMessage(BaseModel):
    """
    A message in a chat completion response.
    """

    role: str = "assistant"
    content: str
    name: Optional[str] = None


class ChatCompletionResponseChoice(BaseModel):
    """
    A choice in a chat completion response.
    """

    index: int
    message: ChatCompletionResponseMessage
    finish_reason: str = "stop"


class ChatCompletionResponseUsage(BaseModel):
    """
    Usage information for a chat completion response.
    """

    prompt_tokens: int
    completion_tokens: int
    total_tokens: int


class ChatCompletionResponse(BaseModel):
    """
    A response from the chat completions API.
    """

    id: str
    object: str = "chat.completion"
    created: int
    model: str
    choices: List[ChatCompletionResponseChoice]
    usage: ChatCompletionResponseUsage


class ChatCompletionRequest(BaseModel):
    """
    A request to the chat completions API.
    """

    model: str
    messages: List[ChatCompletionRequestMessage]
    temperature: Optional[float] = 0.7
    top_p: Optional[float] = 1.0
    n: Optional[int] = 1
    stream: Optional[bool] = False
    stop: Optional[Union[str, List[str]]] = None
    max_tokens: Optional[int] = None
    presence_penalty: Optional[float] = 0.0
    frequency_penalty: Optional[float] = 0.0
    logit_bias: Optional[Dict[str, float]] = None
    user: Optional[str] = None


def convert_to_orchestration_request(
    openai_request: ChatCompletionRequest,
) -> Dict[str, Any]:
    """
    Convert an OpenAI API request to an AI Orchestration request.

    Args:
        openai_request: The OpenAI API request.

    Returns:
        The AI Orchestration request.
    """
    # Extract the prompt from the messages
    prompt = ""
    for message in openai_request.messages:
        if message.role == "user":
            prompt = message.content
            break

    # If no user message was found, use the last message
    if not prompt and openai_request.messages:
        prompt = openai_request.messages[-1].content

    # Create the orchestration request
    orchestration_request = {
        "prompt": prompt,
        "model": openai_request.model,
        "max_tokens": openai_request.max_tokens or 1000,
        "temperature": openai_request.temperature or 0.7,
    }

    return orchestration_request


def convert_to_openai_response(
    orchestration_response: Dict[str, Any], request: ChatCompletionRequest
) -> ChatCompletionResponse:
    """
    Convert an AI Orchestration response to an OpenAI API response.

    Args:
        orchestration_response: The AI Orchestration response.
        request: The original OpenAI API request.

    Returns:
        The OpenAI API response.
    """
    # Extract the text from the orchestration response
    text = orchestration_response.get("text", "")

    # Create the OpenAI API response
    response = ChatCompletionResponse(
        id=f"chatcmpl-{uuid.uuid4().hex}",
        created=int(time.time()),
        model=orchestration_response.get("model", request.model),
        choices=[
            ChatCompletionResponseChoice(
                index=0,
                message=ChatCompletionResponseMessage(role="assistant", content=text),
                finish_reason="stop",
            )
        ],
        usage=ChatCompletionResponseUsage(
            prompt_tokens=len(" ".join([m.content for m in request.messages]))
            // 4,  # Rough estimate
            completion_tokens=len(text) // 4,  # Rough estimate
            total_tokens=(
                len(" ".join([m.content for m in request.messages])) + len(text)
            )
            // 4,  # Rough estimate
        ),
    )

    return response


async def stream_openai_response(
    orchestration_response: Dict[str, Any], request: ChatCompletionRequest
) -> AsyncGenerator[str, None]:
    """
    Stream an AI Orchestration response as an OpenAI API SSE stream.

    Args:
        orchestration_response: The AI Orchestration response.
        request: The original OpenAI API request.

    Yields:
        SSE formatted data chunks.
    """
    # Create a unique ID for this completion
    completion_id = f"chatcmpl-{uuid.uuid4().hex}"
    created_time = int(time.time())
    model = orchestration_response.get("model", request.model)

    # Extract the text from the orchestration response
    text = orchestration_response.get("text", "")

    # Simulate streaming by splitting the text into chunks
    # In a real implementation, you would stream directly from the model
    chunk_size = 10  # Characters per chunk
    chunks = [text[i : i + chunk_size] for i in range(0, len(text), chunk_size)]

    # Send the first chunk with role
    if chunks:
        first_chunk = chunks[0]
        first_message = {
            "id": completion_id,
            "object": "chat.completion.chunk",
            "created": created_time,
            "model": model,
            "choices": [
                {
                    "index": 0,
                    "delta": {"role": "assistant", "content": first_chunk},
                    "finish_reason": None,
                }
            ],
        }
        yield f"data: {json.dumps(first_message)}\n\n"
        await asyncio.sleep(0.01)  # Small delay to simulate streaming

        # Stream the rest of the chunks
        for i, chunk in enumerate(chunks[1:], 1):
            # Last chunk
            is_last = i == len(chunks) - 1

            message = {
                "id": completion_id,
                "object": "chat.completion.chunk",
                "created": created_time,
                "model": model,
                "choices": [
                    {
                        "index": 0,
                        "delta": {"content": chunk},
                        "finish_reason": "stop" if is_last else None,
                    }
                ],
            }
            yield f"data: {json.dumps(message)}\n\n"
            await asyncio.sleep(0.01)  # Small delay to simulate streaming

    # Send the [DONE] message
    yield "data: [DONE]\n\n"
