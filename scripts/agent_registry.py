#!/usr/bin/env python3
"""
Agent Registry - Central database for agent management.

This module provides a central registry for storing and retrieving agent information,
including status, configuration, and communication history.
"""

import os
import json
import sqlite3
import logging
from typing import Dict, List, Optional, Any, Union
from datetime import datetime, timezone

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)
logger = logging.getLogger("agent-registry")


class AgentRegistry:
    """Central registry for agent information."""

    def __init__(self, db_path=None):
        """Initialize the agent registry with a SQLite database.

        Args:
            db_path: Path to the SQLite database file. If None, uses a default path.
        """
        if db_path is None:
            # Use a default path in the user's home directory
            home_dir = os.path.expanduser("~")
            db_dir = os.path.join(home_dir, ".agent_manager")
            os.makedirs(db_dir, exist_ok=True)
            db_path = os.path.join(db_dir, "agent_registry.db")

        self.db_path = db_path
        logger.info(f"Initializing agent registry with database at {db_path}")

        # Connect to the database
        self.conn = sqlite3.connect(db_path)
        self.conn.row_factory = sqlite3.Row

        # Create tables
        self.create_tables()

    def create_tables(self):
        """Create the necessary tables if they don't exist."""
        cursor = self.conn.cursor()

        # Agents table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS agents (
            agent_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            description TEXT,
            model_name TEXT NOT NULL,
            system_prompt TEXT,
            status TEXT NOT NULL,
            config TEXT NOT NULL,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            last_activity TEXT,
            creator_id TEXT,
            workspace_type TEXT,
            container_id TEXT,
            repo_url TEXT,
            branch TEXT,
            port INTEGER,
            uri TEXT
        )
        """
        )

        # Prompts table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS prompts (
            prompt_id TEXT PRIMARY KEY,
            name TEXT NOT NULL,
            content TEXT NOT NULL,
            description TEXT,
            created_at TEXT NOT NULL,
            updated_at TEXT NOT NULL,
            creator_id TEXT
        )
        """
        )

        # Messages table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS messages (
            message_id TEXT PRIMARY KEY,
            sender_id TEXT NOT NULL,
            recipient_id TEXT NOT NULL,
            content TEXT NOT NULL,
            type TEXT NOT NULL,
            metadata TEXT,
            timestamp TEXT NOT NULL,
            status TEXT NOT NULL
        )
        """
        )

        # Conversation history table
        cursor.execute(
            """
        CREATE TABLE IF NOT EXISTS conversation_history (
            entry_id TEXT PRIMARY KEY,
            agent_id TEXT NOT NULL,
            role TEXT NOT NULL,
            content TEXT NOT NULL,
            timestamp TEXT NOT NULL,
            metadata TEXT,
            FOREIGN KEY (agent_id) REFERENCES agents (agent_id)
        )
        """
        )

        self.conn.commit()
        logger.info("Database tables created or verified")

    def register_agent(self, agent_data):
        """Register a new agent in the registry.

        Args:
            agent_data: Dictionary containing agent information

        Returns:
            The registered agent data
        """
        cursor = self.conn.cursor()

        # Convert config to JSON string if it's not already
        if "config" in agent_data and not isinstance(agent_data["config"], str):
            agent_data["config"] = json.dumps(agent_data["config"])

        # Insert agent data
        cursor.execute(
            """
        INSERT INTO agents (
            agent_id, name, description, model_name, system_prompt,
            status, config, created_at, updated_at, last_activity,
            creator_id, workspace_type, container_id, repo_url, branch,
            port, uri
        ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """,
            (
                agent_data.get("agent_id"),
                agent_data.get("name"),
                agent_data.get("description"),
                agent_data.get("llm_model_id"),
                agent_data.get("initial_prompt"),
                agent_data.get("status"),
                agent_data.get("config"),
                agent_data.get("created_at"),
                agent_data.get("updated_at"),
                agent_data.get("last_activity"),
                agent_data.get("creator_id"),
                agent_data.get("workspace_type"),
                agent_data.get("container_id"),
                agent_data.get("repo_url"),
                agent_data.get("branch"),
                agent_data.get("port"),
                agent_data.get("uri"),
            ),
        )

        self.conn.commit()
        logger.info(f"Agent registered: {agent_data.get('agent_id')}")
        return agent_data

    def get_agent(self, agent_id):
        """Get agent information by ID.

        Args:
            agent_id: The agent ID

        Returns:
            Dictionary containing agent information, or None if not found
        """
        cursor = self.conn.cursor()
        cursor.execute("SELECT * FROM agents WHERE agent_id = ?", (agent_id,))
        row = cursor.fetchone()

        if row:
            agent_data = dict(row)

            # Parse config JSON
            if "config" in agent_data and agent_data["config"]:
                try:
                    agent_data["config"] = json.loads(agent_data["config"])
                except json.JSONDecodeError:
                    pass

            return agent_data

        return None

    def list_agents(self, filters=None):
        """List agents with optional filtering.

        Args:
            filters: Optional dictionary of field-value pairs to filter by

        Returns:
            List of dictionaries containing agent information
        """
        cursor = self.conn.cursor()

        query = "SELECT * FROM agents"
        params = []

        if filters:
            conditions = []
            for key, value in filters.items():
                conditions.append(f"{key} = ?")
                params.append(value)

            if conditions:
                query += " WHERE " + " AND ".join(conditions)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        agents = []
        for row in rows:
            agent_data = dict(row)

            # Parse config JSON
            if "config" in agent_data and agent_data["config"]:
                try:
                    agent_data["config"] = json.loads(agent_data["config"])
                except json.JSONDecodeError:
                    pass

            agents.append(agent_data)

        return agents

    def update_agent(self, agent_id, update_data):
        """Update agent information.

        Args:
            agent_id: The agent ID
            update_data: Dictionary containing fields to update

        Returns:
            Updated agent data, or None if agent not found
        """
        cursor = self.conn.cursor()

        # Get current agent data
        cursor.execute("SELECT * FROM agents WHERE agent_id = ?", (agent_id,))
        row = cursor.fetchone()

        if not row:
            return None

        # Prepare update query
        set_clauses = []
        params = []

        for key, value in update_data.items():
            # Map field names
            db_key = key
            if key == "llm_model_id":
                db_key = "model_name"
            elif key == "initial_prompt":
                db_key = "system_prompt"

            # Handle config specially
            if key == "config" and not isinstance(value, str):
                value = json.dumps(value)

            set_clauses.append(f"{db_key} = ?")
            params.append(value)

        # Add updated_at timestamp if not provided
        if "updated_at" not in update_data:
            set_clauses.append("updated_at = ?")
            params.append(datetime.now(timezone.utc).isoformat())

        # Add agent_id to params
        params.append(agent_id)

        # Execute update
        cursor.execute(
            f'UPDATE agents SET {", ".join(set_clauses)} WHERE agent_id = ?', params
        )

        self.conn.commit()
        logger.info(f"Agent updated: {agent_id}")

        # Return updated agent data
        return self.get_agent(agent_id)

    def delete_agent(self, agent_id):
        """Delete an agent from the registry.

        Args:
            agent_id: The agent ID

        Returns:
            True if agent was deleted, False if not found
        """
        cursor = self.conn.cursor()

        # Check if agent exists
        cursor.execute("SELECT agent_id FROM agents WHERE agent_id = ?", (agent_id,))
        if not cursor.fetchone():
            return False

        # Delete agent
        cursor.execute("DELETE FROM agents WHERE agent_id = ?", (agent_id,))

        # Delete related data
        cursor.execute(
            "DELETE FROM conversation_history WHERE agent_id = ?", (agent_id,)
        )
        cursor.execute(
            "DELETE FROM messages WHERE sender_id = ? OR recipient_id = ?",
            (agent_id, agent_id),
        )

        self.conn.commit()
        logger.info(f"Agent deleted: {agent_id}")
        return True

    def close(self):
        """Close the database connection."""
        if self.conn:
            self.conn.close()
            logger.info("Database connection closed")


# Singleton instance
_registry_instance = None


def get_registry(db_path=None):
    """Get the singleton registry instance."""
    global _registry_instance
    if _registry_instance is None:
        _registry_instance = AgentRegistry(db_path)
    return _registry_instance
