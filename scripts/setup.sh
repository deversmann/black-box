#!/bin/bash
# Setup script for Black Box Swarm development environment

set -e

echo "🧠 Setting up Black Box Swarm development environment..."

# Check Python version
PYTHON_VERSION=$(python --version 2>&1 | awk '{print $2}')
REQUIRED_VERSION="3.11"

if ! python -c "import sys; exit(0 if sys.version_info >= (3, 11) else 1)"; then
    echo "❌ Error: Python 3.11+ required (found $PYTHON_VERSION)"
    exit 1
fi

echo "✅ Python version: $PYTHON_VERSION"

# Install package in development mode
echo "📦 Installing dependencies..."
pip install -e ".[dev]"

# Create necessary directories
echo "📁 Creating directories..."
mkdir -p data logs

# Check for .env file
if [ ! -f .env ]; then
    echo "📝 Creating .env from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your OPENROUTER_API_KEY"
else
    echo "✅ .env file already exists"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "  1. Edit .env and add your OPENROUTER_API_KEY"
echo "  2. Run tests: pytest"
echo "  3. Start the app: ./scripts/start.sh"
