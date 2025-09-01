#!/usr/bin/env python3
"""
Minimal Telegram Invite Member Bot
Simple working version to demonstrate functionality
"""

import logging
import requests
import time
from datetime import datetime

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Bot Configuration
TELEGRAM_BOT_TOKEN = "8270681359:AAF1TcTLkbqM9DlloE_-1ThzirSWgVpceyI"
TELEGRAM_GROUP_INVITE_LINK = "https://t.me/+xOBgxKDODnUzYjI1"
PAYMENT_AMOUNT = 10.0

# Simple in-memory storage (replace with database in production)
users = {}
payments = {}

class MinimalBot:
    def __init__(self):
        self.base_url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}"
        self.offset = 0
    
    def send_message(self, chat_id, text, reply_markup=None):
        """Send a message to a chat"""
        url = f"{self.base_url}/sendMessage"
        data = {
            "chat_id": chat_id,
            "text": text,
            "parse_mode": "HTML"
        }
        if reply_markup:
            data["reply_markup"] = reply_markup
        
        response = requests.post(url, json=data)
        return response.json()
    
    def edit_message(self, chat_id, message_id, text, reply_markup=None):
        """Edit an existing message"""
        url = f"{self.base_url}/editMessageText"
        data = {
            "chat_id": chat_id,
            "message_id": message_id,
            "text": text,
            "parse_mode": "HTML"
        }
        if reply_markup:
            data["reply_markup"] = reply_markup
        
        response = requests.post(url, json=data)
        return response.json()
    
    def answer_callback_query(self, callback_query_id, text=None):
        """Answer a callback query"""
        url = f"{self.base_url}/answerCallbackQuery"
        data = {"callback_query_id": callback_query_id}
        if text:
            data["text"] = text
        
        response = requests.post(url, json=data)
        return response.json()
    
    def get_updates(self):
        """Get updates from Telegram"""
        url = f"{self.base_url}/getUpdates"
        params = {"offset": self.offset, "timeout": 30}
        response = requests.get(url, params=params)
        return response.json()
    
    def handle_start_command(self, chat_id, user_id, username, first_name):
        """Handle /start command"""
        # Store user
        users[user_id] = {
            "username": username,
            "first_name": first_name,
            "payment_status": "pending",
            "created_at": datetime.now()
        }
        
        # Check if user already has access
        if users[user_id]["payment_status"] == "verified":
            text = f"""
✅ <b>Welcome back!</b>

You already have access to our exclusive group!

Group invite link:
{TELEGRAM_GROUP_INVITE_LINK}

Enjoy the community! 🎉
            """
            self.send_message(chat_id, text)
            return
        
        # Welcome message with payment button
        text = """
🤖 <b>Welcome to the Invite Bot!</b>

To get access to our exclusive Telegram group, you need to make a payment of 10 USDT.

Click the button below to proceed with payment:
        """
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "💳 Pay 10 USDT", "callback_data": "start_payment"}],
                [{"text": "ℹ️ How it works", "callback_data": "how_it_works"}]
            ]
        }
        
        self.send_message(chat_id, text, keyboard)
    
    def handle_help_command(self, chat_id):
        """Handle /help command"""
        text = """
🤖 <b>Invite Member Bot Help</b>

<b>Commands:</b>
/start - Start the bot and get payment options
/help - Show this help message
/status - Check your payment status

<b>How it works:</b>
1. Click "Pay 10 USDT" to start payment process
2. Complete the payment using PayPal or USDT
3. Once verified, you'll receive the group invite link
4. Join the exclusive Telegram group!

<b>Support:</b>
If you have any issues, contact our support team.
        """
        self.send_message(chat_id, text)
    
    def handle_status_command(self, chat_id, user_id):
        """Handle /status command"""
        if user_id not in users:
            self.send_message(chat_id, "❌ You haven't started the payment process yet. Use /start to begin.")
            return
        
        user_data = users[user_id]
        status_emoji = {
            'pending': '⏳',
            'verified': '✅',
            'failed': '❌'
        }
        
        status_text = f"""
📊 <b>Your Payment Status</b>

Status: {status_emoji.get(user_data['payment_status'], '❓')} {user_data['payment_status'].title()}

"""
        
        if user_data['payment_status'] == 'verified':
            status_text += f"🎉 <b>You have access!</b>\n\n"
            status_text += f"Group invite link:\n{TELEGRAM_GROUP_INVITE_LINK}"
        elif user_data['payment_status'] == 'pending':
            status_text += "⏳ Your payment is being processed. Please wait..."
        else:
            status_text += "❌ Payment failed. Please try again with /start"
        
        self.send_message(chat_id, status_text)
    
    def handle_callback_query(self, callback_query):
        """Handle callback queries (button clicks)"""
        query_id = callback_query["id"]
        chat_id = callback_query["message"]["chat"]["id"]
        message_id = callback_query["message"]["message_id"]
        user_id = callback_query["from"]["id"]
        data = callback_query["data"]
        
        # Answer the callback query
        self.answer_callback_query(query_id)
        
        if data == "start_payment":
            self.handle_payment_start(chat_id, message_id, user_id)
        elif data == "how_it_works":
            self.handle_how_it_works(chat_id, message_id)
        elif data.startswith("paypal_"):
            self.handle_paypal_payment(chat_id, message_id, user_id)
        elif data.startswith("usdt_"):
            self.handle_usdt_payment(chat_id, message_id, user_id)
        elif data.startswith("verify_"):
            self.handle_payment_verification(chat_id, message_id, user_id, data)
    
    def handle_payment_start(self, chat_id, message_id, user_id):
        """Handle payment method selection"""
        text = f"""
💳 <b>Choose Payment Method</b>

Amount: <b>10 USDT</b>

Select your preferred payment method:
        """
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "💳 PayPal", "callback_data": "paypal_payment"}],
                [{"text": "₮ USDT (Crypto)", "callback_data": "usdt_payment"}],
                [{"text": "🔙 Back", "callback_data": "back_to_start"}]
            ]
        }
        
        self.edit_message(chat_id, message_id, text, keyboard)
    
    def handle_how_it_works(self, chat_id, message_id):
        """Handle how it works information"""
        text = """
ℹ️ <b>How It Works</b>

1️⃣ <b>Choose Payment Method</b>
   • PayPal (Credit/Debit Card)
   • USDT (Cryptocurrency)

2️⃣ <b>Complete Payment</b>
   • Amount: 10 USDT
   • Follow the payment instructions

3️⃣ <b>Get Access</b>
   • Payment is verified automatically
   • Receive exclusive group invite link
   • Join our community!

<b>Why do we charge?</b>
This helps us maintain a quality community and filter out spam accounts.

<b>Need help?</b>
Contact our support team if you have any questions.
        """
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🔙 Back", "callback_data": "back_to_start"}]
            ]
        }
        
        self.edit_message(chat_id, message_id, text, keyboard)
    
    def handle_paypal_payment(self, chat_id, message_id, user_id):
        """Handle PayPal payment creation"""
        # Generate payment ID
        payment_id = f"paypal_{user_id}_{int(time.time())}"
        
        # Store payment
        payments[payment_id] = {
            "user_id": user_id,
            "amount": 10.0,
            "currency": "USD",
            "status": "pending",
            "created_at": datetime.now()
        }
        
        # Update user status
        users[user_id]["payment_status"] = "pending"
        users[user_id]["payment_id"] = payment_id
        
        text = f"""
💳 <b>PayPal Payment</b>

Payment ID: <code>{payment_id}</code>

<b>Instructions:</b>
1. Click the button below to open PayPal
2. Complete the payment (10 USD)
3. Return here and click "Verify Payment"

<b>Note:</b> PayPal processes in USD. The equivalent of 10 USDT will be charged.

⚠️ <b>Demo Mode:</b> This is a demonstration. In production, you would integrate with real PayPal API.
        """
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "🌐 Open PayPal (Demo)", "url": "https://www.paypal.com"}],
                [{"text": "✅ Verify Payment", "callback_data": f"verify_{payment_id}"}],
                [{"text": "🔙 Back", "callback_data": "start_payment"}]
            ]
        }
        
        self.edit_message(chat_id, message_id, text, keyboard)
    
    def handle_usdt_payment(self, chat_id, message_id, user_id):
        """Handle USDT payment creation"""
        # Generate payment ID
        payment_id = f"usdt_{user_id}_{int(time.time())}"
        
        # Store payment
        payments[payment_id] = {
            "user_id": user_id,
            "amount": 10.0,
            "currency": "USDT",
            "status": "pending",
            "created_at": datetime.now()
        }
        
        # Update user status
        users[user_id]["payment_status"] = "pending"
        users[user_id]["payment_id"] = payment_id
        
        text = f"""
₮ <b>USDT Payment</b>

Payment ID: <code>{payment_id}</code>

<b>Instructions:</b>
1. Send exactly <b>10 USDT</b> to the address below
2. Wait for 1-2 confirmations
3. Click "Verify Payment" to check status

<b>Payment Address (Demo):</b>
<code>0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6</code>

<b>Amount:</b> 10 USDT
<b>Network:</b> Ethereum (ERC-20)

⚠️ <b>Demo Mode:</b> This is a demonstration. In production, you would integrate with real crypto payment processor.
        """
        
        keyboard = {
            "inline_keyboard": [
                [{"text": "✅ Verify Payment", "callback_data": f"verify_{payment_id}"}],
                [{"text": "🔙 Back", "callback_data": "start_payment"}]
            ]
        }
        
        self.edit_message(chat_id, message_id, text, keyboard)
    
    def handle_payment_verification(self, chat_id, message_id, user_id, data):
        """Handle payment verification"""
        payment_id = data.replace("verify_", "")
        
        if payment_id not in payments:
            self.edit_message(
                chat_id, 
                message_id, 
                "❌ Payment not found. Please try again.",
                {"inline_keyboard": [[{"text": "🔙 Back", "callback_data": "start_payment"}]]}
            )
            return
        
        # For demo purposes, always verify the payment
        # In production, you would check the actual payment status
        payments[payment_id]["status"] = "verified"
        users[user_id]["payment_status"] = "verified"
        
        # Send success message
        text = f"""
✅ <b>Payment verified successfully!</b>

Here's your invite link to join our exclusive group:
{TELEGRAM_GROUP_INVITE_LINK}

Welcome to the community! 🎉

<b>Note:</b> This is a demonstration. In production, payment verification would be automatic.
        """
        
        self.edit_message(chat_id, message_id, text)
    
    def handle_message(self, message):
        """Handle incoming messages"""
        chat_id = message["chat"]["id"]
        user_id = message["from"]["id"]
        username = message["from"].get("username")
        first_name = message["from"].get("first_name", "")
        
        if "text" in message:
            text = message["text"]
            
            if text.startswith("/start"):
                self.handle_start_command(chat_id, user_id, username, first_name)
            elif text.startswith("/help"):
                self.handle_help_command(chat_id)
            elif text.startswith("/status"):
                self.handle_status_command(chat_id, user_id)
            else:
                # Redirect to start command
                self.handle_start_command(chat_id, user_id, username, first_name)
    
    def run(self):
        """Run the bot"""
        logger.info("Starting Minimal Invite Member Bot...")
        logger.info(f"Bot token: {TELEGRAM_BOT_TOKEN[:20]}...")
        logger.info("Bot is running. Press Ctrl+C to stop.")
        
        try:
            while True:
                # Get updates
                response = self.get_updates()
                
                if response["ok"]:
                    updates = response["result"]
                    
                    for update in updates:
                        self.offset = update["update_id"] + 1
                        
                        if "message" in update:
                            self.handle_message(update["message"])
                        elif "callback_query" in update:
                            self.handle_callback_query(update["callback_query"])
                
                # Small delay to avoid overwhelming the API
                time.sleep(1)
                
        except KeyboardInterrupt:
            logger.info("Bot stopped by user")
        except Exception as e:
            logger.error(f"Bot error: {e}")

def main():
    """Main function"""
    bot = MinimalBot()
    bot.run()

if __name__ == '__main__':
    main()