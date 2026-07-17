"""
Example script demonstrating the OpenAI-compatible API.

This script shows how to use the OpenAI Python library with our AI Orchestration system.
"""

import os
import sys
import dotenv
from pprint import pprint

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
dotenv.load_dotenv()

# Import the OpenAI library
from openai import OpenAI

def main():
    # Create an OpenAI client pointing to our API
    client = OpenAI(
        api_key="dummy_key",  # Not actually used by our API, but required by the OpenAI client
        base_url="http://localhost:9000/v1"  # Point to our API
    )
    
    print("Using OpenAI-compatible API with AI Orchestration")
    print("=" * 50)
    
    # List available models
    print("\nListing available models:")
    models = client.models.list()
    for model in models.data:
        print(f"- {model.id} (owned by {model.owned_by})")
    
    # Generate a chat completion
    print("\nGenerating chat completion:")
    response = client.chat.completions.create(
        model="gpt-3.5-turbo",  # This will be routed to the appropriate provider
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Explain how to implement a binary search algorithm in Python."}
        ],
        temperature=0.7
    )
    print(f"Response from {response.model}:")
    print(response.choices[0].message.content)
    
    # Generate a chat completion with streaming
    print("\nGenerating chat completion with streaming:")
    stream = client.chat.completions.create(
        model="gpt-3.5-turbo",
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Write a short poem about AI."}
        ],
        temperature=0.7,
        stream=True
    )
    
    print("Streaming response:")
    for chunk in stream:
        if chunk.choices[0].delta.content is not None:
            print(chunk.choices[0].delta.content, end="")
    print("\n")
    
    # Try with an OpenRouter model
    print("\nGenerating chat completion with an OpenRouter model:")
    try:
        response = client.chat.completions.create(
            model="openrouter/anthropic/claude-3-opus",  # This will be routed to OpenRouter
            messages=[
                {"role": "system", "content": "You are a helpful assistant."},
                {"role": "user", "content": "What are the benefits of quantum computing?"}
            ],
            temperature=0.7
        )
        print(f"Response from {response.model}:")
        print(response.choices[0].message.content)
    except Exception as e:
        print(f"Error: {str(e)}")
        print("Note: This example requires an OpenRouter API key to be set in the .env file.")

if __name__ == "__main__":
    main()
