#!/usr/bin/env python3
"""
Main entry point for the Telegram Invite Member Bot
This script handles startup, error handling, and graceful shutdown
"""

import sys
import os
import signal
import asyncio
import logging
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from telegram_bot import InviteMemberBot
from logger_config import setup_logging
from error_handler import log_error

class BotRunner:
    def __init__(self):
        self.bot = None
        self.running = False
        
    def setup_signal_handlers(self):
        """Setup signal handlers for graceful shutdown"""
        def signal_handler(signum, frame):
            logging.info(f"Received signal {signum}, shutting down gracefully...")
            self.running = False
            
        signal.signal(signal.SIGINT, signal_handler)
        signal.signal(signal.SIGTERM, signal_handler)
    
    def run(self):
        """Run the bot with error handling"""
        try:
            # Setup logging
            setup_logging()
            logging.info("Starting Telegram Invite Member Bot...")
            
            # Setup signal handlers
            self.setup_signal_handlers()
            
            # Create and run bot
            self.bot = InviteMemberBot()
            self.running = True
            
            logging.info("Bot initialized successfully")
            logging.info(f"Bot started at: {datetime.now()}")
            
            # Run the bot
            self.bot.run()
            
        except KeyboardInterrupt:
            logging.info("Bot stopped by user (Ctrl+C)")
        except Exception as e:
            log_error(e, "Bot startup/runtime error")
            logging.error("Bot crashed with error, shutting down...")
            raise
        finally:
            self.cleanup()
    
    def cleanup(self):
        """Cleanup resources"""
        logging.info("Cleaning up resources...")
        self.running = False
        logging.info("Bot shutdown complete")

def main():
    """Main function"""
    print("🤖 Telegram Invite Member Bot")
    print("=" * 40)
    print("Starting bot...")
    print("Press Ctrl+C to stop the bot")
    print("=" * 40)
    
    try:
        runner = BotRunner()
        runner.run()
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"\n❌ Bot crashed: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()