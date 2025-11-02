# Railway Environment Variables Setup

## Required Variables for `stuchai-voice-os` Service

Set these in Railway Dashboard → Your Service → Variables:

### Critical (Required)
```
JWT_SECRET_KEY=<generate-with-openssl-rand-hex-32>
OPENAI_API_KEY=<your-openai-api-key>
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
```

### Application Settings
```
APP_ENV=production
DEBUG=false
API_V1_PREFIX=/api/v1
LOG_LEVEL=INFO
```

### LLM Configuration
```
LLM_TEMPERATURE=0.7
LLM_MAX_TOKENS=2000
```

### Voice Services
```
ASR_PROVIDER=whisper
WHISPER_MODEL=base
TTS_PROVIDER=coqui
COQUI_TTS_URL=<your-tts-service-url-if-needed>
```

### Rate Limiting
```
RATE_LIMIT_ENABLED=true
RATE_LIMIT_PER_MINUTE=60
```

### CORS (Update with your frontend URL)
```
CORS_ORIGINS=https://your-frontend.railway.app,https://your-domain.com
```

## Auto-Provided by Railway
- `DATABASE_URL` - Automatically set from Postgres service
- `PORT` - Automatically set by Railway

## Quick Setup Command

To generate JWT_SECRET_KEY:
```bash
openssl rand -hex 32
```

## After Setting Variables

1. The deployment should automatically rebuild with the fixed `requirements.txt` (MCP version fixed)
2. Once deployed, run database initialization:
   ```bash
   railway run python server/tools/seed_data.py
   ```

