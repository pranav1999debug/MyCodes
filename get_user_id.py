#!/usr/bin/env python3
"""
Simple script to get your Telegram User ID
Run this, then message the bot to get your user ID
"""
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from config import TELEGRAM_BOT_TOKEN

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def get_user_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Get and display user ID"""
    user = update.effective_user
    
    message = f"""
🆔 **Your Telegram User ID Information:**

**User ID:** `{user.id}`
**Username:** @{user.username or 'N/A'}
**First Name:** {user.first_name or 'N/A'}
**Last Name:** {user.last_name or 'N/A'}

**Copy this User ID and add it to your .env file:**
`ADMIN_USER_ID={user.id}`

Once you update the .env file, restart the main bot to get admin access!
    """
    
    await update.message.reply_text(message)
    
    # Also log it
    logger.info(f"User ID for {user.first_name}: {user.id}")
    print(f"\n🆔 USER ID: {user.id}")
    print(f"👤 NAME: {user.first_name} {user.last_name or ''}")
    print(f"📧 USERNAME: @{user.username or 'N/A'}")
    print(f"\n✏️  Add this to your .env file:")
    print(f"ADMIN_USER_ID={user.id}")

def main():
    app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ALL, get_user_id))
    
    print("🤖 User ID Bot started!")
    print("📱 Message this bot to get your User ID")
    print("⏹️  Press Ctrl+C to stop")
    
    app.run_polling()

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        print("\n👋 User ID bot stopped")
    except Exception as e:
        print(f"❌ Error: {e}")