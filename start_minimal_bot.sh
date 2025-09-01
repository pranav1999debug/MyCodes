#!/bin/bash

# Start Minimal Telegram Invite Member Bot

echo "🤖 Starting Minimal Telegram Invite Member Bot..."
echo "================================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Creating one..."
    python3 -m venv venv
    echo "✅ Virtual environment created"
fi

# Activate virtual environment
echo "🔧 Activating virtual environment..."
source venv/bin/activate

# Install dependencies if needed
echo "📦 Checking dependencies..."
pip install requests

# Start the bot
echo "🚀 Starting bot..."
echo "Press Ctrl+C to stop the bot"
echo "================================================"

python minimal_bot.py