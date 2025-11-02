# Setup GitHub & Railway

## ✅ Completed
- ✅ Git repository initialized locally
- ✅ Initial commit created (57 files)
- ✅ Railway CLI installed and authenticated

## 🚀 Next Steps

### 1. Create GitHub Repository

**Option A: Using GitHub CLI (if installed):**
```bash
gh repo create stuchai-voice-os --public --source=. --remote=origin --push
```

**Option B: Manual GitHub Setup:**
1. Go to https://github.com/new
2. Repository name: `stuchai-voice-os`
3. Description: "Voice Operating System for AI-driven property management + automation"
4. Public or Private (your choice)
5. **Don't** check any boxes (README, .gitignore, license) - we already have them
6. Click "Create repository"

Then run:
```bash
git remote add origin https://github.com/YOUR-USERNAME/stuchai-voice-os.git
git push -u origin main
```

### 2. Create Railway Project

Run this command in your terminal:
```bash
railway init
```

When prompted:
- Project name: `stuchai-voice-os` (or any name you prefer)
- Choose "Empty Project" or "From GitHub" if you want to link to GitHub

This will create a `.railway` folder and link your project.

### 3. Add Services to Railway

After creating the project, add services:

**PostgreSQL Database:**
```bash
railway add postgresql
```

**Redis (Optional):**
```bash
railway add redis
```

**Backend Service:**
1. In Railway dashboard, click "New Service"
2. Select "GitHub Repo" and connect your repo
3. Or select "Empty Service" and configure:
   - Root directory: `/` (project root)
   - Build command: (auto-detected from Dockerfile)
   - Start command: `uvicorn server.main:app --host 0.0.0.0 --port $PORT`

**Frontend Service:**
1. Create another service for the frontend
2. Root directory: `/client-admin`
3. Build command: `npm run build`
4. Start command: `npm start`

### 4. Configure Environment Variables

In Railway dashboard, go to your backend service → Variables:

```
OPENAI_API_KEY=sk-your-key-here
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
TTS_PROVIDER=coqui
COQUI_TTS_URL=your-tts-service-url
MCP_SERVER_URL=your-mcp-server-url
APP_ENV=production
DEBUG=false
CORS_ORIGINS=https://your-frontend-domain.railway.app
```

Railway automatically provides:
- `DATABASE_URL` (from PostgreSQL service)
- `REDIS_URL` (if Redis added)

### 5. Initialize Database

After first deployment:
```bash
railway run python server/tools/seed_data.py
```

## Quick Commands Reference

```bash
# Check Railway status
railway status

# View logs
railway logs

# Run commands
railway run python server/tools/seed_data.py

# Deploy
railway up

# List services
railway service
```

## Need Help?

- Railway Docs: https://docs.railway.app
- GitHub CLI: https://cli.github.com

