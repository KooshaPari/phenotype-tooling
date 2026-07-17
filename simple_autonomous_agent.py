#!/usr/bin/env python3
"""
Simple Autonomous Agent

A simplified autonomous agent that can be launched by the centralized agent manager.
This agent runs as an independent process and can communicate autonomously.
"""

import asyncio
import sys
import os
import argparse
import logging
from datetime import datetime

# Add the current directory to the path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Set up logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class SimpleAutonomousAgent:
    """A simple autonomous agent for testing the centralized architecture."""
    
    def __init__(self, agent_id: str, name: str, role: str, model: str, port: int, 
                 system_prompt: str = None, capabilities: list = None):
        self.agent_id = agent_id
        self.name = name
        self.role = role
        self.model = model
        self.port = port
        self.system_prompt = system_prompt
        self.capabilities = capabilities or []
        self.running = False
        
    async def run(self):
        """Run the autonomous agent."""
        self.running = True
        logger.info(f"🤖 Starting autonomous agent: {self.name} ({self.role})")
        logger.info(f"   Agent ID: {self.agent_id}")
        logger.info(f"   Port: {self.port}")
        logger.info(f"   Model: {self.model}")
        logger.info(f"   Capabilities: {', '.join(self.capabilities)}")
        
        if self.system_prompt:
            logger.info(f"   System Prompt: {self.system_prompt[:100]}...")
        
        try:
            # Simulate autonomous agent behavior
            message_count = 0
            while self.running:
                # Simulate checking for messages and processing them
                await asyncio.sleep(5)  # Check every 5 seconds
                
                # Log heartbeat every 30 seconds
                message_count += 1
                if message_count % 6 == 0:  # Every 30 seconds (6 * 5 seconds)
                    logger.info(f"💓 {self.name} heartbeat - Agent running autonomously")
                    
                    # Simulate some autonomous activity
                    if self.role.lower() == "project manager":
                        logger.info(f"📋 {self.name}: Reviewing project status and coordinating tasks...")
                    elif "developer" in self.role.lower():
                        logger.info(f"💻 {self.name}: Analyzing code and planning implementations...")
                    elif "designer" in self.role.lower():
                        logger.info(f"🎨 {self.name}: Working on user experience improvements...")
                    else:
                        logger.info(f"🔧 {self.name}: Performing {self.role} activities...")
                
        except KeyboardInterrupt:
            logger.info(f"🛑 Stopping autonomous agent {self.name}")
        except Exception as e:
            logger.error(f"❌ Error in autonomous agent {self.name}: {e}")
        finally:
            self.running = False
            logger.info(f"👋 Autonomous agent {self.name} stopped")
    
    def stop(self):
        """Stop the autonomous agent."""
        self.running = False

async def main():
    """Main entry point for the simple autonomous agent."""
    parser = argparse.ArgumentParser(description="Run a simple autonomous agent")
    parser.add_argument("--agent-id", required=True, help="Agent ID")
    parser.add_argument("--name", required=True, help="Agent name")
    parser.add_argument("--role", required=True, help="Agent role")
    parser.add_argument("--model", required=True, help="Model name")
    parser.add_argument("--port", type=int, required=True, help="Port number")
    parser.add_argument("--temperature", type=float, default=0.7, help="Temperature")
    parser.add_argument("--max-tools", type=int, default=128, help="Max tools")
    parser.add_argument("--system-prompt", help="System prompt")
    parser.add_argument("--capabilities", help="Comma-separated capabilities")
    
    args = parser.parse_args()
    
    # Parse capabilities
    capabilities = []
    if args.capabilities:
        capabilities = [cap.strip() for cap in args.capabilities.split(",")]
    
    # Create and run the autonomous agent
    agent = SimpleAutonomousAgent(
        agent_id=args.agent_id,
        name=args.name,
        role=args.role,
        model=args.model,
        port=args.port,
        system_prompt=args.system_prompt,
        capabilities=capabilities
    )
    
    await agent.run()

if __name__ == "__main__":
    asyncio.run(main())
