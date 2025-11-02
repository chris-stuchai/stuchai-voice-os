# 🚀 Quick Start Guide - Add Your First Client & Test

## Step 1: Seed the Database (One Time Setup)

First, let's create the default voices and a demo setup:

### Option A: Using the API Docs (Easiest!)
1. Open: https://stuchai-voice-os-production.up.railway.app/docs
2. Find `/api/v1/admin/seed-database` (POST)
3. Click "Try it out"
4. Click "Authorize" at the top, login with:
   - Email: `admin@stuchai.com`
   - Password: `SecurePass123!`
5. Click "Execute"

This creates:
- ✅ 3 default voices (Stella, Rachel, Marcus)
- ✅ Demo client
- ✅ Demo agent

---

## Step 2: Add Your First Real Client

### Via API Docs:
1. Go to `/api/v1/admin/clients` (POST)
2. Use this JSON:
```json
{
  "name": "ABC Property Management",
  "domain": "abcpm.com",
  "subdomain": "abc",
  "settings": {
    "industry": "property_management",
    "timezone": "America/New_York"
  }
}
```

### Via cURL:
```bash
# 1. Login and get token
TOKEN=$(curl -s -X POST "https://stuchai-voice-os-production.up.railway.app/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@stuchai.com&password=SecurePass123!" | jq -r '.access_token')

# 2. Create client
curl -X POST "https://stuchai-voice-os-production.up.railway.app/api/v1/admin/clients" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "ABC Property Management",
    "domain": "abcpm.com",
    "subdomain": "abc",
    "settings": {"industry": "property_management"}
  }' | jq .

# Save the client ID from the response!
```

---

## Step 3: Create an Agent for Your Client

Replace `{CLIENT_ID}` with the ID from Step 2:

```bash
curl -X POST "https://stuchai-voice-os-production.up.railway.app/api/v1/agents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": {CLIENT_ID},
    "name": "Stella - ABC Assistant",
    "voice_id": 1,
    "llm_provider": "openai",
    "llm_model": "gpt-4o",
    "persona_prompt": "You are Stella, a professional property management assistant for ABC Property Management.",
    "system_message": "You help tenants with maintenance requests, rent inquiries, and general questions. Be helpful, professional, and efficient.",
    "mcp_enabled": true
  }' | jq .

# Save the agent_id from the response!
```

**Note:** `voice_id: 1` is Stella. To check available voices:
```bash
curl -X GET "https://stuchai-voice-os-production.up.railway.app/api/v1/voices" \
  -H "Authorization: Bearer $TOKEN" | jq .
```

---

## Step 4: Start a Conversation

```bash
curl -X POST "https://stuchai-voice-os-production.up.railway.app/api/v1/agent/{AGENT_ID}/conversation" \
  -H "Authorization: Bearer $TOKEN" | jq .

# Save the session_id from the response!
```

---

## Step 5: Test Voice Streaming (WebSocket)

### Option A: Using a Simple HTML Test Page

Create `test_voice.html`:

```html
<!DOCTYPE html>
<html>
<head>
    <title>Voice Test</title>
</head>
<body>
    <h1>Stella Voice Test</h1>
    <button id="startBtn">Start Recording</button>
    <button id="stopBtn" disabled>Stop</button>
    <div id="status"></div>
    
    <script>
        const API_URL = 'wss://stuchai-voice-os-production.up.railway.app/api/v1/agent/{AGENT_ID}/stream';
        const SESSION_ID = '{SESSION_ID}'; // From Step 4
        
        let mediaRecorder;
        let websocket;
        let audioChunks = [];
        
        const startBtn = document.getElementById('startBtn');
        const stopBtn = document.getElementById('stopBtn');
        const status = document.getElementById('status');
        
        startBtn.onclick = async () => {
            status.textContent = 'Starting...';
            
            // Get microphone access
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            
            // Setup WebSocket
            websocket = new WebSocket(`${API_URL}?session_id=${SESSION_ID}`);
            
            websocket.onopen = () => {
                status.textContent = 'Connected! Recording...';
                startBtn.disabled = true;
                stopBtn.disabled = false;
                
                // Start recording
                mediaRecorder = new MediaRecorder(stream);
                mediaRecorder.start(100); // Send chunks every 100ms
                
                mediaRecorder.ondataavailable = (event) => {
                    if (event.data.size > 0 && websocket.readyState === WebSocket.OPEN) {
                        // Convert audio blob to array buffer
                        event.data.arrayBuffer().then(buffer => {
                            websocket.send(buffer);
                        });
                    }
                };
            };
            
            websocket.onmessage = (event) => {
                // Received audio response
                const audio = new Audio();
                const blob = new Blob([event.data], { type: 'audio/wav' });
                audio.src = URL.createObjectURL(blob);
                audio.play();
            };
            
            websocket.onerror = (error) => {
                status.textContent = 'Error: ' + error;
            };
        };
        
        stopBtn.onclick = () => {
            if (mediaRecorder && mediaRecorder.state !== 'inactive') {
                mediaRecorder.stop();
            }
            if (websocket) {
                websocket.close();
            }
            status.textContent = 'Stopped';
            startBtn.disabled = false;
            stopBtn.disabled = true;
        };
    </script>
</body>
</html>
```

