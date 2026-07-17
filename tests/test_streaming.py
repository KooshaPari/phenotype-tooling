"""
Test script to verify the streaming functionality.
"""

import asyncio
import json
import sys
import os
import time

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.api.chat_api import stream_chat_completion
from src.llm.models import ChatCompletionRequest, ChatMessage


async def test_streaming():
    """
    Test the streaming functionality.
    """
    print("Testing streaming functionality...")
    
    # Create a simple chat request
    chat_request = ChatCompletionRequest(
        model="gpt-4o-mini",
        messages=[
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="Say hello world."),
        ],
        stream=True,
    )
    
    print("\n1. Testing streaming with default tools:")
    # Collect all chunks
    chunks = []
    async for chunk in stream_chat_completion(chat_request):
        # Parse SSE events: extract data lines
        for line in chunk.splitlines():
            if line.startswith("data: "):
                content = line[len("data: "):]
                if content.strip() == "[DONE]":
                    print("Received [DONE] marker")
                else:
                    try:
                        parsed = json.loads(content)
                        chunks.append(parsed)
                        print(f"Received chunk: {json.dumps(parsed, indent=2)}")
                    except json.JSONDecodeError:
                        print(f"Failed to parse chunk: {content}")
    
    # Verify the chunks
    if len(chunks) > 0:
        # First chunk should have role: assistant
        first_chunk = chunks[0]
        if "choices" in first_chunk and len(first_chunk["choices"]) > 0:
            delta = first_chunk["choices"][0].get("delta", {})
            if delta.get("role") == "assistant":
                print("✅ First chunk has correct role: assistant")
            else:
                print(f"❌ First chunk has incorrect role: {delta.get('role')}")
        
        # Last chunk should have finish_reason: stop
        last_chunk = chunks[-1]
        if "choices" in last_chunk and len(last_chunk["choices"]) > 0:
            finish_reason = last_chunk["choices"][0].get("finish_reason")
            if finish_reason == "stop":
                print("✅ Last chunk has correct finish_reason: stop")
            else:
                print(f"❌ Last chunk has incorrect finish_reason: {finish_reason}")
        
        # All chunks should have the same ID and created timestamp
        ids = set(chunk.get("id") for chunk in chunks)
        created_timestamps = set(chunk.get("created") for chunk in chunks)
        
        if len(ids) == 1:
            print("✅ All chunks have the same ID")
        else:
            print(f"❌ Chunks have different IDs: {ids}")
        
        if len(created_timestamps) == 1:
            print("✅ All chunks have the same created timestamp")
        else:
            print(f"❌ Chunks have different created timestamps: {created_timestamps}")
    else:
        print("❌ No chunks received")
    
    # Test with tool_choice: "none"
    print("\n2. Testing streaming with tool_choice: none")
    chat_request.tool_choice = "none"
    
    # Just count the chunks this time
    chunk_count = 0
    async for chunk in stream_chat_completion(chat_request):
        if chunk.startswith("data: ") and chunk.endswith("\n\n"):
            chunk_content = chunk[6:-2]
            if chunk_content != "[DONE]":
                chunk_count += 1
    
    print(f"Received {chunk_count} chunks with tool_choice: none")


if __name__ == "__main__":
    asyncio.run(test_streaming())
