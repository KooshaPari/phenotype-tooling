#!/usr/bin/env python3
"""
Multi-Agent Project Planning Demonstration

This script demonstrates:
1. Creating multiple independent agent processes
2. Agent-to-agent communication (both blocking and non-blocking)
3. Collaborative project planning conversation
4. Team coordination without actual task execution
"""

import asyncio
import sys
import os
import time

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mcp.tools.agent_management_tools import (
    create_independent_agent_tool,
    invoke_agent_http_tool,
    send_message_tool,
    get_messages_tool,
)


class MultiAgentTeam:
    """Manages a team of independent agents for project planning."""
    
    def __init__(self):
        self.agents = {}
        self.conversation_log = []
    
    async def create_agent(self, name, role, system_prompt):
        """Create an independent agent with a specific role."""
        print(f"🤖 Creating {role}: {name}")
        
        result = await create_independent_agent_tool(
            name=name,
            model_name="gpt-4o-mini",
            system_prompt=system_prompt,
            description=f"{role} agent for project planning",
            temperature=0.7,
            max_tools=128,
        )
        
        if "error" in result:
            print(f"❌ Error creating {name}: {result['error']}")
            return None
        
        agent_info = {
            "id": result["agent_id"],
            "name": name,
            "role": role,
            "port": result["port"],
            "uri": result["uri"],
            "process_id": result["process_id"],
        }
        
        self.agents[name] = agent_info
        print(f"✅ {name} created successfully on port {result['port']}")
        return agent_info
    
    async def send_blocking_message(self, sender_name, recipient_name, message):
        """Send a blocking message (direct HTTP call) between agents."""
        sender = self.agents[sender_name]
        recipient = self.agents[recipient_name]
        
        print(f"\n💬 {sender_name} → {recipient_name} (BLOCKING)")
        print(f"Message: {message}")
        
        response = await invoke_agent_http_tool(
            agent_id=recipient["id"],
            message=f"Message from {sender_name} ({sender['role']}): {message}",
            temperature=0.7,
        )
        
        if "error" in response:
            print(f"❌ Error: {response['error']}")
            return None
        
        if "response" in response and "choices" in response["response"]:
            reply = response["response"]["choices"][0]["message"]["content"]
            print(f"Reply: {reply}")
            
            self.conversation_log.append({
                "type": "blocking",
                "sender": sender_name,
                "recipient": recipient_name,
                "message": message,
                "reply": reply,
                "timestamp": time.time()
            })
            
            return reply
        
        return None
    
    async def send_non_blocking_message(self, sender_name, recipient_name, message):
        """Send a non-blocking message (message queue) between agents."""
        sender = self.agents[sender_name]
        recipient = self.agents[recipient_name]
        
        print(f"\n📨 {sender_name} → {recipient_name} (NON-BLOCKING)")
        print(f"Message: {message}")
        
        result = await send_message_tool(
            sender_id=sender["id"],
            recipient_id=recipient["id"],
            content=message,
            metadata={"sender_role": sender["role"], "type": "planning"}
        )
        
        if "error" in result:
            print(f"❌ Error: {result['error']}")
            return False
        
        print(f"✅ Message queued successfully")
        
        self.conversation_log.append({
            "type": "non_blocking",
            "sender": sender_name,
            "recipient": recipient_name,
            "message": message,
            "timestamp": time.time()
        })
        
        return True
    
    async def get_agent_messages(self, agent_name):
        """Get messages for an agent from the message queue."""
        agent = self.agents[agent_name]
        
        result = await get_messages_tool(
            agent_id=agent["id"],
            limit=10
        )
        
        if "error" in result:
            print(f"❌ Error getting messages for {agent_name}: {result['error']}")
            return []
        
        return result.get("messages", [])


