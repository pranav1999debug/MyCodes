#!/usr/bin/env python3
"""
Main entry point for the Telegram Invite Member Bot
This script provides options to run the bot in different modes
"""
import sys
import argparse
import logging
from bot import InviteMemberBot

def main():
    parser = argparse.ArgumentParser(description='Telegram Invite Member Bot')
    parser.add_argument(
        '--mode', 
        choices=['polling', 'webhook'], 
        default='polling',
        help='Bot running mode (default: polling)'
    )
    parser.add_argument(
        '--webhook-url',
        help='Webhook URL for webhook mode'
    )
    parser.add_argument(
        '--port',
        type=int,
        default=8443,
        help='Port for webhook mode (default: 8443)'
    )
    parser.add_argument(
        '--verbose',
        action='store_true',
        help='Enable verbose logging'
    )
    
    args = parser.parse_args()
    
    # Configure logging
    log_level = logging.DEBUG if args.verbose else logging.INFO
    logging.basicConfig(
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        level=log_level
    )
    
    # Create bot instance
    bot = InviteMemberBot()
    
    try:
        if args.mode == 'polling':
            print("🤖 Starting Telegram bot in polling mode...")
            print("Press Ctrl+C to stop the bot")
            bot.run_polling()
        elif args.mode == 'webhook':
            if not args.webhook_url:
                print("❌ Error: --webhook-url is required for webhook mode")
                sys.exit(1)
            
            print(f"🤖 Starting Telegram bot in webhook mode...")
            print(f"Webhook URL: {args.webhook_url}")
            print(f"Port: {args.port}")
            print("Press Ctrl+C to stop the bot")
            
            import asyncio
            asyncio.run(bot.run_webhook(args.webhook_url, args.port))
            
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Bot error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()