#!/usr/bin/env python3
"""Quick script to seed database via API."""
import requests
import json

API_BASE = "https://stuchai-voice-os-production.up.railway.app/api/v1"

# Login
print("🔐 Logging in...")
login_resp = requests.post(
    f"{API_BASE}/auth/login",
    data={"username": "admin@stuchai.com", "password": "SecurePass123!"},
    headers={"Content-Type": "application/x-www-form-urlencoded"}
)

if login_resp.status_code != 200:
    print(f"❌ Login failed: {login_resp.text}")
    exit(1)

token = login_resp.json()["access_token"]
print("✅ Logged in!")

# Seed database
print("\n🌱 Seeding database...")
seed_resp = requests.post(
    f"{API_BASE}/admin/seed-database",
    headers={"Authorization": f"Bearer {token}"}
)

print(f"Status: {seed_resp.status_code}")
print(json.dumps(seed_resp.json(), indent=2))

if seed_resp.status_code == 200:
    print("\n✅ Database seeded successfully!")
else:
    print(f"\n❌ Error: {seed_resp.text}")

