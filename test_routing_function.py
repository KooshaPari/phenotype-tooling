#!/usr/bin/env python
"""
Test script to verify our routing function works correctly.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_routing_function():
    """Test our get_chat_completion function directly."""
    print("Testing get_chat_completion function...")
    
    try:
        from src.llm.services import get_chat_completion
        
        # Test the exact same request that was failing
        model = "openrouter/qwen/qwen3-235b-a22b:free"
        messages = [
            {"role": "user", "content": "Hello, please respond with just 'Hi!'"}
        ]
        
        print(f"Testing model: {model}")
        print(f"Messages: {messages}")
        
        # Call our routing function
        response = get_chat_completion(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=10,
            stream=False,
            tools=None,
            tool_choice=None
        )
        
        print(f"✅ SUCCESS - Response type: {type(response)}")
        
        # Extract content from response
        if hasattr(response, 'choices') and response.choices:
            content = response.choices[0].message.content
            print(f"Response content: {content}")
        elif isinstance(response, dict) and 'choices' in response:
            content = response['choices'][0]['message']['content']
            print(f"Response content: {content}")
        else:
            print(f"Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing routing function: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_with_tools():
    """Test our routing function with tools."""
    print("\nTesting get_chat_completion function with tools...")
    
    try:
        from src.llm.services import get_chat_completion
        
        # Test with tools (similar to what the agent does)
        model = "openrouter/qwen/qwen3-235b-a22b:free"
        messages = [
            {"role": "user", "content": "Hello, what tools do you have available?"}
        ]
        
        # Simple test tool
        tools = [
            {
                "type": "function",
                "function": {
                    "name": "test_tool",
                    "description": "A test tool",
                    "parameters": {
                        "type": "object",
                        "properties": {
                            "input": {
                                "type": "string",
                                "description": "Test input"
                            }
                        }
                    }
                }
            }
        ]
        
        print(f"Testing model: {model}")
        print(f"Messages: {messages}")
        print(f"Tools: {len(tools)} tools")
        
        # Call our routing function with tools
        response = get_chat_completion(
            model=model,
            messages=messages,
            temperature=0.7,
            max_tokens=50,
            stream=False,
            tools=tools,
            tool_choice="auto"
        )
        
        print(f"✅ SUCCESS - Response type: {type(response)}")
        
        # Extract content from response
        if hasattr(response, 'choices') and response.choices:
            content = response.choices[0].message.content
            print(f"Response content: {content}")
        elif isinstance(response, dict) and 'choices' in response:
            content = response['choices'][0]['message']['content']
            print(f"Response content: {content}")
        else:
            print(f"Response: {response}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing routing function with tools: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Routing Function Test")
    print("====================")
    
    success1 = test_routing_function()
    success2 = test_with_tools()
    
    if success1 and success2:
        print("\n✅ All routing function tests passed!")
        print("The routing is working correctly.")
    else:
        print("\n❌ Some routing function tests failed!")
        print("There may be an issue with the routing implementation.")
