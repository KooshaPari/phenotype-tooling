"""
Test script to verify the tool limit functionality.
"""

import asyncio
import json
import sys
import os

# Add the src directory to the path
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.agent import SWEAgent
from src.mcp.client import get_mcp_tools


async def test_tool_limit():
    """
    Test the tool limit functionality.
    """
    print("Testing tool limit functionality...")
    
    # Test with no limit
    print("\n1. Testing with no limit:")
    tools = await get_mcp_tools()
    print(f"Total tools available: {len(tools)}")
    
    # Test with a limit of 10
    print("\n2. Testing with a limit of 10:")
    limited_tools = await get_mcp_tools(max_tools=10)
    print(f"Limited tools: {len(limited_tools)}")
    print(f"Tool names: {[tool.name for tool in limited_tools]}")
    
    # Test with a limit of 0 (no tools)
    print("\n3. Testing with a limit of 0 (no tools):")
    no_tools = await get_mcp_tools(max_tools=0)
    print(f"No tools: {len(no_tools)}")
    
    # Test SWEAgent with different limits
    print("\n4. Testing SWEAgent with OpenAI model and default limit (128):")
    agent = SWEAgent(model_name="gpt-4")
    await agent.initialize()
    print(f"Agent tools: {len(agent.tools)}")
    
    print("\n5. Testing SWEAgent with OpenAI model and no tools:")
    agent_no_tools = SWEAgent(model_name="gpt-4", max_tools=0)
    await agent_no_tools.initialize()
    print(f"Agent tools: {len(agent_no_tools.tools)}")
    
    print("\n6. Testing SWEAgent with non-OpenAI model:")
    agent_non_openai = SWEAgent(model_name="anthropic/claude-3-opus-20240229")
    await agent_non_openai.initialize()
    print(f"Agent tools: {len(agent_non_openai.tools)}")


if __name__ == "__main__":
    asyncio.run(test_tool_limit())
