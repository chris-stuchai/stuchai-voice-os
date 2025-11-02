"""
Agent API routes.

Handles agent configuration, conversation management,
and voice session endpoints.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import json
import uuid
import logging

from server.models.database import get_db
from server.models.schemas import Agent, Conversation, ConversationStatus, User
from server.api.auth import get_current_active_user
from server.voice.pipeline import VoicePipeline
from server.agent.llm import LLMRouter

logger = logging.getLogger(__name__)

router = APIRouter()


# Pydantic models
class AgentCreate(BaseModel):
    """Agent creation model."""
    client_id: int
    name: str
    voice_id: Optional[int] = None
    llm_provider: str = "openai"
    llm_model: str = "gpt-4o"
    persona_prompt: Optional[str] = None
    system_message: Optional[str] = None
    mcp_enabled: bool = True


class AgentResponse(BaseModel):
    """Agent response model."""
    id: int
    client_id: int
    name: str
    voice_id: Optional[int]
    llm_provider: str
    llm_model: str
    persona_prompt: Optional[str]
    system_message: Optional[str]
    mcp_enabled: bool
    is_active: bool
    
    class Config:
        from_attributes = True


class ConversationResponse(BaseModel):
    """Conversation response model."""
    id: int
    client_id: int
    agent_id: int
    session_id: str
    status: ConversationStatus
    started_at: str
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[AgentResponse])
async def list_agents(
    client_id: Optional[int] = None,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List agents.
    
    Args:
        client_id: Filter by client ID (optional)
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[AgentResponse]: List of agents
    """
    from sqlalchemy import select
    if client_id:
        result = await db.execute(
            select(Agent).where(Agent.client_id == client_id)
        )
    else:
        result = await db.execute(select(Agent))
    
    agents = result.scalars().all()
    return agents


@router.get("/{agent_id}", response_model=AgentResponse)
async def get_agent(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get agent by ID.
    
    Args:
        agent_id: Agent ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        AgentResponse: Agent data
    """
    from sqlalchemy import select
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    return agent


@router.post("/{agent_id}/conversation", response_model=ConversationResponse)
async def start_conversation(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Start a new conversation with an agent.
    
    Args:
        agent_id: Agent ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        ConversationResponse: Created conversation
    """
    # Verify agent exists
    from sqlalchemy import select
    result = await db.execute(
        select(Agent).where(Agent.id == agent_id)
    )
    agent = result.scalar_one_or_none()
    if not agent:
        raise HTTPException(status_code=404, detail="Agent not found")
    
    # Create conversation
    session_id = str(uuid.uuid4())
    conversation = Conversation(
        client_id=agent.client_id,
        agent_id=agent_id,
        session_id=session_id,
        status=ConversationStatus.ACTIVE
    )
    db.add(conversation)
    await db.commit()
    await db.refresh(conversation)
    
    return conversation


@router.websocket("/{agent_id}/stream")
async def agent_voice_stream(
    websocket: WebSocket,
    agent_id: int,
    session_id: Optional[str] = None
):
    """
    WebSocket endpoint for real-time voice streaming.
    
    Handles:
    - Voice input (audio chunks)
    - ASR transcription
    - LLM processing
    - TTS audio output
    
    Args:
        websocket: WebSocket connection
        agent_id: Agent ID
        session_id: Optional session ID for conversation (can be passed as query param)
    """
    await websocket.accept()
    
    # Get session_id from query params if not provided
    if not session_id:
        query_params = dict(websocket.query_params)
        session_id = query_params.get("session_id")
    
    pipeline = None
    try:
        # Initialize voice pipeline
        pipeline = VoicePipeline(agent_id=agent_id, session_id=session_id)
        await pipeline.initialize()
        
        # Main loop: receive audio chunks and process
        while True:
            try:
                # Receive audio data (can be bytes or JSON)
                data = await websocket.receive()
                
                if "bytes" in data:
                    audio_bytes = data["bytes"]
                    # Process through pipeline: ASR -> LLM -> TTS
                    response_audio = await pipeline.process_audio(audio_bytes)
                    
                    # Send response audio back
                    if response_audio:
                        await websocket.send_bytes(response_audio)
                elif "text" in data:
                    # Handle JSON messages for control
                    import json
                    message = json.loads(data["text"])
                    if message.get("type") == "ping":
                        await websocket.send_json({"type": "pong"})
    
    except WebSocketDisconnect:
        # Cleanup on disconnect
        if pipeline:
            await pipeline.cleanup()
        logger.info("WebSocket disconnected")
    except Exception as e:
        # Handle errors
        logger.error(f"WebSocket error: {e}", exc_info=True)
        try:
            await websocket.send_json({
                "error": str(e),
                "type": "error"
            })
            await websocket.close()
        except:
            pass
        if pipeline:
            await pipeline.cleanup()


@router.get("/{agent_id}/conversations", response_model=List[ConversationResponse])
async def list_conversations(
    agent_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List conversations for an agent.
    
    Args:
        agent_id: Agent ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[ConversationResponse]: List of conversations
    """
    from sqlalchemy import select
    result = await db.execute(
        select(Conversation).where(Conversation.agent_id == agent_id).order_by(Conversation.started_at.desc())
    )
    conversations = result.scalars().all()
    return conversations

