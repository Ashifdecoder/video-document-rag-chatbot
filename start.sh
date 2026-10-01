#!/bin/bash
set -e

echo "🚀 Starting Video & Audio RAG Chatbot"
echo ""

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi

echo "✅ Docker found"

# Create backend .env if it doesn't exist
if [ ! -f backend/.env ]; then
    echo "📝 Creating backend/.env from template"
    cp backend/.env.example backend/.env
    echo "⚠️  Please add your OPENAI_API_KEY to backend/.env"
fi

# Check for OPENAI_API_KEY
if grep -q "sk-" backend/.env; then
    echo "✅ OPENAI_API_KEY is configured"
else
    echo "❌ OPENAI_API_KEY not set. Edit backend/.env and add your key."
    exit 1
fi

echo ""
echo "🐳 Starting Docker containers..."
echo ""

docker-compose up --build

echo ""
echo "✅ Services are starting..."
echo ""
echo "📍 Frontend: http://localhost:3000"
echo "📍 API Docs: http://localhost:8000/docs"
echo "📍 Flower: http://localhost:5555"
echo ""
echo "⏳ Note: First startup may take 1-2 minutes for models to download."
