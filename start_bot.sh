#!/bin/bash

# Telegram Invite Member Bot Startup Script

echo "🤖 Starting Telegram Invite Member Bot..."
echo "=========================================="

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install/update dependencies
echo "📦 Installing dependencies..."
pip install -r requirements.txt

# Check if database exists, if not create it
if [ ! -f "bot_database.db" ]; then
    echo "🗄️ Initializing database..."
    python3 -c "from database import DatabaseManager; DatabaseManager()"
    echo "✅ Database initialized"
fi

# Create logs directory if it doesn't exist
mkdir -p logs

# Start the bot
echo "🚀 Starting bot..."
echo "Press Ctrl+C to stop the bot"
echo "=========================================="

python3 run_bot.py