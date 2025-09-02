import logging
import asyncio
import io
import base64
from datetime import datetime, timedelta
from typing import Optional
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, InputFile
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.constants import ParseMode

from config import (
    TELEGRAM_BOT_TOKEN, 
    TELEGRAM_GROUP_INVITE_LINK, 
    PAYMENT_METHODS,
    ADMIN_USER_ID,
    BOT_MODE
)
from database import DatabaseManager
from payment_handler import PaymentHandler

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

class InviteMemberBot:
    def __init__(self):
        self.db = DatabaseManager()
        self.payment_handler = PaymentHandler()
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
        self.app.add_handler(CommandHandler("pending", self.pending_payments_command))
        self.app.add_handler(CommandHandler("approve", self.approve_payment_command))
        self.app.add_handler(CommandHandler("reject", self.reject_payment_command))
        
        # Callback query handler
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handler for general messages and photo uploads
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
        self.app.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        
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

To join our exclusive Telegram group, you need to make a one-time payment.

**Available Payment Methods:**
💳 PayPal - $10.00 USD
₿ Bitcoin - 0.0001 BTC
🪙 TON Coin - 2.0 TON  
🏦 Bank Transfer - ₹100.00 INR
📱 UPI - ₹100.00 INR

**What you get:**
• Access to our premium Telegram group
• Exclusive content and discussions
• Direct access to community members
• Lifetime membership

