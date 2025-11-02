#!/bin/bash

# Setup script for Stuchai Voice OS
# This script helps set up the development environment

set -e

echo "🚀 Setting up Stuchai Voice OS..."

# Check Python version
echo "📦 Checking Python version..."
python3 --version

# Setup Python virtual environment
echo "🐍 Setting up Python virtual environment..."
cd server
if [ ! -d "venv" ]; then
    python3 -m venv venv
fi
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Setup Node.js dependencies
echo "📦 Setting up Node.js dependencies..."
cd client-admin
npm install
cd ..

# Setup shared environment file
if [ ! -f ".env" ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env with your configuration"
fi

# Create necessary directories
echo "📁 Creating necessary directories..."
mkdir -p logs
mkdir -p voice_datasets
mkdir -p server/audio

echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env with your configuration"
echo "2. Start with: docker-compose up -d"
echo "   Or run locally:"
echo "   - Backend: cd server && source venv/bin/activate && python main.py"
echo "   - Frontend: cd client-admin && npm run dev"

