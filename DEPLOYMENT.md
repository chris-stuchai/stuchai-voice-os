# Deployment Guide

## Railway Deployment

### Prerequisites
1. Railway account: https://railway.app
2. Railway CLI installed: `npm i -g @railway/cli`

### Step 1: Initialize Railway Project

```bash
# Login to Railway
railway login

# Initialize project
railway init

# Link to existing project (if needed)
railway link <project-id>
```

### Step 2: Add Services

1. **Postgres Database:**
   ```bash
   railway add postgresql
   ```

2. **Redis (Optional):**
   ```bash
   railway add redis
   ```

3. **Backend Service:**
   - Create new service from Dockerfile
   - Set root directory to project root
   - Railway will detect Dockerfile automatically

4. **Frontend Service:**
   - Create new service for client-admin
   - Set root directory to `client-admin`
   - Use Node.js buildpack or Dockerfile

### Step 3: Configure Environment Variables

In Railway dashboard, add these environment variables:

#### Backend Service:
```
DATABASE_URL=${{Postgres.DATABASE_URL}}
REDIS_URL=${{Redis.REDIS_URL}}
JWT_SECRET_KEY=<generate-secure-random-key>
LLM_PROVIDER=openai
OPENAI_API_KEY=<your-openai-key>
ASR_PROVIDER=whisper
TTS_PROVIDER=coqui
COQUI_TTS_URL=<your-tts-service-url>
MCP_SERVER_URL=<your-mcp-server-url>
APP_ENV=production
DEBUG=false
CORS_ORIGINS=<your-frontend-url>
```

#### Frontend Service:
```
NEXT_PUBLIC_API_URL=<your-backend-url>
NEXT_PUBLIC_WS_URL=<your-websocket-url>
```

### Step 4: Deploy

```bash
# Deploy backend
railway up

# Or deploy specific service
railway up --service <service-name>
```

### Step 5: Initialize Database and Seed Data

After first deployment, initialize the database and seed default data:

```bash
# Option 1: Run the initialization script
railway run bash server/tools/init_railway.sh

# Option 2: Manual steps
railway run python -c "
import asyncio
from server.models.database import init_db
asyncio.run(init_db())
"

railway run python server/tools/seed_data.py
```

This will:
- Create all database tables
- Seed 3 default voices (Stella, Rachel, Marcus)
- Create default admin user
- Create a sample client with Stella agent

**Default Admin Credentials:**
- Email: `admin@stuchai.com`
- Password: `ChangeMe123!`

⚠️ **IMPORTANT:** Change the admin password immediately after first login!

## Docker Deployment (Local/Server)

### Using Docker Compose

```bash
# Copy environment file
cp .env.example .env
# Edit .env with your settings

# Start all services
docker-compose up -d

# View logs
docker-compose logs -f

# Stop services
docker-compose down
```

### Manual Docker Build

```bash
# Build backend
docker build -t stuchai-api .

# Build frontend
cd client-admin
docker build -t stuchai-frontend .
cd ..

# Run with docker-compose or manually
```

## Local Development Setup

### Backend
```bash
cd server
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
pip install -r requirements.txt
python main.py
```

### Frontend
```bash
cd client-admin
npm install
npm run dev
```

### Database Setup
```bash
# Install PostgreSQL locally or use Docker
docker run -d -p 5432:5432 -e POSTGRES_PASSWORD=postgres postgres:15

# Run migrations (after setting up Alembic)
cd server
alembic upgrade head
```

## Environment Variables Reference

See `.env.example` for all available configuration options.

### Required Variables:
- `DATABASE_URL`: PostgreSQL connection string
- `JWT_SECRET_KEY`: Secret key for JWT tokens
- `OPENAI_API_KEY`: OpenAI API key (if using OpenAI LLM)

### Optional Variables:
- `REDIS_URL`: Redis connection string (for caching)
- `LLM_PROVIDER`: LLM provider (openai, local, anthropic)
- `ASR_PROVIDER`: ASR provider (whisper)
- `TTS_PROVIDER`: TTS provider (coqui)
- `MCP_SERVER_URL`: MCP server URL

## Troubleshooting

### Database Connection Issues
- Verify `DATABASE_URL` is correct
- Check database is accessible from deployment environment
- Ensure firewall rules allow connections

### Frontend API Errors
- Verify `NEXT_PUBLIC_API_URL` matches backend URL
- Check CORS settings in backend
- Ensure backend is running and accessible

### Voice Service Issues
- Verify TTS/ASR services are running
- Check service URLs in environment variables
- Review service logs for errors

## Production Checklist

- [ ] Change `JWT_SECRET_KEY` to secure random value
- [ ] Set `DEBUG=false` and `APP_ENV=production`
- [ ] Configure proper CORS origins
- [ ] Set up SSL/TLS certificates
- [ ] Configure rate limiting
- [ ] Set up monitoring and logging
- [ ] Configure database backups
- [ ] Set up CI/CD pipeline
- [ ] Review security settings
- [ ] Configure domain names

