#!/usr/bin/env python
"""
Test script to verify our agent works correctly with the fixed LangChain wrapper.
"""

import sys
import os
import asyncio

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


async def test_agent_creation():
    """Test that we can create an agent with our custom LLM wrapper."""
    print("Testing agent creation...")

    try:
        # Import our agent
        from src.agent import SWEAgent

        # Test model ID that was causing issues
        test_model = "openrouter/qwen/qwen3-235b-a22b:free"

        print(f"Creating SWEAgent with model: {test_model}")

        # Create an agent instance
        agent = SWEAgent(model_name=test_model, temperature=0.7)

        # Initialize the agent (this loads tools and creates the graph)
        await agent.initialize()

        print(f"✅ Agent created successfully")
        print(f"Agent model: {agent.model_name}")
        print(f"Agent temperature: {agent.temperature}")
        print(f"LLM type: {type(agent.model).__name__}")

        # Check if the model has bind_tools method
        if hasattr(agent.model, "bind_tools"):
            print("✅ Agent LLM has bind_tools method")

            # Test binding tools (this was causing the NotImplementedError)
            try:
                bound_model = agent.model.bind_tools(agent.tools)
                print(f"✅ bind_tools method works - bound {len(agent.tools)} tools")
                print(f"Bound model type: {type(bound_model).__name__}")
            except Exception as e:
                print(f"❌ bind_tools failed: {e}")
                return False
        else:
            print("❌ Agent LLM missing bind_tools method")
            return False

        return True

    except Exception as e:
        print(f"❌ Error testing agent creation: {e}")
        import traceback

        traceback.print_exc()
        return False


async def test_agent_invoke():
    """Test that we can invoke the agent with a simple message."""
    print("\nTesting agent invocation...")

    try:
        # Import our agent
        from src.agent import SWEAgent

        # Use a simpler model for testing (gpt-4o-mini should work)
        test_model = "gpt-4o-mini"

        print(f"Creating SWEAgent with model: {test_model}")

        # Create an agent instance
        agent = SWEAgent(model_name=test_model, temperature=0.7)

        # Initialize the agent (this loads tools and creates the graph)
        await agent.initialize()

        # Test input
        test_input = {
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, this is a test message. Please respond briefly.",
                }
            ],
            "agent_config": {
                "temperature": 0.7,
                "max_tokens": 50,
                "user": None,
                "tool_choice": None,
            },
        }

        print("Invoking agent...")

        # This should not raise NotImplementedError anymore
        response = await agent.invoke(test_input)

        print(f"✅ Agent invocation successful")
        print(f"Response type: {type(response)}")

        if isinstance(response, dict) and "messages" in response:
            messages = response["messages"]
            if messages:
                last_message = messages[-1]
                print(f"Last message role: {last_message.get('role', 'unknown')}")
                content = last_message.get("content", "")
                print(f"Response content preview: {content[:100]}...")

        return True

    except Exception as e:
        print(f"❌ Error testing agent invocation: {e}")
        import traceback

        traceback.print_exc()
        return False


async def main():
    """Run all tests."""
    print("Agent Direct Test")
    print("================")

    success1 = await test_agent_creation()
    success2 = await test_agent_invoke()

    if success1 and success2:
        print("\n✅ All agent tests passed!")
        print("The NotImplementedError for bind_tools should now be fixed.")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())
