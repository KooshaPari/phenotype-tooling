#!/usr/bin/env python3
"""
Script to run the enhanced agent management server.
"""

import argparse
import asyncio
import os
import sys
import json
import logging
import time
import signal
import select
import fcntl
import threading

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    stream=sys.stderr,
)
logger = logging.getLogger("agent-management-server")


# Set up signal handlers to prevent premature exit
def signal_handler(sig, frame):
    logger.info(f"Received signal {sig}, ignoring")
    # Don't exit, just log the signal


# Register signal handlers
signal.signal(signal.SIGINT, signal_handler)
signal.signal(signal.SIGTERM, signal_handler)


# Make stdin non-blocking
def make_stdin_nonblocking():
    try:
        # Get the file descriptor's current flags
        fd = sys.stdin.fileno()
        fl = fcntl.fcntl(fd, fcntl.F_GETFL)
        # Add the O_NONBLOCK flag
        fcntl.fcntl(fd, fcntl.F_SETFL, fl | os.O_NONBLOCK)
        logger.info("Set stdin to non-blocking mode")
        return True
    except Exception as e:
        logger.error(f"Failed to set stdin to non-blocking mode: {e}")
        return False


# Print debug information
logger.info(f"Python executable: {sys.executable}")
logger.info(f"Python version: {sys.version}")
logger.info(f"Current directory: {os.getcwd()}")
logger.info(f"PYTHONPATH: {os.environ.get('PYTHONPATH', 'Not set')}")
logger.info(f"Arguments: {sys.argv}")

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    # Import the MCP API client
    from src.mcp_api_client import MCPServer, Tool, ToolCall, ToolResponse

    logger.info("Successfully imported MCP API client")
except ImportError as e:
    logger.error(f"Failed to import MCP API client: {e}")
    sys.exit(1)


# Define a simple echo tool handler
async def echo_handler(tool_call: ToolCall) -> ToolResponse:
    """
    Echo handler for the echo tool.

    Args:
        tool_call: The tool call.

    Returns:
        The tool response.
    """
    logger.info(f"Handling tool call to '{tool_call.tool_name}'")
    logger.info(f"Arguments: {tool_call.arguments}")

    # Get the message from the arguments
    message = tool_call.arguments.get("message", "No message provided")

    # Return a response
    return ToolResponse(result={"message": f"Echo: {message}"})


# In-memory storage for prompts
prompts_storage = {
    "default": {
        "id": "default",
        "name": "Default Prompt",
        "content": "You are a helpful AI assistant.",
        "description": "The default system prompt for the agent.",
        "created_at": "2025-05-20T00:00:00Z",
        "updated_at": "2025-05-20T00:00:00Z",
    },
    "developer": {
        "id": "developer",
        "name": "Developer Prompt",
        "content": "You are a helpful AI assistant specialized in software development.",
        "description": "A system prompt for software development tasks.",
        "created_at": "2025-05-20T00:00:00Z",
        "updated_at": "2025-05-20T00:00:00Z",
    },
}


# Prompt management functions
def list_prompts():
    """List all available prompts."""
    return list(prompts_storage.values())


def get_prompt(prompt_id):
    """Get a prompt by ID."""
    if prompt_id in prompts_storage:
        return prompts_storage[prompt_id]
    return None


def create_prompt(prompt_data):
    """Create a new prompt."""
    import time
    import uuid

    # Generate a unique ID if not provided
    prompt_id = prompt_data.get("id", str(uuid.uuid4()))

    # Get current timestamp
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Create the prompt
    prompt = {
        "id": prompt_id,
        "name": prompt_data.get("name", "Unnamed Prompt"),
        "content": prompt_data.get("content", ""),
        "description": prompt_data.get("description", ""),
        "created_at": timestamp,
        "updated_at": timestamp,
    }

    # Store the prompt
    prompts_storage[prompt_id] = prompt

    return prompt


def update_prompt(prompt_id, prompt_data):
    """Update an existing prompt."""
    if prompt_id not in prompts_storage:
        return None

    import time

    # Get current timestamp
    timestamp = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())

    # Update the prompt
    prompt = prompts_storage[prompt_id]
    if "name" in prompt_data:
        prompt["name"] = prompt_data["name"]
    if "content" in prompt_data:
        prompt["content"] = prompt_data["content"]
    if "description" in prompt_data:
        prompt["description"] = prompt_data["description"]
    prompt["updated_at"] = timestamp

    # Store the updated prompt
    prompts_storage[prompt_id] = prompt

    return prompt


