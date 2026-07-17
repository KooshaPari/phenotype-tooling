#!/usr/bin/env python
"""
Test script to verify our bind_tools fix works correctly without MCP dependencies.
"""

import sys
import os
import asyncio

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

async def test_bind_tools_fix():
    """Test that bind_tools works correctly with our custom LLM wrapper."""
    print("Testing bind_tools fix...")
    
    try:
        # Import our agent
        from src.agent import SWEAgent
        from langchain_core.tools import Tool
        
        # Create a simple test tool
        def test_tool_func(input_text: str) -> str:
            """A simple test tool that echoes the input."""
            return f"Echo: {input_text}"
        
        test_tool = Tool(
            name="test_echo",
            description="A test tool that echoes the input",
            func=test_tool_func
        )
        
        # Use a simple model for testing
        test_model = "gpt-4o-mini"
        
        print(f"Creating SWEAgent with model: {test_model}")
        
        # Create an agent instance with predefined tools (no MCP)
        agent = SWEAgent(
            model_name=test_model,
            temperature=0.7,
            tools=[test_tool]  # Provide tools directly to avoid MCP initialization
        )
        
        # Initialize the agent (this should not try to load MCP tools since we provided tools)
        await agent.initialize()
        
        print(f"✅ Agent created successfully")
        print(f"Agent model: {agent.model_name}")
        print(f"Agent temperature: {agent.temperature}")
        print(f"LLM type: {type(agent.model).__name__}")
        print(f"Number of tools: {len(agent.tools)}")
        
        # Check if the model has bind_tools method
        if hasattr(agent.model, 'bind_tools'):
            print("✅ Agent LLM has bind_tools method")
            
            # Test binding tools (this was causing the NotImplementedError)
            try:
                bound_model = agent.model.bind_tools(agent.tools)
                print(f"✅ bind_tools method works - bound {len(agent.tools)} tools")
                print(f"Bound model type: {type(bound_model).__name__}")
                
                # Test that the bound model has the correct properties
                if hasattr(bound_model, 'tools') and len(bound_model.tools) > 0:
                    print(f"✅ Bound model has {len(bound_model.tools)} tools")
                    print(f"First tool: {bound_model.tools[0]}")
                else:
                    print("❌ Bound model has no tools")
                    return False
                    
            except Exception as e:
                print(f"❌ bind_tools failed: {e}")
                import traceback
                traceback.print_exc()
                return False
        else:
            print("❌ Agent LLM missing bind_tools method")
            return False
        
        # Test that we can create the graph without errors
        try:
            graph = agent._create_graph(None)
            print("✅ Graph creation successful")
            print(f"Graph type: {type(graph)}")
        except Exception as e:
            print(f"❌ Graph creation failed: {e}")
            import traceback
            traceback.print_exc()
            return False
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing bind_tools fix: {e}")
        import traceback
        traceback.print_exc()
        return False

async def test_simple_invocation():
    """Test a simple agent invocation without tool calls."""
    print("\nTesting simple agent invocation...")
    
    try:
        # Import our agent
        from src.agent import SWEAgent
        
        # Use a simple model for testing
        test_model = "gpt-4o-mini"
        
        print(f"Creating SWEAgent with model: {test_model}")
        
        # Create an agent instance with no tools to avoid tool-related issues
        agent = SWEAgent(
            model_name=test_model,
            temperature=0.7,
            tools=[]  # No tools to avoid complications
        )
        
        # Initialize the agent
        await agent.initialize()
        
        print("✅ Agent initialized successfully")
        
        # Test input that shouldn't trigger tool calls
        test_input = {
            "messages": [
                {"role": "user", "content": "Hello, please respond with just 'Hi there!' and nothing else."}
            ]
        }
        
        print("Attempting simple invocation...")
        
        # This should work without the NotImplementedError
        try:
            response = await agent.invoke(test_input)
            print(f"✅ Agent invocation successful")
            print(f"Response type: {type(response)}")
            
            if isinstance(response, dict) and "messages" in response:
                messages = response["messages"]
                if messages:
                    last_message = messages[-1]
                    print(f"Last message role: {getattr(last_message, 'role', 'unknown')}")
                    content = getattr(last_message, 'content', '')
                    print(f"Response content: {content[:100]}...")
            
            return True
            
        except NotImplementedError as e:
            if "bind_tools" in str(e):
                print(f"❌ bind_tools NotImplementedError still occurring: {e}")
                return False
            else:
                print(f"❌ Other NotImplementedError: {e}")
                return False
        except Exception as e:
            print(f"❌ Other error during invocation: {e}")
            import traceback
            traceback.print_exc()
            return False
        
    except Exception as e:
        print(f"❌ Error in simple invocation test: {e}")
        import traceback
        traceback.print_exc()
        return False

async def main():
    """Run all tests."""
    print("Bind Tools Fix Test")
    print("==================")
    
    success1 = await test_bind_tools_fix()
    success2 = await test_simple_invocation()
    
    if success1 and success2:
        print("\n✅ All bind_tools tests passed!")
        print("The NotImplementedError for bind_tools should now be fixed.")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)

if __name__ == "__main__":
    asyncio.run(main())
