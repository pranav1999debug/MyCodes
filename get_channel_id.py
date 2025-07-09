import asyncio
from telegram import Bot
from config import BOT_TOKEN

async def get_channel_info():
    """Utility script to get channel information"""
    bot = Bot(token=BOT_TOKEN)
    
    print("🔍 Channel ID Helper")
    print("=" * 40)
    
    # You need to manually get the channel ID
    print("📝 To get your channel ID:")
    print("1. Add your bot to the channel as admin")
    print("2. Send a message in the channel")
    print("3. Forward that message to @userinfobot")
    print("4. Copy the 'Forwarded from chat' ID")
    print("5. Update the CHANNEL_ID in config.py")
    print()
    
    # Alternative method
    print("🔧 Alternative method:")
    print("1. Add @chatid_echo_bot to your channel")
    print("2. Send /chatid in the channel")
    print("3. Copy the returned chat ID")
    print("4. Update the CHANNEL_ID in config.py")
    print()
    
    print("⚠️  Note: For private channels, you need the actual numeric chat ID")
    print("    Channel username won't work for private channels")

if __name__ == "__main__":
    asyncio.run(get_channel_info())