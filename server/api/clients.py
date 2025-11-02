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
    
    result = await db.execute(
        f"SELECT * FROM clients WHERE id = {current_user.client_id}"
    )
    client = result.fetchone()
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
    
    result = await db.execute(
        f"SELECT * FROM agents WHERE client_id = {current_user.client_id} AND is_active = true"
    )
    agents = result.fetchall()
    return agents

