"""
Shared type definitions and enums.

Provides type hints and data structures used across the application.
"""

from enum import Enum
from typing import Optional, Dict, Any, List
from datetime import datetime
from pydantic import BaseModel, EmailStr


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


class LLMProvider(str, Enum):
    """LLM provider enumeration."""
    OPENAI = "openai"
    LOCAL = "local"
    ANTHROPIC = "anthropic"


class ASRProvider(str, Enum):
    """ASR provider enumeration."""
    WHISPER = "whisper"


class TTSProvider(str, Enum):
    """TTS provider enumeration."""
    COQUI = "coqui"
    ELEVENLABS = "elevenlabs"


# API Response Models
class APIResponse(BaseModel):
    """Standard API response wrapper."""
    success: bool
    data: Optional[Any] = None
    message: Optional[str] = None
    error: Optional[str] = None


class PaginatedResponse(BaseModel):
    """Paginated response wrapper."""
    items: List[Any]
    total: int
    page: int
    page_size: int
    pages: int


# WebSocket Message Types
class WSMessageType(str, Enum):
    """WebSocket message type enumeration."""
    AUDIO = "audio"
    TEXT = "text"
    TRANSCRIPT = "transcript"
    ERROR = "error"
    STATUS = "status"


class WSMessage(BaseModel):
    """WebSocket message structure."""
    type: WSMessageType
    data: Dict[str, Any]
    timestamp: datetime = datetime.now()


# Voice Pipeline Types
class AudioFormat(str, Enum):
    """Audio format enumeration."""
    WAV = "wav"
    MP3 = "mp3"
    PCM = "pcm"
    OPUS = "opus"


class VoiceConfig(BaseModel):
    """Voice configuration."""
    voice_id: int
    name: str
    provider: str
    language: str = "en"
    speed: float = 1.0
    pitch: float = 1.0


# MCP Tool Types
class MCPTool(BaseModel):
    """MCP tool definition."""
    name: str
    description: str
    parameters: Dict[str, Any]
    returns: Dict[str, Any]


class MCPToolCall(BaseModel):
    """MCP tool call request."""
    tool_name: str
    parameters: Dict[str, Any]


class MCPToolResult(BaseModel):
    """MCP tool execution result."""
    success: bool
    data: Optional[Any] = None
    error: Optional[str] = None

