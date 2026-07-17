"""
Script to run an independent SWE Agent API server with custom configuration.
This script is used to launch agent processes with specific configurations.
"""

import argparse
import sys
import os
import atexit
import asyncio
import threading

# Add the current directory to the path to ensure imports work correctly
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Import and apply Pydantic patches
from src.utils.pydantic_compat import apply_pydantic_patches

apply_pydantic_patches()

# Import PTY manager to handle PTY device allocation
from src.utils.pty_manager import cleanup_all_ptys, get_active_pty_count

# Register PTY cleanup on exit
atexit.register(cleanup_all_ptys)

import uvicorn
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Import autonomous components
from src.autonomous.autonomous_agent import AutonomousAgent


def parse_args():
    """Parse command line arguments for agent configuration."""
    parser = argparse.ArgumentParser(
        description="Run an independent SWE Agent API server"
    )

    parser.add_argument(
        "--port", type=int, default=8006, help="Port to run the agent on"
    )
    parser.add_argument("--agent-id", required=True, help="Unique agent ID")
    parser.add_argument("--agent-name", required=True, help="Agent name")
    parser.add_argument("--model", required=True, help="Model name to use")
    parser.add_argument("--system-prompt", help="Custom system prompt")
    parser.add_argument(
        "--temperature", type=float, default=0.7, help="Temperature for generation"
    )
    parser.add_argument(
        "--max-tools", type=int, default=128, help="Maximum number of tools"
    )
    parser.add_argument("--description", help="Agent description")
    parser.add_argument(
        "--autonomous",
        action="store_true",
        help="Enable autonomous communication and collaboration",
    )
    parser.add_argument(
        "--check-interval",
        type=float,
        default=3.0,
        help="Message check interval for autonomous mode",
    )

    return parser.parse_args()


def setup_agent_environment(args):
    """Set up environment variables for the agent."""
    # Set API_MODE environment variable to disable TUI when running the API
    os.environ["API_MODE"] = "true"
    os.environ["TUI_ENABLED"] = "false"

    # Set agent-specific environment variables
    os.environ["AGENT_ID"] = args.agent_id
    os.environ["AGENT_NAME"] = args.agent_name
    os.environ["AGENT_MODEL"] = args.model
    os.environ["AGENT_TEMPERATURE"] = str(args.temperature)
    os.environ["AGENT_MAX_TOOLS"] = str(args.max_tools)
    os.environ["AGENT_PORT"] = str(args.port)

    if args.system_prompt:
        os.environ["AGENT_SYSTEM_PROMPT"] = args.system_prompt
    if args.description:
        os.environ["AGENT_DESCRIPTION"] = args.description


def start_autonomous_agent(args):
    """Start autonomous agent in background."""

    async def run_autonomous():
        autonomous_agent = AutonomousAgent(
            args.agent_id, args.agent_name, args.check_interval
        )
        await autonomous_agent.start()

    # Run autonomous agent in a separate thread
    def autonomous_thread():
        asyncio.run(run_autonomous())

    thread = threading.Thread(target=autonomous_thread, daemon=True)
    thread.start()
    return thread


def main():
    """Main entry point for the independent agent server."""
    args = parse_args()

    print(f"Python version: {sys.version}")
    print(f"Python executable: {sys.executable}")
    print(f"Starting independent SWE Agent: {args.agent_name} ({args.agent_id})")
    print(f"Port: {args.port}")
    print(f"Model: {args.model}")
    print(f"Autonomous mode: {args.autonomous}")
    print(f"Active PTY count at startup: {get_active_pty_count()}")

    # Set up agent environment
    setup_agent_environment(args)

    # Start autonomous agent if enabled
    autonomous_thread = None
    if args.autonomous:
        print("🤖 Starting autonomous communication and collaboration...")
        autonomous_thread = start_autonomous_agent(args)

    # Run the API server
    uvicorn.run(
        "src.api.main:app",
        host="0.0.0.0",
        port=args.port,
        reload=False,  # Disable reload for independent agents
        log_level="info",
    )


if __name__ == "__main__":
    main()
