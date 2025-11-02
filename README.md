# Stuchai Voice OS

Voice Operating System for AI-driven property management + automation

## 🎯 Overview

A self-hosted real-time voice-AI agent platform that can be white-labeled and sold to property management companies and other industries. The system provides:

- Real-time voice interaction (voice-in → ASR → LLM → MCP tools → TTS → voice-out)
- Multi-tenant architecture (each client gets their own agent, settings, logs)
- Admin dashboard for managing clients, agents, and voices
- MCP server integration for taking actions (email, CRM, calendar, Slack, webhooks, etc.)
- Deployable to Railway

## 🏗️ Architecture

```
User Voice
    ↓ (WebRTC/WebSocket)
[Voice Gateway]
    ↓ ASR (Whisper)
[Text Input]
    ↓
[LLM Router] → MCP Tools → Email/CRM/DB/Automations
    ↓
[TTS Engine (Coqui)]
    ↓
User Hears Voice
```

## 🛠️ Tech Stack

| Layer | Tech |
|-------|------|
| Voice pipeline | Pipecat |
| ASR | Whisper (local or faster fork) |
| TTS | Coqui TTS (fine-tunable) |
| Backend | Python + FastAPI |
| Realtime | WebSockets (WebRTC optional) |
| LLM | Configurable (OpenAI, local, or LM Studio) |
| DB | Postgres (Railway) |
| Cache | Redis (Railway optional) |
| Dashboard | Next.js + Tailwind + shadcn/ui |
| Auth | JWT + RBAC |
| Container | Docker |
| Infra | Railway |
| MCP | Built-in MCP client interface |

## 📁 Project Structure

```
/stuchai-voice-os
  /server
    main.py
    /voice
      asr.py
      tts.py
      pipeline.py
    /agent
      llm.py
      memory.py
      mcp_client.py
      actions.py
    /api
      auth.py
      clients.py
      agents.py
      voices.py
    /models
      database.py
      schemas.py
    /tools
      voice_dataset_builder.py
  /client-admin
    pages/
    components/
    supabase/
  /shared
    config.py
    types.py
  docker-compose.yml
  Dockerfile
  README.md
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- Node.js 18+ (for local frontend development)
- Python 3.11+ (for local backend development)
- Railway account (for deployment)

### Local Development

1. **Clone and setup:**
   ```bash
   git clone <repo-url>
   cd stuchai-voice-os
   cp .env.example .env
   # Edit .env with your configuration
   ```

2. **Start with Docker:**
   ```bash
   docker-compose up -d
   ```

3. **Or run locally:**
   
   **Backend:**
   ```bash
   cd server
   pip install -r requirements.txt
   python main.py
   ```
   
   **Frontend:**
   ```bash
   cd client-admin
   npm install
   npm run dev
   ```

### Environment Variables

See `.env.example` for required variables:
- Database credentials
- Redis configuration
- LLM API keys
- JWT secrets
- Voice service URLs

## 📦 Deployment to Railway

1. **Install Railway CLI:**
   ```bash
   npm i -g @railway/cli
   railway login
   ```

2. **Initialize Railway project:**
   ```bash
   railway init
   railway link
   ```

3. **Add services:**
   - Postgres database
   - Redis (optional)
   - Web service (backend)
   - Static site (frontend)

4. **Deploy:**
   ```bash
   railway up
   ```

## 🎤 Voice Configuration

### Adding Custom Voices

Use the voice dataset builder:

```bash
python server/tools/voice_dataset_builder.py
```

This script helps:
- Record or upload voice samples
- Format dataset for Coqui TTS
- Prepare training pipeline

## 🔌 MCP Tools

Built-in MCP tools include:
- Email send
- Calendar check + schedule
- CRM note create
- Property management ticket create
- Google Drive file lookup
- Webhook tool (Make/Zapier)
- Browser tool (optional)

## 👥 Roles

- **Admin**: Chris + founders (full system access)
- **Manager**: Employees (client management)
- **Client**: Business using our product
- **Agent**: LLM personality per client

## 📝 Default Voice Settings

- **Voice name**: Stella
- **Persona**: Calm, intelligent, executive property assistant
- **Tone**: Professional, concise, reassuring, solution-oriented
- **Default Voices**: 
  - **Stella** - Primary executive assistant voice (female)
  - **Rachel** - Clear professional voice (female)
  - **Marcus** - Confident authoritative voice (male)

## 🔒 Security

- JWT-based authentication
- Role-based access control (RBAC)
- Multi-tenant data isolation
- API rate limiting
- Audit logging

## 📚 API Documentation

Once running, visit:
- Swagger UI: `http://localhost:8000/docs`
- ReDoc: `http://localhost:8000/redoc`

## 🤝 Contributing

1. Create a feature branch
2. Make your changes
3. Submit a pull request

## 📄 License

[Specify license]

## 🆘 Support

For issues and questions, please open a GitHub issue.

