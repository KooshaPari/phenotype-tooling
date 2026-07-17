#!/usr/bin/env python3
"""
Autonomous Message Processor

This module handles autonomous message processing for independent agents.
It runs as a background service that:
1. Polls for new messages
2. Processes them with the agent's LLM
3. Generates autonomous responses
4. Sends responses back
"""

import asyncio
import json
import logging
from datetime import datetime
from typing import Dict, List, Optional, Any
from dataclasses import dataclass

from ..services.agent_manager import agent_manager
from ..services.agent_communication import communication_hub
from ..utils.logging import logger


@dataclass
class MessageContext:
    """Context for processing a message."""
    message_id: str
    sender_id: str
    recipient_id: str
    content: str
    message_type: str
    timestamp: str
    metadata: Dict[str, Any]


class AutonomousMessageProcessor:
    """Processes messages autonomously for an agent."""
    
    def __init__(self, agent_id: str, check_interval: float = 3.0):
        self.agent_id = agent_id
        self.check_interval = check_interval
        self.running = False
        self.agent_info = None
        self.last_processed_time = None
        self.conversation_memory: Dict[str, List[Dict]] = {}
        
    async def initialize(self) -> bool:
        """Initialize the message processor."""
        try:
            from ..db.models import get_db
            
            db_gen = get_db()
            db = next(db_gen)
            
            try:
                self.agent_info = await agent_manager.get_agent(agent_id=self.agent_id, db=db)
                if not self.agent_info:
                    logger.error(f"Agent {self.agent_id} not found")
                    return False
                
                logger.info(f"Initialized message processor for {self.agent_info['name']} ({self.agent_id})")
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to initialize message processor for {self.agent_id}: {e}")
            return False
    
    async def start_processing(self):
        """Start the autonomous message processing loop."""
        if not await self.initialize():
            return
        
        self.running = True
        logger.info(f"Starting autonomous message processing for {self.agent_info['name']}")
        
        try:
            while self.running:
                await self.process_new_messages()
                await asyncio.sleep(self.check_interval)
                
        except Exception as e:
            logger.error(f"Error in message processing loop for {self.agent_id}: {e}")
        finally:
            self.running = False
    
    def stop_processing(self):
        """Stop the message processing loop."""
        self.running = False
        logger.info(f"Stopping message processor for {self.agent_id}")
    
    async def process_new_messages(self):
        """Check for and process new messages."""
        try:
            # Get new messages since last check
            messages = communication_hub.get_message_history(
                agent_id=self.agent_id,
                limit=10
            )
            
            # Filter to only new messages
            new_messages = []
            for msg in messages:
                msg_time = msg.get("timestamp")
                if not self.last_processed_time or msg_time > self.last_processed_time:
                    new_messages.append(msg)
            
            # Process each new message
            for message in new_messages:
                await self.process_message(message)
                self.last_processed_time = message.get("timestamp")
                
        except Exception as e:
            logger.error(f"Error processing new messages for {self.agent_id}: {e}")
    
    async def process_message(self, message: Dict[str, Any]):
        """Process a single message and generate autonomous response."""
        try:
            context = MessageContext(
                message_id=message.get("message_id"),
                sender_id=message.get("sender_id"),
                recipient_id=message.get("recipient_id"),
                content=message.get("content"),
                message_type=message.get("type", "text"),
                timestamp=message.get("timestamp"),
                metadata=message.get("metadata", {})
            )
            
            logger.info(f"Agent {self.agent_info['name']} processing message from {context.sender_id}")
            
            # Generate autonomous response
            response = await self.generate_autonomous_response(context)
            
            if response:
                # Send the response
                await self.send_autonomous_response(context.sender_id, response, context)
                
        except Exception as e:
            logger.error(f"Error processing message {message.get('message_id')}: {e}")
    
    async def generate_autonomous_response(self, context: MessageContext) -> Optional[str]:
        """Generate an autonomous response using the agent's LLM."""
        try:
            # Get sender information for context
            sender_info = await self.get_agent_info(context.sender_id)
            sender_name = sender_info.get("name", "Unknown Agent") if sender_info else "Unknown Agent"
            
            # Build conversation context
            conversation_context = self.build_conversation_context(context.sender_id)
            
            # Create the prompt for autonomous response
            prompt = self.build_response_prompt(context, sender_name, conversation_context)
            
            # Generate response using agent's LLM
            response = await agent_manager.invoke_agent(
                agent_id=self.agent_id,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                temperature=0.7,
                max_tokens=800,
            )
            
            if "choices" in response and response["choices"]:
                generated_response = response["choices"][0]["message"]["content"]
                
                # Update conversation memory
                self.update_conversation_memory(context.sender_id, context.content, generated_response)
                
                return generated_response
            else:
                logger.error(f"No response generated for agent {self.agent_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating autonomous response for {self.agent_id}: {e}")
            return None
    
    def build_response_prompt(self, context: MessageContext, sender_name: str, conversation_context: str) -> str:
        """Build the prompt for generating an autonomous response."""
        agent_name = self.agent_info.get("name", "Agent")
        agent_description = self.agent_info.get("description", "")
        system_prompt = self.agent_info.get("initial_prompt", "")
        
        prompt = f"""You are {agent_name}, an autonomous AI agent. {system_prompt}

AGENT DESCRIPTION: {agent_description}

You have received a message from {sender_name}. You should respond autonomously based on your role and expertise.

CONVERSATION CONTEXT:
{conversation_context}

NEW MESSAGE FROM {sender_name}:
{context.content}

MESSAGE TYPE: {context.message_type}
TIMESTAMP: {context.timestamp}

INSTRUCTIONS:
1. Respond thoughtfully based on your role and expertise
2. Be helpful and collaborative
3. Ask follow-up questions if appropriate
4. Stay in character as {agent_name}
5. If this is a task or request, provide actionable insights
6. Keep your response focused and relevant

Generate your autonomous response:"""

        return prompt
    
    def build_conversation_context(self, other_agent_id: str) -> str:
        """Build conversation context for better responses."""
        if other_agent_id not in self.conversation_memory:
            return "This is the start of your conversation."
        
        history = self.conversation_memory[other_agent_id]
        if not history:
            return "This is the start of your conversation."
        
        context_lines = []
        for entry in history[-3:]:  # Last 3 exchanges
            context_lines.append(f"Them: {entry['their_message']}")
            context_lines.append(f"You: {entry['your_response']}")
        
        return "\n".join(context_lines)
    
    def update_conversation_memory(self, other_agent_id: str, their_message: str, your_response: str):
        """Update conversation memory for context."""
        if other_agent_id not in self.conversation_memory:
            self.conversation_memory[other_agent_id] = []
        
        self.conversation_memory[other_agent_id].append({
            "their_message": their_message,
            "your_response": your_response,
            "timestamp": datetime.now().isoformat()
        })
        
        # Keep only last 10 exchanges
        if len(self.conversation_memory[other_agent_id]) > 10:
            self.conversation_memory[other_agent_id] = self.conversation_memory[other_agent_id][-10:]
    
    async def send_autonomous_response(self, recipient_id: str, response: str, original_context: MessageContext):
        """Send an autonomous response."""
        try:
            result = await communication_hub.send_message(
                sender_id=self.agent_id,
                recipient_id=recipient_id,
                content=response,
                metadata={
                    "autonomous": True,
                    "generated_at": datetime.now().isoformat(),
                    "in_response_to": original_context.message_id,
                    "response_type": "autonomous_reply"
                }
            )
            
            if "error" not in result:
                logger.info(f"Agent {self.agent_info['name']} sent autonomous response to {recipient_id}")
            else:
                logger.error(f"Error sending autonomous response: {result['error']}")
                
        except Exception as e:
            logger.error(f"Error sending autonomous response: {e}")
    
    async def get_agent_info(self, agent_id: str) -> Optional[Dict[str, Any]]:
        """Get information about another agent."""
        try:
            from ..db.models import get_db
            
            db_gen = get_db()
            db = next(db_gen)
            
            try:
                return await agent_manager.get_agent(agent_id=agent_id, db=db)
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Error getting agent info for {agent_id}: {e}")
            return None
