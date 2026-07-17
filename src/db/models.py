"""
Database models for the SWE agent.
"""

from sqlalchemy import (
    Column,
    String,
    Text,
    DateTime,
    Boolean,
    Integer,
    create_engine,
    JSON,
)
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy.sql import func
import os
from pathlib import Path
import json

# Create the database directory if it doesn't exist
DB_DIR = Path(__file__).parent.parent.parent / "data"
DB_DIR.mkdir(exist_ok=True)

# Create the database engine
DATABASE_URL = f"sqlite:///{DB_DIR}/agents.db"
engine = create_engine(DATABASE_URL)

# Create a session factory
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

# Create a base class for declarative models
Base = declarative_base()


class Agent(Base):
    """
    Agent model for storing agent configurations.
    """

    __tablename__ = "agents"

    agent_id = Column(String, primary_key=True, index=True)
    name = Column(String, index=True)
    description = Column(Text, nullable=True)
    llm_model_id = Column(String)
    mcp_tools_config_path = Column(String, nullable=True)
    initial_prompt = Column(Text, nullable=True)
    status = Column(String, default="inactive")
    config = Column(JSON, nullable=True)
    port = Column(Integer, nullable=True)
    uri = Column(String, nullable=True)
    process_id = Column(Integer, nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


class Conversation(Base):
    """
    Conversation model for storing agent conversations.
    """

    __tablename__ = "conversations"

    conversation_id = Column(String, primary_key=True, index=True)
    agent_id = Column(String, index=True)
    messages = Column(JSON)
    meta_data = Column(JSON, nullable=True)  # Changed from metadata to meta_data
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())


# Create the tables
Base.metadata.create_all(bind=engine)


def get_db():
    """
    Get a database session.

    Yields:
        A database session.
    """
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()
