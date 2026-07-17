#!/usr/bin/env python3
"""
MINIMAL AUTONOMOUS COMMUNICATION PROOF

This test bypasses the initialization issues and proves autonomous communication
by directly testing the core components that enable agents to think and respond.
"""

import asyncio
import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mcp.tools.agent_management_tools import (
    send_message_tool,
    get_messages_tool,
    list_agents_tool,
)


async def test_existing_agents_autonomous_response():
    """Test if existing agents can respond autonomously using direct invocation."""
    print("🔬 MINIMAL AUTONOMOUS COMMUNICATION PROOF")
    print("=" * 60)
    print("Testing existing agents for autonomous response capabilities")
    print()
    
    # Get existing agents
    agents_result = await list_agents_tool()
    if "error" in agents_result:
        print(f"❌ Error getting agents: {agents_result['error']}")
        return
    
    agents = agents_result.get("agents", [])
    active_agents = [agent for agent in agents if agent.get("status") == "active"]
    
    print(f"Found {len(active_agents)} active agents:")
    for agent in active_agents[:5]:  # Show first 5
        print(f"  • {agent['name']} ({agent['agent_id'][:8]}...)")
    
    if len(active_agents) < 2:
        print("❌ Need at least 2 active agents for communication test")
        return
    
    # Select two agents for testing
    alice = active_agents[0]
    bob = active_agents[1] if len(active_agents) > 1 else active_agents[0]
    
    print(f"\n🧪 Testing communication between:")
    print(f"  Sender: {alice['name']} ({alice['agent_id'][:8]}...)")
    print(f"  Receiver: {bob['name']} ({bob['agent_id'][:8]}...)")
    
    # Get initial message count for Bob
    initial_messages = await get_messages_tool(agent_id=bob["agent_id"], limit=5)
    initial_count = len(initial_messages.get("messages", []))
    print(f"\nInitial message count for {bob['name']}: {initial_count}")
    
    # Send a message from Alice to Bob
    print(f"\n📤 Sending message from {alice['name']} to {bob['name']}...")
    
    message_result = await send_message_tool(
        sender_id=alice["agent_id"],
        recipient_id=bob["agent_id"],
        content=f"""Hi {bob['name']}! This is {alice['name']}.

I'm testing if you can respond autonomously. This is a critical test to prove that agents can communicate independently.

URGENT REQUEST:
Please respond immediately with:
1. Confirmation that you received this message
2. Your role and capabilities
3. A technical recommendation for any project

This test will prove autonomous agent communication is working!""",
        metadata={"test_type": "autonomous_proof", "urgency": "critical"}
    )
    
    if "error" in message_result:
        print(f"❌ Message sending failed: {message_result['error']}")
        return
    
    print(f"✅ Message sent successfully!")
    print(f"   Message ID: {message_result.get('message_id')}")
    
    # Monitor for response
    print(f"\n👀 Monitoring {bob['name']} for autonomous response...")
    print("(If autonomous communication works, Bob should respond within 30 seconds)")
    
    response_detected = False
    
    for i in range(6):  # Monitor for 30 seconds (6 * 5 seconds)
        await asyncio.sleep(5)
        
        # Check for new messages
        current_messages = await get_messages_tool(agent_id=bob["agent_id"], limit=10)
        current_count = len(current_messages.get("messages", []))
        
        if current_count > initial_count:
            print(f"🎉 NEW MESSAGE DETECTED!")
            print(f"   Message count increased from {initial_count} to {current_count}")
            
            # Look for autonomous responses (messages sent BY Bob)
            messages = current_messages.get("messages", [])
            for msg in messages:
                if msg.get("sender_id") == bob["agent_id"]:
                    print(f"🚀 AUTONOMOUS RESPONSE FOUND!")
                    print(f"   From: {bob['name']}")
                    print(f"   Time: {msg.get('timestamp')}")
                    print(f"   Content preview: {msg.get('content', '')[:150]}...")
                    response_detected = True
                    break
            
            if response_detected:
                break
        
        elapsed = (i + 1) * 5
        print(f"  ⏱️  {elapsed}s elapsed - Waiting for autonomous response...")
    
    # Final assessment
    print(f"\n🏆 AUTONOMOUS COMMUNICATION TEST RESULTS:")
    print("=" * 50)
    
    if response_detected:
        print("✅ AUTONOMOUS RESPONSE: CONFIRMED")
        print("✅ AGENTS CAN THINK AND RESPOND INDEPENDENTLY")
        print("✅ AUTONOMOUS COMMUNICATION: PROVEN")
    else:
        print("❌ AUTONOMOUS RESPONSE: NOT DETECTED")
        print("❌ AGENTS MAY NOT BE PROCESSING MESSAGES AUTONOMOUSLY")
        
        # Check if message was at least delivered
        final_messages = await get_messages_tool(agent_id=bob["agent_id"], limit=5)
        final_count = len(final_messages.get("messages", []))
        
        if final_count > initial_count:
            print("✅ MESSAGE DELIVERY: WORKING")
            print("❌ AUTONOMOUS PROCESSING: NOT WORKING")
        else:
            print("❌ MESSAGE DELIVERY: FAILED")
    
    # Show conversation history
    print(f"\n📋 Final Message History for {bob['name']}:")
    final_messages = await get_messages_tool(agent_id=bob["agent_id"], limit=3)
    messages = final_messages.get("messages", [])
    
    for i, msg in enumerate(messages):
        sender_name = "Self" if msg.get("sender_id") == bob["agent_id"] else "Other"
        content_preview = msg.get("content", "")[:100]
        print(f"  {i+1}. [{sender_name}] {content_preview}...")
    
    return response_detected


async def main():
    """Main entry point for minimal autonomous proof."""
    result = await test_existing_agents_autonomous_response()
    
    print(f"\n🎯 FINAL VERDICT:")
    if result:
        print("🎉 AUTONOMOUS AGENT COMMUNICATION: PROVEN!")
        print("   Agents can think, process messages, and respond independently.")
    else:
        print("⚠️  AUTONOMOUS AGENT COMMUNICATION: NOT PROVEN")
        print("   Agents may not be processing messages autonomously.")
        print("   This could be due to initialization issues or missing autonomous components.")


if __name__ == "__main__":
    asyncio.run(main())
