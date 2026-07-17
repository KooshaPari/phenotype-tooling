#!/usr/bin/env python3
"""
Launch Autonomous Agent Swarm

This script launches multiple autonomous agents that can communicate independently.
Each agent runs in its own process and can think/respond autonomously.
"""

import asyncio
import subprocess
import sys
import os
import time
import signal
from typing import List, Dict

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mcp.tools.agent_management_tools import (
    create_agent_tool,
    send_message_tool,
    list_agents_tool,
)
from src.utils.logging import logger


class AutonomousSwarmLauncher:
    """Launches and manages a swarm of autonomous agents."""
    
    def __init__(self):
        self.agent_processes: Dict[str, subprocess.Popen] = {}
        self.agent_info: List[Dict] = []
        
    async def create_agents(self):
        """Create the agent team."""
        agents_config = [
            {
                "name": "Alice-Autonomous",
                "role": "Project Manager",
                "system_prompt": """You are Alice, an autonomous Project Manager. You excel at:
- Breaking down complex projects into manageable tasks
- Coordinating team members and timelines
- Risk assessment and mitigation planning
- Resource allocation and budget planning
- Stakeholder communication

You are part of a team working on an AI-powered task management application. Your team members are:
- Bob (Senior Developer) - Technical architecture and implementation
- Carol (UX Designer) - User experience and design

You can communicate with team members using MCP tools. When you receive messages, respond thoughtfully and autonomously based on your project management expertise. Always focus on coordination, planning, and ensuring project success.

IMPORTANT: You are running autonomously. When you receive messages, you should respond immediately with your own thoughts and insights."""
            },
            {
                "name": "Bob-Autonomous", 
                "role": "Senior Developer",
                "system_prompt": """You are Bob, an autonomous Senior Software Developer with 10+ years of experience. You excel at:
- Technical architecture and system design
- Code quality and best practices
- Technology stack selection and evaluation
- Performance optimization and scalability
- Mentoring junior developers

You are part of a team working on an AI-powered task management application. Your team members are:
- Alice (Project Manager) - Project coordination and planning
- Carol (UX Designer) - User experience and design

You can communicate with team members using MCP tools. When you receive messages, respond thoughtfully and autonomously based on your technical expertise. Always focus on technical excellence, maintainability, and scalable solutions.

IMPORTANT: You are running autonomously. When you receive messages, you should respond immediately with your own technical insights and recommendations."""
            },
            {
                "name": "Carol-Autonomous",
                "role": "UX Designer", 
                "system_prompt": """You are Carol, an autonomous UX Designer passionate about user-centered design. You excel at:
- User research and persona development
- Information architecture and user flows
- Wireframing and prototyping
- Usability testing and iteration
- Accessibility and inclusive design

You are part of a team working on an AI-powered task management application. Your team members are:
- Alice (Project Manager) - Project coordination and planning
- Bob (Senior Developer) - Technical architecture and implementation

You can communicate with team members using MCP tools. When you receive messages, respond thoughtfully and autonomously based on your UX expertise. Always advocate for the end user and focus on creating intuitive, accessible experiences.

IMPORTANT: You are running autonomously. When you receive messages, you should respond immediately with your own UX insights and design recommendations."""
            }
        ]
        
        print("🤖 Creating Autonomous Agents...")
        
        for config in agents_config:
            print(f"Creating {config['name']} ({config['role']})...")
            
            result = await create_agent_tool(
                name=config["name"],
                model_name="gpt-4o-mini",
                system_prompt=config["system_prompt"],
                description=f"Autonomous {config['role']} for AI task management project",
                temperature=0.7,
                max_tools=128,
                launch_process=False,  # We'll launch our own autonomous processes
            )
            
            if "error" not in result:
                self.agent_info.append(result)
                print(f"✅ Created {config['name']}: {result['agent_id']}")
                await asyncio.sleep(1)  # Brief pause between creations
            else:
                print(f"❌ Failed to create {config['name']}: {result['error']}")
        
        print(f"✅ Created {len(self.agent_info)} autonomous agents")
        return self.agent_info
    
    def launch_autonomous_processes(self):
        """Launch autonomous agent processes."""
        print("\n🚀 Launching Autonomous Agent Processes...")
        
        for agent in self.agent_info:
            agent_id = agent["agent_id"]
            agent_name = agent["name"]
            
            print(f"Launching autonomous process for {agent_name}...")
            
            # Launch the autonomous agent runner
            cmd = [
                sys.executable,
                "autonomous_agent_runner.py",
                "--agent-id", agent_id,
                "--check-interval", "3"  # Check for messages every 3 seconds
            ]
            
            try:
                process = subprocess.Popen(
                    cmd,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    cwd=os.path.dirname(os.path.abspath(__file__))
                )
                
                self.agent_processes[agent_id] = process
                print(f"✅ Launched {agent_name} (PID: {process.pid})")
                
            except Exception as e:
                print(f"❌ Failed to launch {agent_name}: {e}")
        
        print(f"✅ Launched {len(self.agent_processes)} autonomous agent processes")
    
    async def test_autonomous_communication(self):
        """Test autonomous communication between agents."""
        if len(self.agent_info) < 2:
            print("❌ Need at least 2 agents for communication test")
            return
        
        print("\n💬 Testing Autonomous Communication...")
        
        # Wait for agents to fully initialize
        print("⏳ Waiting for agents to initialize...")
        await asyncio.sleep(10)
        
        alice = self.agent_info[0]
        bob = self.agent_info[1]
        
        print(f"Sending initial message from {alice['name']} to {bob['name']}...")
        
        # Send initial message to trigger autonomous conversation
        result = await send_message_tool(
            sender_id=alice["agent_id"],
            recipient_id=bob["agent_id"],
            content="""Hi Bob! I'm Alice, your Project Manager. I'm starting our AI-powered task management application project.

PROJECT BRIEF:
- AI-powered task management with smart prioritization
- Natural language task input
- Team collaboration features
- 3-month timeline, $100k budget
- Mobile-responsive, GDPR compliant

As our Senior Developer, I need your technical assessment:
1. What architecture approach would you recommend?
2. What technology stack should we use?
3. How should we integrate AI capabilities?
4. What are the main technical risks?

Please provide your autonomous technical recommendations!""",
            metadata={"type": "project_initiation", "autonomous_test": True}
        )
        
        if "error" in result:
            print(f"❌ Error sending message: {result['error']}")
        else:
            print(f"✅ Initial message sent! Bob should respond autonomously...")
            
            # Wait and monitor for autonomous responses
            print("\n👀 Monitoring for autonomous responses...")
            print("(The agents should now communicate autonomously)")
            print("Press Ctrl+C to stop monitoring...")
            
            try:
                # Monitor for a while to see autonomous communication
                for i in range(60):  # Monitor for 5 minutes
                    await asyncio.sleep(5)
                    if i % 6 == 0:  # Print status every 30 seconds
                        print(f"⏱️  Monitoring autonomous communication... ({i*5}s elapsed)")
                        
            except KeyboardInterrupt:
                print("\n⏹️  Stopping monitoring...")
    
    def cleanup(self):
        """Clean up agent processes."""
        print("\n🧹 Cleaning up agent processes...")
        
        for agent_id, process in self.agent_processes.items():
            try:
                print(f"Stopping process {process.pid}...")
                process.terminate()
                
                # Wait for graceful shutdown
                try:
                    process.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    print(f"Force killing process {process.pid}...")
                    process.kill()
                    
            except Exception as e:
                print(f"Error stopping process: {e}")
        
        print("✅ Cleanup complete")
    
    async def run(self):
        """Run the autonomous swarm demonstration."""
        try:
            print("🚀 Autonomous Agent Swarm Demonstration")
            print("=" * 50)
            
            # Create agents
            await self.create_agents()
            
            if not self.agent_info:
                print("❌ No agents created, exiting...")
                return
            
            # Launch autonomous processes
            self.launch_autonomous_processes()
            
            if not self.agent_processes:
                print("❌ No autonomous processes launched, exiting...")
                return
            
            # Test autonomous communication
            await self.test_autonomous_communication()
            
        except KeyboardInterrupt:
            print("\n⏹️  Interrupted by user")
        except Exception as e:
            print(f"❌ Error: {e}")
        finally:
            self.cleanup()


async def main():
    """Main entry point."""
    launcher = AutonomousSwarmLauncher()
    await launcher.run()


if __name__ == "__main__":
    asyncio.run(main())
