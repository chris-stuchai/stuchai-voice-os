"""
Voice pipeline module.

Orchestrates the complete voice processing pipeline:
Audio Input → ASR → LLM → TTS → Audio Output
"""

import logging
from typing import Optional
import asyncio

from server.voice.asr import get_asr_engine
from server.voice.tts import get_tts_engine
from server.agent.llm import LLMRouter
from server.models.database import get_db
from server.models.schemas import Agent, Message, MessageRole

logger = logging.getLogger(__name__)


class VoicePipeline:
    """
    Voice processing pipeline.
    
    Handles the complete flow from audio input to audio output:
    1. ASR: Convert audio to text
    2. LLM: Process text and generate response
    3. TTS: Convert response text to audio
    """
    
    def __init__(self, agent_id: int, session_id: Optional[str] = None):
        """
        Initialize voice pipeline.
        
        Args:
            agent_id: Agent ID for conversation
            session_id: Optional session ID
        """
        self.agent_id = agent_id
        self.session_id = session_id
        self.asr_engine = None
        self.tts_engine = None
        self.llm_router = None
        self.agent = None
    
    async def initialize(self) -> None:
        """
        Initialize pipeline components.
        
        Loads agent configuration, ASR, TTS, and LLM.
        """
        # Load agent from database
        from server.models.database import AsyncSessionLocal
        from sqlalchemy import select
        
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Agent).where(Agent.id == self.agent_id)
            )
            self.agent = result.scalar_one_or_none()
            
            if not self.agent:
                raise ValueError(f"Agent {self.agent_id} not found")
        
        # Initialize ASR engine
        self.asr_engine = get_asr_engine()
        
        # Initialize TTS engine with agent's voice
        voice_id = self.agent.voice_id if self.agent.voice_id else None
        self.tts_engine = get_tts_engine(voice_id=voice_id)
        
        # Initialize LLM router
        self.llm_router = LLMRouter(
            provider=self.agent.llm_provider,
            model=self.agent.llm_model,
            temperature=self.agent.llm_temperature,
            max_tokens=self.agent.llm_max_tokens,
            system_message=self.agent.system_message or self.agent.persona_prompt
        )
        
        logger.info(f"Voice pipeline initialized for agent {self.agent_id}")
    
    async def process_audio(self, audio_data: bytes) -> Optional[bytes]:
        """
        Process audio input through the complete pipeline.
        
        Args:
            audio_data: Raw audio bytes from user
            
        Returns:
            bytes: Audio response bytes, or None if error
        """
        try:
            # Step 1: ASR - Convert audio to text
            logger.debug("Processing audio through ASR...")
            user_text = await self.asr_engine.transcribe(audio_data)
            
            if not user_text or len(user_text.strip()) == 0:
                logger.warning("Empty transcription, skipping LLM/TTS")
                return None
            
            # Save user message to database
            await self._save_message(user_text, MessageRole.USER, audio_data)
            
            # Step 2: LLM - Generate response
            logger.debug(f"Processing text through LLM: {user_text}")
            response_text = await self.llm_router.generate_response(
                user_text,
                agent_id=self.agent_id,
                session_id=self.session_id,
                mcp_enabled=self.agent.mcp_enabled if hasattr(self.agent, 'mcp_enabled') else False
            )
            
            if not response_text:
                logger.warning("Empty LLM response")
                return None
            
            # Step 3: TTS - Convert response to audio
            logger.debug(f"Converting response to speech: {response_text}")
            response_audio = await self.tts_engine.synthesize(
                response_text,
                voice_id=self.agent.voice_id if self.agent.voice_id else None
            )
            
            # Save assistant message to database
            await self._save_message(response_text, MessageRole.ASSISTANT, response_audio)
            
            return response_audio
        
        except Exception as e:
            logger.error(f"Error processing audio through pipeline: {e}", exc_info=True)
            return None
    
    async def _save_message(
        self,
        content: str,
        role: MessageRole,
        audio_data: Optional[bytes] = None
    ) -> None:
        """
        Save message to database.
        
        Args:
            content: Message text content
            role: Message role (user/assistant)
            audio_data: Optional audio data to save
        """
        if not self.session_id:
            return
        
        try:
            from server.models.database import AsyncSessionLocal
            from sqlalchemy import select
            from server.models.schemas import Conversation
            
            async with AsyncSessionLocal() as db:
                # Find conversation by session_id
                result = await db.execute(
                    select(Conversation).where(Conversation.session_id == self.session_id)
                )
                conversation = result.scalar_one_or_none()
                
                if conversation:
                    # Save audio file if provided
                    audio_path = None
                    if audio_data:
                        import os
                        audio_dir = f"audio/{self.session_id}"
                        os.makedirs(audio_dir, exist_ok=True)
                        audio_path = f"{audio_dir}/{role.value}_{len(content)}.wav"
                        with open(audio_path, "wb") as f:
                            f.write(audio_data)
                    
                    # Create message record
                    message = Message(
                        conversation_id=conversation.id,
                        role=role,
                        content=content,
                        audio_path=audio_path
                    )
                    db.add(message)
                    await db.commit()
        
        except Exception as e:
            logger.error(f"Error saving message: {e}", exc_info=True)
    
    async def cleanup(self) -> None:
        """Cleanup pipeline resources."""
        if self.tts_engine:
            await self.tts_engine.close()
        logger.info("Voice pipeline cleaned up")

