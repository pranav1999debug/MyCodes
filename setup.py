#!/usr/bin/env python3
"""
Setup script for Telegram Refer & Earn Bot
This script helps you set up the bot with proper configuration
"""

import os
import sys
import subprocess

def install_requirements():
    """Install required packages"""
    print("📦 Installing required packages...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("✅ Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("❌ Failed to install requirements")
        return False

def check_config():
    """Check if configuration is complete"""
    print("\n🔧 Checking configuration...")
    
    try:
        from config import BOT_TOKEN, CHANNEL_ID, CHANNEL_LINK
        
        issues = []
        
        if not BOT_TOKEN or BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
            issues.append("❌ BOT_TOKEN not set in config.py")
        else:
            print("✅ BOT_TOKEN is configured")
        
        if CHANNEL_ID is None:
            issues.append("❌ CHANNEL_ID not set in config.py")
        else:
            print("✅ CHANNEL_ID is configured")
        
        if not CHANNEL_LINK or CHANNEL_LINK == "https://t.me/+YOUR_CHANNEL_INVITE_LINK":
            issues.append("❌ CHANNEL_LINK not set in config.py")
        else:
            print("✅ CHANNEL_LINK is configured")
        
        if issues:
            print("\n⚠️  Configuration Issues Found:")
            for issue in issues:
                print(f"   {issue}")
            return False
        else:
            print("✅ All configuration looks good!")
            return True
            
    except ImportError as e:
        print(f"❌ Error importing config: {e}")
        return False

def show_setup_instructions():
    """Show detailed setup instructions"""
    print("\n" + "="*50)
    print("🚀 TELEGRAM REFER & EARN BOT SETUP")
    print("="*50)
    
    print("""
📋 SETUP CHECKLIST:

1. 🤖 CREATE TELEGRAM BOT:
   - Message @BotFather on Telegram
   - Send /newbot command
   - Choose a name and username for your bot
   - Copy the bot token
   
2. 📝 UPDATE CONFIG.PY:
   - Open config.py in a text editor
   - Replace BOT_TOKEN with your actual bot token
   - Keep CHANNEL_LINK as is (or update if different)
   
3. 🆔 GET CHANNEL ID:
   - Add your bot to your channel as administrator
   - Run: python get_channel_id.py
   - Follow the instructions to get your channel ID
   - Update CHANNEL_ID in config.py
   
4. ✅ VERIFY SETUP:
   - Run this setup script again to check configuration
   - Run: python main.py to start the bot
   
5. 🔧 CHANNEL PERMISSIONS:
   - Make sure your bot has these permissions in the channel:
     * View channel members
     * Send messages (optional)
   
📚 For detailed instructions, check the README.md file.
    """)

def main():
    """Main setup function"""
    print("🎯 Telegram Refer & Earn Bot Setup")
    print("-" * 40)
    
    # Install requirements
    if not install_requirements():
        print("\n❌ Setup failed at requirements installation")
        return
    
    # Check configuration
    config_ok = check_config()
    
    if not config_ok:
        print("\n⚠️  Configuration needs attention!")
        show_setup_instructions()
        print("\n💡 Run this script again after updating config.py")
    else:
        print("\n🎉 Setup complete! Your bot is ready to run.")
        print("\n🚀 To start the bot, run:")
        print("   python main.py")
        
        print("\n📋 Quick Start Guide:")
        print("   1. Start the bot: python main.py")
        print("   2. Add bot to your channel as admin")
        print("   3. Send /start to your bot on Telegram")
        print("   4. Test the referral system")

if __name__ == "__main__":
    main()