async def demonstrate_multi_agent_planning():
    """Demonstrate multi-agent project planning conversation."""
    
    print("🚀 Multi-Agent Project Planning Demonstration")
    print("=" * 60)
    
    team = MultiAgentTeam()
    
    # Create a diverse team of agents
    agents_to_create = [
        {
            "name": "Alice",
            "role": "Project Manager",
            "prompt": """You are Alice, an experienced Project Manager. You excel at:
- Breaking down complex projects into manageable tasks
- Coordinating team members and timelines
- Risk assessment and mitigation planning
- Resource allocation and budget planning
- Stakeholder communication

When discussing projects, focus on planning, coordination, and high-level strategy. Always consider timelines, resources, and potential risks."""
        },
        {
            "name": "Bob",
            "role": "Senior Developer",
            "prompt": """You are Bob, a Senior Software Developer with 10+ years experience. You excel at:
- Technical architecture and system design
- Code quality and best practices
- Technology stack selection
- Performance optimization
- Mentoring junior developers

When discussing projects, focus on technical feasibility, architecture decisions, and implementation approaches. Consider scalability, maintainability, and technical debt."""
        },
        {
            "name": "Carol",
            "role": "UX Designer",
            "prompt": """You are Carol, a UX Designer passionate about user-centered design. You excel at:
- User research and persona development
- Information architecture and user flows
- Wireframing and prototyping
- Usability testing and iteration
- Accessibility and inclusive design

When discussing projects, focus on user needs, design thinking, and user experience considerations. Always advocate for the end user."""
        },
        {
            "name": "David",
            "role": "DevOps Engineer",
            "prompt": """You are David, a DevOps Engineer focused on infrastructure and deployment. You excel at:
- CI/CD pipeline design and implementation
- Cloud infrastructure and containerization
- Monitoring and observability
- Security and compliance
- Automation and tooling

When discussing projects, focus on deployment strategies, infrastructure requirements, and operational considerations."""
        }
    ]
    
    # Create all agents
    print("\n🏗️ Creating Agent Team")
    print("-" * 30)
    
    for agent_config in agents_to_create:
        await team.create_agent(
            agent_config["name"],
            agent_config["role"],
            agent_config["prompt"]
        )
        # Wait between agent creation to avoid port conflicts
        await asyncio.sleep(3)
    
    print(f"\n✅ Team created! {len(team.agents)} agents ready.")
    
    # Wait for all agents to fully initialize
    print("\n⏳ Waiting for agents to fully initialize...")
    await asyncio.sleep(10)
    
    # Start the project planning conversation
    print("\n🎯 Starting Project Planning Session")
    print("=" * 50)
    
    project_brief = """
    PROJECT: AI-Powered Task Management Application
    
    OVERVIEW: Build a web application that uses AI to help users manage their tasks more effectively.
    
    KEY FEATURES:
    - Smart task prioritization using AI
    - Natural language task input
    - Automated scheduling suggestions
    - Progress tracking and analytics
    - Team collaboration features
    
    CONSTRAINTS:
    - 3-month timeline
    - Team of 5 developers
    - $100k budget
    - Must be mobile-responsive
    - GDPR compliance required
    """
    
    # Alice (PM) initiates the planning session
    await team.send_blocking_message(
        "Alice", "Bob",
        f"Hi Bob! I'd like to start planning our new project. Here's the brief: {project_brief}\n\nAs our senior developer, what are your initial thoughts on the technical approach and architecture?"
    )
    
    await asyncio.sleep(2)
    
    # Bob responds with technical considerations
    await team.send_blocking_message(
        "Bob", "Carol",
        "Hi Carol! Alice and I are planning the AI task management app. From a technical perspective, I'm thinking we should use a microservices architecture with React frontend, Node.js backend, and integrate with OpenAI's API for the AI features. What are your thoughts on the user experience and design approach for this type of application?"
    )
    
    await asyncio.sleep(2)
    
    # Carol provides UX perspective
    await team.send_blocking_message(
        "Carol", "David",
        "Great project! From a UX perspective, I think we need to focus on simplicity and intuitive AI interactions. Users should be able to just type 'finish the quarterly report by Friday' and have the AI understand context, priority, and scheduling. David, what infrastructure considerations do we need for handling AI API calls and user data securely?"
    )
    
    await asyncio.sleep(2)
    
    # David addresses infrastructure and security
    await team.send_blocking_message(
        "David", "Alice",
        "Good points, Carol! For infrastructure, we'll need robust API rate limiting for the AI calls, secure data encryption for GDPR compliance, and probably a Redis cache for frequently accessed data. Alice, how should we structure the development phases and what are the key milestones you're thinking about?"
    )
    
    await asyncio.sleep(2)
    
    # Alice provides project structure
    await team.send_blocking_message(
        "Alice", "Bob",
        "Excellent insights everyone! I'm thinking 3 phases: Phase 1 (Month 1) - Core task management and basic AI integration, Phase 2 (Month 2) - Advanced AI features and team collaboration, Phase 3 (Month 3) - Polish, testing, and deployment. Bob, can you break down the technical tasks for Phase 1?"
    )
    
    # Demonstrate non-blocking communication for side conversations
    print("\n📨 Side Conversations (Non-blocking)")
    print("-" * 40)
    
    await team.send_non_blocking_message(
        "Carol", "Bob",
        "Hey Bob, I'm working on some wireframes for the AI task input interface. Could you review the technical feasibility when you have a moment?"
    )
    
    await team.send_non_blocking_message(
        "David", "Alice",
        "Alice, I've been researching GDPR compliance tools. We should schedule a meeting to discuss data handling policies."
    )
    
    await team.send_non_blocking_message(
        "Bob", "David",
        "David, I'm concerned about API costs for the AI features. Can we set up monitoring and alerts for usage?"
    )
    
    # Show message queues
    print("\n📬 Checking Message Queues")
    print("-" * 30)
    
    for agent_name in team.agents.keys():
        messages = await team.get_agent_messages(agent_name)
        if messages:
            print(f"\n{agent_name} has {len(messages)} queued messages:")
            for msg in messages:
                print(f"  - From: {msg.get('sender_id', 'Unknown')}")
                print(f"    Content: {msg.get('content', '')[:100]}...")
    
    # Summary
    print("\n🎉 Project Planning Session Complete!")
    print("=" * 50)
    print(f"Total conversation entries: {len(team.conversation_log)}")
    print(f"Blocking messages: {len([c for c in team.conversation_log if c['type'] == 'blocking'])}")
    print(f"Non-blocking messages: {len([c for c in team.conversation_log if c['type'] == 'non_blocking'])}")
    
    print("\n📋 Key Planning Outcomes:")
    print("- Technical architecture: Microservices with React/Node.js")
    print("- AI integration: OpenAI API with rate limiting")
    print("- UX approach: Natural language input with smart suggestions")
    print("- Infrastructure: Cloud-based with Redis caching")
    print("- Timeline: 3-phase approach over 3 months")
    print("- Compliance: GDPR-ready data handling")
    
    return team


if __name__ == "__main__":
    asyncio.run(demonstrate_multi_agent_planning())
