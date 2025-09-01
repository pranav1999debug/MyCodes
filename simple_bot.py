#!/usr/bin/env python3
"""
Simple Telegram Invite Member Bot
Compatible with python-telegram-bot 20.7
"""

import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode

from config import (
    TELEGRAM_BOT_TOKEN, TELEGRAM_GROUP_INVITE_LINK, PAYMENT_AMOUNT,
    WELCOME_MESSAGE, PAYMENT_SUCCESS_MESSAGE, PAYMENT_FAILED_MESSAGE, PAYMENT_PENDING_MESSAGE
)
from database import DatabaseManager
from paypal_integration import PayPalManager, USDTPaymentManager

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class SimpleInviteBot:
    def __init__(self):
        self.db = DatabaseManager()
        self.paypal_manager = PayPalManager()
        self.usdt_manager = USDTPaymentManager()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        user = update.effective_user
        
        # Add user to database
        self.db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Check if user already has access
        user_data = self.db.get_user(user.id)
        if user_data and user_data['payment_status'] == 'verified':
            await update.message.reply_text(
                PAYMENT_SUCCESS_MESSAGE.format(invite_link=TELEGRAM_GROUP_INVITE_LINK),
                parse_mode=ParseMode.HTML
            )
            return
        
        # Create payment button
        keyboard = [
            [InlineKeyboardButton("💳 Pay 10 USDT", callback_data="start_payment")],
            [InlineKeyboardButton("ℹ️ How it works", callback_data="how_it_works")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            WELCOME_MESSAGE,
            reply_markup=reply_markup,
            parse_mode=ParseMode.HTML
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        help_text = """
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
        await update.message.reply_text(help_text, parse_mode=ParseMode.HTML)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command"""
        user = update.effective_user
        user_data = self.db.get_user(user.id)
        
        if not user_data:
            await update.message.reply_text("❌ You haven't started the payment process yet. Use /start to begin.")
            return
        
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
        
        await update.message.reply_text(status_text, parse_mode=ParseMode.HTML)
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle button callbacks"""
        query = update.callback_query
        await query.answer()
        
        user = update.effective_user
        
        if query.data == "start_payment":
            await self.handle_payment_start(query, user)
        elif query.data == "how_it_works":
            await self.handle_how_it_works(query)
        elif query.data.startswith("paypal_"):
            await self.handle_paypal_payment(query, user)
        elif query.data.startswith("usdt_"):
            await self.handle_usdt_payment(query, user)
        elif query.data.startswith("verify_"):
            await self.handle_payment_verification(query, user)
    
    async def handle_payment_start(self, query, user):
        """Handle payment method selection"""
        keyboard = [
            [InlineKeyboardButton("💳 PayPal", callback_data="paypal_payment")],
            [InlineKeyboardButton("₮ USDT (Crypto)", callback_data="usdt_payment")],
            [InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        text = f"""
💳 <b>Choose Payment Method</b>

Amount: <b>10 USDT</b>

Select your preferred payment method:
        """
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    
    async def handle_how_it_works(self, query):
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
        
        keyboard = [[InlineKeyboardButton("🔙 Back", callback_data="back_to_start")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
    
    async def handle_paypal_payment(self, query, user):
        """Handle PayPal payment creation"""
        try:
            # Create PayPal payment
            payment_data = self.paypal_manager.create_payment(
                user_id=user.id,
                description="Telegram Group Access - 10 USDT"
            )
            
            if payment_data:
                # Update user payment status
                self.db.update_user_payment_status(user.id, 'pending', payment_data['payment_id'])
                self.db.add_payment(
                    user_id=user.id,
                    payment_id=payment_data['payment_id'],
                    amount=10.0,
                    currency='USD',
                    status='pending'
                )
                
                text = f"""
💳 <b>PayPal Payment</b>

Payment ID: <code>{payment_data['payment_id']}</code>

<b>Instructions:</b>
1. Click the button below to open PayPal
2. Complete the payment (10 USD)
3. Return here and click "Verify Payment"

<b>Note:</b> PayPal processes in USD. The equivalent of 10 USDT will be charged.
                """
                
                keyboard = [
                    [InlineKeyboardButton("🌐 Open PayPal", url=payment_data['approval_url'])],
                    [InlineKeyboardButton("✅ Verify Payment", callback_data=f"verify_{payment_data['payment_id']}")],
                    [InlineKeyboardButton("🔙 Back", callback_data="start_payment")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:
                await query.edit_message_text(
                    "❌ Failed to create payment. Please try again later.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start_payment")]])
                )
                
        except Exception as e:
            logger.error(f"Error creating PayPal payment: {e}")
            await query.edit_message_text(
                "❌ An error occurred. Please try again later.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start_payment")]])
            )
    
    async def handle_usdt_payment(self, query, user):
        """Handle USDT payment creation"""
        try:
            # Create USDT payment
            payment_data = self.usdt_manager.create_payment(
                user_id=user.id,
                description="Telegram Group Access - 10 USDT"
            )
            
            if payment_data:
                # Update user payment status
                self.db.update_user_payment_status(user.id, 'pending', payment_data['payment_id'])
                self.db.add_payment(
                    user_id=user.id,
                    payment_id=payment_data['payment_id'],
                    amount=10.0,
                    currency='USDT',
                    status='pending'
                )
                
                text = f"""
₮ <b>USDT Payment</b>

Payment ID: <code>{payment_data['payment_id']}</code>

<b>Instructions:</b>
1. Send exactly <b>10 USDT</b> to the address below
2. Wait for 1-2 confirmations
3. Click "Verify Payment" to check status

<b>Payment Address:</b>
<code>{payment_data['address']}</code>

<b>Amount:</b> 10 USDT
<b>Network:</b> Ethereum (ERC-20)

⚠️ <b>Important:</b> Send exactly 10 USDT. Any other amount will not be accepted.
                """
                
                keyboard = [
                    [InlineKeyboardButton("✅ Verify Payment", callback_data=f"verify_{payment_data['payment_id']}")],
                    [InlineKeyboardButton("🔙 Back", callback_data="start_payment")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                await query.edit_message_text(text, reply_markup=reply_markup, parse_mode=ParseMode.HTML)
            else:
                await query.edit_message_text(
                    "❌ Failed to create payment. Please try again later.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start_payment")]])
                )
                
        except Exception as e:
            logger.error(f"Error creating USDT payment: {e}")
            await query.edit_message_text(
                "❌ An error occurred. Please try again later.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start_payment")]])
            )
    
    async def handle_payment_verification(self, query, user):
        """Handle payment verification"""
        payment_id = query.data.replace("verify_", "")
        
        try:
            # Get payment from database
            payment_data = self.db.get_payment(payment_id)
            
            if not payment_data:
                await query.edit_message_text(
                    "❌ Payment not found. Please try again.",
                    reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start_payment")]])
                )
                return
            
            # Verify payment based on currency
            if payment_data['currency'] == 'USD':
                verification_result = self.paypal_manager.verify_payment(payment_id)
            else:  # USDT
                verification_result = self.usdt_manager.verify_payment(payment_id)
            
            if verification_result and verification_result['status'] == 'verified':
                # Update payment status
                self.db.update_payment_status(payment_id, 'verified')
                self.db.update_user_payment_status(user.id, 'verified', payment_id)
                
                # Send success message with invite link
                await query.edit_message_text(
                    PAYMENT_SUCCESS_MESSAGE.format(invite_link=TELEGRAM_GROUP_INVITE_LINK),
                    parse_mode=ParseMode.HTML
                )
            else:
                # Payment not verified yet
                await query.edit_message_text(
                    PAYMENT_PENDING_MESSAGE,
                    reply_markup=InlineKeyboardMarkup([
                        [InlineKeyboardButton("🔄 Check Again", callback_data=f"verify_{payment_id}")],
                        [InlineKeyboardButton("🔙 Back", callback_data="start_payment")]
                    ]),
                    parse_mode=ParseMode.HTML
                )
                
        except Exception as e:
            logger.error(f"Error verifying payment {payment_id}: {e}")
            await query.edit_message_text(
                "❌ An error occurred during verification. Please try again later.",
                reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton("🔙 Back", callback_data="start_payment")]])
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle regular messages"""
        # For now, just redirect to start command
        await self.start_command(update, context)
    
    def setup_handlers(self, application: Application):
        """Setup bot handlers"""
        # Command handlers
        application.add_handler(CommandHandler("start", self.start_command))
        application.add_handler(CommandHandler("help", self.help_command))
        application.add_handler(CommandHandler("status", self.status_command))
        
        # Callback query handler
        application.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handler (for any other messages)
        application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def run(self):
        """Run the bot"""
        # Create application
        application = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Setup handlers
        self.setup_handlers(application)
        
        # Start the bot
        logger.info("Starting Simple Invite Member Bot...")
        
        # Use the simpler run_polling method
        await application.run_polling(allowed_updates=Update.ALL_TYPES)

async def main():
    """Main function"""
    bot = SimpleInviteBot()
    await bot.run()

if __name__ == '__main__':
    asyncio.run(main())