"""
SQLAlchemy database models (schemas).

This module defines all database tables and relationships
for the multi-tenant voice OS platform.
"""

from datetime import datetime
from enum import Enum
from typing import Optional

from sqlalchemy import (
    Boolean, Column, DateTime, Enum as SQLEnum, ForeignKey,
    Integer, String, Text, JSON, Float
)
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func

from server.models.database import Base


class UserRole(str, Enum):
    """User role enumeration."""
    ADMIN = "admin"
    MANAGER = "manager"
    CLIENT = "client"


class ConversationStatus(str, Enum):
    """Conversation status enumeration."""
    ACTIVE = "active"
    ENDED = "ended"
    ERROR = "error"


class MessageRole(str, Enum):
    """Message role in conversation."""
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"


class User(Base):
    """
    User model for authentication and authorization.
    
    Supports multiple roles: Admin, Manager, Client
    """
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    email = Column(String(255), unique=True, index=True, nullable=False)
    hashed_password = Column(String(255), nullable=False)
    full_name = Column(String(255))
    role = Column(SQLEnum(UserRole), nullable=False, default=UserRole.CLIENT)
    
    # Relationships
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    client = relationship("Client", back_populates="users")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    last_login = Column(DateTime(timezone=True), nullable=True)
    
    # Status
    is_active = Column(Boolean, default=True)
    is_verified = Column(Boolean, default=False)


class Client(Base):
    """
    Client model representing a tenant/customer.
    
    Each client can have multiple agents and users.
    """
    __tablename__ = "clients"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, index=True)
    domain = Column(String(255), unique=True, index=True, nullable=True)
    subdomain = Column(String(100), unique=True, index=True, nullable=True)
    
    # Configuration
    settings = Column(JSON, default=dict)
    
    # Relationships
    users = relationship("User", back_populates="client")
    agents = relationship("Agent", back_populates="client", cascade="all, delete-orphan")
    conversations = relationship("Conversation", back_populates="client", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)


class Agent(Base):
    """
    Agent model representing an LLM personality per client.
    
    Each agent has a voice, persona, and configuration.
    """
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    name = Column(String(255), nullable=False)
    
    # Voice configuration
    voice_id = Column(Integer, ForeignKey("voices.id"), nullable=True)
    voice = relationship("Voice", back_populates="agents")
    
    # LLM configuration
    llm_provider = Column(String(50), default="openai")
    llm_model = Column(String(100), default="gpt-4o")
    llm_temperature = Column(Float, default=0.7)
    llm_max_tokens = Column(Integer, default=2000)
    
    # Persona configuration
    persona_prompt = Column(Text)
    system_message = Column(Text)
    
    # MCP configuration
    mcp_enabled = Column(Boolean, default=True)
    mcp_tools = Column(JSON, default=list)
    
    # Relationships
    client = relationship("Client", back_populates="agents")
    conversations = relationship("Conversation", back_populates="agent", cascade="all, delete-orphan")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)


class Voice(Base):
    """
    Voice model for TTS configuration.
    
    Stores voice models and their configurations.
    """
    __tablename__ = "voices"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(255), nullable=False, unique=True, index=True)
    description = Column(Text)
    
    # Voice characteristics
    provider = Column(String(50), default="coqui")
    model_path = Column(String(500))
    voice_id = Column(String(255))
    
    # Audio settings
    sample_rate = Column(Integer, default=24000)
    speed = Column(Float, default=1.0)
    pitch = Column(Float, default=1.0)
    
    # Metadata
    language = Column(String(10), default="en")
    gender = Column(String(20), nullable=True)
    
    # File storage
    dataset_path = Column(String(500), nullable=True)
    
    # Relationships
    agents = relationship("Agent", back_populates="voice")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Status
    is_active = Column(Boolean, default=True)


class Conversation(Base):
    """
    Conversation model tracking voice sessions.
    
    Each conversation belongs to a client and agent.
    """
    __tablename__ = "conversations"
    
    id = Column(Integer, primary_key=True, index=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=False)
    agent_id = Column(Integer, ForeignKey("agents.id"), nullable=False)
    
    # Session information
    session_id = Column(String(255), unique=True, index=True)
    status = Column(SQLEnum(ConversationStatus), default=ConversationStatus.ACTIVE)
    
    # Metadata
    user_metadata = Column(JSON, default=dict)
    duration_seconds = Column(Integer, default=0)
    
    # Relationships
    client = relationship("Client", back_populates="conversations")
    agent = relationship("Agent", back_populates="conversations")
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    
    # Timestamps
    started_at = Column(DateTime(timezone=True), server_default=func.now())
    ended_at = Column(DateTime(timezone=True), nullable=True)


class Message(Base):
    """
    Message model storing conversation transcripts.
    
    Stores both user inputs and assistant responses.
    """
    __tablename__ = "messages"
    
    id = Column(Integer, primary_key=True, index=True)
    conversation_id = Column(Integer, ForeignKey("conversations.id"), nullable=False)
    
    # Message content
    role = Column(SQLEnum(MessageRole), nullable=False)
    content = Column(Text, nullable=False)
    audio_path = Column(String(500), nullable=True)
    
    # Metadata
    message_metadata = Column(JSON, default=dict)
    tokens_used = Column(Integer, default=0)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())


class AuditLog(Base):
    """
    Audit log model for tracking system events.
    
    Logs admin actions, API calls, and system changes.
    """
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    
    # Event information
    user_id = Column(Integer, ForeignKey("users.id"), nullable=True)
    client_id = Column(Integer, ForeignKey("clients.id"), nullable=True)
    action = Column(String(100), nullable=False)
    resource_type = Column(String(50))
    resource_id = Column(Integer)
    
    # Event details
    details = Column(JSON, default=dict)
    ip_address = Column(String(45))
    user_agent = Column(String(500))
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now(), index=True)

