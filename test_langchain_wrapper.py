#!/usr/bin/env python
"""
Test script to verify our LangChain wrapper works correctly.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_langchain_wrapper():
    """Test the LangChain wrapper directly."""
    print("Testing LangChain wrapper...")
    
    try:
        # Import our custom wrapper
        from src.llm.langchain_wrapper import CustomChatLLM
        from langchain_core.messages import HumanMessage
        
        # Test model ID that was causing issues
        test_model = "openrouter/qwen/qwen3-235b-a22b:free"
        
        print(f"Creating CustomChatLLM with model: {test_model}")
        
        # Create an instance
        llm = CustomChatLLM(
            model=test_model,
            temperature=0.7
        )
        
        print(f"✅ LangChain wrapper created successfully")
        print(f"Model: {llm.model}")
        print(f"Temperature: {llm.temperature}")
        print(f"LLM Type: {llm._llm_type}")
        
        # Test bind_tools method
        print("\nTesting bind_tools method...")
        
        # Create a mock tool
        class MockTool:
            def __init__(self, name, description):
                self.name = name
                self.description = description
                self.args_schema = {"type": "object", "properties": {}}
        
        mock_tools = [
            MockTool("test_tool_1", "A test tool for testing"),
            MockTool("test_tool_2", "Another test tool")
        ]
        
        # Test binding tools
        llm_with_tools = llm.bind_tools(mock_tools)
        
        print(f"✅ bind_tools method works")
        print(f"LLM with tools type: {type(llm_with_tools).__name__}")
        print(f"Number of tools bound: {len(llm_with_tools.tools)}")
        
        # Test that the bound LLM has the correct model
        print(f"Bound LLM model: {llm_with_tools.model}")
        
        if llm_with_tools.model == test_model:
            print("✅ Model preserved correctly in bound LLM")
        else:
            print(f"❌ Model not preserved: expected '{test_model}', got '{llm_with_tools.model}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing LangChain wrapper: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_message_conversion():
    """Test message conversion functionality."""
    print("\nTesting message conversion...")
    
    try:
        from src.llm.langchain_wrapper import CustomChatLLM
        from langchain_core.messages import HumanMessage, AIMessage, SystemMessage
        
        llm = CustomChatLLM(model="test-model")
        
        # Test messages
        messages = [
            SystemMessage(content="You are a helpful assistant."),
            HumanMessage(content="Hello, how are you?"),
            AIMessage(content="I'm doing well, thank you!")
        ]
        
        # Convert messages
        dict_messages = llm._convert_messages_to_dict(messages)
        
        print(f"✅ Message conversion works")
        print(f"Original messages: {len(messages)}")
        print(f"Converted messages: {len(dict_messages)}")
        
        # Check the conversion
        expected_roles = ["system", "user", "assistant"]
        for i, (original, converted) in enumerate(zip(messages, dict_messages)):
            if converted["role"] == expected_roles[i]:
                print(f"✅ Message {i+1} role correct: {converted['role']}")
            else:
                print(f"❌ Message {i+1} role incorrect: expected '{expected_roles[i]}', got '{converted['role']}'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing message conversion: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("LangChain Wrapper Test")
    print("=====================")
    
    success1 = test_langchain_wrapper()
    success2 = test_message_conversion()
    
    if success1 and success2:
        print("\n✅ All LangChain wrapper tests passed!")
        print("The bind_tools NotImplementedError should now be fixed.")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
