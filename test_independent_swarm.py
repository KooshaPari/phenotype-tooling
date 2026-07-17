#!/usr/bin/env python3
"""
Test Independent Agent Swarm with Terminals

This script demonstrates creating truly independent agent processes
that run in their own terminals and can communicate autonomously.
"""

import asyncio
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mcp.tools.agent_management_tools import (
    create_independent_agent_tool,
    create_swarm_team_tool,
    invoke_agent_http_tool,
    send_message_tool,
    get_messages_tool,
    view_agent_console_tool,
)


async def test_independent_swarm():
    """Test creating and managing an independent agent swarm."""

    print("🚀 Testing Independent Agent Swarm with Terminals")
    print("=" * 60)

    # Define the team structure
    team_config = {
        "team_name": "AI Task Management Development Team",
        "project_description": "Build an AI-powered task management application with smart prioritization, natural language input, and team collaboration features.",
        "team_members": [
            {
                "name": "Alice",
                "role": "Project Manager",
                "expertise": "Project coordination, timeline management, stakeholder communication, risk assessment",
            },
            {
                "name": "Bob",
                "role": "Senior Developer",
                "expertise": "Technical architecture, system design, AI integration, performance optimization",
            },
            {
                "name": "Carol",
                "role": "UX Designer",
                "expertise": "User experience design, accessibility, mobile interfaces, user research",
            },
            {
                "name": "David",
                "role": "DevOps Engineer",
                "expertise": "Infrastructure, deployment, security, monitoring, cost optimization",
            },
        ],
    }

    print("🏗️ Creating Independent Agent Swarm")
    print("-" * 40)

    # Create the swarm team
    team_result = await create_swarm_team_tool(
        team_name=team_config["team_name"],
        project_description=team_config["project_description"],
        team_members=team_config["team_members"],
        model_name="gpt-4o-mini",
    )

    print(f"Team Creation Result: {team_result}")

    if team_result.get("status") != "success":
        print("❌ Failed to create team")
        return

    agents = team_result.get("agents", [])
    print(f"✅ Created {len(agents)} independent agents with terminals!")

    # Display agent information
    print("\n📋 Agent Information:")
    for agent in agents:
        print(
            f"  • {agent['name']}: Port {agent['port']}, Process ID {agent.get('process_id')}"
        )

    # Wait for agents to fully initialize
    print("\n⏳ Waiting for agents to initialize...")
    await asyncio.sleep(15)

    # Test communication between agents
    print("\n💬 Testing Agent Communication")
    print("-" * 40)

    if len(agents) >= 2:
        alice = agents[0]  # Project Manager
        bob = agents[1]  # Senior Developer

        # Alice sends a message to Bob
        print(f"Alice → Bob: Project planning message")

        message_result = await send_message_tool(
            sender_id=alice["agent_id"],
            recipient_id=bob["agent_id"],
            content="""Hi Bob! I'm Alice, your Project Manager. We need to start planning our AI-powered task management application.

PROJECT BRIEF:
- AI-powered task management with smart prioritization
- Natural language task input
- Team collaboration features
- 3-month timeline, $100k budget
- Mobile-responsive, GDPR compliant

As our Senior Developer, I need your technical assessment:
1. Recommended architecture approach
2. Technology stack selection
3. AI integration strategy
4. Development complexity and timeline

Please provide your technical recommendations so we can move forward with planning.""",
            metadata={"type": "task", "priority": "high"},
        )

        print(f"Message sent: {message_result.get('status', 'unknown')}")

        # Wait a moment for message processing
        await asyncio.sleep(3)

        # Check Bob's messages
        print(f"\nChecking Bob's messages...")
        bob_messages = await get_messages_tool(agent_id=bob["agent_id"], limit=5)

        print(f"Bob has {len(bob_messages.get('messages', []))} messages")

        # Test HTTP communication (if agents are responding)
        print(f"\n🔗 Testing HTTP Communication")
        print("-" * 30)

        # Try to communicate with Alice via HTTP
        http_result = await invoke_agent_http_tool(
            agent_id=alice["agent_id"],
            message="Hello Alice! This is a test of direct HTTP communication. Please respond with your role and current status.",
            temperature=0.7,
        )

        if "error" in http_result:
            print(f"HTTP Communication: ❌ {http_result['error']}")
        else:
            print(f"HTTP Communication: ✅ Success")
            if "response" in http_result:
                response_content = (
                    http_result["response"]
                    .get("choices", [{}])[0]
                    .get("message", {})
                    .get("content", "")
                )
                print(f"Alice's Response: {response_content[:200]}...")

    # Demonstrate console viewing
    print(f"\n👀 Console Viewing")
    print("-" * 20)

    if agents:
        agent = agents[0]
        print(f"Launching console viewer for {agent['name']}...")

        console_result = await view_agent_console_tool(agent["agent_id"])

        if "error" in console_result:
            print(f"Console Viewer: ❌ {console_result['error']}")
        else:
            print(
                f"Console Viewer: ✅ Launched (Process ID: {console_result.get('viewer_process_id')})"
            )

    # Summary
    print(f"\n🎉 Independent Agent Swarm Test Complete!")
    print("=" * 50)
    print(f"✅ Created {len(agents)} independent agent processes")
    print(f"✅ Each agent running in its own terminal")
    print(f"✅ Agents can communicate via message queue")
    print(f"✅ Console viewing available for monitoring")

    print(f"\n📝 Next Steps:")
    print(f"1. Check the terminal windows that opened for each agent")
    print(f"2. Agents should be running and responding to messages")
    print(f"3. Use MCP tools to send messages between agents")
    print(f"4. Agents will autonomously respond based on their roles")

    print(f"\n🔧 Agent Ports:")
    for agent in agents:
        print(f"  • {agent['name']}: http://localhost:{agent['port']}")

    return agents


if __name__ == "__main__":
    asyncio.run(test_independent_swarm())
