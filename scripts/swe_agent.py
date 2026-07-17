#!/usr/bin/env python3
"""
Software Engineering Agent - A specialized agent for software engineering tasks.

This module provides a Software Engineering agent that can analyze codebases,
create work breakdown structures, and coordinate with other agents to complete
software engineering tasks.
"""

import os
import sys
import json
import uuid
import time
import logging
import asyncio
from typing import Dict, List, Optional, Any, Union, Tuple
from datetime import datetime, timezone
from enum import Enum

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("swe-agent")

# Add the parent directory to the path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from fastmcp import FastMCP, Context
    logger.info("Successfully imported FastMCP")
except ImportError:
    logger.error("Failed to import FastMCP. Please install it with 'pip install fastmcp'")
    sys.exit(1)

# Import agent registry
try:
    from agent_registry import get_registry
    logger.info("Successfully imported agent registry")
except ImportError:
    logger.error("Failed to import agent registry")
    sys.exit(1)

# Agent roles
class AgentRole(str, Enum):
    LEAD = "lead"
    DEVELOPER = "developer"
    REVIEWER = "reviewer"
    TESTER = "tester"
    DEVOPS = "devops"
    SECURITY = "security"
    DOCUMENTATION = "documentation"

# Initialize agent registry
registry = get_registry()

# Create the FastMCP server
mcp = FastMCP(
    name="Software Engineering Agent",
    description="Tools for software engineering tasks"
)

