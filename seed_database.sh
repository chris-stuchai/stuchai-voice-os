#!/bin/bash
# Seed the database via API

API_URL="https://stuchai-voice-os-production.up.railway.app/api/v1"

echo "🔐 Logging in as admin..."
LOGIN_RESPONSE=$(curl -s -X POST "$API_URL/auth/login" \
  -H "Content-Type: application/x-www-form-urlencoded" \
  -d "username=admin@stuchai.com&password=SecurePass123!")

TOKEN=$(echo $LOGIN_RESPONSE | jq -r '.access_token')

if [ "$TOKEN" == "null" ] || [ -z "$TOKEN" ]; then
    echo "❌ Login failed!"
    echo "$LOGIN_RESPONSE" | jq .
    exit 1
fi

echo "✅ Login successful!"
echo ""

echo "🌱 Seeding database..."
SEED_RESPONSE=$(curl -s -X POST "$API_URL/admin/seed-database" \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json")

echo "$SEED_RESPONSE" | jq .
echo ""
echo "✅ Database seeded successfully!"

