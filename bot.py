import logging
import asyncio
from datetime import datetime, timedelta
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode

from config import (
    TELEGRAM_BOT_TOKEN, 
    TELEGRAM_GROUP_INVITE_LINK, 
    PAYMENT_AMOUNT, 
    PAYMENT_CURRENCY,
    ADMIN_USER_ID
)
from database import DatabaseManager
from paypal_handler import PayPalHandler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class InviteMemberBot:
    def __init__(self):
        self.db = DatabaseManager()
        self.paypal = PayPalHandler()
        self.app = None
        
        # For webhook mode (if you want to use webhooks instead of polling)
        self.webhook_base_url = "https://your-domain.com"  # Update this if using webhooks
    
    def setup_application(self):
        """Setup the Telegram bot application"""
        self.app = Application.builder().token(TELEGRAM_BOT_TOKEN).build()
        
        # Command handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        self.app.add_handler(CommandHandler("status", self.status_command))
        self.app.add_handler(CommandHandler("pay", self.pay_command))
        
        # Admin commands
        self.app.add_handler(CommandHandler("admin", self.admin_command))
        self.app.add_handler(CommandHandler("stats", self.stats_command))
        
        # Callback query handler
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handler for general messages
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        
        logger.info("Bot application setup complete")
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command"""
        user = update.effective_user
        chat_id = update.effective_chat.id
        
        # Add user to database
        self.db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Check if user has already paid
        if self.db.user_has_paid(user.id):
            if self.db.user_has_invite(user.id):
                await update.message.reply_text(
                    "✅ You have already paid and received the invite link!\n\n"
                    "If you need the link again, please contact support."
                )
            else:
                # Send invite link
                await self.send_invite_link(update, user.id)
            return
        
        welcome_message = f"""
🤖 **Welcome to the Premium Group Access Bot!**

Hello {user.first_name}! 👋

To join our exclusive Telegram group, you need to make a one-time payment of **${PAYMENT_AMOUNT} {PAYMENT_CURRENCY}**.

**What you get:**
• Access to our premium Telegram group
• Exclusive content and discussions
• Direct access to community members
• Lifetime membership

**How it works:**
1. Click the "💳 Pay Now" button below
2. Complete the payment via PayPal
3. Receive your invite link automatically

