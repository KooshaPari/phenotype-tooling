# SWE Agent with LangChain and LangGraph

A Software Engineering agent built with LangChain and LangGraph that supports MCP tools and provides both OpenAI-compatible and agent-specific APIs.

## Features

- **MCP Tool Integration**: Load and use tools from MCP servers defined in config.json
- **Multi-Provider LLM Support**: Use models from OpenAI and OpenRouter
- **OpenAI-Compatible API**: Drop-in replacement for OpenAI API clients
- **Agent Management API**: Create, update, and delete agent instances
- **Streaming Support**: Stream responses for both chat completions and agent invocations
- **Database Integration**: Persistent storage for agents and conversations
- **Monitoring and Logging**: Prometheus metrics and structured logging

## Architecture

The SWE Agent is built with the following components:

- **LangChain and LangGraph**: Core agent implementation
- **FastAPI**: API server
- **MCP Client**: Integration with MCP servers
- **LLM Services**: Integration with OpenAI and OpenRouter
- **SQLAlchemy**: Database ORM for persistence
- **Prometheus**: Metrics collection and monitoring

## API Endpoints

### OpenAI-Compatible Endpoints

- `GET /v1/models`: List available models
- `POST /v1/chat/completions`: Create a chat completion

### Agent Management Endpoints

- `POST /v1/agents`: Create a new agent
- `GET /v1/agents`: List all agents
- `GET /v1/agents/{agent_id}`: Get agent details
- `PUT /v1/agents/{agent_id}`: Update an agent
- `DELETE /v1/agents/{agent_id}`: Delete an agent
- `POST /v1/agents/{agent_id}/completions`: Invoke an agent

### Monitoring Endpoints

- `GET /metrics`: Prometheus metrics endpoint

## Setup

1. Install dependencies:

```bash
pip install -r requirements.txt
```

2. Configure environment variables:

```bash
# .env
OPENAI_API_KEY=REDACTED_AIRLOCK
OPENROUTER_API_KEY=REDACTED_AIRLOCK
```

3. Configure MCP tools in `config/config.json`:

```json
{
	"mcp_servers": [
		{
			"name": "math",
			"transport": "stdio",
			"command": "python",
			"args": ["mcp_servers/math_server.py"]
		}
	],
	"mcp_tools": []
}
```

4. Run the API server:

```bash
python run_api.py
```

## Usage

### Using the OpenAI-Compatible API

```python
import openai

# Configure the client to use your SWE Agent API
client = openai.OpenAI(
    base_url="http://localhost:8000/v1",
    api_key="REDACTED_AIRLOCK"  # Not used but required
)

# List available models
models = client.models.list()
print(models)

# Create a chat completion
response = client.chat.completions.create(
    model="gpt-4",
    messages=[
        {"role": "user", "content": "Hello, how can you help me with coding?"}
    ]
)
print(response.choices[0].message.content)
```

### Using the Agent Management API

```python
import requests

# Create a new agent
response = requests.post(
    "http://localhost:8000/v1/agents",
    json={
        "name": "My SWE Agent",
        "description": "A Software Engineering agent",
        "llm_model_id": "gpt-4"
    }
)
agent_id = response.json()["agent_id"]

# Invoke the agent
response = requests.post(
    f"http://localhost:8000/v1/agents/{agent_id}/completions",
    json={
        "messages": [
            {"role": "user", "content": "Write a Python function to calculate Fibonacci numbers"}
        ]
    }
)
print(response.json())
```

## Monitoring

The SWE Agent includes built-in monitoring and logging:

- **Prometheus Metrics**: Available at `/metrics` endpoint
- **Request/Response Logging**: All API requests and responses are logged
- **Performance Metrics**: Request latency and count metrics are collected

## License

MIT
