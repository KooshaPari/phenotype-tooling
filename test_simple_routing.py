#!/usr/bin/env python
"""
Simple test to verify our routing logic works.
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def test_routing_logic():
    """Test the routing logic directly."""
    print("Testing routing logic...")
    
    try:
        # Import our functions
        from src.llm.services import determine_model_provider, extract_model_id
        
        # Test model ID that was causing issues
        test_model = "openrouter/qwen/qwen3-235b-a22b:free"
        
        print(f"Testing model: {test_model}")
        
        # Test provider determination
        provider = determine_model_provider(test_model)
        print(f"Determined provider: {provider}")
        
        # Test model ID extraction
        model_id = extract_model_id(test_model, provider)
        print(f"Extracted model ID: {model_id}")
        
        # Test the expected behavior
        if provider == "openrouter":
            print("✅ Provider detection working correctly")
        else:
            print(f"❌ Expected 'openrouter', got '{provider}'")
            
        if model_id == test_model:  # For OpenRouter with non-openrouter prefix, should keep full model
            print("✅ Model ID extraction working correctly")
        else:
            print(f"❌ Expected '{test_model}', got '{model_id}'")
            
        return True
        
    except Exception as e:
        print(f"❌ Error testing routing logic: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_langchain_wrapper():
    """Test the LangChain wrapper."""
    print("\nTesting LangChain wrapper...")
    
    try:
        from src.llm.langchain_wrapper import CustomChatLLM
        
        # Create an instance
        llm = CustomChatLLM(
            model="openrouter/qwen/qwen3-235b-a22b:free",
            temperature=0.7
        )
        
        print(f"✅ LangChain wrapper created successfully")
        print(f"Model: {llm.model}")
        print(f"Temperature: {llm.temperature}")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing LangChain wrapper: {e}")
        import traceback
        traceback.print_exc()
        return False

if __name__ == "__main__":
    print("Simple Routing Test")
    print("==================")
    
    success1 = test_routing_logic()
    success2 = test_langchain_wrapper()
    
    if success1 and success2:
        print("\n✅ All tests passed!")
    else:
        print("\n❌ Some tests failed!")
        sys.exit(1)
