#!/bin/bash

# Setup script for Learn Pandas Bot

echo "🐼 Learn Pandas Bot - Setup Script"
echo "=================================="
echo ""

# Check if .env exists
if [ ! -f .env ]; then
    echo "📝 Creating .env file from .env.example..."
    cp .env.example .env
    echo "⚠️  Please edit .env and add your TELEGRAM_BOT_TOKEN"
    echo ""
fi

# Install dependencies with Poetry
echo "📦 Installing dependencies with Poetry..."
export PATH="$HOME/.local/bin:$PATH"
poetry install
PYTHON_CMD="poetry run python"

echo ""
echo "🗄️  Running database migrations..."
$PYTHON_CMD manage.py migrate

echo ""
echo "📚 Loading sample questions..."
$PYTHON_CMD manage.py load_sample_data

echo ""
echo "✅ Setup complete!"
echo ""
echo "Next steps:"
echo "1. Edit .env and add your TELEGRAM_BOT_TOKEN"
echo "2. Create a superuser: $PYTHON_CMD manage.py createsuperuser"
echo "3. Run the bot: $PYTHON_CMD run_bot.py"
echo ""
