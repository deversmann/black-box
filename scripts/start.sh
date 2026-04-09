#!/bin/bash
# Start script for Black Box Swarm

set -e

echo "🧠 Starting Black Box Swarm..."

# Check if .env exists
if [ ! -f .env ]; then
    echo "❌ Error: .env file not found"
    echo "Please copy .env.example to .env and add your OPENROUTER_API_KEY"
    exit 1
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
