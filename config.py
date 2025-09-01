import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = "8270681359:AAF1TcTLkbqM9DlloE_-1ThzirSWgVpceyI"
TELEGRAM_GROUP_INVITE_LINK = "https://t.me/+xOBgxKDODnUzYjI1"

# PayPal Configuration
PAYPAL_CLIENT_ID = "AYoXO1m62hxQZJ5Kvi64723cNFYABj4_6cThvEQGwzSssMw7inZb_Zw8oujLX77kKpXSgbGDwaezdQ7M"
PAYPAL_CLIENT_SECRET = "ELzXi6pbH-6xGA46w04NRcE1yAw1Wo2Y8WUbA7iAEimk4QezR-wYrkdRXxUmsyP5BQaYmAAVO0LqHxUA"
PAYPAL_MODE = "sandbox"  # Change to "live" for production

# Payment Configuration
PAYMENT_AMOUNT = 10.0  # USDT amount
PAYMENT_CURRENCY = "USD"  # PayPal uses USD, you'll need to handle USDT conversion

# Database Configuration
DATABASE_FILE = "bot_database.db"

# Bot Messages
WELCOME_MESSAGE = """
🤖 Welcome to the Invite Bot!

To get access to our exclusive Telegram group, you need to make a payment of 10 USDT.

Click the button below to proceed with payment:
"""

PAYMENT_SUCCESS_MESSAGE = """
✅ Payment verified successfully!

Here's your invite link to join our exclusive group:
{invite_link}

Welcome to the community! 🎉
"""

PAYMENT_FAILED_MESSAGE = """
❌ Payment verification failed.

Please try again or contact support if you believe this is an error.
"""

PAYMENT_PENDING_MESSAGE = """
⏳ Your payment is being processed...

Please wait while we verify your payment. This may take a few minutes.
"""