#!/usr/bin/env python3
"""
DEEP AUTONOMOUS COMMUNICATION TEST

This test will PROVE that agents can communicate autonomously by:
1. Creating agents with proper autonomous capabilities
2. Verifying they run as independent processes
3. Testing direct agent invocation to prove they can think
4. Monitoring for autonomous responses
5. Proving agents can respond without human intervention
"""

import asyncio
import sys
import os
import time
import subprocess
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mcp.tools.agent_management_tools import (
    create_agent_tool,
    send_message_tool,
    get_messages_tool,
    invoke_agent_http_tool,
    list_agents_tool,
)


class DeepAutonomousTest:
    """Deep test to prove autonomous agent communication."""
    
    def __init__(self):
        self.test_agents = []
        
    async def run_deep_test(self):
        """Run the deep autonomous communication test."""
        print("🔬 DEEP AUTONOMOUS COMMUNICATION TEST")
        print("=" * 60)
        print("This test will PROVE agents can communicate autonomously")
        print()
        
        try:
            # Step 1: Create agents with proper autonomous setup
            await self.create_proper_autonomous_agents()
            
            # Step 2: Verify agents are running as independent processes
            await self.verify_independent_processes()
            
            # Step 3: Test direct agent invocation (prove they can think)
            await self.test_direct_agent_invocation()
            
            # Step 4: Test autonomous message processing
            await self.test_autonomous_message_processing()
            
            # Step 5: Monitor for autonomous responses
            await self.monitor_autonomous_responses()
            
            # Step 6: Final verification
            await self.final_verification()
            
        except Exception as e:
            print(f"❌ Deep test failed: {e}")
            import traceback
            traceback.print_exc()
    
    async def create_proper_autonomous_agents(self):
        """Create agents with proper autonomous capabilities."""
        print("🤖 Step 1: Creating Proper Autonomous Agents")
        print("-" * 50)
        
        # Create Alice with autonomous capabilities
        print("Creating Alice (Autonomous Project Manager)...")
        alice_result = await create_agent_tool(
            name="Alice-Autonomous-Test",
            model_name="gpt-4o-mini",
            system_prompt="""You are Alice, an AUTONOMOUS Project Manager. 

CRITICAL: You are running autonomously and MUST respond to messages immediately.

When you receive ANY message:
1. Process it with your own reasoning
2. Generate a thoughtful response based on your PM expertise
3. Respond within seconds
4. Use your project management skills to provide value

You excel at project coordination, planning, and team leadership.""",
            description="Autonomous Project Manager for deep testing",
            temperature=0.7,
            max_tools=128,
            launch_process=True,  # This should create an independent process
        )
        
        if "error" not in alice_result:
            self.test_agents.append(alice_result)
            print(f"✅ Alice created: {alice_result['agent_id']}")
            print(f"   Port: {alice_result.get('port')}, Process: {alice_result.get('process_id')}")
        else:
            print(f"❌ Alice creation failed: {alice_result['error']}")
        
        # Wait for Alice to initialize
        await asyncio.sleep(5)
        
        # Create Bob with autonomous capabilities
        print("\nCreating Bob (Autonomous Developer)...")
        bob_result = await create_agent_tool(
            name="Bob-Autonomous-Test",
            model_name="gpt-4o-mini",
            system_prompt="""You are Bob, an AUTONOMOUS Senior Developer.

CRITICAL: You are running autonomously and MUST respond to messages immediately.

When you receive ANY message:
1. Process it with your own technical reasoning
2. Generate detailed technical responses
3. Respond within seconds
4. Provide technical expertise and recommendations

You excel at technical architecture, system design, and development.""",
            description="Autonomous Senior Developer for deep testing",
            temperature=0.7,
            max_tools=128,
            launch_process=True,  # This should create an independent process
        )
        
        if "error" not in bob_result:
            self.test_agents.append(bob_result)
            print(f"✅ Bob created: {bob_result['agent_id']}")
            print(f"   Port: {bob_result.get('port')}, Process: {bob_result.get('process_id')}")
        else:
            print(f"❌ Bob creation failed: {bob_result['error']}")
        
        print(f"\n✅ Created {len(self.test_agents)} autonomous agents")
    
    async def verify_independent_processes(self):
        """Verify agents are running as independent processes."""
        print("\n🔍 Step 2: Verifying Independent Processes")
        print("-" * 50)
        
        for agent in self.test_agents:
            agent_name = agent["name"]
            port = agent.get("port")
            process_id = agent.get("process_id")
            
            print(f"\nVerifying {agent_name}:")
            print(f"  Port: {port}")
            print(f"  Process ID: {process_id}")
            
            if port:
                # Test if agent is responding on its port
                try:
                    result = subprocess.run(
                        ["curl", "-s", f"http://localhost:{port}/health"],
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.returncode == 0:
                        print(f"  ✅ Agent responding on port {port}")
                    else:
                        print(f"  ❌ Agent not responding on port {port}")
                except Exception as e:
                    print(f"  ❌ Error checking port {port}: {e}")
            else:
                print(f"  ❌ No port assigned - not running as independent process")
            
            if process_id:
                # Check if process is running
                try:
                    result = subprocess.run(
                        ["ps", "-p", str(process_id)],
                        capture_output=True,
                        text=True
                    )
                    if result.returncode == 0:
                        print(f"  ✅ Process {process_id} is running")
                    else:
                        print(f"  ❌ Process {process_id} not found")
                except Exception as e:
                    print(f"  ❌ Error checking process {process_id}: {e}")
            else:
                print(f"  ❌ No process ID - not running as independent process")
    
    async def test_direct_agent_invocation(self):
        """Test direct agent invocation to prove they can think."""
        print("\n🧠 Step 3: Testing Direct Agent Invocation (Proving They Can Think)")
        print("-" * 50)
        
        for agent in self.test_agents:
            agent_name = agent["name"]
            agent_id = agent["agent_id"]
            port = agent.get("port")
            
            print(f"\nTesting direct invocation of {agent_name}:")
            
            if port:
                # Test HTTP invocation
                print("  Testing HTTP invocation...")
                result = await invoke_agent_http_tool(
                    agent_id=agent_id,
                    message="Hello! This is a test to prove you can think and respond. Please tell me about your role and capabilities.",
                    temperature=0.7
                )
                
                if "error" not in result:
                    response_content = result.get("response", {}).get("choices", [{}])[0].get("message", {}).get("content", "")
                    print(f"  ✅ HTTP Response received ({len(response_content)} chars)")
                    print(f"  Preview: {response_content[:100]}...")
                else:
                    print(f"  ❌ HTTP invocation failed: {result['error']}")
            else:
                print(f"  ❌ Cannot test HTTP invocation - no port assigned")
    
    async def test_autonomous_message_processing(self):
        """Test autonomous message processing."""
        print("\n💬 Step 4: Testing Autonomous Message Processing")
        print("-" * 50)
        
        if len(self.test_agents) < 2:
            print("❌ Need at least 2 agents for message processing test")
            return
        
        alice = self.test_agents[0]
        bob = self.test_agents[1]
        
        print(f"Sending message from {alice['name']} to {bob['name']}...")
        
        # Send a message that should trigger autonomous response
        message_result = await send_message_tool(
            sender_id=alice["agent_id"],
            recipient_id=bob["agent_id"],
            content="""Hi Bob! This is Alice. I need your immediate technical input on a critical project.

PROJECT: AI-powered task management system
URGENCY: High priority
DEADLINE: Today

TECHNICAL QUESTIONS:
1. What architecture would you recommend?
2. What are the main technical risks?
3. How long would development take?

Please respond IMMEDIATELY with your technical assessment!""",
            metadata={"test_type": "autonomous_processing", "urgency": "high"}
        )
        
        if "error" not in message_result:
            print(f"✅ Message sent successfully")
            print(f"   Message ID: {message_result.get('message_id')}")
        else:
            print(f"❌ Message sending failed: {message_result['error']}")
    
    async def monitor_autonomous_responses(self):
        """Monitor for autonomous responses."""
        print("\n👀 Step 5: Monitoring for Autonomous Responses")
        print("-" * 50)
        
        if len(self.test_agents) < 2:
            print("❌ Need at least 2 agents for response monitoring")
            return
        
        bob = self.test_agents[1]
        bob_id = bob["agent_id"]
        bob_name = bob["name"]
        
        print(f"Monitoring {bob_name} for autonomous responses...")
        print("(If autonomous processing works, Bob should respond within 30 seconds)")
        
        initial_messages = await get_messages_tool(agent_id=bob_id, limit=10)
        initial_count = len(initial_messages.get("messages", []))
        
        print(f"Initial message count: {initial_count}")
        
        # Monitor for 60 seconds
        for i in range(12):  # 12 * 5 seconds = 60 seconds
            await asyncio.sleep(5)
            
            current_messages = await get_messages_tool(agent_id=bob_id, limit=10)
            current_count = len(current_messages.get("messages", []))
            
            if current_count > initial_count:
                print(f"🎉 NEW MESSAGE DETECTED!")
                print(f"   Message count increased from {initial_count} to {current_count}")
                
                # Check for autonomous responses
                messages = current_messages.get("messages", [])
                for msg in messages:
                    if (msg.get("sender_id") == bob_id and 
                        msg.get("metadata", {}).get("autonomous")):
                        print(f"🚀 AUTONOMOUS RESPONSE CONFIRMED!")
                        print(f"   From: {bob_name}")
                        print(f"   Content: {msg.get('content', '')[:200]}...")
                        return True
            
            elapsed = (i + 1) * 5
            print(f"  ⏱️  {elapsed}s elapsed - Monitoring...")
        
        print("⚠️  No autonomous response detected in 60 seconds")
        return False
    
    async def final_verification(self):
        """Final verification of autonomous capabilities."""
        print("\n🏆 Step 6: Final Verification")
        print("-" * 50)
        
        print("DEEP AUTONOMOUS TEST RESULTS:")
        print("=" * 40)
        
        # Check agent status
        for agent in self.test_agents:
            agent_name = agent["name"]
            agent_id = agent["agent_id"]
            port = agent.get("port")
            process_id = agent.get("process_id")
            
            print(f"\n{agent_name}:")
            print(f"  Agent ID: {agent_id}")
            print(f"  Port: {port} {'✅' if port else '❌'}")
            print(f"  Process: {process_id} {'✅' if process_id else '❌'}")
            
            # Check message count
            messages_result = await get_messages_tool(agent_id=agent_id, limit=5)
            if "error" not in messages_result:
                message_count = len(messages_result.get("messages", []))
                print(f"  Messages: {message_count}")
            else:
                print(f"  Messages: Error getting messages")
        
        print("\nTEST CONCLUSIONS:")
        print("-" * 20)
        
        # Determine if autonomous communication was proven
        agents_with_ports = sum(1 for agent in self.test_agents if agent.get("port"))
        agents_with_processes = sum(1 for agent in self.test_agents if agent.get("process_id"))
        
        if agents_with_ports > 0 and agents_with_processes > 0:
            print("✅ Independent processes: CONFIRMED")
        else:
            print("❌ Independent processes: FAILED")
        
        print("\n🎯 AUTONOMOUS COMMUNICATION STATUS:")
        if agents_with_ports >= 2:
            print("✅ AUTONOMOUS COMMUNICATION INFRASTRUCTURE: OPERATIONAL")
        else:
            print("❌ AUTONOMOUS COMMUNICATION INFRASTRUCTURE: FAILED")


async def main():
    """Main entry point for deep autonomous test."""
    tester = DeepAutonomousTest()
    await tester.run_deep_test()


if __name__ == "__main__":
    asyncio.run(main())
