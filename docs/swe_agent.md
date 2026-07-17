# SWE Agent Documentation

## Overview

The SWE Agent is a software engineering agent built with LangChain and LangGraph that can function both as a chatbot and as part of an agent network. It provides both OpenAI-compatible and agent-specific APIs, supports multiple LLM providers (OpenAI, OpenRouter), and can load and use MCP tools from a configuration file.

## Architecture

The SWE Agent is built with a modular architecture that separates concerns and allows for easy extension:

```
new/
├── config/
│   └── config.json       # MCP tools configuration
├── data/                 # Database storage
├── requirements.txt      # Project dependencies
├── run_api.py            # Script to run the API server
└── src/
    ├── agent.py          # Core agent implementation
    ├── api/
    │   ├── main.py       # FastAPI application
    │   ├── models_api.py # Models API endpoints
    │   ├── chat_api.py   # Chat API endpoints
    │   └── agents_api.py # Agent management API endpoints
    ├── db/
    │   ├── models.py     # Database models
    │   └── crud.py       # Database operations
    ├── llm/
    │   ├── models.py     # LLM models
    │   └── services.py   # LLM services
    ├── mcp/
    │   └── client.py     # MCP client implementation
    └── utils/
        ├── config.py     # Configuration utilities
        └── logging.py    # Logging utilities
```

## Core Components

### SWE Agent

The SWE Agent is implemented in `src/agent.py` and provides the core functionality for the agent. It uses LangGraph's `create_react_agent` to create a ReAct agent that can use tools and follow a system prompt.

Key features:
- Loads MCP tools from a configuration file
- Supports multiple LLM providers (OpenAI, OpenRouter)
- Uses LangGraph for agent execution
- Provides a streaming interface for responses

### API Endpoints

The API endpoints are implemented in `src/api/` and provide both OpenAI-compatible and agent-specific APIs:

#### OpenAI-Compatible API

- `GET /v1/models`: Lists available models from OpenAI and OpenRouter
- `POST /v1/chat/completions`: Creates a chat completion using the SWE agent

#### Agent Management API

- `POST /v1/agents`: Creates a new agent instance
- `GET /v1/agents`: Lists all agent instances
- `GET /v1/agents/{agent_id}`: Gets details for a specific agent instance
- `PUT /v1/agents/{agent_id}`: Updates an agent instance
- `DELETE /v1/agents/{agent_id}`: Deletes an agent instance
- `POST /v1/agents/{agent_id}/completions`: Invokes an agent with a set of messages

### MCP Integration

The MCP integration is implemented in `src/mcp/client.py` and provides the ability to load and use MCP tools from a configuration file.

Key features:
- Loads MCP tools from a configuration file
- Supports multiple MCP servers
- Provides a unified interface for tool execution

### LLM Integration

The LLM integration is implemented in `src/llm/services.py` and provides the ability to use models from multiple providers.

Key features:
- Supports OpenAI and OpenRouter models
- Provides a unified interface for model execution
- Handles model-specific parameters

## Configuration

### config.json

The `config.json` file in the root directory contains the configuration for MCP tools:

```json
{
    "mcp_servers": [
        {
            "name": "math",
            "transport": "stdio",
            "command": "python",
            "args": ["mcp_servers/math_server.py"],
            "auto_approve": ["add", "multiply", "subtract", "divide"],
            "timeout": 60
        }
    ],
    "mcp_tools": []
}
```

### .env

The `.env` file contains environment variables for the application:

```
# API Keys
OPENAI_API_KEY=REDACTED_AIRLOCK
OPENROUTER_API_KEY=REDACTED_AIRLOCK

# Server Configuration
PORT=8000
HOST=0.0.0.0

# Database Configuration
DATABASE_URL=sqlite:///data/agents.db

# Logging Configuration
LOG_LEVEL=INFO
```

## Usage

### Running the API Server

To run the API server:

```bash
cd new
python run_api.py
```

### Using the API

#### List Models

```bash
curl http://localhost:8000/v1/models
```

#### Create a Chat Completion

```bash
curl -X POST http://localhost:8000/v1/chat/completions \
  -H "Content-Type: application/json" \
  -d '{
    "model": "gpt-4",
    "messages": [
      {
        "role": "system",
        "content": "You are a helpful assistant."
      },
      {
        "role": "user",
        "content": "Hello, world!"
      }
    ]
  }'
```

#### Create an Agent

```bash
curl -X POST http://localhost:8000/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My Agent",
    "model_name": "gpt-4",
    "temperature": 0.7,
    "system_prompt": "You are a helpful assistant."
  }'
```

#### Invoke an Agent

```bash
curl -X POST http://localhost:8000/v1/agents/1/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [
      {
        "role": "user",
        "content": "Hello, world!"
      }
    ]
  }'
```

## Development

### Running Tests

To run the tests:

```bash
cd new
python run_tests.py
```

### Adding New Features

To add new features to the SWE agent:

1. Add the feature to the appropriate module
2. Add tests for the feature
3. Update the documentation
4. Run the tests to ensure everything works

### Adding New MCP Tools

To add new MCP tools:

1. Add the tool to the `config.json` file
2. Implement the tool in the appropriate MCP server
3. Update the documentation
4. Test the tool with the SWE agent