@mcp.tool(
    annotations={
        "title": "Create SWE Agent",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False
    }
)
async def create_swe_agent(
    name: str,
    model_name: str,
    role: str,
    system_prompt: Optional[str] = None,
    description: Optional[str] = None,
    temperature: float = 0.7,
    max_tools: int = 128,
    auto_healthcheck: bool = True,
    port: Optional[int] = None,
    uri: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """Create a new Software Engineering agent with a specific role.
    
    Args:
        name: The name of the agent
        model_name: The name of the model to use
        role: The role of the agent (lead, developer, reviewer, tester, devops, security, documentation)
        system_prompt: Optional custom system prompt to use
        description: Optional description of the agent
        temperature: The temperature to use for generation
        max_tools: Maximum number of tools to use
        auto_healthcheck: Whether to automatically perform a health check after creation
        port: Optional port number for the agent
        uri: Optional URI for the agent
        metadata: Optional additional metadata
        
    Returns:
        The created agent configuration
    """
    logger.info(f"Creating SWE agent: {name} with role: {role}")
    
    try:
        # Generate a unique ID for the agent
        agent_id = f"swe-{role}-{uuid.uuid4().hex[:8]}"
        
        # Set default system prompt based on role if not provided
        if system_prompt is None:
            if role == AgentRole.LEAD:
                system_prompt = "You are a Software Engineering Lead agent responsible for analyzing codebases, creating work breakdown structures, and coordinating with other agents to complete software engineering tasks."
            elif role == AgentRole.DEVELOPER:
                system_prompt = "You are a Software Engineering Developer agent responsible for implementing features, fixing bugs, and writing code according to specifications."
            elif role == AgentRole.REVIEWER:
                system_prompt = "You are a Software Engineering Reviewer agent responsible for reviewing code, providing feedback, and ensuring code quality."
            elif role == AgentRole.TESTER:
                system_prompt = "You are a Software Engineering Tester agent responsible for writing and executing tests, identifying bugs, and ensuring software quality."
            elif role == AgentRole.DEVOPS:
                system_prompt = "You are a Software Engineering DevOps agent responsible for managing infrastructure, deployment, and CI/CD pipelines."
            elif role == AgentRole.SECURITY:
                system_prompt = "You are a Software Engineering Security agent responsible for identifying security vulnerabilities, recommending fixes, and ensuring secure coding practices."
            elif role == AgentRole.DOCUMENTATION:
                system_prompt = "You are a Software Engineering Documentation agent responsible for writing and maintaining documentation, including API docs, user guides, and technical specifications."
            else:
                system_prompt = "You are a Software Engineering agent responsible for helping with software development tasks."
        
        # Set default description based on role if not provided
        if description is None:
            description = f"Software Engineering {role.capitalize()} agent"
        
        # Create agent metadata
        agent_metadata = {
            "role": role,
            "specialization": role,
            "skills": get_skills_for_role(role),
            "team": "software-engineering",
            **(metadata or {})
        }
        
        # Create the agent
        agent_config = {
            "agent_id": agent_id,
            "name": name,
            "description": description,
            "llm_model_id": model_name,
            "initial_prompt": system_prompt,
            "status": "initializing",
            "config": {
                "temperature": temperature,
                "max_tools": max_tools,
            },
            "created_at": datetime.now(timezone.utc).isoformat(),
            "updated_at": datetime.now(timezone.utc).isoformat(),
            "last_activity": datetime.now(timezone.utc).isoformat(),
            "port": port,
            "uri": uri,
            "metadata": agent_metadata
        }
        
        # Register agent in the central registry
        registry.register_agent(agent_config)
        
        # Simulate agent initialization
        await asyncio.sleep(0.5)
        
        # Update agent status to active
        agent_config["status"] = "active"
        agent_config["updated_at"] = datetime.now(timezone.utc).isoformat()
        
        # Update in registry
        registry.update_agent(
            agent_id,
            {
                "status": agent_config["status"],
                "updated_at": agent_config["updated_at"]
            }
        )
        
        return {
            "agent": agent_config,
            "message": f"Software Engineering {role.capitalize()} agent created successfully"
        }
    except Exception as e:
        logger.error(f"Error creating SWE agent: {e}")
        return {"error": str(e), "status": "error"}

@mcp.tool(
    annotations={
        "title": "Create SWE Team",
        "readOnlyHint": False,
        "destructiveHint": False,
        "openWorldHint": False
    }
)
async def create_swe_team(
    team_name: str,
    lead_model: str = "gpt-4",
    developer_model: str = "gpt-3.5-turbo",
    reviewer_model: str = "gpt-4",
    tester_model: str = "gpt-3.5-turbo",
    include_devops: bool = False,
    include_security: bool = False,
    include_documentation: bool = False,
    team_size: int = 5,
    temperature: float = 0.7,
    max_tools: int = 128
) -> Dict[str, Any]:
    """Create a team of Software Engineering agents with different roles.
    
    Args:
        team_name: The name of the team
        lead_model: The model to use for the lead agent
        developer_model: The model to use for developer agents
        reviewer_model: The model to use for reviewer agents
        tester_model: The model to use for tester agents
        include_devops: Whether to include a DevOps agent
        include_security: Whether to include a Security agent
        include_documentation: Whether to include a Documentation agent
        team_size: The total number of agents in the team (minimum 3)
        temperature: The temperature to use for generation
        max_tools: Maximum number of tools to use
        
    Returns:
        The created team configuration
    """
    logger.info(f"Creating SWE team: {team_name}")
    
    try:
        # Ensure minimum team size
        team_size = max(3, team_size)
        
        # Calculate number of developers based on team size and included roles
        num_required_roles = 3  # Lead, Reviewer, Tester
        if include_devops:
            num_required_roles += 1
        if include_security:
            num_required_roles += 1
        if include_documentation:
            num_required_roles += 1
        
        num_developers = max(1, team_size - num_required_roles)
        
        # Generate team ID
        team_id = f"team-{uuid.uuid4().hex[:8]}"
        
        # Create team metadata
        team_metadata = {
            "team_id": team_id,
            "team_name": team_name,
            "created_at": datetime.now(timezone.utc).isoformat()
        }
        
        # Create lead agent
        lead_result = await create_swe_agent(
            name=f"{team_name} Lead",
            model_name=lead_model,
            role=AgentRole.LEAD,
            temperature=temperature,
            max_tools=max_tools,
            metadata={"team_id": team_id, "team_name": team_name}
        )
        
        if "error" in lead_result:
            return lead_result
        
        lead_agent = lead_result["agent"]
        
        # Create developer agents
        developer_agents = []
        for i in range(num_developers):
            dev_result = await create_swe_agent(
                name=f"{team_name} Developer {i+1}",
                model_name=developer_model,
                role=AgentRole.DEVELOPER,
                temperature=temperature,
                max_tools=max_tools,
                metadata={"team_id": team_id, "team_name": team_name}
            )
            
            if "error" not in dev_result:
                developer_agents.append(dev_result["agent"])
        
        # Create reviewer agent
        reviewer_result = await create_swe_agent(
            name=f"{team_name} Reviewer",
            model_name=reviewer_model,
            role=AgentRole.REVIEWER,
            temperature=temperature,
            max_tools=max_tools,
            metadata={"team_id": team_id, "team_name": team_name}
        )
        
        reviewer_agent = None
        if "error" not in reviewer_result:
            reviewer_agent = reviewer_result["agent"]
        
        # Create tester agent
        tester_result = await create_swe_agent(
            name=f"{team_name} Tester",
            model_name=tester_model,
            role=AgentRole.TESTER,
            temperature=temperature,
            max_tools=max_tools,
            metadata={"team_id": team_id, "team_name": team_name}
        )
        
        tester_agent = None
        if "error" not in tester_result:
            tester_agent = tester_result["agent"]
        
        # Create optional agents
        devops_agent = None
        security_agent = None
        documentation_agent = None
        
        if include_devops:
            devops_result = await create_swe_agent(
                name=f"{team_name} DevOps",
                model_name=developer_model,
                role=AgentRole.DEVOPS,
                temperature=temperature,
                max_tools=max_tools,
                metadata={"team_id": team_id, "team_name": team_name}
            )
            
            if "error" not in devops_result:
                devops_agent = devops_result["agent"]
        
        if include_security:
            security_result = await create_swe_agent(
                name=f"{team_name} Security",
                model_name=reviewer_model,
                role=AgentRole.SECURITY,
                temperature=temperature,
                max_tools=max_tools,
                metadata={"team_id": team_id, "team_name": team_name}
            )
            
            if "error" not in security_result:
                security_agent = security_result["agent"]
        
        if include_documentation:
            doc_result = await create_swe_agent(
                name=f"{team_name} Documentation",
                model_name=developer_model,
                role=AgentRole.DOCUMENTATION,
                temperature=temperature,
                max_tools=max_tools,
                metadata={"team_id": team_id, "team_name": team_name}
            )
            
            if "error" not in doc_result:
                documentation_agent = doc_result["agent"]
        
        # Compile team
        team = {
            "team_id": team_id,
            "team_name": team_name,
            "lead": lead_agent,
            "developers": developer_agents,
            "reviewer": reviewer_agent,
            "tester": tester_agent,
            "devops": devops_agent,
            "security": security_agent,
            "documentation": documentation_agent,
            "created_at": team_metadata["created_at"]
        }
        
        return {
            "team": team,
            "message": f"Software Engineering team '{team_name}' created successfully with {len(developer_agents) + 1 + (1 if reviewer_agent else 0) + (1 if tester_agent else 0) + (1 if devops_agent else 0) + (1 if security_agent else 0) + (1 if documentation_agent else 0)} agents"
        }
    except Exception as e:
        logger.error(f"Error creating SWE team: {e}")
        return {"error": str(e), "status": "error"}

def get_skills_for_role(role: str) -> List[str]:
    """Get the skills for a specific role.
    
    Args:
        role: The role
        
    Returns:
        List of skills
    """
    if role == AgentRole.LEAD:
        return ["project_management", "code_analysis", "architecture", "task_delegation", "code_review"]
    elif role == AgentRole.DEVELOPER:
        return ["coding", "debugging", "testing", "refactoring", "optimization"]
    elif role == AgentRole.REVIEWER:
        return ["code_review", "code_quality", "best_practices", "security_review", "performance_review"]
    elif role == AgentRole.TESTER:
        return ["test_planning", "test_execution", "bug_reporting", "test_automation", "quality_assurance"]
    elif role == AgentRole.DEVOPS:
        return ["ci_cd", "deployment", "infrastructure", "monitoring", "automation"]
    elif role == AgentRole.SECURITY:
        return ["security_analysis", "vulnerability_assessment", "security_testing", "security_best_practices", "threat_modeling"]
    elif role == AgentRole.DOCUMENTATION:
        return ["technical_writing", "api_documentation", "user_guides", "code_documentation", "knowledge_management"]
    else:
        return ["coding", "debugging", "testing"]

# Main entry point
if __name__ == "__main__":
    # Run the server
    logger.info("Starting Software Engineering agent server")
    mcp.run(transport="stdio")
