import os
import sys
import dotenv
from pprint import pprint

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# Load environment variables
dotenv.load_dotenv()

from client import AIOrchestrationClient

def main():
    # Create client
    client = AIOrchestrationClient()
    
    # List available plugins
    print("Available plugins:")
    plugins = client.list_plugins()
    for plugin in plugins:
        print(f"- {plugin['name']}: {plugin['description']}")
    
    # Generate text with default settings
    print("\nGenerating with default settings:")
    response = client.generate(
        prompt="Explain how to implement a binary search algorithm in Python."
    )
    print(f"Response from {response.get('source', 'unknown')} model {response.get('model', 'unknown')}:")
    print(response.get('text', 'No response'))
    
    # Generate text with performance routing
    print("\nGenerating with performance routing:")
    response = client.generate(
        prompt="Explain how to implement a binary search algorithm in Python.",
        routing_policy="performance"
    )
    print(f"Response from {response.get('source', 'unknown')} model {response.get('model', 'unknown')}:")
    print(response.get('text', 'No response'))
    
    # Generate text with privacy routing
    print("\nGenerating with privacy routing:")
    response = client.generate(
        prompt="Explain how to implement a binary search algorithm in Python.",
        routing_policy="privacy"
    )
    print(f"Response from {response.get('source', 'unknown')} model {response.get('model', 'unknown')}:")
    print(response.get('text', 'No response'))
    
    # Use a plugin if available
    if plugins and any(p.get('id') == 'code_assistant' for p in plugins):
        print("\nGenerating with code assistant plugin:")
        response = client.generate(
            prompt="Refactor this code to be more efficient: def fibonacci(n): if n <= 1: return n; return fibonacci(n-1) + fibonacci(n-2)",
            plugins=["code_assistant"]
        )
        print(f"Response from {response.get('source', 'unknown')} model {response.get('model', 'unknown')}:")
        print(response.get('text', 'No response'))

if __name__ == "__main__":
    main()
