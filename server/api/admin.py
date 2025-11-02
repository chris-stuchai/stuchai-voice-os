"""
Admin API routes.

Handles admin-only operations for managing clients, users, agents,
and system-wide configurations.
"""

from typing import List, Optional
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.ext.asyncio import AsyncSession
from pydantic import BaseModel, EmailStr

from shared.config import settings
from server.models.database import get_db
from server.models.schemas import User, Client, Agent, UserRole
from server.api.auth import get_current_active_user, require_role

router = APIRouter()


# Pydantic models
class ClientCreate(BaseModel):
    """Client creation model."""
    name: str
    domain: Optional[str] = None
    subdomain: Optional[str] = None
    settings: dict = {}


class ClientUpdate(BaseModel):
    """Client update model."""
    name: Optional[str] = None
    domain: Optional[str] = None
    subdomain: Optional[str] = None
    settings: Optional[dict] = None
    is_active: Optional[bool] = None


class ClientResponse(BaseModel):
    """Client response model."""
    id: int
    name: str
    domain: Optional[str]
    subdomain: Optional[str]
    settings: dict
    is_active: bool
    
    class Config:
        from_attributes = True


class UserCreateAdmin(BaseModel):
    """Admin user creation model."""
    email: EmailStr
    password: str
    full_name: Optional[str] = None
    role: UserRole
    client_id: Optional[int] = None


class UserUpdateAdmin(BaseModel):
    """Admin user update model."""
    email: Optional[EmailStr] = None
    full_name: Optional[str] = None
    role: Optional[UserRole] = None
    client_id: Optional[int] = None
    is_active: Optional[bool] = None


class UserResponseAdmin(BaseModel):
    """Admin user response model."""
    id: int
    email: str
    full_name: Optional[str]
    role: UserRole
    client_id: Optional[int]
    is_active: bool
    
    class Config:
        from_attributes = True


# Admin-only dependency
admin_only = require_role([UserRole.ADMIN, UserRole.MANAGER])


@router.get("/clients", response_model=List[ClientResponse])
async def list_clients(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(admin_only),
    db: AsyncSession = Depends(get_db)
):
    """
    List all clients (admin/manager only).
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated admin/manager user
        db: Database session
        
    Returns:
        List[ClientResponse]: List of clients
    """
    result = await db.execute(
        f"SELECT * FROM clients ORDER BY created_at DESC LIMIT {limit} OFFSET {skip}"
    )
    clients = result.fetchall()
    return clients


@router.post("/clients", response_model=ClientResponse, status_code=status.HTTP_201_CREATED)
async def create_client(
    client_data: ClientCreate,
    current_user: User = Depends(admin_only),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new client (admin/manager only).
    
    Args:
        client_data: Client creation data
        current_user: Current authenticated admin/manager user
        db: Database session
        
    Returns:
        ClientResponse: Created client
    """
    new_client = Client(
        name=client_data.name,
        domain=client_data.domain,
        subdomain=client_data.subdomain,
        settings=client_data.settings
    )
    db.add(new_client)
    await db.commit()
    await db.refresh(new_client)
    return new_client


@router.get("/clients/{client_id}", response_model=ClientResponse)
async def get_client(
    client_id: int,
    current_user: User = Depends(admin_only),
    db: AsyncSession = Depends(get_db)
):
    """
    Get client by ID (admin/manager only).
    
    Args:
        client_id: Client ID
        current_user: Current authenticated admin/manager user
        db: Database session
        
    Returns:
        ClientResponse: Client data
    """
    result = await db.execute(
        f"SELECT * FROM clients WHERE id = {client_id}"
    )
    client = result.fetchone()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    return client


@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(
    client_id: int,
    client_data: ClientUpdate,
    current_user: User = Depends(admin_only),
    db: AsyncSession = Depends(get_db)
):
    """
    Update client (admin/manager only).
    
    Args:
        client_id: Client ID
        client_data: Client update data
        current_user: Current authenticated admin/manager user
        db: Database session
        
    Returns:
        ClientResponse: Updated client
    """
    result = await db.execute(
        f"SELECT * FROM clients WHERE id = {client_id}"
    )
    client = result.fetchone()
    if not client:
        raise HTTPException(status_code=404, detail="Client not found")
    
    # Update fields
    if client_data.name is not None:
        client.name = client_data.name
    if client_data.domain is not None:
        client.domain = client_data.domain
    if client_data.subdomain is not None:
        client.subdomain = client_data.subdomain
    if client_data.settings is not None:
        client.settings = client_data.settings
    if client_data.is_active is not None:
        client.is_active = client_data.is_active
    
    await db.commit()
    await db.refresh(client)
    return client


@router.get("/users", response_model=List[UserResponseAdmin])
async def list_users(
    skip: int = 0,
    limit: int = 100,
    current_user: User = Depends(admin_only),
    db: AsyncSession = Depends(get_db)
):
    """
    List all users (admin/manager only).
    
    Args:
        skip: Number of records to skip
        limit: Maximum number of records to return
        current_user: Current authenticated admin/manager user
        db: Database session
        
    Returns:
        List[UserResponseAdmin]: List of users
    """
    result = await db.execute(
        f"SELECT * FROM users ORDER BY created_at DESC LIMIT {limit} OFFSET {skip}"
    )
    users = result.fetchall()
    return users


@router.post("/users", response_model=UserResponseAdmin, status_code=status.HTTP_201_CREATED)
async def create_user(
    user_data: UserCreateAdmin,
    current_user: User = Depends(admin_only),
    db: AsyncSession = Depends(get_db)
):
    """
    Create a new user (admin/manager only).
    
    Args:
        user_data: User creation data
        current_user: Current authenticated admin/manager user
        db: Database session
        
    Returns:
        UserResponseAdmin: Created user
    """
    from server.agent.memory import get_password_hash
    
    # Check if user exists
    result = await db.execute(
        f"SELECT * FROM users WHERE email = '{user_data.email}'"
    )
    existing = result.fetchone()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Email already registered"
        )
    
    new_user = User(
        email=user_data.email,
        hashed_password=get_password_hash(user_data.password),
        full_name=user_data.full_name,
        role=user_data.role,
        client_id=user_data.client_id
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user


@router.get("/stats")
async def get_stats(
    current_user: User = Depends(admin_only),
    db: AsyncSession = Depends(get_db)
):
    """
    Get system statistics (admin/manager only).
    
    Args:
        current_user: Current authenticated admin/manager user
        db: Database session
        
    Returns:
        dict: System statistics
    """
    # Get counts
    clients_result = await db.execute("SELECT COUNT(*) FROM clients")
    users_result = await db.execute("SELECT COUNT(*) FROM users")
    agents_result = await db.execute("SELECT COUNT(*) FROM agents")
    conversations_result = await db.execute("SELECT COUNT(*) FROM conversations")
    
    return {
        "total_clients": clients_result.scalar() or 0,
        "total_users": users_result.scalar() or 0,
        "total_agents": agents_result.scalar() or 0,
        "total_conversations": conversations_result.scalar() or 0,
    }

