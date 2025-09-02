import os
from dotenv import load_dotenv

load_dotenv()

# Telegram Bot Configuration
TELEGRAM_BOT_TOKEN = os.getenv('TELEGRAM_BOT_TOKEN')
TELEGRAM_GROUP_INVITE_LINK = os.getenv('TELEGRAM_GROUP_INVITE_LINK')

# PayPal Configuration
PAYPAL_CLIENT_ID = os.getenv('PAYPAL_CLIENT_ID')
PAYPAL_CLIENT_SECRET = os.getenv('PAYPAL_CLIENT_SECRET')
PAYPAL_MODE = os.getenv('PAYPAL_MODE', 'live')  # 'sandbox' or 'live'

# Payment Configuration
PAYMENT_AMOUNT_USD = float(os.getenv('PAYMENT_AMOUNT_USD', '10.00'))
PAYMENT_AMOUNT_INR = float(os.getenv('PAYMENT_AMOUNT_INR', '830.00'))
PAYMENT_AMOUNT_TON = float(os.getenv('PAYMENT_AMOUNT_TON', '2.0'))
PAYMENT_AMOUNT_BTC = float(os.getenv('PAYMENT_AMOUNT_BTC', '0.0001'))

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
    'paypal': {
        'name': 'PayPal',
        'symbol': '$',
        'amount': PAYMENT_AMOUNT_USD,
        'currency': 'USD',
        'type': 'automated',
        'description': 'Secure payment via PayPal'
    },
    'bitcoin': {
        'name': 'Bitcoin (BTC)',
        'symbol': '₿',
        'wallet': BITCOIN_WALLET,
        'amount': PAYMENT_AMOUNT_BTC,
        'currency': 'BTC',
        'network': 'Bitcoin Network',
        'confirmations': 1,
        'type': 'manual',
        'description': 'Send Bitcoin to the wallet address'
    },
    'ton': {
        'name': 'TON Coin',
        'symbol': 'TON',
        'wallet': TON_WALLET,
        'amount': PAYMENT_AMOUNT_TON,
        'currency': 'TON',
        'network': 'TON Network',
        'confirmations': 1,
        'type': 'manual',
        'description': 'Send TON to the wallet address'
    },
    'bank_transfer': {
        'name': 'Bank Transfer (India)',
        'symbol': '₹',
        'amount': PAYMENT_AMOUNT_INR,
        'currency': 'INR',
        'bank_name': BANK_NAME,
        'account_name': BANK_ACCOUNT_NAME,
        'account_number': BANK_ACCOUNT_NUMBER,
        'ifsc': BANK_IFSC,
        'type': 'manual',
        'description': 'Transfer to Indian bank account'
    },
    'upi': {
        'name': 'UPI Payment (India)',
        'symbol': '₹',
        'amount': PAYMENT_AMOUNT_INR,
        'currency': 'INR',
        'upi_id': UPI_ID,
        'type': 'manual',
        'description': 'Pay via UPI to the given ID'
    }
}

# Validate required environment variables
required_vars = [
    'TELEGRAM_BOT_TOKEN',
    'TELEGRAM_GROUP_INVITE_LINK',
    'PAYPAL_CLIENT_ID',
    'PAYPAL_CLIENT_SECRET',
    'BITCOIN_WALLET',
    'TON_WALLET',
    'BANK_ACCOUNT_NUMBER',
    'UPI_ID'
]

for var in required_vars:
    if not os.getenv(var):
        raise ValueError(f"Required environment variable {var} is not set")