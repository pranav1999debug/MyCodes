import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_GROUP_INVITE_LINK = os.getenv('TELEGRAM_GROUP_INVITE_LINK')

# PayPal Configuration
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
PAYPAL_MODE = os.getenv('PAYPAL_MODE', 'sandbox')  # 'sandbox' or 'live'

# Bot Configuration
PAYMENT_AMOUNT = float(os.getenv('PAYMENT_AMOUNT', '10.00'))
PAYMENT_CURRENCY = os.getenv('PAYMENT_CURRENCY', 'USD')
ADMIN_USER_ID = os.getenv('ADMIN_USER_ID')

# Database Configuration
DATABASE_PATH = 'bot_database.db'

# Validate required environment variables
required_vars = [
    'TELEGRAM_BOT_TOKEN',
    'TELEGRAM_GROUP_INVITE_LINK',
    'PAYPAL_CLIENT_ID',
    'PAYPAL_CLIENT_SECRET'
]

for var in required_vars:
    if not os.getenv(var):
        raise ValueError(f"Required environment variable {var} is not set")