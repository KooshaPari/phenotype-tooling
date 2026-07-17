#!/usr/bin/env python
"""
Test script to verify model routing is working correctly.
"""

import requests
import json
import sys


def test_model_routing():
    """Test that model routing works correctly for different model IDs."""

    # Test cases with different model ID formats
    test_cases = [
        {
            "name": "OpenRouter Qwen Model",
            "model": "openrouter/qwen/qwen3-235b-a22b:free",
            "expected_provider": "openrouter",
        },
        {
            "name": "OpenRouter DeepSeek Model",
            "model": "openrouter/deepseek/deepseek-r1:free",
            "expected_provider": "openrouter",
        },
        {
            "name": "Direct Qwen Model",
            "model": "qwen/qwen3-235b-a22b:free",
            "expected_provider": "openrouter",
        },
        {
            "name": "OpenAI GPT Model",
            "model": "openai/gpt-4o-mini",
            "expected_provider": "openai",
        },
    ]

    base_url = "http://localhost:8002"

    for test_case in test_cases:
        print(f"\n=== Testing {test_case['name']} ===")
        print(f"Model: {test_case['model']}")
        print(f"Expected Provider: {test_case['expected_provider']}")

        # Prepare the request
        payload = {
            "model": test_case["model"],
            "messages": [
                {
                    "role": "user",
                    "content": "Hello, this is a test message. Please respond briefly.",
                }
            ],
            "temperature": 0.7,
            "stream": False,
            "max_tokens": 50,
        }

        try:
            # Make the request
            response = requests.post(
                f"{base_url}/v1/chat/completions",
                headers={"Content-Type": "application/json"},
                json=payload,
                timeout=30,
            )

            print(f"Status Code: {response.status_code}")

            if response.status_code == 200:
                result = response.json()
                print(f"Response Model: {result.get('model', 'N/A')}")
                print(
                    f"Response Content: {result.get('choices', [{}])[0].get('message', {}).get('content', 'N/A')[:100]}..."
                )
                print("✅ SUCCESS")
            else:
                print(f"❌ FAILED - Status: {response.status_code}")
                print(f"Response: {response.text[:500]}...")

        except requests.exceptions.RequestException as e:
            print(f"❌ REQUEST FAILED: {e}")
        except Exception as e:
            print(f"❌ UNEXPECTED ERROR: {e}")


def test_provider_detection():
    """Test the provider detection logic directly."""
    print("\n=== Testing Provider Detection Logic ===")

    # Import our provider detection function
    sys.path.insert(
        0, "/Users/kooshapari/Downloads/home-2/ubuntu/swe_agent_project/new/new"
    )
    from src.llm.services import determine_model_provider

    test_models = [
        "openrouter/qwen/qwen3-235b-a22b:free",
        "qwen/qwen3-235b-a22b:free",
        "openai/gpt-4o-mini",
        "gpt-4o-mini",
        "anthropic/claude-3-sonnet",
        "deepseek/deepseek-r1:free",
    ]

    for model in test_models:
        provider = determine_model_provider(model)
        print(f"Model: {model} -> Provider: {provider}")


if __name__ == "__main__":
    print("Model Routing Test Script")
    print("========================")

    # Test provider detection logic first
    test_provider_detection()

    # Test actual API requests
    test_model_routing()

    print("\n=== Test Complete ===")
