"""
Client API routes.

Handles client-specific operations and client portal access.
"""

from typing import List
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from server.models.database import get_db
from server.models.schemas import Client, User
from server.api.auth import get_current_active_user

router = APIRouter()


@router.get("/me")
async def get_my_client(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get current user's client information.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        Client: Client data
    """
    if not current_user.client_id:
        raise HTTPException(status_code=404, detail="User has no associated client")
    
    from sqlalchemy import select
    result = await db.execute(
        select(Client).where(Client.id == current_user.client_id)
    )
    client = result.scalar_one_or_none()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.get("/agents")
async def get_client_agents(
    current_user: User = Depends(get_current_active_user),
    db: AsyncSession = Depends(get_db)
):
    """
    Get agents for current user's client.
    
    Args:
        current_user: Current authenticated user
        db: Database session
        
    Returns:
        List: List of agents
    """
    if not current_user.client_id:
        raise HTTPException(status_code=404, detail="User has no associated client")
    
    from sqlalchemy import select
    from server.models.schemas import Agent
    result = await db.execute(
        select(Agent).where(
            Agent.client_id == current_user.client_id,
            Agent.is_active == True
        )
    )
    agents = result.scalars().all()
    return agents

