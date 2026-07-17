# SWE Agent Integration Tests

This directory contains integration tests for the SWE agent. The tests are designed to verify that the agent works correctly with different models, providers, and streaming options.

## Test Structure

The tests are organized into the following categories:

1. **Basic Tests**: Test basic functionality with simple questions.
2. **Tool Check Tests**: Test the agent's ability to list its MCP tools.
3. **Tool Execution Tests**: Test the agent's ability to use the Sequential Thinking tool.
4. **Reasoning Tests**: Test the agent's reasoning capabilities.

Each test category is run with the following combinations:

- Model: 4o-mini, o4-mini
- Provider: OpenAI, OpenRouter
- Streaming: Enabled, Disabled

## Running the Tests

To run all tests with mock responses (no server required):

```bash
cd new
python run_tests.py --integration
```

To run all tests with the actual server (server must be running):

```bash
cd new
python run_tests.py --integration --use-server
```

To specify a different model to use:

```bash
cd new
python run_tests.py --integration --use-server --model gpt-4o
```

To enable debug mode with more verbose output:

```bash
cd new
python run_tests.py --integration --use-server --debug
```

To run specific test categories:

```bash
cd new
python run_tests.py --integration --test-types basic tool_check
```

To run only unit tests:

```bash
cd new
python run_tests.py --unit
```

To run both unit and integration tests:

```bash
cd new
python run_tests.py --unit --integration
```

### Starting the Server

Before running tests with `--use-server`, make sure the SWE Agent API server is running:

```bash
cd new
python -m swe_agent.api
```

The server should be running on `http://localhost:8000`.

## Test Results

The test results are saved in the `tests/integration/results` directory. Each test result is saved as a JSON file with the following structure:

```json
{
  "test_name": "basic_openai_4o_mini_streaming",
  "prompt": "Hello! What is 1+1?",
  "response": {
    "id": "chatcmpl-123456789",
    "model": "gpt-4o-mini",
    "content": "Hello! 1+1 equals 2.",
    "streaming": true
  },
  "evaluation": {
    "content_length": 22,
    "has_expected_content": true,
    "critique": "The response is correct, clear, and concise..."
  }
}
```

## LLM Critic

The LLM critic is a component that evaluates the agent's responses using a separate LLM. It provides a detailed critique of each response based on criteria specific to the test category.

To run the LLM critic on existing test results:

```bash
cd new
python -m tests.integration.llm_critic
```

## Configuration

The tests use a custom `config.json` file located in the `tests/integration` directory. This file configures the MCP tools that the agent should have access to during the tests.

## Requirements

The tests require the following dependencies:

- openai
- aiohttp
- asyncio
- requests

These dependencies should be included in the project's `requirements.txt` file.
