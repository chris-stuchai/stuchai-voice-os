"""
Voice API routes.

Handles voice model management, upload, and configuration.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, UploadFile, File
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel
import os

from shared.config import settings
from server.models.database import get_db
from server.models.schemas import Voice, User
from server.api.auth import get_current_active_user, require_role
from server.models.schemas import UserRole

router = APIRouter()


# Pydantic models
class VoiceCreate(BaseModel):
    """Voice creation model."""
    name: str
    description: Optional[str] = None
    provider: str = "coqui"
    language: str = "en"
    gender: Optional[str] = None


class VoiceUpdate(BaseModel):
    """Voice update model."""
    name: Optional[str] = None
    description: Optional[str] = None
    sample_rate: Optional[int] = None
    speed: Optional[float] = None
    pitch: Optional[float] = None
    is_active: Optional[bool] = None


class VoiceResponse(BaseModel):
    """Voice response model."""
    id: int
    name: str
    description: Optional[str]
    provider: str
    language: str
    gender: Optional[str]
    sample_rate: int
    speed: float
    pitch: float
    is_active: bool
    
    class Config:
        from_attributes = True


@router.get("/", response_model=List[VoiceResponse])
async def list_voices(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    List all voices.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List[VoiceResponse]: List of voices
    """
    result = await db.execute(
        "SELECT * FROM voices WHERE is_active = true ORDER BY name"
    )
    voices = result.fetchall()
    return voices


@router.get("/{voice_id}", response_model=VoiceResponse)
async def get_voice(
    voice_id: int,
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get voice by ID.
    
    Args:
        voice_id: Voice ID
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        VoiceResponse: Voice data
    """
    result = await db.execute(
        f"SELECT * FROM voices WHERE id = {voice_id}"
    )
    voice = result.fetchone()
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    return voice


@router.post("/", response_model=VoiceResponse, status_code=201)
async def create_voice(
    voice_data: VoiceCreate,
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new voice (admin/manager only).
    
    Args:
        voice_data: Voice creation data
        current_user: Current authenticated admin/manager user
        db: Database session
        
    Returns:
        VoiceResponse: Created voice
    """
    new_voice = Voice(
        name=voice_data.name,
        description=voice_data.description,
        provider=voice_data.provider,
        language=voice_data.language,
        gender=voice_data.gender
    )
    db.add(new_voice)
    await db.commit()
    await db.refresh(new_voice)
    return new_voice


@router.post("/{voice_id}/upload")
async def upload_voice_dataset(
    voice_id: int,
    file: UploadFile = File(...),
    current_user: User = Depends(require_role([UserRole.ADMIN, UserRole.MANAGER])),
    db: AsyncSession = Depends(get_db)
):
    """
    Upload voice dataset for training (admin/manager only).
    
    Args:
        voice_id: Voice ID
        file: Voice dataset file (ZIP or audio files)
        current_user: Current authenticated admin/manager user
        db: Database session
        
    Returns:
        dict: Upload status
    """
    # Verify voice exists
    result = await db.execute(
        f"SELECT * FROM voices WHERE id = {voice_id}"
    )
    voice = result.fetchone()
    if not voice:
        raise HTTPException(status_code=404, detail="Voice not found")
    
    # Create dataset directory
    dataset_dir = os.path.join(
        settings.VOICE_DATASET_PATH,
        f"voice_{voice_id}"
    )
    os.makedirs(dataset_dir, exist_ok=True)
    
    # Save uploaded file
    file_path = os.path.join(dataset_dir, file.filename)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    # Update voice record
    voice.dataset_path = dataset_dir
    await db.commit()
    
    return {
        "status": "uploaded",
        "voice_id": voice_id,
        "dataset_path": dataset_dir
    }

