#!/usr/bin/env python3
"""
Simple test to verify bot is working
"""
import asyncio
from telegram import Bot
from config import TELEGRAM_BOT_TOKEN

async def test_bot():
    bot = Bot(token=TELEGRAM_BOT_TOKEN)
    
    try:
        # Get bot info
        me = await bot.get_me()
        print(f"✅ Bot is online!")
        print(f"🤖 Bot Name: {me.first_name}")
        print(f"📧 Bot Username: @{me.username}")
        print(f"🆔 Bot ID: {me.id}")
        print(f"🔗 Bot Link: https://t.me/{me.username}")
        
        return True
    except Exception as e:
        print(f"❌ Bot test failed: {e}")
        return False

if __name__ == "__main__":
    asyncio.run(test_bot())