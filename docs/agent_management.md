# Agent Management System

This document provides an overview of the Agent Management System, which enables programmatic creation, management, and communication between agents.

## Overview

The Agent Management System provides a comprehensive set of tools for creating, retrieving, updating, and deleting agents, as well as facilitating communication between agents in a swarm-like architecture. It is designed to be accessible through multiple interfaces:

1. **REST API**: A set of HTTP endpoints for agent management
2. **CLI**: A command-line interface for agent management
3. **MCP Tools**: A set of MCP tools for agent management
4. **MCP Server**: A dedicated MCP server for agent management

## Components

### Agent Manager

The Agent Manager is a service that handles agent lifecycle management. It provides functionality for:

- Creating agents with custom prompts
- Retrieving agent information
- Updating agent configuration
- Deleting agents
- Invoking agents with messages

### Agent Communication Hub

The Agent Communication Hub facilitates communication between agents. It provides functionality for:

- Sending messages between agents
- Broadcasting messages to multiple agents
- Retrieving message history
- Receiving messages in real-time

### REST API

The REST API provides HTTP endpoints for agent management. The following endpoints are available:

#### Agent Management

- `POST /v1/agents`: Create a new agent
- `GET /v1/agents`: List all agents
- `GET /v1/agents/{agent_id}`: Get an agent by ID
- `PUT /v1/agents/{agent_id}`: Update an agent
- `DELETE /v1/agents/{agent_id}`: Delete an agent
- `POST /v1/agents/{agent_id}/completions`: Invoke an agent

#### Agent Communication

- `POST /v1/agents/messages/send`: Send a message from one agent to another
- `POST /v1/agents/messages/broadcast`: Broadcast a message to multiple agents
- `GET /v1/agents/{agent_id}/messages`: Get messages for an agent
- `GET /v1/agents/{agent_id}/messages/receive`: Receive messages for an agent

### CLI

The CLI provides a command-line interface for agent management. The following commands are available:

#### Agent Management

- `agent_cli.py create`: Create a new agent
- `agent_cli.py list`: List all agents
- `agent_cli.py get`: Get an agent by ID
- `agent_cli.py update`: Update an agent
- `agent_cli.py delete`: Delete an agent
- `agent_cli.py invoke`: Invoke an agent

#### Headless Mode

For programmatic use, a headless mode is available through `agent_headless.py`. This mode returns parsable JSON output for all commands.

### MCP Tools

The MCP tools provide a set of functions for agent management that can be used by other agents. The following tools are available:

#### Agent Management

- `create_agent_tool`: Create a new agent
- `get_agent_tool`: Get an agent by ID
- `list_agents_tool`: List all agents
- `update_agent_tool`: Update an agent
- `delete_agent_tool`: Delete an agent
- `invoke_agent_tool`: Invoke an agent

#### Agent Communication

- `send_message_tool`: Send a message from one agent to another
- `broadcast_message_tool`: Broadcast a message to multiple agents
- `get_messages_tool`: Get messages for an agent
- `receive_messages_tool`: Receive messages for an agent

### MCP Server

The MCP server provides a dedicated server for agent management that can be used by other agents. It exposes all the MCP tools as MCP server tools.

## Usage Examples

### Creating an Agent

#### Using the REST API

```bash
curl -X POST http://localhost:8000/v1/agents \
  -H "Content-Type: application/json" \
  -d '{
    "name": "math-agent",
    "llm_model_id": "gpt-4o-mini",
    "description": "An agent that can solve math problems",
    "initial_prompt": "You are a math expert. Solve math problems step by step."
  }'
```

#### Using the CLI

```bash
python src/cli/agent_cli.py create \
  --name "math-agent" \
  --model "gpt-4o-mini" \
  --description "An agent that can solve math problems" \
  --system-prompt "You are a math expert. Solve math problems step by step."
```

#### Using the Headless CLI

```bash
python src/cli/agent_headless.py create \
  --name "math-agent" \
  --model "gpt-4o-mini" \
  --description "An agent that can solve math problems" \
  --system-prompt "You are a math expert. Solve math problems step by step."
```

### Invoking an Agent

#### Using the REST API

```bash
curl -X POST http://localhost:8000/v1/agents/agent-123/completions \
  -H "Content-Type: application/json" \
  -d '{
    "messages": [{"role": "user", "content": "What is 2+2?"}],
    "stream": false
  }'
```

#### Using the CLI

```bash
python src/cli/agent_cli.py invoke agent-123 "What is 2+2?"
```

### Agent Communication

#### Sending a Message

```bash
curl -X POST http://localhost:8000/v1/agents/messages/send \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "agent-123",
    "recipient_id": "agent-456",
    "content": "Hello, can you help me solve this math problem?"
  }'
```

#### Broadcasting a Message

```bash
curl -X POST http://localhost:8000/v1/agents/messages/broadcast \
  -H "Content-Type: application/json" \
  -d '{
    "sender_id": "agent-123",
    "content": "Hello everyone, I need help with a complex problem.",
    "recipient_ids": ["agent-456", "agent-789"]
  }'
```

## Running the MCP Server

To run the agent management MCP server:

```bash
python scripts/run_agent_management_server.py --host localhost --port 8080
```

## Integration with Team-Communications MCP Tools

The Agent Management System is designed to work seamlessly with team-communications MCP tools. Agents can communicate with each other using the Agent Communication Hub, and the MCP server provides a standardized interface for agent management.

## Conclusion

The Agent Management System provides a comprehensive set of tools for creating, managing, and facilitating communication between agents. It is designed to be accessible through multiple interfaces, making it easy to integrate with existing systems and workflows.
