#!/usr/bin/env python3
"""
Conversation Initiator

This module enables agents to proactively initiate conversations and collaborations.
Agents can:
1. Identify when to start conversations
2. Reach out to other agents for collaboration
3. Propose new ideas and projects
4. Check in on ongoing work
"""

import asyncio
import random
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from ..services.agent_manager import agent_manager
from ..services.agent_communication import communication_hub
from ..utils.logging import logger


class ConversationInitiator:
    """Handles proactive conversation initiation for autonomous agents."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.running = False
        self.agent_info = None
        self.last_initiation_time = None
        self.initiation_interval = 300  # 5 minutes between potential initiations
        
    async def initialize(self) -> bool:
        """Initialize the conversation initiator."""
        try:
            from ..db.models import get_db
            
            db_gen = get_db()
            db = next(db_gen)
            
            try:
                self.agent_info = await agent_manager.get_agent(agent_id=self.agent_id, db=db)
                if not self.agent_info:
                    logger.error(f"Agent {self.agent_id} not found")
                    return False
                
                logger.info(f"Initialized conversation initiator for {self.agent_info['name']}")
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to initialize conversation initiator for {self.agent_id}: {e}")
            return False
    
    async def start_initiating(self):
        """Start the conversation initiation loop."""
        if not await self.initialize():
            return
        
        self.running = True
        logger.info(f"Starting conversation initiation for {self.agent_info['name']}")
        
        # Wait a bit before starting to initiate conversations
        await asyncio.sleep(60)  # Wait 1 minute after startup
        
        try:
            while self.running:
                await self.consider_initiating_conversation()
                await asyncio.sleep(self.initiation_interval)
                
        except Exception as e:
            logger.error(f"Error in conversation initiation loop for {self.agent_id}: {e}")
        finally:
            self.running = False
    
    def stop_initiating(self):
        """Stop the conversation initiation loop."""
        self.running = False
        logger.info(f"Stopping conversation initiator for {self.agent_id}")
    
    async def consider_initiating_conversation(self):
        """Consider whether to initiate a new conversation."""
        try:
            # Get list of other agents
            other_agents = await self.get_other_agents()
            
            if not other_agents:
                return
            
            # Decide whether to initiate a conversation (30% chance)
            if random.random() < 0.3:
                await self.initiate_conversation(other_agents)
                
        except Exception as e:
            logger.error(f"Error considering conversation initiation: {e}")
    
    async def initiate_conversation(self, other_agents: List[Dict[str, Any]]):
        """Initiate a conversation with another agent."""
        try:
            # Choose a random agent to talk to
            target_agent = random.choice(other_agents)
            target_id = target_agent["agent_id"]
            target_name = target_agent["name"]
            
            # Generate conversation starter based on agent role
            conversation_starter = await self.generate_conversation_starter(target_agent)
            
            if conversation_starter:
                # Send the conversation starter
                result = await communication_hub.send_message(
                    sender_id=self.agent_id,
                    recipient_id=target_id,
                    content=conversation_starter,
                    metadata={
                        "autonomous": True,
                        "conversation_type": "proactive_initiation",
                        "initiated_at": datetime.now().isoformat()
                    }
                )
                
                if "error" not in result:
                    logger.info(f"Agent {self.agent_info['name']} initiated conversation with {target_name}")
                    self.last_initiation_time = datetime.now()
                else:
                    logger.error(f"Error initiating conversation: {result['error']}")
                    
        except Exception as e:
            logger.error(f"Error initiating conversation: {e}")
    
    async def generate_conversation_starter(self, target_agent: Dict[str, Any]) -> Optional[str]:
        """Generate a conversation starter based on agent roles and context."""
        try:
            target_name = target_agent["name"]
            target_description = target_agent.get("description", "")
            
            # Create prompt for generating conversation starter
            prompt = f"""You are {self.agent_info['name']}, an autonomous AI agent. You want to proactively start a conversation with {target_name}.

YOUR ROLE: {self.agent_info.get('description', '')}
THEIR ROLE: {target_description}

Generate a natural, helpful conversation starter that:
1. Introduces yourself briefly
2. Shows interest in collaboration
3. Suggests a specific topic or question related to your roles
4. Is friendly and professional
5. Encourages a response

Examples of good conversation starters:
- Asking for expertise in their domain
- Proposing collaboration on a project
- Sharing an insight they might find interesting
- Asking for feedback on an idea

Generate your conversation starter (keep it concise, 2-3 sentences):"""

            # Generate conversation starter using agent's LLM
            response = await agent_manager.invoke_agent(
                agent_id=self.agent_id,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                temperature=0.8,  # Higher temperature for more creative conversation starters
                max_tokens=200,
            )
            
            if "choices" in response and response["choices"]:
                return response["choices"][0]["message"]["content"]
            else:
                logger.error(f"No conversation starter generated for agent {self.agent_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating conversation starter: {e}")
            return None
    
    async def get_other_agents(self) -> List[Dict[str, Any]]:
        """Get list of other active agents."""
        try:
            from ..db.models import get_db
            
            db_gen = get_db()
            db = next(db_gen)
            
            try:
                # Get all agents except self
                all_agents = await agent_manager.list_agents(db=db)
                other_agents = [
                    agent for agent in all_agents 
                    if agent["agent_id"] != self.agent_id and agent.get("status") == "active"
                ]
                
                return other_agents
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting other agents: {e}")
            return []
