#!/usr/bin/env python3
"""
Autonomous Agent Runner

This script creates truly autonomous agents that:
1. Run as independent processes
2. Automatically check for new messages
3. Process messages with their own reasoning
4. Generate and send autonomous responses
"""

import asyncio
import sys
import os
import argparse
import json
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from src.mcp.tools.agent_management_tools import (
    get_messages_tool,
    send_message_tool,
    get_agent_tool,
)
from src.services.agent_manager import agent_manager
from src.utils.logging import logger


class AutonomousAgent:
    """An autonomous agent that can think and respond independently."""
    
    def __init__(self, agent_id: str, check_interval: int = 5):
        self.agent_id = agent_id
        self.check_interval = check_interval
        self.running = False
        self.agent_info = None
        self.last_message_time = None
        
    async def initialize(self):
        """Initialize the agent and get its information."""
        try:
            # Get agent information
            from src.db.models import get_db
            
            db_gen = get_db()
            db = next(db_gen)
            
            try:
                self.agent_info = await agent_manager.get_agent(agent_id=self.agent_id, db=db)
                if not self.agent_info:
                    raise ValueError(f"Agent {self.agent_id} not found")
                
                logger.info(f"Initialized autonomous agent: {self.agent_info['name']} ({self.agent_id})")
                return True
                
            finally:
                db.close()
                
        except Exception as e:
            logger.error(f"Failed to initialize agent {self.agent_id}: {e}")
            return False
    
    async def check_and_process_messages(self):
        """Check for new messages and process them autonomously."""
        try:
            # Get new messages
            messages_result = await get_messages_tool(
                agent_id=self.agent_id,
                limit=10
            )
            
            if "error" in messages_result:
                logger.error(f"Error getting messages: {messages_result['error']}")
                return
            
            messages = messages_result.get("messages", [])
            
            # Process each new message
            for message in messages:
                message_time = message.get("timestamp")
                
                # Skip if we've already processed this message
                if self.last_message_time and message_time <= self.last_message_time:
                    continue
                
                await self.process_message(message)
                self.last_message_time = message_time
                
        except Exception as e:
            logger.error(f"Error checking messages for agent {self.agent_id}: {e}")
    
    async def process_message(self, message):
        """Process a message and generate an autonomous response."""
        try:
            sender_id = message.get("sender_id")
            content = message.get("content")
            message_type = message.get("type", "text")
            
            logger.info(f"Agent {self.agent_info['name']} processing message from {sender_id}")
            logger.info(f"Message content: {content[:100]}...")
            
            # Generate autonomous response using the agent's LLM
            response = await self.generate_response(content, sender_id, message_type)
            
            if response:
                # Send the autonomous response
                await self.send_response(sender_id, response)
                
        except Exception as e:
            logger.error(f"Error processing message for agent {self.agent_id}: {e}")
    
    async def generate_response(self, message_content: str, sender_id: str, message_type: str) -> str:
        """Generate an autonomous response using the agent's reasoning."""
        try:
            # Get sender information for context
            sender_info = None
            try:
                from src.db.models import get_db
                db_gen = get_db()
                db = next(db_gen)
                try:
                    sender_info = await agent_manager.get_agent(agent_id=sender_id, db=db)
                finally:
                    db.close()
            except:
                pass
            
            sender_name = sender_info.get("name", "Unknown") if sender_info else "Unknown"
            
            # Create a prompt for the agent to respond
            prompt = f"""You are {self.agent_info['name']}, and you have received a message from {sender_name}.

Your role and expertise: {self.agent_info.get('description', '')}

Message from {sender_name}: {message_content}

Please respond thoughtfully based on your role and expertise. Your response should:
1. Acknowledge the message
2. Provide relevant insights based on your specialization
3. Ask follow-up questions if appropriate
4. Be helpful and collaborative

Generate your response:"""

            # Use the agent manager to generate a response
            response = await agent_manager.invoke_agent(
                agent_id=self.agent_id,
                messages=[{"role": "user", "content": prompt}],
                stream=False,
                temperature=0.7,
                max_tokens=500,
            )
            
            if "choices" in response and response["choices"]:
                return response["choices"][0]["message"]["content"]
            else:
                logger.error(f"No response generated for agent {self.agent_id}")
                return None
                
        except Exception as e:
            logger.error(f"Error generating response for agent {self.agent_id}: {e}")
            return None
    
    async def send_response(self, recipient_id: str, response_content: str):
        """Send an autonomous response to another agent."""
        try:
            result = await send_message_tool(
                sender_id=self.agent_id,
                recipient_id=recipient_id,
                content=response_content,
                metadata={"autonomous": True, "generated_at": datetime.now().isoformat()}
            )
            
            if "error" in result:
                logger.error(f"Error sending response: {result['error']}")
            else:
                logger.info(f"Agent {self.agent_info['name']} sent autonomous response to {recipient_id}")
                
        except Exception as e:
            logger.error(f"Error sending response for agent {self.agent_id}: {e}")
    
    async def run(self):
        """Run the autonomous agent loop."""
        if not await self.initialize():
            return
        
        self.running = True
        logger.info(f"Starting autonomous agent loop for {self.agent_info['name']}")
        
        try:
            while self.running:
                await self.check_and_process_messages()
                await asyncio.sleep(self.check_interval)
                
        except KeyboardInterrupt:
            logger.info(f"Stopping autonomous agent {self.agent_info['name']}")
        except Exception as e:
            logger.error(f"Error in autonomous agent loop: {e}")
        finally:
            self.running = False
    
    def stop(self):
        """Stop the autonomous agent."""
        self.running = False


async def main():
    """Main entry point for autonomous agent runner."""
    parser = argparse.ArgumentParser(description="Run an autonomous agent")
    parser.add_argument("--agent-id", required=True, help="Agent ID to run")
    parser.add_argument("--check-interval", type=int, default=5, help="Message check interval in seconds")
    
    args = parser.parse_args()
    
    # Create and run the autonomous agent
    agent = AutonomousAgent(args.agent_id, args.check_interval)
    await agent.run()


if __name__ == "__main__":
    asyncio.run(main())
