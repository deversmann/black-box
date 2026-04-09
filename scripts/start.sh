#!/bin/bash
# Start script for Black Box Swarm

set -e

echo "🧠 Starting Black Box Swarm..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo ""
    echo "To fix this:"
    echo "  1. Copy .env.example to .env:"
    echo "     cp .env.example .env"
    echo ""
    echo "  2. Edit .env and add your OpenRouter API key:"
    echo "     nano .env"
    echo ""
    echo "  Get an API key at: https://openrouter.ai/keys"
    exit 1
fi

# Check if OPENROUTER_API_KEY is set in .env
if ! grep -q "OPENROUTER_API_KEY=sk-" .env 2>/dev/null; then
    echo "⚠️  Warning: OPENROUTER_API_KEY may not be set in .env"
    echo ""
    echo "Make sure your .env file contains:"
    echo "  OPENROUTER_API_KEY=sk-or-v1-your-key-here"
    echo ""
    echo "Get an API key at: https://openrouter.ai/keys"
    echo ""
    read -p "Continue anyway? (y/N) " -n 1 -r
    echo
    if [[ ! $REPLY =~ ^[Yy]$ ]]; then
        exit 1
    fi
fi

# Check if dependencies are installed
if ! python -c "import streamlit" 2>/dev/null; then
    echo "📦 Installing dependencies..."
    pip install -e .
fi

# Create data directories if they don't exist
mkdir -p data logs

# Start Streamlit
echo "🚀 Launching Streamlit UI..."
streamlit run frontend/app.py
