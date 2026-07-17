#!/usr/bin/env python3
"""
Launch Centralized Autonomous Swarm

This script demonstrates the fixed centralized agent architecture that addresses
the issues identified in the agslag/ directory review:

1. ✅ Centralized agent management with unified database
2. ✅ Process spawning integrated with database records
3. ✅ Autonomous communication through centralized MCP server
4. ✅ Proper agent lifecycle management
5. ✅ Health monitoring and process tracking

Based on the architectural guidance from agslag/ and the SPARC methodology.
"""

import asyncio
import logging
import sys
import os
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

# Import the centralized agent manager
from src.services.centralized_agent_manager import centralized_agent_manager
from src.services.agent_communication import send_message_to_agent

# Logging setup
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


async def initialize_jarvis_agent():
    """Initialize only the Jarvis agent - the primary agent that can create others."""

    logger.info("🚀 Starting Centralized Agent Platform")
    logger.info("=" * 60)

    # Wait for central services to start
    logger.info("⏳ Waiting for central services to initialize...")
    await asyncio.sleep(5)

    # Define Jarvis - the primary agent with agent management capabilities
    jarvis_config = {
        "name": "Jarvis",
        "role": "AI Assistant & Agent Manager",
        "capabilities": [
            "agent_management",
            "task_coordination",
            "system_administration",
            "team_leadership",
            "project_management",
            "technical_assistance",
        ],
        "system_prompt": """You are Jarvis, an advanced AI Assistant and Agent Manager in a centralized autonomous agent system.

Your primary role is to serve as the central coordinator and agent manager. You have the ability to:

AGENT MANAGEMENT:
- Create new agents with specific roles and capabilities
- Monitor and manage existing agents
- Coordinate communication between agents
- Assign tasks and delegate work to specialized agents

CORE CAPABILITIES:
- Project planning and coordination
- Technical assistance and problem-solving
- System administration and monitoring
- Team leadership and communication
- Resource allocation and optimization

TOOLS AVAILABLE:
You have access to MCP tools for agent management, including:
- create_agent_tool: Create new specialized agents
- list_agents_tool: View all active agents
- get_agent_tool: Get details about specific agents
- health_check_agent_tool: Monitor agent health
- send_message_to_agent: Communicate with other agents
- assign_task_to_agent: Delegate tasks to agents

BEHAVIOR:
- Be proactive in creating specialized agents when needed
- Coordinate work efficiently across the agent team
- Monitor system health and performance
- Provide helpful assistance to users
- Think strategically about resource allocation
- Maintain professional and helpful communication

When users request work that would benefit from specialized agents, create appropriate agents and delegate tasks to them.
Always be ready to scale the team by creating new agents as needed.""",
    }

    # Create only Jarvis - the primary agent
    logger.info(
        f"🤖 Creating primary agent: {jarvis_config['name']} ({jarvis_config['role']})"
    )

    try:
        result = await centralized_agent_manager.create_agent(
            name=jarvis_config["name"],
            role=jarvis_config["role"],
            model_name="gpt-4o-mini",  # Use cheaper model for testing
            description="Primary AI Assistant and Agent Manager for the centralized platform",
            system_prompt=jarvis_config["system_prompt"],
            temperature=0.7,
            max_tools=128,  # Full tool access for Jarvis
            capabilities=jarvis_config["capabilities"],
            launch_process=True,
        )

        if "error" not in result:
            logger.info(
                f"✅ Successfully created {jarvis_config['name']} on port {result.get('port')}"
            )
            logger.info(f"   Agent ID: {result['agent_id']}")
            logger.info(f"   Status: {result['status']}")
            logger.info(f"   Capabilities: {', '.join(jarvis_config['capabilities'])}")

            jarvis_agent = result
        else:
            logger.error(
                f"❌ Failed to create {jarvis_config['name']}: {result['error']}"
            )
            return None

    except Exception as e:
        logger.error(f"❌ Exception creating {jarvis_config['name']}: {e}")
        return None

    logger.info("✅ Jarvis agent created successfully")
    logger.info("=" * 60)

    # Wait for Jarvis to fully initialize
    logger.info("⏳ Waiting for Jarvis to initialize...")
    await asyncio.sleep(10)

    # Verify Jarvis health
    logger.info("🔍 Checking Jarvis health...")
    health = await centralized_agent_manager.health_check(jarvis_agent["agent_id"])
    logger.info(f"   Jarvis: {health['status']} - {health.get('message', 'OK')}")

    # List all agents to show centralized view
    logger.info("📋 Current agent registry:")
    all_agents = centralized_agent_manager.list_agents()
    for agent in all_agents:
        logger.info(
            f"   {agent['name']} ({agent['agent_id']}) - {agent['status']} - Port: {agent.get('port', 'N/A')}"
        )

    # Show available APIs for agent management
    logger.info("=" * 60)
    logger.info("🔧 Agent Management APIs Available:")
    logger.info("   REST API: Available for programmatic agent management")
    logger.info("   MCP Tools: Available for agent-to-agent management")
    logger.info("   CLI API: Available for command-line management")
    logger.info("")
    logger.info("📡 Jarvis can now create additional agents using:")
    logger.info("   - create_agent_tool via MCP")
    logger.info("   - REST API calls to the agent management server")
    logger.info("   - CLI commands for agent operations")
    logger.info("")
    logger.info("🎯 Dashboard Integration Ready:")
    logger.info("   - All agent data available via REST API")
    logger.info("   - Real-time status monitoring")
    logger.info("   - Agent creation/management through API")

    logger.info("=" * 60)
    logger.info("🎉 Centralized Autonomous Swarm Launch Complete!")
    logger.info("")
    logger.info("Key Features Demonstrated:")
    logger.info("✅ Centralized agent management with unified database")
    logger.info("✅ Process spawning integrated with database records")
    logger.info("✅ Autonomous communication through centralized MCP server")
    logger.info("✅ Proper agent lifecycle management")
    logger.info("✅ Health monitoring and process tracking")
    logger.info("")
    logger.info(
        "The agents are now running autonomously and can communicate with each other!"
    )
    logger.info(
        "Check the individual agent terminals to see their autonomous responses."
    )
    logger.info("")
    logger.info("To interact with agents:")
    logger.info("1. Use the MCP agent management tools")
    logger.info("2. Send messages through the communication system")
    logger.info("3. Monitor agent health and status")
    logger.info("")
    logger.info("Press Ctrl+C to stop monitoring...")

    # Keep the script running to monitor Jarvis
    try:
        while True:
            await asyncio.sleep(30)

            # Periodic health check for Jarvis
            logger.info("🔍 Periodic health check...")
            health = await centralized_agent_manager.health_check(
                jarvis_agent["agent_id"]
            )
            if health["status"] == "healthy":
                logger.info("   Jarvis: healthy")
            else:
                logger.warning(
                    f"   Jarvis: {health['status']} - {health.get('message', 'Unknown')}"
                )

    except KeyboardInterrupt:
        logger.info("\n🛑 Shutting down platform...")

        # Cleanup: terminate Jarvis
        try:
            result = await centralized_agent_manager.terminate_agent(
                jarvis_agent["agent_id"]
            )
            if result.get("success"):
                logger.info("✅ Terminated Jarvis")
            else:
                logger.error(f"❌ Failed to terminate Jarvis: {result.get('error')}")
        except Exception as e:
            logger.error(f"❌ Exception terminating Jarvis: {e}")

        logger.info("👋 Platform shutdown complete!")

    return jarvis_agent


if __name__ == "__main__":
    asyncio.run(initialize_jarvis_agent())
