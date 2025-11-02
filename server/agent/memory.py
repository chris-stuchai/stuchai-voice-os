"""
Memory module for conversation history and context management.

Also includes password hashing utilities.
"""

import logging
from typing import List, Dict, Optional
from datetime import datetime
from passlib.context import CryptContext

from server.models.database import AsyncSessionLocal
from server.models.schemas import Message, MessageRole, Conversation

logger = logging.getLogger(__name__)

# Password hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")


def get_password_hash(password: str) -> str:
    """
    Hash a password.
    
    Args:
        password: Plain text password
        
    Returns:
        str: Hashed password
    """
    return pwd_context.hash(password)


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """
    Verify a password against its hash.
    
    Args:
        plain_password: Plain text password
        hashed_password: Hashed password
        
    Returns:
        bool: True if password matches
    """
    return pwd_context.verify(plain_password, hashed_password)


class ConversationMemory:
    """
    Manages conversation history and context.
    
    Stores and retrieves messages for maintaining conversation state.
    """
    
    def __init__(self, session_id: str):
        """
        Initialize conversation memory.
        
        Args:
            session_id: Conversation session ID
        """
        self.session_id = session_id
        self.messages: List[Dict] = []
        self.loaded = False
    
    async def load_history(self, limit: int = 20) -> None:
        """
        Load conversation history from database.
        
        Args:
            limit: Maximum number of messages to load
        """
        if self.loaded:
            return
        
        try:
            async with AsyncSessionLocal() as db:
                # Find conversation
                result = await db.execute(
                    f"SELECT * FROM conversations WHERE session_id = '{self.session_id}'"
                )
                conversation = result.fetchone()
                
                if conversation:
                    # Load messages
                    result = await db.execute(
                        f"SELECT * FROM messages WHERE conversation_id = {conversation.id} "
                        f"ORDER BY created_at DESC LIMIT {limit}"
                    )
                    messages = result.fetchall()
                    
                    # Convert to dict format and reverse (oldest first)
                    self.messages = [
                        {
                            "role": msg.role.value,
                            "content": msg.content
                        }
                        for msg in reversed(messages)
                    ]
                    
                    logger.debug(f"Loaded {len(self.messages)} messages for session {self.session_id}")
                
                self.loaded = True
        
        except Exception as e:
            logger.error(f"Error loading conversation history: {e}", exc_info=True)
    
    async def add_message(self, role: MessageRole, content: str) -> None:
        """
        Add message to memory.
        
        Args:
            role: Message role (user/assistant)
            content: Message content
        """
        self.messages.append({
            "role": role.value,
            "content": content
        })
        
        # Keep only recent messages in memory (e.g., last 20)
        if len(self.messages) > 20:
            self.messages = self.messages[-20:]
    
    def get_history(self) -> List[Dict]:
        """
        Get conversation history.
        
        Returns:
            List[Dict]: List of messages
        """
        return self.messages.copy()
    
    async def clear(self) -> None:
        """Clear conversation memory."""
        self.messages = []
        self.loaded = False

