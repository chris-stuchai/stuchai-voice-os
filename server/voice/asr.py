"""
Automatic Speech Recognition (ASR) module.

Handles speech-to-text conversion using Whisper or other ASR providers.
"""

import os
import logging
from typing import Optional
import whisper
import numpy as np
from io import BytesIO

from shared.config import settings

logger = logging.getLogger(__name__)


class ASREngine:
    """
    ASR Engine for converting audio to text.
    
    Supports multiple providers (Whisper, etc.)
    """
    
    def __init__(self, provider: str = "whisper", model: str = None):
        """
        Initialize ASR engine.
        
        Args:
            provider: ASR provider name ("whisper", etc.)
            model: Model name/identifier
        """
        self.provider = provider
        self.model_name = model or settings.WHISPER_MODEL
        self.model = None
        
        if provider == "whisper":
            self._load_whisper()
        else:
            raise ValueError(f"Unsupported ASR provider: {provider}")
    
    def _load_whisper(self) -> None:
        """Load Whisper model."""
        try:
            logger.info(f"Loading Whisper model: {self.model_name}")
            self.model = whisper.load_model(self.model_name)
            logger.info("Whisper model loaded successfully")
        except Exception as e:
            logger.error(f"Failed to load Whisper model: {e}")
            raise
    
    async def transcribe(self, audio_data: bytes, language: str = "en") -> str:
        """
        Transcribe audio data to text.
        
        Args:
            audio_data: Raw audio bytes
            language: Language code (e.g., "en")
            
        Returns:
            str: Transcribed text
        """
        if not self.model:
            raise RuntimeError("ASR model not loaded")
        
        try:
            # Convert bytes to numpy array for Whisper
            # This is a simplified conversion - actual implementation
            # may need proper audio format handling
            audio_np = self._bytes_to_numpy(audio_data)
            
            # Transcribe with Whisper
            result = self.model.transcribe(
                audio_np,
                language=language,
                task="transcribe"
            )
            
            text = result["text"].strip()
            logger.debug(f"Transcribed text: {text}")
            return text
        
        except Exception as e:
            logger.error(f"ASR transcription error: {e}")
            raise
    
    def _bytes_to_numpy(self, audio_data: bytes) -> np.ndarray:
        """
        Convert audio bytes to numpy array.
        
        Args:
            audio_data: Raw audio bytes
            
        Returns:
            np.ndarray: Audio as numpy array
        """
        # This is a placeholder - actual implementation should
        # properly decode the audio format (WAV, MP3, etc.)
        # For now, assume it's already in the right format
        import wave
        
        try:
            # Try to read as WAV
            audio_io = BytesIO(audio_data)
            with wave.open(audio_io, 'rb') as wav_file:
                frames = wav_file.getnframes()
                sample_rate = wav_file.getframerate()
                audio_bytes = wav_file.readframes(frames)
                audio_np = np.frombuffer(audio_bytes, dtype=np.int16).astype(np.float32) / 32768.0
                return audio_np
        except Exception:
            # Fallback: assume raw PCM or handle differently
            logger.warning("Could not parse audio as WAV, using fallback conversion")
            audio_np = np.frombuffer(audio_data, dtype=np.int16).astype(np.float32) / 32768.0
            return audio_np


# Global ASR engine instance
_asr_engine: Optional[ASREngine] = None


def get_asr_engine() -> ASREngine:
    """
    Get or create global ASR engine instance.
    
    Returns:
        ASREngine: ASR engine instance
    """
    global _asr_engine
    if _asr_engine is None:
        _asr_engine = ASREngine(
            provider=settings.ASR_PROVIDER,
            model=settings.WHISPER_MODEL
        )
    return _asr_engine

