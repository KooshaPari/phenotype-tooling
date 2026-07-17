#!/usr/bin/env python3
"""
Agent Management CLI

Command-line interface for managing agents in the centralized platform.
Provides automation-friendly commands for agent operations.
"""

import asyncio
import sys
import os
import json
import argparse
from pathlib import Path
from typing import Dict, List, Any, Optional

# Add the project root to the Python path
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))

from src.services.centralized_agent_manager import centralized_agent_manager
from src.services.agent_communication import send_message_to_agent

async def create_agent_cmd(args):
    """Create a new agent via CLI."""
    try:
        capabilities = []
        if args.capabilities:
            capabilities = [cap.strip() for cap in args.capabilities.split(",")]
        
        result = await centralized_agent_manager.create_agent(
            name=args.name,
            role=args.role,
            model_name=args.model,
            description=args.description,
            system_prompt=args.system_prompt,
            temperature=args.temperature,
            max_tools=args.max_tools,
            capabilities=capabilities,
            launch_process=args.launch_process
        )
        
        if "error" in result:
            print(f"❌ Error creating agent: {result['error']}")
            return 1
        
        print(f"✅ Agent created successfully:")
        print(f"   Name: {result['name']}")
        print(f"   ID: {result['agent_id']}")
        print(f"   Role: {result['role']}")
        print(f"   Port: {result.get('port', 'N/A')}")
        print(f"   Status: {result['status']}")
        
        if args.json:
            print(json.dumps(result, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"❌ Exception creating agent: {e}")
        return 1

async def list_agents_cmd(args):
    """List all agents via CLI."""
    try:
        agents = centralized_agent_manager.list_agents()
        
        if args.json:
            print(json.dumps(agents, indent=2))
            return 0
        
        print(f"📋 Agent Registry ({len(agents)} agents):")
        print("=" * 80)
        
        for agent in agents:
            status_emoji = {
                "running": "🟢",
                "healthy": "🟢", 
                "active": "🟢",
                "error": "🔴",
                "failed": "🔴",
                "terminated": "⚫",
                "inactive": "🟡"
            }.get(agent.get("status", "unknown"), "❓")
            
            print(f"{status_emoji} {agent['name']} ({agent.get('config', {}).get('role', 'Unknown Role')})")
            print(f"   ID: {agent['agent_id']}")
            print(f"   Status: {agent['status']}")
            print(f"   Port: {agent.get('port', 'N/A')}")
            if agent.get('runtime_status'):
                print(f"   Runtime: {agent['runtime_status']}")
            print()
        
        return 0
        
    except Exception as e:
        print(f"❌ Exception listing agents: {e}")
        return 1

async def get_agent_cmd(args):
    """Get details about a specific agent."""
    try:
        agent = await centralized_agent_manager.get_agent(args.agent_id)
        
        if agent is None:
            print(f"❌ Agent '{args.agent_id}' not found")
            return 1
        
        if args.json:
            print(json.dumps(agent, indent=2))
            return 0
        
        print(f"🤖 Agent Details: {agent['name']}")
        print("=" * 50)
        print(f"ID: {agent['agent_id']}")
        print(f"Name: {agent['name']}")
        print(f"Role: {agent.get('config', {}).get('role', 'Unknown')}")
        print(f"Model: {agent['model_name']}")
        print(f"Status: {agent['status']}")
        print(f"Port: {agent.get('port', 'N/A')}")
        print(f"URI: {agent.get('uri', 'N/A')}")
        
        if agent.get('runtime_status'):
            print(f"Runtime Status: {agent['runtime_status']}")
        if agent.get('capabilities'):
            print(f"Capabilities: {', '.join(agent['capabilities'])}")
        if agent.get('created_at'):
            print(f"Created: {agent['created_at']}")
        
        return 0
        
    except Exception as e:
        print(f"❌ Exception getting agent: {e}")
        return 1

async def health_check_cmd(args):
    """Check health of an agent."""
    try:
        health = await centralized_agent_manager.health_check(args.agent_id)
        
        if args.json:
            print(json.dumps(health, indent=2))
            return 0
        
        status_emoji = {
            "healthy": "🟢",
            "unresponsive": "🟡", 
            "dead": "🔴",
            "not_running": "⚫",
            "not_found": "❓",
            "error": "🔴"
        }.get(health.get("status", "unknown"), "❓")
        
        print(f"{status_emoji} Health Check: {health['status']}")
        print(f"Message: {health.get('message', 'No message')}")
        
        if health.get('pid'):
            print(f"PID: {health['pid']}")
        if health.get('uptime_seconds'):
            uptime_hours = health['uptime_seconds'] / 3600
            print(f"Uptime: {uptime_hours:.1f} hours")
        if health.get('last_heartbeat'):
            print(f"Last Heartbeat: {health['last_heartbeat']}")
        
        return 0 if health['status'] == 'healthy' else 1
        
    except Exception as e:
        print(f"❌ Exception checking health: {e}")
        return 1

async def terminate_agent_cmd(args):
    """Terminate an agent."""
    try:
        if not args.force:
            response = input(f"Are you sure you want to terminate agent '{args.agent_id}'? (y/N): ")
            if response.lower() != 'y':
                print("❌ Termination cancelled")
                return 1
        
        result = await centralized_agent_manager.terminate_agent(args.agent_id)
        
        if result.get("success"):
            print(f"✅ Agent '{args.agent_id}' terminated successfully")
            return 0
        else:
            print(f"❌ Failed to terminate agent: {result.get('error', 'Unknown error')}")
            return 1
        
    except Exception as e:
        print(f"❌ Exception terminating agent: {e}")
        return 1

async def send_message_cmd(args):
    """Send a message between agents."""
    try:
        result = await send_message_to_agent(
            sender_id=args.sender_id,
            recipient_id=args.recipient_id,
            content=args.content,
            message_type=args.message_type
        )
        
        print(f"✅ Message sent successfully")
        print(f"   Message ID: {result.get('message_id', 'N/A')}")
        print(f"   From: {args.sender_id}")
        print(f"   To: {args.recipient_id}")
        print(f"   Type: {args.message_type}")
        print(f"   Content: {args.content[:100]}{'...' if len(args.content) > 100 else ''}")
        
        if args.json:
            print(json.dumps(result, indent=2))
        
        return 0
        
    except Exception as e:
        print(f"❌ Exception sending message: {e}")
        return 1

def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(description="Agent Management CLI")
    parser.add_argument("--json", action="store_true", help="Output in JSON format")
    
    subparsers = parser.add_subparsers(dest="command", help="Available commands")
    
    # Create agent command
    create_parser = subparsers.add_parser("create", help="Create a new agent")
    create_parser.add_argument("name", help="Agent name")
    create_parser.add_argument("role", help="Agent role")
    create_parser.add_argument("--model", default="gpt-4o-mini", help="Model name")
    create_parser.add_argument("--description", help="Agent description")
    create_parser.add_argument("--system-prompt", help="System prompt")
    create_parser.add_argument("--temperature", type=float, default=0.7, help="Temperature")
    create_parser.add_argument("--max-tools", type=int, default=128, help="Max tools")
    create_parser.add_argument("--capabilities", help="Comma-separated capabilities")
    create_parser.add_argument("--no-launch", dest="launch_process", action="store_false", help="Don't launch process")
    
    # List agents command
    list_parser = subparsers.add_parser("list", help="List all agents")
    
    # Get agent command
    get_parser = subparsers.add_parser("get", help="Get agent details")
    get_parser.add_argument("agent_id", help="Agent ID")
    
    # Health check command
    health_parser = subparsers.add_parser("health", help="Check agent health")
    health_parser.add_argument("agent_id", help="Agent ID")
    
    # Terminate agent command
    terminate_parser = subparsers.add_parser("terminate", help="Terminate an agent")
    terminate_parser.add_argument("agent_id", help="Agent ID")
    terminate_parser.add_argument("--force", action="store_true", help="Force termination without confirmation")
    
    # Send message command
    message_parser = subparsers.add_parser("message", help="Send message between agents")
    message_parser.add_argument("sender_id", help="Sender agent ID")
    message_parser.add_argument("recipient_id", help="Recipient agent ID")
    message_parser.add_argument("content", help="Message content")
    message_parser.add_argument("--type", dest="message_type", default="text", help="Message type")
    
    args = parser.parse_args()
    
    if not args.command:
        parser.print_help()
        return 1
    
    # Command mapping
    commands = {
        "create": create_agent_cmd,
        "list": list_agents_cmd,
        "get": get_agent_cmd,
        "health": health_check_cmd,
        "terminate": terminate_agent_cmd,
        "message": send_message_cmd
    }
    
    if args.command in commands:
        return asyncio.run(commands[args.command](args))
    else:
        print(f"❌ Unknown command: {args.command}")
        return 1

if __name__ == "__main__":
    sys.exit(main())
