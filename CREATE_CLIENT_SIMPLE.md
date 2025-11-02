# 🎯 Simple Guide: Create Your First Client

## Method 1: Use the Visual API Docs (Easiest!)

### Step 1: Open the API Documentation
Go to: **https://stuchai-voice-os-production.up.railway.app/docs**

You'll see a page with all the available endpoints listed.

### Step 2: Login to Get a Token
1. Click the **"Authorize"** button at the top right (green button)
2. You'll see a popup with two fields:
   - **username**: `admin@stuchai.com`
   - **password**: `SecurePass123!`
3. Click **"Authorize"** at the bottom
4. Click **"Close"** - you're now logged in!

### Step 3: Seed the Database (First Time Only)
1. Scroll down and find **`POST /api/v1/admin/seed-database`**
2. Click on it to expand
3. Click the **"Try it out"** button
4. Click **"Execute"** (the blue button)
5. You should see a response saying voices were created ✅

### Step 4: Create Your Client
1. Find **`POST /api/v1/admin/clients`**
2. Click to expand it
3. Click **"Try it out"**
4. You'll see a JSON box - replace it with this:

```json
{
  "name": "My First Client",
  "domain": "myclient.com",
  "subdomain": "myclient",
  "settings": {
    "industry": "property_management",
    "timezone": "America/New_York"
  }
}
```

5. Click **"Execute"**
6. **IMPORTANT**: Look at the response - you'll see an `"id"` field. **Copy that number!** That's your Client ID.

### Step 5: Check Available Voices
1. Find **`GET /api/v1/voices`**
2. Click **"Try it out"** → **"Execute"**
3. You'll see a list of voices with IDs (usually 1=Stella, 2=Rachel, 3=Marcus)
4. Note the ID of the voice you want (probably `1` for Stella)

### Step 6: Create an Agent
1. Find **`POST /api/v1/agents`**
2. Click **"Try it out"**
3. Replace the JSON with this (use YOUR Client ID from Step 4):

```json
{
  "client_id": 1,
  "name": "My First Agent",
  "voice_id": 1,
  "llm_provider": "openai",
  "llm_model": "gpt-4o",
  "persona_prompt": "You are Stella, a helpful property management assistant.",
  "system_message": "You are Stella, a calm, intelligent, executive property assistant. You speak clearly, take action fast, and sound like a human operations manager.",
  "mcp_enabled": true
}
```

**Replace `"client_id": 1` with your actual Client ID from Step 4!**

4. Click **"Execute"**
5. **Copy the `"id"` from the response** - that's your Agent ID!

### Step 7: Start a Conversation
1. Find **`POST /api/v1/agent/{agent_id}/conversation`**
2. Click **"Try it out"**
3. In the path, replace `{agent_id}` with your Agent ID from Step 6
4. Click **"Execute"**
5. **Copy the `"session_id"`** from the response!

---

## Method 2: Use the Automated Script

I created a script that does everything for you:

```bash
./add_first_client.sh
```

Just run it and answer the prompts!

---

## Method 3: Copy-Paste Terminal Commands

### Step 1: Get Your Login Token
```bash
curl -X POST "https://stuchai-voice-os-production.up.railway.app/api/v1/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@stuchai.com&password=SecurePass123!" \
  | jq -r '.access_token'
```

**Copy the token that appears!**

### Step 2: Seed Database
```bash
# Replace YOUR_TOKEN_HERE with the token from Step 1
curl -X POST "https://stuchai-voice-os-production.up.railway.app/api/v1/admin/seed-database" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  | jq .
```

### Step 3: Create Client
```bash
# Replace YOUR_TOKEN_HERE with your token
curl -X POST "https://stuchai-voice-os-production.up.railway.app/api/v1/admin/clients" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "name": "My First Client",
    "domain": "myclient.com",
    "subdomain": "myclient",
    "settings": {
      "industry": "property_management"
    }
  }' | jq .

# Look for "id" in the response - that's your CLIENT_ID!
```

### Step 4: Create Agent
```bash
# Replace YOUR_TOKEN_HERE and CLIENT_ID (from Step 3)
curl -X POST "https://stuchai-voice-os-production.up.railway.app/api/v1/agents" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": CLIENT_ID,
    "name": "My First Agent",
    "voice_id": 1,
    "llm_provider": "openai",
    "llm_model": "gpt-4o",
    "mcp_enabled": true
  }' | jq .

# Look for "id" in the response - that's your AGENT_ID!
```

### Step 5: Start Conversation
```bash
# Replace YOUR_TOKEN_HERE and AGENT_ID (from Step 4)
curl -X POST "https://stuchai-voice-os-production.up.railway.app/api/v1/agent/AGENT_ID/conversation" \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  | jq .

# Look for "session_id" in the response - that's your SESSION_ID!
```

---

## 🎯 Quick Reference: What Each ID Means

- **Client ID**: The ID of your client company (you create this)
- **Agent ID**: The ID of your AI agent (you create this for a client)
- **Voice ID**: Pre-defined voices (1=Stella, 2=Rachel, 3=Marcus)
- **Session ID**: A conversation session (created when you start talking)

---

## ✅ Test It!

Once you have:
- ✅ Agent ID
- ✅ Session ID

Open `test_voice_conversation.html` in your browser and enter:
- **Agent ID**: Your agent ID
- **Session ID**: Your session ID
- Click "Start Conversation"!

---

## 🆘 Still Confused?

**Use Method 1 (API Docs)** - it's visual and shows you exactly what's happening at each step!

Just go to: https://stuchai-voice-os-production.up.railway.app/docs

Everything is clickable and shows you the responses!

