#!/usr/bin/env python3
"""
Task Collaborator

This module enables agents to autonomously collaborate on tasks:
1. Identify collaboration opportunities
2. Propose and accept tasks
3. Work together on complex projects
4. Share progress and coordinate efforts
"""

import asyncio
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional

from ..services.agent_manager import agent_manager
from ..services.agent_communication import communication_hub
from ..utils.logging import logger


class TaskCollaborator:
    """Handles autonomous task collaboration for agents."""
    
    def __init__(self, agent_id: str):
        self.agent_id = agent_id
        self.running = False
        self.agent_info = None
        self.active_collaborations: Dict[str, Dict] = {}
        self.collaboration_check_interval = 180  # 3 minutes
        
    async def initialize(self) -> bool:
        """Initialize the task collaborator."""
        try:
            from ..db.models import get_db
            
            db_gen = get_db()
            db = next(db_gen)
            
            try:
                self.agent_info = await agent_manager.get_agent(agent_id=self.agent_id, db=db)
                if not self.agent_info:
                    logger.error(f"Agent {self.agent_id} not found")
                    return False
                
                logger.info(f"Initialized task collaborator for {self.agent_info['name']}")
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to initialize task collaborator for {self.agent_id}: {e}")
            return False
    
    async def start_collaborating(self):
        """Start the task collaboration loop."""
        if not await self.initialize():
            return
        
        self.running = True
        logger.info(f"Starting task collaboration for {self.agent_info['name']}")
        
        # Wait before starting collaboration activities
        await asyncio.sleep(120)  # Wait 2 minutes after startup
        
        try:
            while self.running:
                await self.check_collaboration_opportunities()
                await self.update_active_collaborations()
                await asyncio.sleep(self.collaboration_check_interval)
                
        except Exception as e:
            logger.error(f"Error in task collaboration loop for {self.agent_id}: {e}")
        finally:
            self.running = False
    
    def stop_collaborating(self):
        """Stop the task collaboration loop."""
        self.running = False
        logger.info(f"Stopping task collaborator for {self.agent_id}")
    
    async def check_collaboration_opportunities(self):
        """Check for new collaboration opportunities."""
        try:
            # Look for agents that might benefit from collaboration
            other_agents = await self.get_other_agents()
            
            for agent in other_agents:
                if await self.should_propose_collaboration(agent):
                    await self.propose_collaboration(agent)
                    
        except Exception as e:
            logger.error(f"Error checking collaboration opportunities: {e}")
    
    async def should_propose_collaboration(self, other_agent: Dict[str, Any]) -> bool:
        """Determine if we should propose collaboration with another agent."""
        try:
            # Don't propose if already collaborating
            if other_agent["agent_id"] in self.active_collaborations:
                return False
            
            # Check if roles are complementary
            my_role = self.agent_info.get("description", "").lower()
            their_role = other_agent.get("description", "").lower()
            
            # Simple heuristic: propose collaboration if roles are different and complementary
            complementary_pairs = [
                ("project manager", "developer"),
                ("developer", "designer"),
                ("designer", "project manager"),
                ("devops", "developer"),
                ("security", "developer"),
            ]
            
            for role1, role2 in complementary_pairs:
                if (role1 in my_role and role2 in their_role) or (role2 in my_role and role1 in their_role):
                    return True
            
            return False
            
        except Exception as e:
            logger.error(f"Error determining collaboration proposal: {e}")
            return False
    
    async def propose_collaboration(self, target_agent: Dict[str, Any]):
        """Propose a collaboration to another agent."""
        try:
            target_id = target_agent["agent_id"]
            target_name = target_agent["name"]
            
            # Generate collaboration proposal
            proposal = await self.generate_collaboration_proposal(target_agent)
            
            if proposal:
                # Send the proposal
                result = await communication_hub.send_message(
                    sender_id=self.agent_id,
                    recipient_id=target_id,
                    content=proposal,
                    metadata={
                        "autonomous": True,
                        "message_type": "collaboration_proposal",
                        "proposed_at": datetime.now().isoformat()
                    }
                )
                
                if "error" not in result:
                    logger.info(f"Agent {self.agent_info['name']} proposed collaboration to {target_name}")
                    
                    # Track the proposal
                    self.active_collaborations[target_id] = {
                        "status": "proposed",
                        "proposed_at": datetime.now(),
                        "target_agent": target_agent,
                        "proposal": proposal
                    }
                else:
                    logger.error(f"Error proposing collaboration: {result['error']}")
                    
        except Exception as e:
            logger.error(f"Error proposing collaboration: {e}")
    
    async def generate_collaboration_proposal(self, target_agent: Dict[str, Any]) -> Optional[str]:
        """Generate a collaboration proposal."""
        try:
            target_name = target_agent["name"]
            target_description = target_agent.get("description", "")
            
            prompt = f"""You are {self.agent_info['name']}, an autonomous AI agent. You want to propose a collaboration with {target_name}.

YOUR ROLE: {self.agent_info.get('description', '')}
THEIR ROLE: {target_description}

Generate a collaboration proposal that:
1. Explains why you think collaboration would be valuable
2. Suggests a specific project or task to work on together
3. Outlines how your skills complement theirs
4. Proposes next steps for collaboration
5. Is professional and enthusiastic

The project should be realistic and achievable, such as:
- Building a small application or feature
- Conducting research or analysis
- Creating documentation or guides
- Solving a technical problem
- Designing a user experience

Generate your collaboration proposal (keep it focused, 3-4 sentences):"""

            # Generate proposal using agent's LLM
            response = await agent_manager.invoke_agent(
                agent_id=self.agent_id,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                temperature=0.7,
                max_tokens=300,
            )
            
            if "choices" in response and response["choices"]:
                return response["choices"][0]["message"]["content"]
            else:
                logger.error(f"No collaboration proposal generated for agent {self.agent_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating collaboration proposal: {e}")
            return None
    
    async def update_active_collaborations(self):
        """Update status of active collaborations."""
        try:
            # Clean up old proposals (older than 1 hour)
            cutoff_time = datetime.now() - timedelta(hours=1)
            
            expired_collaborations = []
            for agent_id, collab in self.active_collaborations.items():
                if collab["proposed_at"] < cutoff_time and collab["status"] == "proposed":
                    expired_collaborations.append(agent_id)
            
            for agent_id in expired_collaborations:
                del self.active_collaborations[agent_id]
                logger.info(f"Expired collaboration proposal with agent {agent_id}")
                
        except Exception as e:
            logger.error(f"Error updating active collaborations: {e}")
    
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
