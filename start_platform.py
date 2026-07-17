#!/usr/bin/env python3
"""
Start Centralized Agent Platform

This script starts the centralized agent platform with:
1. Only Jarvis agent (primary agent manager)
2. REST API server for dashboard integration
3. MCP tools for agent-to-agent management
4. CLI tools for automation

All other agents should be created programmatically through APIs.
"""

import asyncio
import subprocess
import sys
import os
import signal
import time
from pathlib import Path

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.centralized_agent_manager import centralized_agent_manager

def start_api_server():
    """Start the REST API server in a separate process."""
    print("🚀 Starting REST API server...")
    
    api_script = project_root / "agent_management_api.py"
    cmd = [sys.executable, str(api_script)]
    
    api_process = subprocess.Popen(
        cmd,
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE,
        cwd=str(project_root)
    )
    
    # Give it time to start
    time.sleep(3)
    
    if api_process.poll() is None:
        print(f"✅ REST API server started with PID: {api_process.pid}")
        print("📡 API available at: http://localhost:8000")
        print("📚 API docs at: http://localhost:8000/docs")
        return api_process
    else:
        print("❌ Failed to start REST API server")
        return None

async def initialize_jarvis():
    """Initialize only Jarvis - the primary agent manager."""
    print("🤖 Initializing Jarvis (Primary Agent Manager)...")
    
    jarvis_config = {
        "name": "Jarvis",
        "role": "AI Assistant & Agent Manager",
        "capabilities": [
            "agent_management",
            "task_coordination", 
            "system_administration",
            "team_leadership",
            "project_management",
            "technical_assistance"
        ],
        "system_prompt": """You are Jarvis, an advanced AI Assistant and Agent Manager in a centralized autonomous agent system.

Your primary role is to serve as the central coordinator and agent manager. You have the ability to:

AGENT MANAGEMENT:
- Create new agents with specific roles and capabilities using create_agent_tool
- Monitor and manage existing agents using list_agents_tool and get_agent_tool
- Check agent health using health_check_agent_tool
- Coordinate communication between agents using send_message_to_agent
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
Always be ready to scale the team by creating new agents as needed.

The platform also provides REST API and CLI tools for agent management that external systems can use."""
    }
    
    try:
        result = await centralized_agent_manager.create_agent(
            name=jarvis_config["name"],
            role=jarvis_config["role"],
            model_name="gpt-4o-mini",
            description="Primary AI Assistant and Agent Manager for the centralized platform",
            system_prompt=jarvis_config["system_prompt"],
            temperature=0.7,
            max_tools=128,
            capabilities=jarvis_config["capabilities"],
            launch_process=True
        )
        
        if "error" not in result:
            print(f"✅ Jarvis initialized successfully")
            print(f"   Agent ID: {result['agent_id']}")
            print(f"   Port: {result.get('port')}")
            print(f"   Status: {result['status']}")
            return result
        else:
            print(f"❌ Failed to initialize Jarvis: {result['error']}")
            return None
            
    except Exception as e:
        print(f"❌ Exception initializing Jarvis: {e}")
        return None

async def main():
    """Main startup function."""
    print("🚀 Starting Centralized Agent Platform")
    print("=" * 60)
    
    # Start API server first
    api_process = start_api_server()
    
    # Wait for central services to initialize
    print("⏳ Waiting for central services to initialize...")
    await asyncio.sleep(5)
    
    # Initialize Jarvis
    jarvis = await initialize_jarvis()
    if not jarvis:
        print("❌ Failed to initialize platform")
        if api_process:
            api_process.terminate()
        return 1
    
    print("=" * 60)
    print("🎉 Platform Initialization Complete!")
    print("")
    print("🤖 Jarvis is now active and ready to manage agents")
    print("")
    print("📡 Available Interfaces:")
    print("   REST API: http://localhost:8000")
    print("   API Docs: http://localhost:8000/docs")
    print("   CLI Tool: python agent_cli.py --help")
    print("   MCP Tools: Available to Jarvis and other agents")
    print("")
    print("🎯 Dashboard Integration:")
    print("   Connect your dashboard to: http://localhost:8000")
    print("   All agent data available via REST API")
    print("   Real-time status monitoring enabled")
    print("")
    print("🔧 Agent Management:")
    print("   Create agents: POST /agents")
    print("   List agents: GET /agents")
    print("   Agent details: GET /agents/{agent_id}")
    print("   Health checks: GET /agents/{agent_id}/health")
    print("   Send messages: POST /agents/message")
    print("   Assign tasks: POST /agents/task")
    print("")
    print("💡 Example CLI Commands:")
    print("   python agent_cli.py list")
    print("   python agent_cli.py create 'Alice' 'Project Manager'")
    print("   python agent_cli.py health <agent_id>")
    print("")
    print("Press Ctrl+C to shutdown the platform...")
    
    # Monitor the platform
    try:
        while True:
            await asyncio.sleep(30)
            
            # Check Jarvis health
            health = await centralized_agent_manager.health_check(jarvis["agent_id"])
            if health["status"] != "healthy":
                print(f"⚠️  Jarvis health warning: {health['status']} - {health.get('message')}")
            
            # Check API server
            if api_process and api_process.poll() is not None:
                print("⚠️  API server has stopped")
                break
                
    except KeyboardInterrupt:
        print("\n🛑 Shutting down platform...")
        
        # Terminate Jarvis
        try:
            result = await centralized_agent_manager.terminate_agent(jarvis["agent_id"])
            if result.get("success"):
                print("✅ Jarvis terminated")
            else:
                print(f"❌ Failed to terminate Jarvis: {result.get('error')}")
        except Exception as e:
            print(f"❌ Exception terminating Jarvis: {e}")
        
        # Terminate API server
        if api_process:
            try:
                api_process.terminate()
                api_process.wait(timeout=5)
                print("✅ API server terminated")
            except subprocess.TimeoutExpired:
                api_process.kill()
                print("🔨 API server force killed")
            except Exception as e:
                print(f"❌ Exception terminating API server: {e}")
        
        print("👋 Platform shutdown complete!")
        return 0

if __name__ == "__main__":
    try:
        exit_code = asyncio.run(main())
        sys.exit(exit_code)
    except Exception as e:
        print(f"❌ Fatal error: {e}")
        sys.exit(1)
