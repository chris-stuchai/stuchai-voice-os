#!/bin/bash
# Script to add your first client and agent, then test

API_URL="https://stuchai-voice-os-production.up.railway.app/api/v1"

echo "🔐 Step 1: Logging in..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@stuchai.com&password=SecurePass123!")

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ Login failed!"
    echo "$LOGIN_RESPONSE"
    exit 1
fi

echo "✅ Logged in!"
echo ""

echo "🌱 Step 2: Seeding database (if needed)..."
SEED_RESPONSE=$(curl -s -X POST "$API_URL/admin/seed-database" \
  -H "Authorization: Bearer $TOKEN")
echo "$SEED_RESPONSE" | jq .
echo ""

echo "🏢 Step 3: Creating your first client..."
read -p "Enter client name (e.g., 'ABC Property Management'): " CLIENT_NAME
read -p "Enter client email: " CLIENT_EMAIL

CLIENT_RESPONSE=$(curl -s -X POST "$API_URL/admin/clients" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"name\": \"$CLIENT_NAME\",
    \"domain\": \"${CLIENT_NAME,,}.com\",
    \"subdomain\": \"${CLIENT_NAME,,}\",
    \"settings\": {
      \"industry\": \"property_management\",
      \"timezone\": \"America/New_York\"
    }
  }")

CLIENT_ID=$(echo $CLIENT_RESPONSE | jq -r '.id')

if [ "$CLIENT_ID" == "null" ] || [ -z "$CLIENT_ID" ]; then
    echo "❌ Client creation failed!"
    echo "$CLIENT_RESPONSE" | jq .
    exit 1
fi

echo "✅ Client created! ID: $CLIENT_ID"
echo "$CLIENT_RESPONSE" | jq .
echo ""

echo "🎤 Step 4: Getting available voices..."
VOICES=$(curl -s -X GET "$API_URL/voices" \
  -H "Authorization: Bearer $TOKEN")

VOICE_IDS=$(echo $VOICES | jq -r '.[] | "\(.id) - \(.name)"')
echo "$VOICE_IDS"
echo ""

read -p "Enter voice ID (1 = Stella, 2 = Rachel, 3 = Marcus): " VOICE_ID

echo ""
echo "🤖 Step 5: Creating agent..."
AGENT_NAME="${CLIENT_NAME} Assistant"
AGENT_RESPONSE=$(curl -s -X POST "$API_URL/agents" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d "{
    \"client_id\": $CLIENT_ID,
    \"name\": \"$AGENT_NAME\",
    \"voice_id\": $VOICE_ID,
    \"llm_provider\": \"openai\",
    \"llm_model\": \"gpt-4o\",
    \"persona_prompt\": \"You are Stella, a professional property management assistant for $CLIENT_NAME.\",
    \"system_message\": \"You help tenants with maintenance requests, rent inquiries, and general questions. Be helpful, professional, and efficient.\",
    \"mcp_enabled\": true
  }")

AGENT_ID=$(echo $AGENT_RESPONSE | jq -r '.id')

if [ "$AGENT_ID" == "null" ] || [ -z "$AGENT_ID" ]; then
    echo "❌ Agent creation failed!"
    echo "$AGENT_RESPONSE" | jq .
    exit 1
fi

echo "✅ Agent created! ID: $AGENT_ID"
echo "$AGENT_RESPONSE" | jq .
echo ""

echo "💬 Step 6: Starting conversation..."
CONV_RESPONSE=$(curl -s -X POST "$API_URL/agent/$AGENT_ID/conversation" \
  -H "Authorization: Bearer $TOKEN")

SESSION_ID=$(echo $CONV_RESPONSE | jq -r '.session_id')

if [ "$SESSION_ID" == "null" ] || [ -z "$SESSION_ID" ]; then
    echo "❌ Conversation creation failed!"
    echo "$CONV_RESPONSE" | jq .
    exit 1
fi

echo "✅ Conversation started! Session ID: $SESSION_ID"
echo "$CONV_RESPONSE" | jq .
echo ""

echo "✅ Setup Complete!"
echo ""
echo "📋 Summary:"
echo "  Client ID: $CLIENT_ID"
echo "  Agent ID: $AGENT_ID"
echo "  Session ID: $SESSION_ID"
echo ""
echo "🔗 Test WebSocket:"
echo "  wss://stuchai-voice-os-production.up.railway.app/api/v1/agent/$AGENT_ID/stream?session_id=$SESSION_ID"
echo ""
echo "💡 Next Steps:"
echo "  1. Open test_voice.html in a browser (see QUICK_START_GUIDE.md)"
echo "  2. Replace {AGENT_ID} with $AGENT_ID"
echo "  3. Replace {SESSION_ID} with $SESSION_ID"
echo "  4. Make sure OPENAI_API_KEY is set in Railway"
echo ""
echo "✨ You're ready to test!"