def delete_prompt(prompt_id):
    """Delete a prompt."""
    if prompt_id not in prompts_storage:
        return False

    # Delete the prompt
    del prompts_storage[prompt_id]

    return True


def main():
    """Main entry point for the script."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Enhanced Agent Management MCP Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument(
        "--async", dest="async_mode", action="store_true", help="Run in async mode"
    )

    args = parser.parse_args()

    # Create the server
    logger.info(f"Creating server on {args.host}:{args.port}")
    server = MCPServer(name="agent-management", host=args.host, port=args.port)

    # Register a tool
    logger.info("Registering echo tool")
    server.register_tool(
        Tool(
            name="echo",
            description="Echo a message",
            parameters={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "A message to echo"}
                },
                "required": ["message"],
            },
            handler=echo_handler,
        )
    )

    try:
        if args.async_mode:
            # Run in async mode
            logger.info("Starting server in async mode")
            asyncio.run(async_main(server))
        else:
            # Run in sync mode
            logger.info(f"Starting server in sync mode on {args.host}:{args.port}")

            # Simple HTTP server implementation
            from http.server import HTTPServer, BaseHTTPRequestHandler
            import json

            class SimpleHTTPRequestHandler(BaseHTTPRequestHandler):
                def do_GET(self):
                    if self.path == "/":
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        response = {
                            "message": f"MCP Server - {server.name}",
                            "status": "running",
                        }
                        self.wfile.write(json.dumps(response).encode())
                    elif self.path == "/tools":
                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        tools = [tool.to_dict() for tool in server.tools.values()]
                        response = {"tools": tools}
                        self.wfile.write(json.dumps(response).encode())
                    else:
                        self.send_response(404)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        response = {"error": "Not found"}
                        self.wfile.write(json.dumps(response).encode())

                def do_POST(self):
                    if self.path == "/call":
                        content_length = int(self.headers["Content-Length"])
                        post_data = self.rfile.read(content_length).decode("utf-8")
                        request = json.loads(post_data)

                        tool_name = request.get("tool_name")
                        arguments = request.get("arguments", {})

                        if tool_name not in server.tools:
                            self.send_response(404)
                            self.send_header("Content-type", "application/json")
                            self.end_headers()
                            response = {"error": f"Tool '{tool_name}' not found"}
                            self.wfile.write(json.dumps(response).encode())
                            return

                        # Create a tool call
                        tool_call = ToolCall(tool_name=tool_name, arguments=arguments)

                        # Handle the tool call synchronously
                        import asyncio

                        loop = asyncio.new_event_loop()
                        asyncio.set_event_loop(loop)
                        response = loop.run_until_complete(
                            server.tools[tool_name].handler(tool_call)
                        )
                        loop.close()

                        self.send_response(200)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        self.wfile.write(json.dumps(response.model_dump()).encode())
                    else:
                        self.send_response(404)
                        self.send_header("Content-type", "application/json")
                        self.end_headers()
                        response = {"error": "Not found"}
                        self.wfile.write(json.dumps(response).encode())

            # Start the HTTP server
            httpd = HTTPServer((args.host, args.port), SimpleHTTPRequestHandler)
            logger.info(f"Server started at http://{args.host}:{args.port}")
            httpd.serve_forever()
    except KeyboardInterrupt:
        # Stop the server on keyboard interrupt
        logger.info("Keyboard interrupt received, stopping server...")
    except Exception as e:
        logger.error(f"Error running enhanced agent management MCP server: {e}")
        import traceback

        logger.error(traceback.format_exc())


async def async_main(server):
    """Async main entry point for the script."""
    try:
        await server.start()

        # Keep the server running
        while True:
            await asyncio.sleep(1)
    except KeyboardInterrupt:
        # Stop the server on keyboard interrupt
        logger.info("Keyboard interrupt received, stopping server...")
        await server.stop()
    except Exception as e:
        logger.error(f"Error running enhanced agent management MCP server: {e}")
        await server.stop()


# Handle MCP protocol
def handle_mcp_stdio():
    """Handle MCP protocol over stdio."""
    logger.info("Starting MCP stdio handler")

    # Make stdin non-blocking
    make_stdin_nonblocking()

    # Make sure stdout is line-buffered
    sys.stdout.reconfigure(line_buffering=True)
    logger.info("Set stdout to line-buffered mode")

    # Create a server instance for tool registration
    server = MCPServer(name="agent-management", host="localhost", port=8080)

    # Register the echo tool
    server.register_tool(
        Tool(
            name="echo",
            description="Echo a message",
            parameters={
                "type": "object",
                "properties": {
                    "message": {"type": "string", "description": "A message to echo"}
                },
                "required": ["message"],
            },
            handler=echo_handler,
        )
    )

    # Function to read from stdin with timeout
    def read_line_with_timeout(timeout=1.0):
        """Read a line from stdin with timeout."""
        ready_to_read, _, _ = select.select([sys.stdin], [], [], timeout)
        if ready_to_read:
            try:
                return sys.stdin.readline().strip()
            except Exception as e:
                logger.error(f"Error reading from stdin: {e}")
                return ""
        return None  # Timeout occurred

    # Read the first line to get the initialization message
    logger.info("Waiting for initialization message...")

    # Keep trying to read the initialization message
    init_line = None
    while init_line is None or init_line == "":
        init_line = read_line_with_timeout()
        if init_line:
            logger.info(f"Received init line: {init_line}")
        else:
            # If timeout occurred, just log and continue
            logger.info("Waiting for initialization message (timeout)...")
            # Sleep a bit to avoid busy waiting
            time.sleep(0.1)

    try:
        init_data = json.loads(init_line)
        logger.info(f"Parsed init data: {init_data}")

        # Extract the initialization method
        method = init_data.get("method")

        # If method is not set, assume it's initialize
        if not method and "jsonrpc" in init_data:
            logger.info("No method found, assuming initialize")
            method = "initialize"

        if method == "initialize":
            # Send initialization response with tools
            tools = []
            for tool in server.tools.values():
                tools.append(
                    {
                        "name": tool.name,
                        "description": tool.description,
                        "parameters": tool.parameters,
                    }
                )

            response = {
                "jsonrpc": "2.0",
                "id": init_data.get("id"),
                "result": {
                    "name": "agent-management",
                    "version": "1.0.0",
                    "protocolVersion": "2024-11-05",
                    "capabilities": {},
                    "serverInfo": {
                        "name": "agent-management-server",
                        "version": "1.0.0",
                    },
                    "tools": tools,
                },
            }

            logger.info(f"Sending initialization response: {json.dumps(response)}")
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            logger.info("Initialization response sent and flushed")

            # Process incoming messages
            logger.info("Starting message processing loop")

            # Create a heartbeat thread to keep the connection alive
            def heartbeat():
                """Send a heartbeat message to stderr every 5 seconds."""
                while True:
                    logger.info("Heartbeat: MCP server is still running")
                    time.sleep(5)

            # Start the heartbeat thread
            heartbeat_thread = threading.Thread(target=heartbeat, daemon=True)
            heartbeat_thread.start()
            logger.info("Started heartbeat thread")

            while True:
                # Read from stdin with timeout
                line = read_line_with_timeout(timeout=0.5)

                # If timeout occurred, just continue the loop
                if line is None:
                    continue

                # If empty line, continue
                if not line:
                    continue

                logger.info(f"Received line: {line}")

                # Process the message
                try:
                    data = json.loads(line)
                    method = data.get("method")

                    if method == "shutdown":
                        # Handle shutdown request
                        logger.info("Received shutdown request")
                        response = {
                            "jsonrpc": "2.0",
                            "id": data.get("id"),
                            "result": None,
                        }
                        logger.info(
                            f"Sending shutdown response: {json.dumps(response)}"
                        )
                        sys.stdout.write(json.dumps(response) + "\n")
                        sys.stdout.flush()
                        logger.info("Shutdown response sent and flushed")

                        # Don't actually exit, just acknowledge the shutdown
                        continue

                    elif method == "prompts/list":
                        # Handle prompts/list request
                        logger.info("Received prompts/list request")
                        prompts = list_prompts()

                        # Format the response according to the expected schema
                        # The client expects an object with a 'prompts' field containing the array
                        response = {
                            "jsonrpc": "2.0",
                            "id": data.get("id"),
                            "result": {
                                "prompts": prompts,
                                "method": "prompts/list",  # Include the method in the response
                            },
                        }

                        logger.info(
                            f"Sending prompts/list response with {len(prompts)} prompts"
                        )
                        sys.stdout.write(json.dumps(response) + "\n")
                        sys.stdout.flush()
                        logger.info("Prompts/list response sent and flushed")
                        continue

                    elif method == "prompts/get":
                        # Handle prompts/get request
                        params = data.get("params", {})
                        prompt_id = params.get("id")
                        logger.info(
                            f"Received prompts/get request for prompt ID: {prompt_id}"
                        )

                        prompt = get_prompt(prompt_id)
                        if prompt:
                            response = {
                                "jsonrpc": "2.0",
                                "id": data.get("id"),
                                "result": {
                                    "prompt": prompt,
                                    "method": "prompts/get",  # Include the method in the response
                                },
                            }
                        else:
                            response = {
                                "jsonrpc": "2.0",
                                "id": data.get("id"),
                                "error": {
                                    "code": -32602,
                                    "message": f"Prompt with ID '{prompt_id}' not found",
                                },
                            }

                        logger.info(f"Sending prompts/get response")
                        sys.stdout.write(json.dumps(response) + "\n")
                        sys.stdout.flush()
                        logger.info("Prompts/get response sent and flushed")
                        continue

                    elif method == "prompts/create":
                        # Handle prompts/create request
                        params = data.get("params", {})
                        logger.info(
                            f"Received prompts/create request with params: {params}"
                        )

                        prompt = create_prompt(params)
                        response = {
                            "jsonrpc": "2.0",
                            "id": data.get("id"),
                            "result": {
                                "prompt": prompt,
                                "method": "prompts/create",  # Include the method in the response
                            },
                        }

                        logger.info(f"Sending prompts/create response")
                        sys.stdout.write(json.dumps(response) + "\n")
                        sys.stdout.flush()
                        logger.info("Prompts/create response sent and flushed")
                        continue

                    elif method == "prompts/update":
                        # Handle prompts/update request
                        params = data.get("params", {})
                        prompt_id = params.get("id")
                        logger.info(
                            f"Received prompts/update request for prompt ID: {prompt_id}"
                        )

                        prompt = update_prompt(prompt_id, params)
                        if prompt:
                            response = {
                                "jsonrpc": "2.0",
                                "id": data.get("id"),
                                "result": {
                                    "prompt": prompt,
                                    "method": "prompts/update",  # Include the method in the response
                                },
                            }
                        else:
                            response = {
                                "jsonrpc": "2.0",
                                "id": data.get("id"),
                                "error": {
                                    "code": -32602,
                                    "message": f"Prompt with ID '{prompt_id}' not found",
                                },
                            }

                        logger.info(f"Sending prompts/update response")
                        sys.stdout.write(json.dumps(response) + "\n")
                        sys.stdout.flush()
                        logger.info("Prompts/update response sent and flushed")
                        continue

                    elif method == "prompts/delete":
                        # Handle prompts/delete request
                        params = data.get("params", {})
                        prompt_id = params.get("id")
                        logger.info(
                            f"Received prompts/delete request for prompt ID: {prompt_id}"
                        )

                        success = delete_prompt(prompt_id)
                        if success:
                            response = {
                                "jsonrpc": "2.0",
                                "id": data.get("id"),
                                "result": {
                                    "success": True,
                                    "method": "prompts/delete",  # Include the method in the response
                                },
                            }
                        else:
                            response = {
                                "jsonrpc": "2.0",
                                "id": data.get("id"),
                                "error": {
                                    "code": -32602,
                                    "message": f"Prompt with ID '{prompt_id}' not found",
                                },
                            }

                        logger.info(f"Sending prompts/delete response")
                        sys.stdout.write(json.dumps(response) + "\n")
                        sys.stdout.flush()
                        logger.info("Prompts/delete response sent and flushed")
                        continue

                    elif method == "invoke":
                        # Handle tool invocation
                        params = data.get("params", {})
                        tool_name = params.get("name")
                        arguments = params.get("parameters", {})

                        logger.info(
                            f"Invoking tool: {tool_name} with arguments: {arguments}"
                        )

                        if tool_name in server.tools:
                            # Create a tool call
                            tool_call = ToolCall(
                                tool_name=tool_name, arguments=arguments
                            )

                            # Handle the tool call synchronously
                            import asyncio

                            loop = asyncio.new_event_loop()
                            asyncio.set_event_loop(loop)

                            try:
                                tool_response = loop.run_until_complete(
                                    server.tools[tool_name].handler(tool_call)
                                )
                                loop.close()

                                # Send response
                                response = {
                                    "jsonrpc": "2.0",
                                    "id": data.get("id"),
                                    "result": tool_response.result,
                                }

                                if tool_response.error:
                                    response = {
                                        "jsonrpc": "2.0",
                                        "id": data.get("id"),
                                        "error": {
                                            "code": -32000,
                                            "message": tool_response.error,
                                        },
                                    }

                                logger.info(
                                    f"Sending tool response: {json.dumps(response)}"
                                )
                                sys.stdout.write(json.dumps(response) + "\n")
                                sys.stdout.flush()
                                logger.info("Tool response sent and flushed")
                            except Exception as e:
                                logger.error(f"Error handling tool call: {e}")
                                response = {
                                    "jsonrpc": "2.0",
                                    "id": data.get("id"),
                                    "error": {"code": -32000, "message": str(e)},
                                }
                                sys.stdout.write(json.dumps(response) + "\n")
                                sys.stdout.flush()
                                logger.info("Error response sent and flushed")
                        else:
                            # Unknown tool
                            response = {
                                "jsonrpc": "2.0",
                                "id": data.get("id"),
                                "error": {
                                    "code": -32601,
                                    "message": f"Tool '{tool_name}' not found",
                                },
                            }

                            logger.info(f"Sending error response: unknown tool")
                            sys.stdout.write(json.dumps(response) + "\n")
                            sys.stdout.flush()
                            logger.info("Unknown tool error response sent and flushed")
                    elif method == "tools/list":
                        # Handle tools/list request
                        logger.info("Received tools/list request")

                        # Get the list of tools
                        tools = []
                        for tool in server.tools.values():
                            tools.append(
                                {
                                    "name": tool.name,
                                    "description": tool.description,
                                    "parameters": tool.parameters,
                                }
                            )

                        response = {
                            "jsonrpc": "2.0",
                            "id": data.get("id"),
                            "result": {
                                "tools": tools,
                                "method": "tools/list",  # Include the method in the response
                            },
                        }

                        logger.info(
                            f"Sending tools/list response with {len(tools)} tools"
                        )
                        sys.stdout.write(json.dumps(response) + "\n")
                        sys.stdout.flush()
                        logger.info("Tools/list response sent and flushed")
                        continue

                    elif method == "resources/list":
                        # Handle resources/list request
                        logger.info("Received resources/list request")

                        # Return an empty list of resources for now
                        response = {
                            "jsonrpc": "2.0",
                            "id": data.get("id"),
                            "result": {
                                "resources": [],
                                "method": "resources/list",  # Include the method in the response
                            },
                        }

                        logger.info("Sending resources/list response")
                        sys.stdout.write(json.dumps(response) + "\n")
                        sys.stdout.flush()
                        logger.info("Resources/list response sent and flushed")
                        continue

                    elif method == "notifications/initialized":
                        # Handle notifications/initialized request
                        logger.info("Received notifications/initialized request")

                        # This is a notification, so no response is needed
                        logger.info("Notification received, no response needed")
                        continue

                    elif method == "exit":
                        # Handle exit request
                        logger.info("Received exit request")
                        response = {
                            "jsonrpc": "2.0",
                            "id": data.get("id"),
                            "result": {"method": "exit"},
                        }
                        logger.info(f"Sending exit response: {json.dumps(response)}")
                        sys.stdout.write(json.dumps(response) + "\n")
                        sys.stdout.flush()
                        logger.info("Exit response sent and flushed")

                        # Don't actually exit, just acknowledge the exit
                        continue

                    else:
                        # Unknown method
                        logger.info(f"Unknown method: {method}")
                        response = {
                            "jsonrpc": "2.0",
                            "id": data.get("id"),
                            "error": {
                                "code": -32601,
                                "message": f"Method '{method}' not found",
                            },
                        }

                        logger.info(f"Sending error response: unknown method")
                        sys.stdout.write(json.dumps(response) + "\n")
                        sys.stdout.flush()
                        logger.info("Unknown method error response sent and flushed")
                except json.JSONDecodeError as e:
                    logger.error(f"Failed to parse JSON: {e}")
                    # Use a default ID of 0 if none is provided
                    response = {
                        "jsonrpc": "2.0",
                        "id": 0,  # Use a default ID instead of null
                        "error": {"code": -32700, "message": f"Parse error: {str(e)}"},
                    }
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
                    logger.info("JSON parse error response sent and flushed")
                except Exception as e:
                    logger.error(f"Error processing message: {e}")
                    import traceback

                    logger.error(traceback.format_exc())
                    # Use a default ID or the one from the request
                    response_id = 0
                    if "data" in locals() and data.get("id") is not None:
                        response_id = data.get("id")

                    response = {
                        "jsonrpc": "2.0",
                        "id": response_id,  # Use a default ID or the one from the request
                        "error": {
                            "code": -32603,
                            "message": f"Internal error: {str(e)}",
                        },
                    }
                    sys.stdout.write(json.dumps(response) + "\n")
                    sys.stdout.flush()
                    logger.info("Internal error response sent and flushed")
        else:
            # Unknown initialization method
            response = {
                "jsonrpc": "2.0",
                "id": init_data.get("id"),
                "error": {"code": -32601, "message": f"Method '{method}' not found"},
            }

            logger.info(f"Sending error response: unknown initialization method")
            sys.stdout.write(json.dumps(response) + "\n")
            sys.stdout.flush()
            logger.info("Unknown initialization method error response sent and flushed")
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse initialization JSON: {e}")
        response = {
            "jsonrpc": "2.0",
            "id": 0,  # Use a default ID instead of null
            "error": {"code": -32700, "message": f"Parse error: {str(e)}"},
        }
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()
        logger.info("JSON parse initialization error response sent and flushed")
    except Exception as e:
        logger.error(f"Error in MCP stdio handler: {e}")
        import traceback

        logger.error(traceback.format_exc())
        # Use a default ID or the one from the initialization request
        response_id = 0
        if "init_data" in locals() and init_data.get("id") is not None:
            response_id = init_data.get("id")

        response = {
            "jsonrpc": "2.0",
            "id": response_id,  # Use a default ID or the one from the request
            "error": {"code": -32603, "message": f"Internal error: {str(e)}"},
        }
        sys.stdout.write(json.dumps(response) + "\n")
        sys.stdout.flush()
        logger.info("Internal initialization error response sent and flushed")


if __name__ == "__main__":
    # Set up a keep-alive mechanism to prevent the process from exiting
    def keep_alive():
        """Keep the process alive by sleeping in a loop."""
        while True:
            time.sleep(10)

    # Start the keep-alive thread
    keep_alive_thread = threading.Thread(target=keep_alive, daemon=True)
    keep_alive_thread.start()
    logger.info("Started keep-alive thread")

    # Check if we're running in MCP mode
    mcp_config = os.environ.get("MCP_CONFIG", "")
    mcp_mode = os.environ.get("MCP_MODE", "")
    transport = os.environ.get("transport", "")

    # Print all environment variables for debugging
    logger.info("Environment variables:")
    for key, value in os.environ.items():
        if key.startswith("MCP") or key.startswith("PYTHON") or key in ["HOME", "PATH"]:
            logger.info(f"  {key}={value}")

    # More aggressive detection of MCP mode
    is_mcp_mode = (
        mcp_mode == "stdio"
        or "stdio" in mcp_mode
        or transport == "stdio"
        or "transport" in mcp_config
        or "stdio" in mcp_config
        or "--mcp" in " ".join(sys.argv)
        or any("mcp" in arg.lower() for arg in sys.argv)
    )

    try:
        if is_mcp_mode:
            logger.info("Running in MCP stdio mode")
            # Force stdout to be unbuffered
            sys.stdout.reconfigure(line_buffering=True)
            handle_mcp_stdio()
        else:
            logger.info("Running in HTTP server mode")
            main()
    except Exception as e:
        logger.error(f"Unhandled exception in main: {e}")
        import traceback

        logger.error(traceback.format_exc())

    # If we get here, keep the process alive
    logger.info("Main function completed, but keeping process alive")
    keep_alive_thread.join()
