#!/usr/bin/env python
"""
Test script to verify OpenRouter API is working correctly.
"""

import os
import requests
import json

def test_openrouter_api():
    """Test OpenRouter API directly."""
    print("Testing OpenRouter API...")
    
    # Check if API key is set
    api_key = REDACTED_AIRLOCK"OPENROUTER_API_KEY")
    if not api_key:
        REDACTED_AIRLOCK"❌ OPENROUTER_API_KEY not set")
        return False
    
    print(f"✅ API key found: {api_key[:10]}...")
    
    # Test with a simple model first
    test_models = [
        "qwen/qwen3-235b-a22b:free",  # The problematic model
        "openai/gpt-3.5-turbo",       # A known working model
        "meta-llama/llama-3.2-3b-instruct:free",  # Another free model
    ]
    
    for model in test_models:
        print(f"\nTesting model: {model}")
        
        headers = {
            "Authorization": REDACTED_AIRLOCK"Bearer {api_key}",
            "Content-Type": "application/json",
            "HTTP-Referer": "https://github.com/KooshaPari/swe_agent_project",
            "X-Title": "SWE Agent Project",
        }
        
        data = {
            "model": model,
            "messages": [
                {"role": "user", "content": "Hello, please respond with just 'Hi!'"}
            ],
            "temperature": 0.7,
            "max_tokens": 10
        }
        
        try:
            response = requests.post(
                "https://openrouter.ai/api/v1/chat/completions",
                headers=headers,
                json=data,
                timeout=30
            )
            
            print(f"Status Code: {response.status_code}")
            
            if response.status_code == 200:
                result = response.json()
                content = result.get("choices", [{}])[0].get("message", {}).get("content", "")
                print(f"✅ SUCCESS - Response: {content}")
                return True
            else:
                print(f"❌ FAILED - Status: {response.status_code}")
                print(f"Response: {response.text}")
                
        except Exception as e:
            print(f"❌ REQUEST FAILED: {e}")
    
    return False

def test_openrouter_models_list():
    """Test listing available models from OpenRouter."""
    print("\nTesting OpenRouter models list...")
    
    api_key = REDACTED_AIRLOCK"OPENROUTER_API_KEY")
    if not api_key:
        REDACTED_AIRLOCK"❌ OPENROUTER_API_KEY not set")
        return False
    
    try:
        response = requests.get(
            "https://openrouter.ai/api/v1/models",
            headers={"Authorization": REDACTED_AIRLOCK"Bearer {api_key}"},
            timeout=30
        )
        
        if response.status_code == 200:
            models = response.json().get("data", [])
            print(f"✅ Found {len(models)} models")
            
            # Look for qwen models
            qwen_models = [m for m in models if "qwen" in m.get("id", "").lower()]
            print(f"Found {len(qwen_models)} Qwen models:")
            for model in qwen_models[:5]:  # Show first 5
                print(f"  - {model.get('id')}")
            
            # Check if our specific model exists
            target_model = "qwen/qwen3-235b-a22b:free"
            model_exists = any(m.get("id") == target_model for m in models)
            if model_exists:
                print(f"✅ Target model '{target_model}' found in models list")
            else:
                print(f"❌ Target model '{target_model}' NOT found in models list")
                # Show similar models
                similar = [m for m in models if "qwen" in m.get("id", "").lower() and "free" in m.get("id", "")]
                print("Similar free Qwen models:")
                for model in similar[:3]:
                    print(f"  - {model.get('id')}")
            
            return True
        else:
            print(f"❌ Failed to get models list: {response.status_code}")
            print(f"Response: {response.text}")
            return False
            
    except Exception as e:
        print(f"❌ Error getting models list: {e}")
        return False

if __name__ == "__main__":
    print("OpenRouter API Test")
    print("==================")
    
    success1 = test_openrouter_models_list()
    success2 = test_openrouter_api()
    
    if success1 or success2:
        print("\n✅ OpenRouter API is accessible")
    else:
        print("\n❌ OpenRouter API issues detected")
        print("Check your OPENROUTER_API_KEY and network connection")
