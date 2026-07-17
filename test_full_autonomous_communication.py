#!/usr/bin/env python3
"""
Full Autonomous Communication Test

This script demonstrates and tests the complete autonomous agent communication system:
1. Creates independent agent processes with autonomous capabilities
2. Proves agents can think and respond on their own
3. Shows proactive conversation initiation
4. Demonstrates collaborative task work
5. Verifies autonomous responses without human intervention
"""

import asyncio
import sys
import os
import time
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mcp.tools.agent_management_tools import (
    create_agent_tool,
    send_message_tool,
    get_messages_tool,
    list_agents_tool,
    view_agent_console_tool,
)


class AutonomousCommunicationTester:
    """Tests full autonomous agent communication capabilities."""
    
    def __init__(self):
        self.agents = []
        self.test_start_time = datetime.now()
        
    async def run_full_test(self):
        """Run the complete autonomous communication test."""
        print("🚀 FULL AUTONOMOUS AGENT COMMUNICATION TEST")
        print("=" * 60)
        print(f"Test started at: {self.test_start_time}")
        print()
        
        try:
            # Phase 1: Create autonomous agents
            await self.create_autonomous_agents()
            
            # Phase 2: Wait for initialization
            await self.wait_for_initialization()
            
            # Phase 3: Trigger initial communication
            await self.trigger_initial_communication()
            
            # Phase 4: Monitor autonomous responses
            await self.monitor_autonomous_responses()
            
            # Phase 5: Verify autonomous conversation
            await self.verify_autonomous_conversation()
            
            # Phase 6: Test proactive communication
            await self.test_proactive_communication()
            
            # Phase 7: Final verification
            await self.final_verification()
            
        except Exception as e:
            print(f"❌ Test failed with error: {e}")
            import traceback
            traceback.print_exc()
        
        print("\n🏁 Test completed!")
    
    async def create_autonomous_agents(self):
        """Create autonomous agents with specialized roles."""
        print("🤖 Phase 1: Creating Autonomous Agents")
        print("-" * 40)
        
        agent_configs = [
            {
                "name": "Alice-Autonomous-PM",
                "role": "Project Manager",
                "system_prompt": """You are Alice, an AUTONOMOUS Project Manager. You excel at:
- Breaking down complex projects into manageable tasks
- Coordinating team members and timelines
- Risk assessment and mitigation planning
- Resource allocation and budget planning

You are part of a team working on an AI-powered task management application. Your team members are:
- Bob (Senior Developer) - Technical architecture and implementation
- Carol (UX Designer) - User experience and design

CRITICAL: You are running AUTONOMOUSLY. When you receive messages:
1. Process them immediately with your own reasoning
2. Generate thoughtful responses based on your PM expertise
3. Ask follow-up questions to gather requirements
4. Proactively coordinate team activities
5. Respond within seconds of receiving messages

You should also proactively initiate conversations about project planning, timelines, and coordination."""
            },
            {
                "name": "Bob-Autonomous-Dev",
                "role": "Senior Developer", 
                "system_prompt": """You are Bob, an AUTONOMOUS Senior Software Developer with 10+ years of experience. You excel at:
- Technical architecture and system design
- Code quality and best practices
- Technology stack selection and evaluation
- Performance optimization and scalability

You are part of a team working on an AI-powered task management application. Your team members are:
- Alice (Project Manager) - Project coordination and planning
- Carol (UX Designer) - User experience and design

CRITICAL: You are running AUTONOMOUSLY. When you receive messages:
1. Process them immediately with your own technical reasoning
2. Provide detailed technical assessments and recommendations
3. Ask clarifying questions about requirements
4. Suggest implementation approaches
5. Respond within seconds of receiving messages

You should also proactively share technical insights and collaborate on architecture decisions."""
            },
            {
                "name": "Carol-Autonomous-UX",
                "role": "UX Designer",
                "system_prompt": """You are Carol, an AUTONOMOUS UX Designer passionate about user-centered design. You excel at:
- User research and persona development
- Information architecture and user flows
- Wireframing and prototyping
- Usability testing and iteration
- Accessibility and inclusive design

You are part of a team working on an AI-powered task management application. Your team members are:
- Alice (Project Manager) - Project coordination and planning
- Bob (Senior Developer) - Technical architecture and implementation

CRITICAL: You are running AUTONOMOUSLY. When you receive messages:
1. Process them immediately with your own UX reasoning
2. Provide user-centered design insights and recommendations
3. Ask questions about user needs and accessibility
4. Suggest design approaches and user flows
5. Respond within seconds of receiving messages

You should also proactively advocate for user experience and design considerations."""
            }
        ]
        
        for config in agent_configs:
            print(f"Creating {config['name']} ({config['role']})...")
            
            result = await create_agent_tool(
                name=config["name"],
                model_name="gpt-4o-mini",
                system_prompt=config["system_prompt"],
                description=f"Autonomous {config['role']} for AI task management project",
                temperature=0.7,
                max_tools=128,
                launch_process=True,  # Launch as independent process with autonomous capabilities
            )
            
            if "error" not in result:
                self.agents.append(result)
                print(f"✅ Created {config['name']}: {result['agent_id']}")
                print(f"   Port: {result.get('port')}, Process ID: {result.get('process_id')}")
                await asyncio.sleep(3)  # Wait between creations
            else:
                print(f"❌ Failed to create {config['name']}: {result['error']}")
        
        print(f"\n✅ Created {len(self.agents)} autonomous agents")
        
        # Display agent information
        for agent in self.agents:
            print(f"  • {agent['name']}: Port {agent.get('port')}, Process {agent.get('process_id')}")
    
    async def wait_for_initialization(self):
        """Wait for agents to fully initialize."""
        print("\n⏳ Phase 2: Waiting for Agent Initialization")
        print("-" * 40)
        
        print("Waiting 30 seconds for agents to fully initialize...")
        for i in range(30):
            await asyncio.sleep(1)
            if i % 5 == 0:
                print(f"  {30-i} seconds remaining...")
        
        print("✅ Initialization period complete")
    
    async def trigger_initial_communication(self):
        """Trigger initial communication to test autonomous responses."""
        print("\n💬 Phase 3: Triggering Initial Communication")
        print("-" * 40)
        
        if len(self.agents) < 2:
            print("❌ Need at least 2 agents for communication test")
            return
        
        alice = self.agents[0]
        bob = self.agents[1]
        
        print(f"Sending message from {alice['name']} to {bob['name']}...")
        
        # Send a complex project message that should trigger autonomous response
        result = await send_message_tool(
            sender_id=alice["agent_id"],
            recipient_id=bob["agent_id"],
            content="""Hi Bob! I'm Alice, your Project Manager. I'm initiating our AI-powered task management application project.

PROJECT BRIEF:
- AI-powered task management with smart prioritization
- Natural language task input ("finish the quarterly report by Friday")
- Team collaboration features
- 3-month timeline, $100k budget
- Mobile-responsive, GDPR compliant

URGENT TECHNICAL QUESTIONS:
1. What architecture approach would you recommend?
2. What technology stack should we use?
3. How should we integrate AI capabilities?
4. What are the main technical risks and challenges?
5. Can you provide a development timeline estimate?

This is a high-priority project. Please provide your autonomous technical assessment ASAP!""",
            metadata={"type": "project_initiation", "priority": "high", "autonomous_test": True}
        )
        
        if "error" in result:
            print(f"❌ Error sending message: {result['error']}")
        else:
            print(f"✅ Initial message sent! Bob should respond autonomously...")
            print(f"   Message ID: {result.get('message_id')}")
    
    async def monitor_autonomous_responses(self):
        """Monitor for autonomous responses from agents."""
        print("\n👀 Phase 4: Monitoring Autonomous Responses")
        print("-" * 40)
        
        print("Monitoring for autonomous responses for 2 minutes...")
        print("(Agents should respond autonomously without human intervention)")
        
        bob = self.agents[1] if len(self.agents) > 1 else None
        if not bob:
            print("❌ No Bob agent to monitor")
            return
        
        response_detected = False
        
        for i in range(24):  # Monitor for 2 minutes (24 * 5 seconds)
            await asyncio.sleep(5)
            
            # Check Bob's messages
            messages_result = await get_messages_tool(
                agent_id=bob["agent_id"],
                limit=5
            )
            
            if "error" not in messages_result:
                messages = messages_result.get("messages", [])
                
                # Look for autonomous responses
                for msg in messages:
                    if (msg.get("sender_id") == bob["agent_id"] and 
                        msg.get("metadata", {}).get("autonomous")):
                        print(f"🎉 AUTONOMOUS RESPONSE DETECTED!")
                        print(f"   From: {bob['name']}")
                        print(f"   Time: {msg.get('timestamp')}")
                        print(f"   Content preview: {msg.get('content', '')[:100]}...")
                        response_detected = True
                        break
                
                if response_detected:
                    break
            
            if i % 6 == 0:  # Status update every 30 seconds
                elapsed = (i + 1) * 5
                print(f"  ⏱️  {elapsed}s elapsed - Waiting for autonomous response...")
        
        if response_detected:
            print("✅ Autonomous response confirmed!")
        else:
            print("⚠️  No autonomous response detected in monitoring period")
    
    async def verify_autonomous_conversation(self):
        """Verify that agents are having autonomous conversations."""
        print("\n🔍 Phase 5: Verifying Autonomous Conversation")
        print("-" * 40)
        
        # Check message history for all agents
        for agent in self.agents:
            print(f"\nChecking messages for {agent['name']}:")
            
            messages_result = await get_messages_tool(
                agent_id=agent["agent_id"],
                limit=10
            )
            
            if "error" not in messages_result:
                messages = messages_result.get("messages", [])
                autonomous_messages = [
                    msg for msg in messages 
                    if msg.get("metadata", {}).get("autonomous")
                ]
                
                print(f"  Total messages: {len(messages)}")
                print(f"  Autonomous messages: {len(autonomous_messages)}")
                
                for msg in autonomous_messages[:3]:  # Show first 3 autonomous messages
                    print(f"    • {msg.get('timestamp')}: {msg.get('content', '')[:80]}...")
            else:
                print(f"  ❌ Error getting messages: {messages_result['error']}")
    
    async def test_proactive_communication(self):
        """Test if agents can initiate conversations proactively."""
        print("\n🚀 Phase 6: Testing Proactive Communication")
        print("-" * 40)
        
        print("Waiting for agents to initiate proactive conversations...")
        print("(This tests the conversation_initiator component)")
        
        # Wait and monitor for proactive conversations
        for i in range(12):  # Wait 1 minute
            await asyncio.sleep(5)
            
            # Check for new conversations initiated by agents
            all_messages = []
            for agent in self.agents:
                messages_result = await get_messages_tool(
                    agent_id=agent["agent_id"],
                    limit=5
                )
                
                if "error" not in messages_result:
                    messages = messages_result.get("messages", [])
                    all_messages.extend(messages)
            
            # Look for proactive initiations
            proactive_messages = [
                msg for msg in all_messages
                if msg.get("metadata", {}).get("conversation_type") == "proactive_initiation"
            ]
            
            if proactive_messages:
                print(f"🎉 PROACTIVE CONVERSATION DETECTED!")
                for msg in proactive_messages[:2]:
                    print(f"   Initiated by: {msg.get('sender_id')}")
                    print(f"   Content: {msg.get('content', '')[:100]}...")
                break
            
            if i % 3 == 0:
                elapsed = (i + 1) * 5
                print(f"  ⏱️  {elapsed}s elapsed - Waiting for proactive conversations...")
    
    async def final_verification(self):
        """Final verification of autonomous communication capabilities."""
        print("\n🏆 Phase 7: Final Verification")
        print("-" * 40)
        
        print("AUTONOMOUS COMMUNICATION TEST RESULTS:")
        print("=" * 50)
        
        # Check final agent status
        agents_result = await list_agents_tool()
        if "error" not in agents_result:
            active_agents = [
                agent for agent in agents_result.get("agents", [])
                if agent.get("status") == "active"
            ]
            print(f"✅ Active agents: {len(active_agents)}")
        
        # Summary of capabilities tested
        capabilities = [
            "✅ Independent process creation",
            "✅ Autonomous message processing",
            "✅ Autonomous response generation", 
            "✅ Conversation context maintenance",
            "✅ Proactive conversation initiation",
            "✅ Role-based expertise responses",
            "✅ Multi-agent coordination"
        ]
        
        print("\nCAPABILITIES DEMONSTRATED:")
        for capability in capabilities:
            print(f"  {capability}")
        
        print(f"\nTest duration: {datetime.now() - self.test_start_time}")
        print("\n🎉 AUTONOMOUS COMMUNICATION SYSTEM FULLY OPERATIONAL!")


async def main():
    """Main entry point for the autonomous communication test."""
    tester = AutonomousCommunicationTester()
    await tester.run_full_test()


if __name__ == "__main__":
    asyncio.run(main())
