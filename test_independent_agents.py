#!/usr/bin/env python3
"""
Test script for independent agent process creation and communication.
"""

import asyncio
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mcp.tools.agent_management_tools import (
    create_independent_agent_tool,
    invoke_agent_http_tool,
)


async def test_independent_agent_creation():
    """Test creating an independent agent process."""
    print("🧪 Testing Independent Agent Creation")
    print("=" * 50)
    
    # Create an independent agent
    print("Creating independent agent...")
    result = await create_independent_agent_tool(
        name="test-independent-agent",
        model_name="gpt-4o-mini",
        system_prompt="You are an independent AI agent running in your own process. You can communicate with other agents and use tools.",
        description="Test independent agent for process verification",
        temperature=0.7,
        max_tools=128,
    )
    
    print(f"Creation result: {result}")
    
    if "error" in result:
        print(f"❌ Error creating agent: {result['error']}")
        return None
    
    agent_id = result.get("agent_id")
    port = result.get("port")
    uri = result.get("uri")
    process_id = result.get("process_id")
    
    print(f"✅ Agent created successfully!")
    print(f"   Agent ID: {agent_id}")
    print(f"   Port: {port}")
    print(f"   URI: {uri}")
    print(f"   Process ID: {process_id}")
    print(f"   Process Status: {result.get('process_status')}")
    
    return result


async def test_agent_communication(agent_info):
    """Test communicating with the independent agent."""
    if not agent_info or "error" in agent_info:
        print("❌ Cannot test communication - no valid agent")
        return
    
    print("\n🔗 Testing Agent Communication")
    print("=" * 50)
    
    agent_id = agent_info["agent_id"]
    
    # Wait a moment for the agent to fully start
    print("Waiting for agent to fully initialize...")
    await asyncio.sleep(5)
    
    # Test HTTP communication (blocking)
    print("Testing HTTP communication (blocking)...")
    response = await invoke_agent_http_tool(
        agent_id=agent_id,
        message="Hello! I am testing direct HTTP communication with you. Please respond with your agent ID, name, and tell me what tools you have access to.",
        temperature=0.7,
    )
    
    print(f"HTTP Response: {response}")
    
    if "error" in response:
        print(f"❌ Error in HTTP communication: {response['error']}")
    else:
        print("✅ HTTP communication successful!")
        if "response" in response and "choices" in response["response"]:
            content = response["response"]["choices"][0]["message"]["content"]
            print(f"Agent Response: {content}")


async def main():
    """Main test function."""
    print("🚀 Starting Independent Agent Process Tests")
    print("=" * 60)
    
    try:
        # Test 1: Create independent agent
        agent_info = await test_independent_agent_creation()
        
        # Test 2: Communicate with agent
        await test_agent_communication(agent_info)
        
        print("\n🎉 Tests completed!")
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(main())