Ready to join? Choose your payment method below! 👇
        """
        
        keyboard = [
            [InlineKeyboardButton("💳 PayPal ($10)", callback_data="pay_paypal")],
            [InlineKeyboardButton("₿ Bitcoin (0.0001 BTC)", callback_data="pay_bitcoin")],
            [InlineKeyboardButton("🪙 TON Coin (2 TON)", callback_data="pay_ton")],
            [InlineKeyboardButton("🏦 Bank Transfer (₹100)", callback_data="pay_bank_transfer")],
            [InlineKeyboardButton("📱 UPI (₹100)", callback_data="pay_upi")],
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

**Payment Methods:**

**💳 PayPal** - Instant verification
• Amount: $10.00 USD
• Process: Click PayPal button → Pay → Get instant access

**₿ Bitcoin** - Manual verification  
• Amount: $10.00 USD equivalent in BTC
• Process: Send BTC → Upload screenshot → Wait for approval

**🪙 TON Coin** - Manual verification
• Amount: $10.00 USD equivalent in TON
• Process: Send TON → Upload screenshot → Wait for approval

**🏦 Bank Transfer** - Manual verification
• Amount: ₹100.00 INR
• Process: Transfer to bank → Upload screenshot → Wait for approval

**📱 UPI** - Manual verification  
• Amount: ₹100.00 INR
• Process: Pay via UPI → Upload screenshot → Wait for approval

**Need Support?**
Contact admin if you encounter any issues.

**Security Note:**
All payments are verified before granting access.
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
                         f"You haven't completed the payment yet.\n\n" \
                         f"Available amounts:\n" \
                         f"• PayPal: $10.00 USD\n" \
                         f"• Crypto: 0.0001 BTC / 2.0 TON\n" \
                         f"• Bank/UPI: ₹100.00 INR\n\n" \
                         f"Use /pay to start the payment process."
        
        keyboard = []
        if not has_paid:
            keyboard = [
                [InlineKeyboardButton("💳 Choose Payment Method", callback_data="choose_payment")],
                [InlineKeyboardButton("🔄 Refresh Status", callback_data="status")]
            ]
        
        reply_markup = InlineKeyboardMarkup(keyboard) if keyboard else None
        
        await update.message.reply_text(
            status_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def pay_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pay command"""
        user_id = update.effective_user.id
        
        # Check if user already paid
        if self.db.user_has_paid(user_id):
            await update.message.reply_text("✅ You have already completed the payment!")
            return
        
        await self.show_payment_methods(update)
    
    async def show_payment_methods(self, update):
        """Show available payment methods"""
        payment_text = """
💳 **Choose Your Payment Method**

Select your preferred payment option:
        """
        
        keyboard = [
            [InlineKeyboardButton("💳 PayPal - $10.00 USD", callback_data="pay_paypal")],
            [InlineKeyboardButton("₿ Bitcoin - 0.0001 BTC", callback_data="pay_bitcoin")],
            [InlineKeyboardButton("🪙 TON Coin - 2.0 TON", callback_data="pay_ton")],
            [InlineKeyboardButton("🏦 Bank Transfer - ₹100.00", callback_data="pay_bank_transfer")],
            [InlineKeyboardButton("📱 UPI - ₹100.00", callback_data="pay_upi")],
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
• `/pending` - View pending payments
• `/approve <payment_ref>` - Approve a payment
• `/reject <payment_ref>` - Reject a payment
• `/admin` - Show this admin panel

**Bot Mode:** Production 🔴

**Quick Actions:**
Use the commands above to manage payments and users.
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
• Total Revenue: ${stats['total_revenue']:.2f} USD

📈 **Conversion Rate:**
• Payment Rate: {(stats['paid_users'] / max(stats['total_users'], 1) * 100):.1f}%
• Invite Rate: {(stats['invited_users'] / max(stats['paid_users'], 1) * 100):.1f}%

🤖 **Bot Mode:** Production
        """
        
        await update.message.reply_text(
            stats_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def pending_payments_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /pending command"""
        user_id = update.effective_user.id
        
        if str(user_id) != str(ADMIN_USER_ID):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        pending_payments = self.db.get_pending_payments()
        
        if not pending_payments:
            await update.message.reply_text("✅ No pending payments to review.")
            return
        
        for payment in pending_payments[:5]:  # Show first 5
            payment_text = f"""
🔍 **Pending Payment Review**

👤 **User:** {payment.get('first_name', 'N/A')} (@{payment.get('username', 'N/A')})
💳 **Method:** {payment['payment_method'].title()}
💰 **Amount:** {payment['amount']} {payment['currency']}
🔖 **Reference:** `{payment['payment_ref']}`
📅 **Date:** {payment['created_at']}

**Actions:**
• `/approve {payment['payment_ref']}` - Approve payment
• `/reject {payment['payment_ref']}` - Reject payment
            """
            
            await update.message.reply_text(
                payment_text,
                parse_mode=ParseMode.MARKDOWN
            )
    
    async def approve_payment_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /approve command"""
        user_id = update.effective_user.id
        
        if str(user_id) != str(ADMIN_USER_ID):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Please provide payment reference: `/approve PAY_XXX_XXX`")
            return
        
        payment_ref = context.args[0]
        payment = self.db.get_payment_by_ref(payment_ref)
        
        if not payment:
            await update.message.reply_text("❌ Payment not found.")
            return
        
        # Update payment status
        if self.db.update_payment_status(payment_ref, "completed"):
            # Mark user as paid
            self.db.mark_user_paid(payment['user_id'])
            
            # Send invite link to user
            try:
                await self.app.bot.send_message(
                    chat_id=payment['user_id'],
                    text=f"""
🎉 **Payment Approved!**

Your payment has been verified and approved by admin.

Here's your exclusive invite link:
{TELEGRAM_GROUP_INVITE_LINK}

Welcome to our premium community! 🚀
                    """,
                    parse_mode=ParseMode.MARKDOWN,
                    disable_web_page_preview=True
                )
                
                # Mark invite as sent
                self.db.mark_invite_sent(payment['user_id'])
                
                await update.message.reply_text(f"✅ Payment {payment_ref} approved and invite sent!")
                
            except Exception as e:
                logger.error(f"Error sending invite: {e}")
                await update.message.reply_text(f"✅ Payment approved but failed to send invite. Please send manually.")
        else:
            await update.message.reply_text("❌ Failed to approve payment.")
    
    async def reject_payment_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /reject command"""
        user_id = update.effective_user.id
        
        if str(user_id) != str(ADMIN_USER_ID):
            await update.message.reply_text("❌ Access denied. Admin only.")
            return
        
        if not context.args:
            await update.message.reply_text("❌ Please provide payment reference: `/reject PAY_XXX_XXX`")
            return
        
        payment_ref = context.args[0]
        payment = self.db.get_payment_by_ref(payment_ref)
        
        if not payment:
            await update.message.reply_text("❌ Payment not found.")
            return
        
        # Update payment status
        if self.db.update_payment_status(payment_ref, "rejected"):
            # Notify user
            try:
                await self.app.bot.send_message(
                    chat_id=payment['user_id'],
                    text="""
❌ **Payment Rejected**

Your payment submission has been reviewed and rejected.

This could be due to:
• Incorrect amount
• Invalid transaction
• Insufficient proof

Please try again with correct details or contact support.
                    """,
                    parse_mode=ParseMode.MARKDOWN
                )
                
                await update.message.reply_text(f"❌ Payment {payment_ref} rejected and user notified.")
                
            except Exception as e:
                logger.error(f"Error notifying user: {e}")
                await update.message.reply_text(f"❌ Payment rejected but failed to notify user.")
        else:
            await update.message.reply_text("❌ Failed to reject payment.")
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle inline button callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        if data.startswith("pay_"):
            method = data.replace("pay_", "")
            await self.initiate_payment(query, user_id, method)
        elif data == "help":
            await self.help_command(query, context)
        elif data == "status":
            await self.status_command(query, context)
        elif data == "choose_payment":
            await self.show_payment_methods(query)
        elif data == "cancel_payment":
            await query.edit_message_text("❌ Payment cancelled. Use /start to try again.")
    
    async def initiate_payment(self, update, user_id: int, method: str):
        """Initiate payment process for specific method"""
        try:
            if method not in PAYMENT_METHODS:
                await update.edit_message_text("❌ Invalid payment method.")
                return
            
            # Create payment instructions
            payment_data = self.payment_handler.create_payment_instructions(method, user_id)
            
            if not payment_data:
                await update.edit_message_text("❌ Failed to create payment instructions. Please try again.")
                return
            
            # Store payment in database
            self.db.add_payment(
                user_id=user_id,
                payment_method=method,
                payment_id=payment_data.get('payment_id', ''),
                payment_ref=payment_data['payment_ref'],
                amount=payment_data['amount'],
                currency=payment_data['currency'],
                status="pending"
            )
            
            if method == 'paypal':
                await self.handle_paypal_payment(update, payment_data)
            else:
                await self.handle_manual_payment(update, payment_data)
                
        except Exception as e:
            logger.error(f"Error initiating payment: {e}")
            await update.edit_message_text("❌ An error occurred. Please try again later.")
    
    async def handle_paypal_payment(self, update, payment_data):
        """Handle PayPal payment"""
        payment_text = f"""
💳 **PayPal Payment Ready**

Amount: **${payment_data['amount']} {payment_data['currency']}**
Reference: `{payment_data['payment_ref']}`

Click the button below to complete your payment via PayPal.

⏰ This payment link expires in 30 minutes.
After successful payment, you'll automatically receive your invite link!
        """
        
        keyboard = [
            [InlineKeyboardButton("💳 Pay with PayPal", url=payment_data['payment_url'])],
            [InlineKeyboardButton("❌ Cancel", callback_data="cancel_payment")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await update.edit_message_text(
            payment_text,
            parse_mode=ParseMode.MARKDOWN,
            reply_markup=reply_markup
        )
    
    async def handle_manual_payment(self, update, payment_data):
        """Handle manual payment methods"""
        method = payment_data['method']
        
        # Send payment instructions
        await update.edit_message_text(
            payment_data['instructions'],
            parse_mode=ParseMode.MARKDOWN
        )
        
        # Send QR code if available
        if payment_data.get('qr_code'):
            try:
                qr_image_data = base64.b64decode(payment_data['qr_code'])
                qr_image = io.BytesIO(qr_image_data)
                qr_image.name = f"{method}_qr.png"
                
                await update.get_bot().send_photo(
                    chat_id=update.effective_chat.id,
                    photo=InputFile(qr_image),
                    caption=f"📱 **QR Code for {payment_data['method'].title()} Payment**\n\nScan with your wallet app"
                )
            except Exception as e:
                logger.error(f"Error sending QR code: {e}")
        
        # Send follow-up instructions
        followup_text = f"""
📤 **Next Steps:**

1. Complete the payment using the details above
2. Take a screenshot of your successful transaction
3. Send the screenshot here in this chat
4. Wait for admin verification (usually within 24 hours)

**Payment Reference:** `{payment_data['payment_ref']}`
**Status:** Pending Payment

💡 **Tip:** Include the payment reference in your transaction if possible.
        """
        
        await update.get_bot().send_message(
            chat_id=update.effective_chat.id,
            text=followup_text,
            parse_mode=ParseMode.MARKDOWN
        )
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle photo uploads (payment screenshots)"""
        user_id = update.effective_user.id
        
        # Check if user has pending payments
        # For simplicity, we'll just acknowledge the screenshot
        await update.message.reply_text(
            """
📸 **Screenshot Received!**

Thank you for submitting your payment proof. 

Your screenshot has been forwarded to our admin for verification.
You will be notified once your payment is approved (usually within 24 hours).

**Status:** Under Review ⏳

If you have any questions, please contact support.
            """
        )
        
        # Forward screenshot to admin if configured
        if ADMIN_USER_ID:
            try:
                await context.bot.forward_message(
                    chat_id=ADMIN_USER_ID,
                    from_chat_id=update.effective_chat.id,
                    message_id=update.message.message_id
                )
                
                await context.bot.send_message(
                    chat_id=ADMIN_USER_ID,
                    text=f"""
📸 **Payment Screenshot Received**

👤 **From:** {update.effective_user.first_name} (@{update.effective_user.username or 'N/A'})
🆔 **User ID:** {user_id}
📅 **Date:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Use `/pending` to see all pending payments for review.
                    """
                )
            except Exception as e:
                logger.error(f"Error forwarding to admin: {e}")
    
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

**Available Payment Methods:**
💳 PayPal - $10.00 USD (Instant)
₿ Bitcoin - 0.0001 BTC
🪙 TON Coin - 2.0 TON
🏦 Bank Transfer - ₹100.00 INR
📱 UPI - ₹100.00 INR

**Commands:**
• /start - Begin the process
• /pay - Choose payment method
• /status - Check payment status
• /help - Get help and support

Ready to join our exclusive group? Use /start! 🚀
        """
        
        await update.message.reply_text(response_text)
    
    def run_polling(self):
        """Run the bot using polling"""
        if not self.app:
            self.setup_application()
        
        logger.info("Starting bot in polling mode (Production)...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)
    
    async def run_webhook(self, webhook_url: str, port: int = 8443):
        """Run the bot using webhooks"""
        if not self.app:
            self.setup_application()
        
        logger.info(f"Starting bot in webhook mode on port {port} (Production)")
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