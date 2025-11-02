# Configuration Guide

## Environment Variables

All configuration is done via environment variables. Copy `.env.example` to `.env` and configure.

## Required Configuration

### 1. OpenAI API Key

```bash
OPENAI_API_KEY=sk-your-openai-api-key-here
LLM_PROVIDER=openai
LLM_MODEL=gpt-4o
```

### 2. Database (Railway PostgreSQL)

Railway will automatically provide `DATABASE_URL`. For local development:

```bash
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/stuchai_voice_os
```

### 3. JWT Secret Key

Generate a secure random key:

```bash
# Generate secure key
openssl rand -hex 32

# Add to .env
JWT_SECRET_KEY=<generated-key>
```

## Default Voices

The system comes with 3 pre-configured voices:

1. **Stella** (Primary)
   - Voice ID: `ljspeech`
   - Type: Female, professional
   - Description: Calm, intelligent executive assistant

2. **Rachel**
   - Voice ID: `tts_models/en/ljspeech/tacotron2-DDC`
   - Type: Female, clear
   - Description: Perfect for professional communications

3. **Marcus**
   - Voice ID: `tts_models/en/vctk/vits`
   - Type: Male, authoritative
   - Description: Confident executive voice

These are seeded automatically when you run `python server/tools/seed_data.py`

## Voice Service Configuration

### Coqui TTS

```bash
TTS_PROVIDER=coqui
COQUI_TTS_URL=http://localhost:5002
```

For production, use your own Coqui TTS service or cloud provider.

### Whisper ASR

```bash
ASR_PROVIDER=whisper
WHISPER_MODEL=base  # Options: tiny, base, small, medium, large
```

Model downloads automatically on first use. Larger models = better accuracy, slower processing.

## MCP Server Configuration

```bash
MCP_SERVER_URL=http://localhost:3001
MCP_ENABLED=true
```

Set to your MCP server URL. See MCP tools documentation for setup.

## CORS Configuration

For production, configure allowed origins:

```bash
CORS_ORIGINS=https://your-frontend-domain.com,https://admin.your-domain.com
```

For local development:
```bash
CORS_ORIGINS=http://localhost:3000,http://localhost:3001
```

## Railway-Specific Configuration

Railway automatically provides:
- `DATABASE_URL` (from PostgreSQL service)
- `REDIS_URL` (if Redis service added)

You need to set:
- `OPENAI_API_KEY`
- `JWT_SECRET_KEY`
- `COQUI_TTS_URL`
- `CORS_ORIGINS`
- `APP_ENV=production`
- `DEBUG=false`

## Security Settings

**Production Checklist:**
- ✅ Generate secure `JWT_SECRET_KEY`
- ✅ Set `APP_ENV=production`
- ✅ Set `DEBUG=false`
- ✅ Configure proper `CORS_ORIGINS`
- ✅ Use HTTPS for all services
- ✅ Change default admin password
- ✅ Enable rate limiting

## Default Admin Account

After running seed script:
- Email: `admin@stuchai.com`
- Password: `ChangeMe123!`

**⚠️ CHANGE THIS IMMEDIATELY IN PRODUCTION!**

## Testing Configuration

To verify your configuration:

```bash
# Test database connection
python -c "from server.models.database import init_db; import asyncio; asyncio.run(init_db())"

# Test OpenAI connection
python -c "from server.agent.llm import LLMRouter; import asyncio; router = LLMRouter(); print('OpenAI configured')"

# Test voice services
# Start Coqui TTS service locally or configure URL
```

## Troubleshooting

### OpenAI API Errors
- Verify API key is correct
- Check account has credits
- Verify model name is available (`gpt-4o`)

### Voice Service Errors
- Verify Coqui TTS service is running
- Check `COQUI_TTS_URL` is accessible
- Test TTS API endpoint manually

### Database Connection Errors
- Verify `DATABASE_URL` format
- Check database is accessible
- Verify credentials are correct

