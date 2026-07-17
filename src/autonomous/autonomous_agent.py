#!/usr/bin/env python3
"""
Autonomous Agent Runner

This module creates truly autonomous agents that can:
1. Run as independent processes
2. Process messages autonomously
3. Generate their own responses
4. Initiate conversations
5. Work collaboratively on tasks
"""

import asyncio
import sys
import os
import signal
import argparse
from typing import Optional, Dict, Any

# Add the parent directory to the path
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))))

from src.autonomous.message_processor import AutonomousMessageProcessor
from src.autonomous.conversation_initiator import ConversationInitiator
from src.autonomous.task_collaborator import TaskCollaborator
from src.utils.logging import logger


class AutonomousAgent:
    """A fully autonomous agent that can think, communicate, and act independently."""
    
    def __init__(self, agent_id: str, agent_name: str, check_interval: float = 3.0):
        self.agent_id = agent_id
        self.agent_name = agent_name
        self.check_interval = check_interval
        self.running = False
        
        # Core autonomous components
        self.message_processor = AutonomousMessageProcessor(agent_id, check_interval)
        self.conversation_initiator = ConversationInitiator(agent_id)
        self.task_collaborator = TaskCollaborator(agent_id)
        
        # Setup signal handlers for graceful shutdown
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
    
    def _signal_handler(self, signum, frame):
        """Handle shutdown signals gracefully."""
        logger.info(f"Agent {self.agent_name} received shutdown signal")
        self.stop()
    
    async def start(self):
        """Start the autonomous agent."""
        logger.info(f"🤖 Starting autonomous agent: {self.agent_name} ({self.agent_id})")
        
        self.running = True
        
        # Start all autonomous components concurrently
        tasks = [
            asyncio.create_task(self.message_processor.start_processing()),
            asyncio.create_task(self.conversation_initiator.start_initiating()),
            asyncio.create_task(self.task_collaborator.start_collaborating()),
            asyncio.create_task(self._status_monitor()),
        ]
        
        try:
            # Wait for all tasks to complete (or until stopped)
            await asyncio.gather(*tasks, return_exceptions=True)
        except Exception as e:
            logger.error(f"Error in autonomous agent {self.agent_name}: {e}")
        finally:
            logger.info(f"Autonomous agent {self.agent_name} stopped")
    
    def stop(self):
        """Stop the autonomous agent."""
        logger.info(f"Stopping autonomous agent {self.agent_name}")
        self.running = False
        
        # Stop all components
        self.message_processor.stop_processing()
        self.conversation_initiator.stop_initiating()
        self.task_collaborator.stop_collaborating()
    
    async def _status_monitor(self):
        """Monitor agent status and log periodic updates."""
        while self.running:
            try:
                logger.info(f"🔄 Agent {self.agent_name} is running autonomously...")
                await asyncio.sleep(30)  # Status update every 30 seconds
            except Exception as e:
                logger.error(f"Error in status monitor: {e}")
                break


async def main():
    """Main entry point for autonomous agent."""
    parser = argparse.ArgumentParser(description="Run an autonomous agent")
    parser.add_argument("--agent-id", required=True, help="Agent ID")
    parser.add_argument("--agent-name", required=True, help="Agent name")
    parser.add_argument("--check-interval", type=float, default=3.0, help="Message check interval in seconds")
    
    args = parser.parse_args()
    
    # Create and start the autonomous agent
    agent = AutonomousAgent(args.agent_id, args.agent_name, args.check_interval)
    
    try:
        await agent.start()
    except KeyboardInterrupt:
        logger.info("Autonomous agent interrupted by user")
    except Exception as e:
        logger.error(f"Error running autonomous agent: {e}")
    finally:
        agent.stop()


if __name__ == "__main__":
    asyncio.run(main())