Ready to join? Click the button below! 👇
        """
        
        keyboard = [
            [InlineKeyboardButton("💳 Pay Now", callback_data="pay_now")],
            [InlineKeyboardButton("ℹ️ Help", callback_data="help")],
            [InlineKeyboardButton("📊 My Status", callback_data="status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.message.reply_text(
            welcome_message,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command"""
        help_text = """
🆘 **Help & Support**

**Available Commands:**
• `/start` - Start the bot and see payment options
• `/help` - Show this help message
• `/status` - Check your payment status
• `/pay` - Start the payment process

**How to join the group:**
1. Use `/start` to begin
2. Click "💳 Pay Now" to make payment
3. Complete PayPal payment
4. Receive your invite link

**Payment Information:**
• Amount: $10.00 USD
• Method: PayPal
• One-time payment
• Lifetime access

**Need Support?**
If you encounter any issues, please contact our support team.

**Security Note:**
We use secure PayPal payments. Your financial information is protected.
        """
        
        await update.message.reply_text(
            help_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command"""
        user_id = update.effective_user.id
        user_data = self.db.get_user(user_id)
        
        if not user_data:
            await update.message.reply_text("❌ User not found. Please use /start first.")
            return
        
        has_paid = self.db.user_has_paid(user_id)
        has_invite = self.db.user_has_invite(user_id)
        
        if has_paid and has_invite:
            status_text = "✅ **Payment Status: COMPLETED**\n\n" \
                         "You have successfully paid and received access to the group!"
        elif has_paid and not has_invite:
            status_text = "⏳ **Payment Status: PAID**\n\n" \
                         "Your payment is confirmed. Processing your invite link..."
            # Send invite link
            await self.send_invite_link(update, user_id)
        else:
            status_text = f"❌ **Payment Status: PENDING**\n\n" \
                         f"You haven't completed the payment yet.\n" \
                         f"Amount required: ${PAYMENT_AMOUNT} {PAYMENT_CURRENCY}\n\n" \
                         f"Use /pay to start the payment process."
        
        keyboard = [
            [InlineKeyboardButton("💳 Pay Now", callback_data="pay_now")] if not has_paid else [],
            [InlineKeyboardButton("🔄 Refresh Status", callback_data="status")]
        ]
        reply_markup = InlineKeyboardMarkup([btn for btn in keyboard if btn])
        
        await update.message.reply_text(
            status_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup if keyboard else None
        )
    
    async def pay_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pay command"""
        user_id = update.effective_user.id
        
        # Check if user already paid
        if self.db.user_has_paid(user_id):
            await update.message.reply_text("✅ You have already completed the payment!")
            return
        
        await self.initiate_payment(update, user_id)
    
    async def admin_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /admin command"""
        user_id = update.effective_user.id
        
        if str(user_id) != str(ADMIN_USER_ID):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        admin_text = """
🔧 **Admin Panel**

**Available Commands:**
• `/stats` - View bot statistics
• `/admin` - Show this admin panel

**Quick Stats:**
Use /stats for detailed statistics.
        """
        
        await update.message.reply_text(
            admin_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /stats command"""
        user_id = update.effective_user.id
        
        if str(user_id) != str(ADMIN_USER_ID):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        stats = self.db.get_user_stats()
        
        stats_text = f"""
📊 **Bot Statistics**

👥 **Users:**
• Total Users: {stats['total_users']}
• Paid Users: {stats['paid_users']}
• Invited Users: {stats['invited_users']}

💰 **Revenue:**
• Total Revenue: ${stats['total_revenue']:.2f} {PAYMENT_CURRENCY}

📈 **Conversion Rate:**
• Payment Rate: {(stats['paid_users'] / max(stats['total_users'], 1) * 100):.1f}%
• Invite Rate: {(stats['invited_users'] / max(stats['paid_users'], 1) * 100):.1f}%
        """
        
        await update.message.reply_text(
            stats_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        if data == "pay_now":
            await self.initiate_payment(query, user_id)
        elif data == "help":
            await self.help_command(query, context)
        elif data == "status":
            await self.status_command(query, context)
    
    async def initiate_payment(self, update, user_id: int):
        """Initiate PayPal payment process"""
        try:
            # Generate session ID
            session_id = PayPalHandler.generate_session_id()
            
            # Create return URLs (for webhook mode, update base URL)
            return_url, cancel_url = self.paypal.create_return_urls(
                self.webhook_base_url, 
                session_id
            )
            
            # Create PayPal payment
            payment_url, payment_id = self.paypal.create_payment(
                user_id=user_id,
                return_url=return_url,
                cancel_url=cancel_url
            )
            
            if payment_url and payment_id:
                # Store payment session
                expires_at = datetime.now() + timedelta(minutes=30)  # 30 minutes expiry
                self.db.add_payment_session(
                    user_id=user_id,
                    session_id=session_id,
                    payment_url=payment_url,
                    expires_at=expires_at
                )
                
                payment_text = f"""
💳 **Payment Ready**

Amount: **${PAYMENT_AMOUNT} {PAYMENT_CURRENCY}**

Click the button below to complete your payment via PayPal.

⏰ This payment link expires in 30 minutes.

After successful payment, you'll automatically receive your invite link!
                """
                
                keyboard = [
                    [InlineKeyboardButton("💳 Pay with PayPal", url=payment_url)],
                    [InlineKeyboardButton("❌ Cancel", callback_data="cancel_payment")]
                ]
                reply_markup = InlineKeyboardMarkup(keyboard)
                
                if hasattr(update, 'message'):
                    await update.message.reply_text(
                        payment_text,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=reply_markup
                    )
                else:
                    await update.edit_message_text(
                        payment_text,
                        parse_mode=ParseMode.MARKDOWN,
                        reply_markup=reply_markup
                    )
            else:
                error_text = "❌ Failed to create payment. Please try again later."
                if hasattr(update, 'message'):
                    await update.message.reply_text(error_text)
                else:
                    await update.edit_message_text(error_text)
                    
        except Exception as e:
            logger.error(f"Error initiating payment: {e}")
            error_text = "❌ An error occurred while processing your request. Please try again."
            if hasattr(update, 'message'):
                await update.message.reply_text(error_text)
            else:
                await update.edit_message_text(error_text)
    
    async def send_invite_link(self, update, user_id: int):
        """Send the Telegram group invite link to user"""
        try:
            invite_text = f"""
🎉 **Welcome to the Premium Group!**

Congratulations! Your payment has been confirmed.

Here's your exclusive invite link:
{TELEGRAM_GROUP_INVITE_LINK}

**Important Notes:**
• This link is for your personal use only
• Click the link to join the group immediately
• Save this message for future reference

Welcome to our community! 🚀
            """
            
            # Mark invite as sent
            self.db.mark_invite_sent(user_id)
            
            if hasattr(update, 'message'):
                await update.message.reply_text(
                    invite_text,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
            else:
                # Send as new message to user
                await self.app.bot.send_message(
                    chat_id=user_id,
                    text=invite_text,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
            
            logger.info(f"Invite link sent to user {user_id}")
            
        except Exception as e:
            logger.error(f"Error sending invite link: {e}")
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle general text messages"""
        user_id = update.effective_user.id
        
        # Add user to database if not exists
        user = update.effective_user
        self.db.add_user(
            user_id=user.id,
            username=user.username,
            first_name=user.first_name,
            last_name=user.last_name
        )
        
        # Provide helpful response
        response_text = """
👋 Hello! I'm the Premium Group Access Bot.

To get started, use one of these commands:
• /start - Begin the process
• /pay - Make payment for group access
• /status - Check your payment status
• /help - Get help and support

Ready to join our exclusive group? Use /start! 🚀
        """
        
        await update.message.reply_text(response_text)
    
    def run_polling(self):
        """Run the bot using polling"""
        if not self.app:
            self.setup_application()
        
        logger.info("Starting bot in polling mode...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def run_webhook(self, webhook_url: str, port: int = 8443):
        """Run the bot using webhooks"""
        if not self.app:
            self.setup_application()
        
        logger.info(f"Starting bot in webhook mode on port {port}")
        await self.app.bot.set_webhook(url=webhook_url)
        
        # Start webhook server
        await self.app.start()
        await self.app.updater.start_webhook(
            listen="0.0.0.0",
            port=port,
            url_path="webhook"
        )

if __name__ == "__main__":
    bot = InviteMemberBot()
    
    try:
        # Run in polling mode (easier for development)
        bot.run_polling()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Bot error: {e}")
        raise