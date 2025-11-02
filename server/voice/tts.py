"""
Text-to-Speech (TTS) module.

Handles text-to-audio conversion using Coqui TTS or other providers.
"""

import os
import logging
from typing import Optional
import httpx
import asyncio
from io import BytesIO

from shared.config import settings

logger = logging.getLogger(__name__)


class TTSEngine:
    """
    TTS Engine for converting text to audio.
    
    Supports multiple providers (Coqui TTS, etc.)
    """
    
    def __init__(self, provider: str = "coqui", voice_id: str = None):
        """
        Initialize TTS engine.
        
        Args:
            provider: TTS provider name ("coqui", etc.)
            voice_id: Voice model identifier
        """
        self.provider = provider
        self.voice_id = voice_id or "default"
        self.client = None
        
        if provider == "coqui":
            self._init_coqui()
        else:
            raise ValueError(f"Unsupported TTS provider: {provider}")
    
    def _init_coqui(self) -> None:
        """Initialize Coqui TTS client."""
        self.base_url = settings.COQUI_TTS_URL
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info(f"Initialized Coqui TTS client: {self.base_url}")
    
    async def synthesize(
        self,
        text: str,
        voice_id: Optional[str] = None,
        speed: float = 1.0,
        language: str = "en"
    ) -> bytes:
        """
        Synthesize text to speech audio.
        
        Args:
            text: Text to synthesize
            voice_id: Voice identifier (overrides default)
            speed: Speech speed multiplier
            language: Language code
            
        Returns:
            bytes: Audio data (WAV format)
        """
        if not self.client:
            raise RuntimeError("TTS client not initialized")
        
        voice = voice_id or self.voice_id
        
        try:
            # Call Coqui TTS API
            response = await self.client.post(
                f"{self.base_url}/api/tts",
                json={
                    "text": text,
                    "voice_id": voice,
                    "language": language,
                    "speed": speed
                }
            )
            response.raise_for_status()
            
            # Return audio bytes
            audio_data = response.content
            logger.debug(f"Generated audio: {len(audio_data)} bytes")
            return audio_data
        
        except httpx.RequestError as e:
            logger.error(f"TTS API request error: {e}")
            raise
        except Exception as e:
            logger.error(f"TTS synthesis error: {e}")
            raise
    
    async def close(self) -> None:
        """Close TTS client connection."""
        if self.client:
            await self.client.aclose()
            self.client = None


# Global TTS engine instance
_tts_engine: Optional[TTSEngine] = None


def get_tts_engine(voice_id: Optional[str] = None) -> TTSEngine:
    """
    Get or create global TTS engine instance.
    
    Args:
        voice_id: Optional voice identifier
        
    Returns:
        TTSEngine: TTS engine instance
    """
    global _tts_engine
    if _tts_engine is None or voice_id:
        _tts_engine = TTSEngine(
            provider=settings.TTS_PROVIDER,
            voice_id=voice_id
        )
    return _tts_engine

