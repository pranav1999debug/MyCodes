import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_GROUP_INVITE_LINK = os.getenv('TELEGRAM_GROUP_INVITE_LINK')

# Payment Configuration
PAYMENT_AMOUNT_USD = float(os.getenv('PAYMENT_AMOUNT_USD', '10.00'))
PAYMENT_AMOUNT_INR = float(os.getenv('PAYMENT_AMOUNT_INR', '830.00'))

# Cryptocurrency Wallet Addresses
BITCOIN_WALLET = os.getenv('BITCOIN_WALLET')
TON_WALLET = os.getenv('TON_WALLET')

# Bank Transfer Details
BANK_NAME = os.getenv('BANK_NAME')
BANK_ACCOUNT_NAME = os.getenv('BANK_ACCOUNT_NAME')
BANK_ACCOUNT_NUMBER = os.getenv('BANK_ACCOUNT_NUMBER')
BANK_IFSC = os.getenv('BANK_IFSC')
UPI_ID = os.getenv('UPI_ID')

# Bot Configuration
ADMIN_USER_ID = os.getenv('ADMIN_USER_ID')
BOT_MODE = os.getenv('BOT_MODE', 'production')

# Database Configuration
DATABASE_PATH = 'bot_database.db'

# Payment Methods Configuration
PAYMENT_METHODS = {
    'bitcoin': {
        'name': 'Bitcoin (BTC)',
        'symbol': '₿',
        'wallet': BITCOIN_WALLET,
        'amount': PAYMENT_AMOUNT_USD,
        'currency': 'USD',
        'network': 'Bitcoin Network',
        'confirmations': 1
    },
    'ton': {
        'name': 'TON Coin',
        'symbol': 'TON',
        'wallet': TON_WALLET,
        'amount': PAYMENT_AMOUNT_USD,
        'currency': 'USD',
        'network': 'TON Network',
        'confirmations': 1
    },
    'bank_transfer': {
        'name': 'Bank Transfer (India)',
        'symbol': '₹',
        'amount': PAYMENT_AMOUNT_INR,
        'currency': 'INR',
        'bank_name': BANK_NAME,
        'account_name': BANK_ACCOUNT_NAME,
        'account_number': BANK_ACCOUNT_NUMBER,
        'ifsc': BANK_IFSC
    },
    'upi': {
        'name': 'UPI Payment (India)',
        'symbol': '₹',
        'amount': PAYMENT_AMOUNT_INR,
        'currency': 'INR',
        'upi_id': UPI_ID
    }
}

# Validate required environment variables
required_vars = [
    'TELEGRAM_BOT_TOKEN',
    'TELEGRAM_GROUP_INVITE_LINK',
    'BITCOIN_WALLET',
    'TON_WALLET',
    'BANK_ACCOUNT_NUMBER',
    'UPI_ID'
]

for var in required_vars:
    if not os.getenv(var):
        raise ValueError(f"Required environment variable {var} is not set")