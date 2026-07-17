#!/usr/bin/env python3
"""
Script to run the agent management MCP server.
"""

import asyncio
import os
import sys
import argparse

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.mcp.servers.agent_management_server import AgentManagementServer
from src.utils.logging import logger


def main():
    """Main entry point for the script."""
    # Parse command-line arguments
    parser = argparse.ArgumentParser(description="Agent Management MCP Server")
    parser.add_argument("--host", default="localhost", help="Host to bind to")
    parser.add_argument("--port", type=int, default=8080, help="Port to bind to")
    parser.add_argument(
        "--async", dest="async_mode", action="store_true", help="Run in async mode"
    )

    args = parser.parse_args()

    # Create the server
    server = AgentManagementServer(host=args.host, port=args.port)

    try:
        if args.async_mode:
            # Run in async mode
            asyncio.run(async_main(server))
        else:
            # Run in sync mode
            logger.info(
                f"Starting agent management MCP server on {args.host}:{args.port}"
            )
            server.start_sync()
    except KeyboardInterrupt:
        # Stop the server on keyboard interrupt
        logger.info("Keyboard interrupt received, stopping server...")
    except Exception as e:
        logger.error(f"Error running agent management MCP server: {e}")


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
        logger.error(f"Error running agent management MCP server: {e}")
        await server.stop()


if __name__ == "__main__":
    main()
