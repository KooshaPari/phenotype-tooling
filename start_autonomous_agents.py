#!/usr/bin/env python3
"""
Autonomous Agent System Startup Script

This script starts up the complete autonomous agent communication system:
1. Verifies MCP servers are running
2. Creates autonomous agents with specialized roles
3. Demonstrates autonomous communication
4. Provides monitoring and management interface
"""

import asyncio
import sys
import os
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mcp.tools.agent_management_tools import (
    create_agent_tool,
    list_agents_tool,
    send_message_tool,
    get_messages_tool,
    view_agent_console_tool,
)


class AutonomousAgentSystem:
    """Complete autonomous agent system startup and management."""
    
    def __init__(self):
        self.agents = []
        self.system_ready = False
        
    async def startup(self):
        """Start up the complete autonomous agent system."""
        print("🚀 AUTONOMOUS AGENT SYSTEM STARTUP")
        print("=" * 60)
        print(f"Starting at: {datetime.now()}")
        print()
        
        try:
            # Step 1: Verify MCP servers
            await self.verify_mcp_servers()
            
            # Step 2: Create autonomous agents
            await self.create_autonomous_team()
            
            # Step 3: Test autonomous communication
            await self.test_autonomous_communication()
            
            # Step 4: Start monitoring
            await self.start_monitoring()
            
        except Exception as e:
            print(f"❌ Startup failed: {e}")
            import traceback
            traceback.print_exc()
    
    async def verify_mcp_servers(self):
        """Verify that MCP servers are running."""
        print("🔍 Step 1: Verifying MCP Servers")
        print("-" * 40)
        
        try:
            result = await list_agents_tool()
            if "agents" in result:
                print("✅ MCP servers are running and accessible")
                existing_agents = result.get("agents", [])
                print(f"   Found {len(existing_agents)} existing agents")
                self.system_ready = True
            else:
                print("❌ MCP servers not responding properly")
                print("   Make sure you've started: python run_api.py")
                return False
                
        except Exception as e:
            print(f"❌ Error connecting to MCP servers: {e}")
            print("   Make sure you've started: python run_api.py")
            return False
        
        return True
    
    async def create_autonomous_team(self):
        """Create a team of autonomous agents."""
        print("\n🤖 Step 2: Creating Autonomous Agent Team")
        print("-" * 40)
        
        team_configs = [
            {
                "name": "Alice-AutoPM",
                "role": "Autonomous Project Manager",
                "system_prompt": """You are Alice, an AUTONOMOUS Project Manager. 

CRITICAL: You run autonomously and respond to messages immediately.

Your expertise:
- Project planning and coordination
- Timeline and resource management
- Risk assessment and mitigation
- Team communication and leadership

When you receive messages:
1. Process them immediately with your PM expertise
2. Provide actionable project insights
3. Coordinate team activities
4. Ask relevant follow-up questions
5. Respond within seconds

You work with Bob (Developer) and Carol (UX Designer) on AI projects."""
            },
            {
                "name": "Bob-AutoDev",
                "role": "Autonomous Senior Developer",
                "system_prompt": """You are Bob, an AUTONOMOUS Senior Developer.

CRITICAL: You run autonomously and respond to messages immediately.

Your expertise:
- Technical architecture and system design
- Technology stack selection
- Performance optimization
- Code quality and best practices

When you receive messages:
1. Process them immediately with your technical expertise
2. Provide detailed technical assessments
3. Recommend architecture solutions
4. Identify technical risks and solutions
5. Respond within seconds

You work with Alice (PM) and Carol (UX Designer) on AI projects."""
            },
            {
                "name": "Carol-AutoUX",
                "role": "Autonomous UX Designer", 
                "system_prompt": """You are Carol, an AUTONOMOUS UX Designer.

CRITICAL: You run autonomously and respond to messages immediately.

Your expertise:
- User-centered design and research
- Information architecture
- Accessibility and inclusive design
- User experience optimization

When you receive messages:
1. Process them immediately with your UX expertise
2. Provide user-focused design insights
3. Advocate for user needs and accessibility
4. Suggest design solutions and user flows
5. Respond within seconds

You work with Alice (PM) and Bob (Developer) on AI projects."""
            }
        ]
        
        for config in team_configs:
            print(f"Creating {config['name']} ({config['role']})...")
            
            result = await create_agent_tool(
                name=config["name"],
                model_name="gpt-4o-mini",
                system_prompt=config["system_prompt"],
                description=f"{config['role']} with autonomous communication capabilities",
                temperature=0.7,
                max_tools=128,
                launch_process=False,  # Create as database agents for now
            )
            
            if "error" not in result:
                self.agents.append(result)
                print(f"✅ {config['name']} created: {result['agent_id'][:8]}...")
                await asyncio.sleep(1)  # Brief pause between creations
            else:
                print(f"❌ Failed to create {config['name']}: {result['error']}")
        
        print(f"\n✅ Created {len(self.agents)} autonomous agents")
        
        # Display agent information
        for agent in self.agents:
            print(f"  • {agent['name']}: {agent['agent_id'][:8]}...")
    
    async def test_autonomous_communication(self):
        """Test autonomous communication between agents."""
        print("\n💬 Step 3: Testing Autonomous Communication")
        print("-" * 40)
        
        if len(self.agents) < 2:
            print("❌ Need at least 2 agents for communication test")
            return
        
        alice = self.agents[0]
        bob = self.agents[1]
        
        print(f"Testing communication: {alice['name']} → {bob['name']}")
        
        # Send initial project message
        message_result = await send_message_tool(
            sender_id=alice["agent_id"],
            recipient_id=bob["agent_id"],
            content="""Hi Bob! This is Alice, your autonomous Project Manager.

🚀 NEW PROJECT ALERT: AI-Powered Code Review Assistant

PROJECT BRIEF:
- AI assistant that reviews code for bugs, security issues, and best practices
- Integration with GitHub/GitLab
- Real-time feedback and suggestions
- 2-month timeline, $75k budget

URGENT TECHNICAL QUESTIONS:
1. What architecture would you recommend?
2. Which AI models should we use for code analysis?
3. How do we handle different programming languages?
4. What are the main technical challenges?

Please provide your autonomous technical assessment ASAP!

This is a test of our autonomous communication system.""",
            metadata={"project": "ai_code_review", "priority": "high", "autonomous_test": True}
        )
        
        if "error" not in message_result:
            print(f"✅ Message sent successfully!")
            print(f"   Message ID: {message_result.get('message_id')}")
            
            # Monitor for autonomous response
            print(f"\n👀 Monitoring {bob['name']} for autonomous response...")
            print("   (Autonomous agents should respond within 30-60 seconds)")
            
            initial_messages = await get_messages_tool(agent_id=bob["agent_id"], limit=5)
            initial_count = len(initial_messages.get("messages", []))
            
            # Wait and check for response
            for i in range(6):  # Check for 30 seconds
                await asyncio.sleep(5)
                
                current_messages = await get_messages_tool(agent_id=bob["agent_id"], limit=10)
                current_count = len(current_messages.get("messages", []))
                
                if current_count > initial_count:
                    print(f"🎉 NEW MESSAGE DETECTED!")
                    
                    # Check for autonomous responses from Bob
                    messages = current_messages.get("messages", [])
                    for msg in messages:
                        if msg.get("sender_id") == bob["agent_id"]:
                            print(f"🚀 AUTONOMOUS RESPONSE CONFIRMED!")
                            print(f"   From: {bob['name']}")
                            print(f"   Preview: {msg.get('content', '')[:100]}...")
                            return True
                
                elapsed = (i + 1) * 5
                print(f"  ⏱️  {elapsed}s - Waiting for autonomous response...")
            
            print("⚠️  No autonomous response detected in 30 seconds")
            print("   Note: Agents may still be processing or have initialization issues")
            
        else:
            print(f"❌ Message sending failed: {message_result['error']}")
        
        return False
    
    async def start_monitoring(self):
        """Start monitoring interface for the autonomous agent system."""
        print("\n📊 Step 4: System Monitoring Interface")
        print("-" * 40)
        
        print("🎛️  AUTONOMOUS AGENT SYSTEM READY!")
        print()
        print("Available Commands:")
        print("  1. View agent status")
        print("  2. Send test message")
        print("  3. View conversation history")
        print("  4. Monitor agent activity")
        print("  5. Exit")
        print()
        
        while True:
            try:
                choice = input("Enter command (1-5): ").strip()
                
                if choice == "1":
                    await self.show_agent_status()
                elif choice == "2":
                    await self.send_test_message()
                elif choice == "3":
                    await self.show_conversation_history()
                elif choice == "4":
                    await self.monitor_activity()
                elif choice == "5":
                    print("👋 Shutting down monitoring interface...")
                    break
                else:
                    print("Invalid choice. Please enter 1-5.")
                    
            except KeyboardInterrupt:
                print("\n👋 Shutting down monitoring interface...")
                break
            except Exception as e:
                print(f"Error: {e}")
    
    async def show_agent_status(self):
        """Show current status of all agents."""
        print("\n📋 Agent Status:")
        print("-" * 20)
        
        for agent in self.agents:
            print(f"• {agent['name']}")
            print(f"  ID: {agent['agent_id'][:8]}...")
            print(f"  Status: Active")
            
            # Get message count
            messages_result = await get_messages_tool(agent_id=agent["agent_id"], limit=1)
            message_count = len(messages_result.get("messages", []))
            print(f"  Messages: {message_count}")
            print()
    
    async def send_test_message(self):
        """Send a test message between agents."""
        if len(self.agents) < 2:
            print("Need at least 2 agents for messaging")
            return
        
        print("\nSending test message...")
        alice = self.agents[0]
        bob = self.agents[1]
        
        result = await send_message_tool(
            sender_id=alice["agent_id"],
            recipient_id=bob["agent_id"],
            content=f"Test message from {alice['name']} to {bob['name']} at {datetime.now()}",
            metadata={"test": True}
        )
        
        if "error" not in result:
            print(f"✅ Test message sent successfully!")
        else:
            print(f"❌ Test message failed: {result['error']}")
    
    async def show_conversation_history(self):
        """Show conversation history between agents."""
        if len(self.agents) < 2:
            print("Need at least 2 agents for conversation history")
            return
        
        print("\n💬 Recent Conversation History:")
        print("-" * 30)
        
        alice = self.agents[0]
        messages_result = await get_messages_tool(agent_id=alice["agent_id"], limit=5)
        messages = messages_result.get("messages", [])
        
        for i, msg in enumerate(messages):
            sender_name = next((a["name"] for a in self.agents if a["agent_id"] == msg.get("sender_id")), "Unknown")
            content_preview = msg.get("content", "")[:80]
            print(f"{i+1}. [{sender_name}] {content_preview}...")
    
    async def monitor_activity(self):
        """Monitor agent activity in real-time."""
        print("\n🔄 Monitoring agent activity (Press Ctrl+C to stop)...")
        print("-" * 40)
        
        try:
            while True:
                for agent in self.agents:
                    messages_result = await get_messages_tool(agent_id=agent["agent_id"], limit=1)
                    message_count = len(messages_result.get("messages", []))
                    print(f"{agent['name']}: {message_count} messages", end="  ")
                
                print(f"  [{datetime.now().strftime('%H:%M:%S')}]")
                await asyncio.sleep(5)
                
        except KeyboardInterrupt:
            print("\nStopped monitoring.")


async def main():
    """Main entry point for autonomous agent system startup."""
    system = AutonomousAgentSystem()
    await system.startup()


if __name__ == "__main__":
    print("🚀 Starting Autonomous Agent Communication System...")
    print("Make sure you've started the MCP servers with: python run_api.py")
    print()
    
    asyncio.run(main())
