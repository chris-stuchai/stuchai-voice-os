#!/bin/bash
# Test script for Stella Voice OS API

API_URL="https://stuchai-voice-os-production.up.railway.app/api/v1"

echo "🔐 Step 1: Login as admin..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@stuchai.com&password=SecurePass123!")

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')
echo "✅ Token received: ${TOKEN:0:50}..."
echo ""

echo "🏢 Step 2: Create a test client..."
CLIENT_RESPONSE=$(curl -s -X POST "$API_URL/admin/clients" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "company_name": "ABC Property Management",
    "contact_name": "John Doe",
    "contact_email": "john@abcpm.com",
    "phone": "+1-555-0123",
    "subscription_plan": "professional"
  }')

echo "$CLIENT_RESPONSE" | jq .
CLIENT_ID=$(echo $CLIENT_RESPONSE | jq -r '.id')
echo "✅ Client created with ID: $CLIENT_ID"
echo ""

echo "🤖 Step 3: Create an AI agent for this client..."
AGENT_RESPONSE=$(curl -s -X POST "$API_URL/agents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "client_id": '$CLIENT_ID',
    "name": "Stella - ABC Property Assistant",
    "llm_provider": "openai",
    "llm_model": "gpt-4o",
    "persona_prompt": "You are Stella, a professional property management assistant for ABC Property Management.",
    "system_message": "You help tenants with maintenance requests, rent inquiries, and general questions. Be helpful, professional, and efficient.",
    "mcp_enabled": true
  }')

echo "$AGENT_RESPONSE" | jq .
AGENT_ID=$(echo $AGENT_RESPONSE | jq -r '.id')
echo "✅ Agent created with ID: $AGENT_ID"
echo ""

echo "📋 Step 4: View all clients..."
curl -s -X GET "$API_URL/admin/clients" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

echo "📋 Step 5: View all agents..."
curl -s -X GET "$API_URL/agents" \
  -H "Authorization: Bearer $TOKEN" | jq .
echo ""

echo "✅ DONE! Your test client and agent are ready."
echo ""
echo "🎯 NEXT STEPS:"
echo "1. Complete voice pipeline (ASR + TTS + WebSocket)"
echo "2. Deploy admin dashboard"
echo "3. Test end-to-end voice call"

