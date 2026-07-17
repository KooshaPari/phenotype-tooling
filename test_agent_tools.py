#!/usr/bin/env python3
"""
Test script to verify that agents can properly use MCP tools.
This will test the fixed system prompt and tool loading.
"""

import asyncio
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.agent_prompt_based import PromptBasedSWEAgent


async def test_agent_tool_capabilities():
    """Test that the agent can properly use MCP tools."""
    print("🧪 TESTING AGENT MCP TOOL CAPABILITIES")
    print("=" * 50)
    
    try:
        # Create agent with MCP system prompt
        print("Creating agent with MCP system prompt...")
        agent = PromptBasedSWEAgent(
            model_name="gpt-4o-mini",
            temperature=0.7,
            max_tools=80,
            use_agent_management_priority=True
        )
        
        # Initialize the agent (this loads tools into system prompt)
        print("Initializing agent (loading MCP tools)...")
        await agent.initialize()
        
        print(f"✅ Agent initialized successfully!")
        print(f"   System prompt length: {len(agent.system_prompt)} characters")
        print(f"   Available tools: {len(agent.available_tools)}")
        print(f"   First 10 tools: {list(agent.available_tools.keys())[:10]}")
        
        # Test 1: Simple tool usage request
        print("\n🔧 Test 1: Testing tool recognition and usage")
        print("-" * 40)
        
        test_message = """Hello! I need you to create 3 additional agents for a Japanese real estate website project. 

Please create:
1. A Frontend Developer agent specialized in React and modern web development
2. A Backend Developer agent specialized in Node.js and database design  
3. A UX/UI Designer agent specialized in user experience and interface design

Use your MCP tools to create these agents with appropriate system prompts for each role."""
        
        # Invoke the agent
        print("Sending test message to agent...")
        response = await agent.invoke({
            "messages": [{"role": "user", "content": test_message}]
        })
        
        print("✅ Agent response received!")
        
        # Check the response
        if "messages" in response and response["messages"]:
            last_message = response["messages"][-1]
            if hasattr(last_message, "content"):
                content = last_message.content
                print(f"Response length: {len(content)} characters")
                print(f"Response preview: {content[:200]}...")
                
                # Check if agent recognizes tools
                if "create_agent" in content.lower() or "<create_agent>" in content:
                    print("🎉 SUCCESS: Agent recognizes and attempts to use MCP tools!")
                    return True
                else:
                    print("⚠️  Agent responded but didn't use MCP tools")
                    print(f"Full response: {content}")
            else:
                print("⚠️  Agent response has no content")
        else:
            print("⚠️  No messages in agent response")
            
        return False
        
    except Exception as e:
        print(f"❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()
        return False


async def main():
    """Main test function."""
    print("🚀 Starting Agent MCP Tool Test")
    print("Make sure MCP servers are running (python run_api.py)")
    print()
    
    success = await test_agent_tool_capabilities()
    
    print(f"\n🏁 Test Result: {'SUCCESS' if success else 'FAILED'}")
    
    if success:
        print("✅ Agent can properly recognize and use MCP tools!")
        print("✅ System prompt injection is working correctly!")
        print("✅ Tool loading and formatting is functional!")
    else:
        print("❌ Agent cannot properly use MCP tools")
        print("❌ Check system prompt injection and tool loading")


if __name__ == "__main__":
    asyncio.run(main())
