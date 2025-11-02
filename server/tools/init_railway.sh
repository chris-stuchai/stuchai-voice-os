#!/bin/bash
# Railway initialization script
# Run this after deploying to Railway to set up the database

echo "🚂 Initializing Railway deployment..."

# Check if we're in Railway environment
if [ -z "$RAILWAY_ENVIRONMENT" ]; then
    echo "⚠️  Not running in Railway environment"
    exit 1
fi

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🗄️  Initializing database..."
python -c "
import asyncio
from server.models.database import init_db
asyncio.run(init_db())
print('Database tables created!')
"

echo "🌱 Seeding default data..."
python server/tools/seed_data.py

echo "✅ Railway initialization complete!"
echo ""
echo "Your admin credentials:"
echo "  Email: admin@stuchai.com"
echo "  Password: ChangeMe123!"
echo "  ⚠️  Please change this password immediately!"

