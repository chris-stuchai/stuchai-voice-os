"""
Database seed script.

Creates initial default data:
- Default voices (Stella and 2 others)
- Default admin user
- Sample client

Run this after initial database setup.
"""

import asyncio
import sys
import os
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from server.models.database import AsyncSessionLocal, init_db
from server.models.schemas import User, Client, Voice, Agent, UserRole
from server.agent.memory import get_password_hash
from shared.config import settings


async def seed_default_voices():
    """Seed 3 default voices for the system."""
    async with AsyncSessionLocal() as db:
        # Check if voices already exist
        from sqlalchemy import select
        result = await db.execute(select(Voice))
        existing = result.scalars().all()
        
        if existing:
            print("Voices already exist, skipping seed...")
            return existing
        
        # Create 3 default voices
        voices = [
            Voice(
                name="Stella",
                description="Calm, intelligent, executive property assistant voice. Professional and solution-oriented.",
                provider="coqui",
                voice_id="ljspeech",  # Popular Coqui TTS voice
                language="en",
                gender="female",
                sample_rate=22050,
                speed=1.0,
                pitch=1.0,
                is_active=True
            ),
            Voice(
                name="Rachel",
                description="Clear, articulate female voice. Perfect for professional communications.",
                provider="coqui",
                voice_id="tts_models/en/ljspeech/tacotron2-DDC",
                language="en",
                gender="female",
                sample_rate=22050,
                speed=1.0,
                pitch=1.0,
                is_active=True
            ),
            Voice(
                name="Marcus",
                description="Confident, authoritative male voice. Ideal for executive communications.",
                provider="coqui",
                voice_id="tts_models/en/vctk/vits",
                language="en",
                gender="male",
                sample_rate=22050,
                speed=1.0,
                pitch=1.0,
                is_active=True
            )
        ]
        
        for voice in voices:
            db.add(voice)
        
        await db.commit()
        
        for voice in voices:
            await db.refresh(voice)
        
        print(f"✅ Created {len(voices)} default voices: {[v.name for v in voices]}")
        return voices


async def seed_admin_user():
    """Seed default admin user."""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        
        # Check if admin exists
        result = await db.execute(
            select(User).where(User.email == settings.DEFAULT_ADMIN_EMAIL)
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print("Admin user already exists, skipping seed...")
            return existing
        
        # Create admin user
        admin_user = User(
            email=settings.DEFAULT_ADMIN_EMAIL,
            hashed_password=get_password_hash(settings.DEFAULT_ADMIN_PASSWORD),
            full_name="Admin User",
            role=UserRole.ADMIN,
            is_active=True,
            is_verified=True
        )
        
        db.add(admin_user)
        await db.commit()
        await db.refresh(admin_user)
        
        print(f"✅ Created admin user: {admin_user.email}")
        print(f"   Password: {settings.DEFAULT_ADMIN_PASSWORD} (please change this!)")
        return admin_user


async def seed_sample_client():
    """Seed a sample client for testing."""
    async with AsyncSessionLocal() as db:
        from sqlalchemy import select
        
        # Check if sample client exists
        result = await db.execute(
            select(Client).where(Client.name == "Demo Property Management")
        )
        existing = result.scalar_one_or_none()
        
        if existing:
            print("Sample client already exists, skipping seed...")
            return existing
        
        # Create sample client
        client = Client(
            name="Demo Property Management",
            domain="demo.stuchai.com",
            subdomain="demo",
            settings={
                "industry": "property_management",
                "timezone": "America/New_York"
            },
            is_active=True
        )
        
        db.add(client)
        await db.commit()
        await db.refresh(client)
        
        # Get Stella voice for default agent
        voice_result = await db.execute(
            select(Voice).where(Voice.name == "Stella")
        )
        stella_voice = voice_result.scalar_one_or_none()
        
        if stella_voice:
            # Create default agent for this client
            agent = Agent(
                client_id=client.id,
                name="Stella Assistant",
                voice_id=stella_voice.id,
                llm_provider="openai",
                llm_model="gpt-4o",
                llm_temperature=0.7,
                llm_max_tokens=2000,
                persona_prompt="You are Stella, a calm, intelligent, executive property assistant.",
                system_message="""You are Stella, a calm, intelligent, executive property assistant. 
You speak clearly, take action fast, and sound like a human operations manager.
Your tone is professional, concise, reassuring, and solution-oriented.
Always be helpful, efficient, and focused on solving problems.""",
                mcp_enabled=True,
                is_active=True
            )
            db.add(agent)
            await db.commit()
            await db.refresh(agent)
            print(f"✅ Created default agent '{agent.name}' for client")
        
        print(f"✅ Created sample client: {client.name}")
        return client


async def main():
    """Main seed function."""
    print("🌱 Seeding database...")
    print("=" * 50)
    
    # Initialize database
    await init_db()
    
    # Seed data
    voices = await seed_default_voices()
    admin = await seed_admin_user()
    client = await seed_sample_client()
    
    print("=" * 50)
    print("✅ Database seeding complete!")
    print("\nSummary:")
    print(f"  - Voices: {len(voices)} created")
    print(f"  - Admin user: {admin.email}")
    print(f"  - Sample client: {client.name}")
    print("\nNext steps:")
    print(f"  1. Login with admin credentials:")
    print(f"     Email: {settings.DEFAULT_ADMIN_EMAIL}")
    print(f"     Password: {settings.DEFAULT_ADMIN_PASSWORD}")
    print("  2. Change the default admin password!")
    print("  3. Configure your OpenAI API key in .env")


if __name__ == "__main__":
    asyncio.run(main())