**Important:** Replace `{AGENT_ID}` and `{SESSION_ID}` with your actual values!

Then open this file in Chrome/Firefox and click "Start Recording".

---

### Option B: Using Python Script

Create `test_voice.py`:

```python
import asyncio
import websockets
import audioop
import pyaudio

# Configuration
AGENT_ID = 1  # Replace with your agent ID
SESSION_ID = "your-session-id"  # Replace with session ID from Step 4
WS_URL = f"wss://stuchai-voice-os-production.up.railway.app/api/v1/agent/{AGENT_ID}/stream?session_id={SESSION_ID}"

# Audio settings
CHUNK = 1024
FORMAT = pyaudio.paInt16
CHANNELS = 1
RATE = 16000

async def test_voice():
    async with websockets.connect(WS_URL) as websocket:
        print("Connected! Recording... (say something)")
        
        # Initialize PyAudio
        p = pyaudio.PyAudio()
        stream = p.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=RATE,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        # Send audio chunks
        async def send_audio():
            while True:
                data = stream.read(CHUNK)
                await websocket.send(data)
                await asyncio.sleep(0.1)
        
        # Receive audio responses
        async def receive_audio():
            async for message in websocket:
                # Save received audio
                with open("response.wav", "wb") as f:
                    f.write(message)
                print("Received audio response!")
        
        # Run both tasks
        await asyncio.gather(
            send_audio(),
            receive_audio()
        )

if __name__ == "__main__":
    asyncio.run(test_voice())
```

---

## Step 6: Test Text-Only (Without Voice)

Test the LLM directly without audio:

```bash
# This tests the backend without needing audio setup
curl -X POST "https://stuchai-voice-os-production.up.railway.app/api/v1/agent/{AGENT_ID}/message" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "message": "Hello, what can you help me with?",
    "session_id": "{SESSION_ID}"
  }' | jq .
```

**Note:** You might need to create this endpoint if it doesn't exist. For now, use the WebSocket method above.

---

## ⚠️ **Important Setup Notes**

### 1. **OpenAI API Key Required**
Make sure `OPENAI_API_KEY` is set in Railway environment variables:
- Go to Railway dashboard → Your service → Variables
- Add: `OPENAI_API_KEY=sk-your-key-here`

### 2. **TTS Service**
Coqui TTS needs to be running separately or you'll get TTS errors. For testing:
- You can temporarily return mock audio in the TTS engine
- Or deploy Coqui TTS as a separate service

### 3. **ASR (Whisper)**
Whisper model will download on first use (can be slow). Consider:
- Pre-loading in Dockerfile
- Using a faster model like "tiny" for testing

---

## 🎯 **Quick Test Checklist**

- [ ] Database seeded (3 voices created)
- [ ] Client created
- [ ] Agent created for client
- [ ] Conversation started (session_id obtained)
- [ ] WebSocket connection successful
- [ ] Audio input working
- [ ] Audio output received

---

## 🐛 **Troubleshooting**

**WebSocket won't connect?**
- Check Railway logs: Railway dashboard → Deployments → Logs
- Verify agent_id and session_id are correct
- Make sure service is running (check `/health` endpoint)

**No audio response?**
- Check OpenAI API key is set
- Check Railway logs for errors
- Verify TTS service is accessible (or mock it for testing)

**ASR not working?**
- Whisper model needs to download first time (wait ~2-5 minutes)
- Check logs for download progress

---

## 📞 **Need Help?**
Check logs in Railway or the API docs at:
https://stuchai-voice-os-production.up.railway.app/docs

