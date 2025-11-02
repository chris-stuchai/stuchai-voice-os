# Quick Start Guide

Get Stuchai Voice OS running in minutes!

## Prerequisites

- Python 3.11+
- Node.js 18+
- Docker & Docker Compose (recommended)
- OpenAI API key

## 1. Clone & Setup

```bash
# Run setup script
./setup.sh

# Or manually:
cd server && pip install -r requirements.txt
cd ../client-admin && npm install
```

## 2. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env and add:
OPENAI_API_KEY=sk-your-key-here
JWT_SECRET_KEY=$(openssl rand -hex 32)
```

## 3. Start Services

### Option A: Docker (Recommended)

```bash
docker-compose up -d

# View logs
docker-compose logs -f
```

### Option B: Local Development

**Terminal 1 - Backend:**
```bash
cd server
source venv/bin/activate  # or venv\Scripts\activate on Windows
python main.py
```

**Terminal 2 - Frontend:**
```bash
cd client-admin
npm run dev
```

## 4. Initialize Database

```bash
# Run seed script to create default data
cd server
python tools/seed_data.py
```

This creates:
- ✅ 3 default voices (Stella, Rachel, Marcus)
- ✅ Admin user (admin@stuchai.com / ChangeMe123!)
- ✅ Sample client with Stella agent

## 5. Access Application

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## 6. First Login

1. Go to http://localhost:3000/login
2. Login with:
   - Email: `admin@stuchai.com`
   - Password: `ChangeMe123!`
3. **Change password immediately!**

## Next Steps

1. **Configure Voices**: Upload or fine-tune voice models in `/voices`
2. **Create Clients**: Add your first client in `/clients`
3. **Setup Agents**: Configure AI agents with personas and voices
4. **Test Voice**: Start a conversation via WebSocket API

## Railway Deployment

See [DEPLOYMENT.md](./DEPLOYMENT.md) for Railway deployment instructions.

## Troubleshooting

### Database Connection Issues
```bash
# Make sure PostgreSQL is running
docker-compose ps

# Check database URL in .env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/stuchai_voice_os
```

### Port Already in Use
```bash
# Change ports in docker-compose.yml or .env
# Backend: 8000
# Frontend: 3000
```

### Voice Services Not Available
- Coqui TTS: Set `COQUI_TTS_URL` in `.env` or use external service
- Whisper ASR: Will download models on first use (may take time)

## Need Help?

- Check logs: `docker-compose logs -f`
- Review API docs: http://localhost:8000/docs
- See [DEPLOYMENT.md](./DEPLOYMENT.md) for production setup

