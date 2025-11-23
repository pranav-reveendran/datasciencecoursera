#!/bin/bash

# Setup script for Equity Research AI Tool

echo "🚀 Setting up Equity Research AI Tool..."
echo ""

# Check Python version
python_version=$(python3 --version 2>&1 | grep -oP '\d+\.\d+')
required_version="3.9"

if [ "$(printf '%s\n' "$required_version" "$python_version" | sort -V | head -n1)" != "$required_version" ]; then
    echo "❌ Python 3.9 or higher is required. You have Python $python_version"
    exit 1
fi

echo "✅ Python version check passed ($python_version)"

# Create virtual environment
echo ""
echo "📦 Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Upgrade pip
echo "⬆️  Upgrading pip..."
pip install --upgrade pip

# Install requirements
echo ""
echo "📥 Installing dependencies..."
pip install -r requirements.txt

# Create .env from example if it doesn't exist
if [ ! -f .env ]; then
    echo ""
    echo "📝 Creating .env file from template..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your API keys!"
fi

# Create data directories
echo ""
echo "📁 Creating data directories..."
mkdir -p data/chroma_db
mkdir -p data/raw_articles

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your API keys (especially OPENAI_API_KEY)"
echo "2. Activate the virtual environment: source venv/bin/activate"
echo "3. Run the app: streamlit run app.py"
echo ""
echo "Happy researching! 📈"
