import logging
import asyncio
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ChatMemberOwner, ChatMemberAdministrator, ChatMemberMember
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters
from telegram.error import TelegramError
from database import Database
from config import BOT_TOKEN, CHANNEL_LINK, CHANNEL_ID, REFERRAL_REWARD, MINIMUM_WITHDRAWAL

# Setup logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# Initialize database
db = Database()

class TelegramBot:
    def __init__(self):
        self.app = Application.builder().token(BOT_TOKEN).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """Setup all command and callback handlers"""
        # Command handlers
        self.app.add_handler(CommandHandler("start", self.start_command))
        self.app.add_handler(CommandHandler("help", self.help_command))
        
        # Callback query handlers
        self.app.add_handler(CallbackQueryHandler(self.button_callback))
        
        # Message handler for channel check
        self.app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_message))
    
    async def check_channel_membership(self, user_id: int, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Check if user is a member of the required channel"""
        try:
            if CHANNEL_ID is None:
                logger.warning("CHANNEL_ID is not set in config.py. Please update it with the actual channel ID.")
                return False
            
            member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
            return member.status in [ChatMemberMember.MEMBER, ChatMemberAdministrator.ADMINISTRATOR, ChatMemberOwner.OWNER]
        except TelegramError as e:
            logger.error(f"Error checking channel membership: {e}")
            return False
    
    def create_main_menu_keyboard(self):
        """Create the main menu with 2x2 button layout"""
        keyboard = [
            [
                InlineKeyboardButton("💰 Balance", callback_data="balance"),
                InlineKeyboardButton("👥 Referrals", callback_data="referrals")
            ],
            [
                InlineKeyboardButton("💸 Withdraw", callback_data="withdraw"),
                InlineKeyboardButton("📖 Earning Guide", callback_data="guide")
            ],
            [
                InlineKeyboardButton("🔗 Get Referral Link", callback_data="get_link")
            ]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    def create_back_keyboard(self):
        """Create a back button to return to main menu"""
        keyboard = [[InlineKeyboardButton("🔙 Back to Menu", callback_data="main_menu")]]
        return InlineKeyboardMarkup(keyboard)
    
    def create_channel_join_keyboard(self):
        """Create keyboard for channel joining"""
        keyboard = [
            [InlineKeyboardButton("📢 Join Channel", url=CHANNEL_LINK)],
            [InlineKeyboardButton("✅ Check Membership", callback_data="check_membership")]
        ]
        return InlineKeyboardMarkup(keyboard)
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /start command"""
        user = update.effective_user
        user_id = user.id
        username = user.username or ""
        first_name = user.first_name or ""
        
        # Check if user came with a referral code
        referred_by = None
        if context.args:
            referral_code = context.args[0]
            referred_by = db.get_user_by_referral_code(referral_code)
        
        # Check if user exists in database
        existing_user = db.get_user(user_id)
        if not existing_user:
            # Add new user
            db.add_user(user_id, username, first_name, referred_by)
            welcome_msg = f"🎉 Welcome {first_name}!\n\n"
            if referred_by:
                welcome_msg += f"✅ You were referred by someone and they got {REFERRAL_REWARD} coins!\n\n"
        else:
            welcome_msg = f"👋 Welcome back {first_name}!\n\n"
        
        # Check channel membership
        is_member = await self.check_channel_membership(user_id, context)
        
        if not is_member:
            db.update_membership_status(user_id, False)
            join_msg = (
                f"{welcome_msg}"
                f"🔒 To access all bot features, you must join our channel first!\n\n"
                f"📢 Please join the channel below and then click 'Check Membership':"
            )
            await update.message.reply_text(
                join_msg,
                reply_markup=self.create_channel_join_keyboard()
            )
        else:
            db.update_membership_status(user_id, True)
            main_msg = (
                f"{welcome_msg}"
                f"🤖 **Refer & Earn Bot**\n\n"
                f"💰 Earn {REFERRAL_REWARD} coins for each friend you refer!\n"
                f"💸 Minimum withdrawal: {MINIMUM_WITHDRAWAL} coins\n\n"
                f"Choose an option below:"
            )
            await update.message.reply_text(
                main_msg,
                reply_markup=self.create_main_menu_keyboard(),
                parse_mode='Markdown'
            )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle the /help command"""
        help_text = (
            "🤖 **Refer & Earn Bot Help**\n\n"
            "📋 **Available Commands:**\n"
            "/start - Start the bot\n"
            "/help - Show this help message\n\n"
            "💰 **How to Earn:**\n"
            f"• Get {REFERRAL_REWARD} coins for each friend you refer\n"
            f"• Minimum withdrawal: {MINIMUM_WITHDRAWAL} coins\n"
            "• Share your referral link with friends\n\n"
            "🔗 **Getting Started:**\n"
            "1. Join our channel\n"
            "2. Get your referral link\n"
            "3. Share with friends\n"
            "4. Earn coins and withdraw!"
        )
        await update.message.reply_text(help_text, parse_mode='Markdown')
    
    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle all button callbacks"""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        # Check if user is a channel member for protected actions
        if data != "check_membership" and data != "main_menu":
            user = db.get_user(user_id)
            if not user or not user[7]:  # is_member field
                await query.edit_message_text(
                    "🔒 Please join our channel first to access this feature!",
                    reply_markup=self.create_channel_join_keyboard()
                )
                return
        
        if data == "balance":
            await self.show_balance(query)
        elif data == "referrals":
            await self.show_referrals(query)
        elif data == "withdraw":
            await self.show_withdraw(query)
        elif data == "guide":
            await self.show_earning_guide(query)
        elif data == "get_link":
            await self.show_referral_link(query)
        elif data == "main_menu":
            await self.show_main_menu(query)
        elif data == "check_membership":
            await self.check_membership_callback(query, context)
    
    async def show_balance(self, query):
        """Show user's current balance"""
        user_id = query.from_user.id
        balance = db.get_user_balance(user_id)
        
        balance_text = (
            f"💰 **Your Balance**\n\n"
            f"Current Balance: **{balance:.2f} coins**\n\n"
            f"💸 Minimum withdrawal: {MINIMUM_WITHDRAWAL} coins\n"
            f"🎯 You need {max(0, MINIMUM_WITHDRAWAL - balance):.2f} more coins to withdraw"
        )
        
        await query.edit_message_text(
            balance_text,
            reply_markup=self.create_back_keyboard(),
            parse_mode='Markdown'
        )
    
    async def show_referrals(self, query):
        """Show user's referral information"""
        user_id = query.from_user.id
        total_referrals, referral_code = db.get_user_referrals(user_id)
        
        bot_username = (await query.bot.get_me()).username
        referral_link = f"https://t.me/{bot_username}?start={referral_code}"
        
        referral_text = (
            f"👥 **Your Referrals**\n\n"
            f"Total Referrals: **{total_referrals}**\n"
            f"Earnings per referral: **{REFERRAL_REWARD} coins**\n"
            f"Total earned: **{total_referrals * REFERRAL_REWARD} coins**\n\n"
            f"🔗 **Your Referral Link:**\n"
            f"`{referral_link}`\n\n"
            f"📤 Share this link with friends to earn coins!"
        )
        
        await query.edit_message_text(
            referral_text,
            reply_markup=self.create_back_keyboard(),
            parse_mode='Markdown'
        )
    
    async def show_withdraw(self, query):
        """Show withdrawal information"""
        user_id = query.from_user.id
        balance = db.get_user_balance(user_id)
        
        if balance < MINIMUM_WITHDRAWAL:
            withdraw_text = (
                f"💸 **Withdrawal**\n\n"
                f"Current Balance: **{balance:.2f} coins**\n"
                f"Minimum Withdrawal: **{MINIMUM_WITHDRAWAL} coins**\n\n"
                f"❌ You need {MINIMUM_WITHDRAWAL - balance:.2f} more coins to withdraw.\n\n"
                f"💡 Refer more friends to increase your balance!"
            )
        else:
            withdraw_text = (
                f"💸 **Withdrawal**\n\n"
                f"Current Balance: **{balance:.2f} coins**\n"
                f"Available for withdrawal: **{balance:.2f} coins**\n\n"
                f"✅ You can withdraw your coins!\n\n"
                f"💳 To request a withdrawal, contact admin:\n"
                f"📞 @admin_username"
            )
        
        await query.edit_message_text(
            withdraw_text,
            reply_markup=self.create_back_keyboard(),
            parse_mode='Markdown'
        )
    
    async def show_earning_guide(self, query):
        """Show earning guide"""
        guide_text = (
            f"📖 **Earning Guide**\n\n"
            f"🎯 **How to Earn Coins:**\n\n"
            f"1️⃣ **Get Your Link**: Click 'Get Referral Link'\n"
            f"2️⃣ **Share**: Send your link to friends\n"
            f"3️⃣ **Earn**: Get {REFERRAL_REWARD} coins per referral\n"
            f"4️⃣ **Withdraw**: Cash out at {MINIMUM_WITHDRAWAL} coins\n\n"
            f"💡 **Tips to Maximize Earnings:**\n"
            f"• Share in groups and social media\n"
            f"• Tell friends about the benefits\n"
            f"• Be active and engage others\n"
            f"• The more you refer, the more you earn!\n\n"
            f"🚀 **Start sharing and earning now!**"
        )
        
        await query.edit_message_text(
            guide_text,
            reply_markup=self.create_back_keyboard(),
            parse_mode='Markdown'
        )
    
    async def show_referral_link(self, query):
        """Show user's referral link"""
        user_id = query.from_user.id
        _, referral_code = db.get_user_referrals(user_id)
        
        bot_username = (await query.bot.get_me()).username
        referral_link = f"https://t.me/{bot_username}?start={referral_code}"
        
        link_text = (
            f"🔗 **Your Referral Link**\n\n"
            f"`{referral_link}`\n\n"
            f"📤 **How to use:**\n"
            f"• Copy the link above\n"
            f"• Share with friends\n"
            f"• Earn {REFERRAL_REWARD} coins per friend\n\n"
            f"💰 Start sharing and earning now!"
        )
        
        await query.edit_message_text(
            link_text,
            reply_markup=self.create_back_keyboard(),
            parse_mode='Markdown'
        )
    
    async def show_main_menu(self, query):
        """Show the main menu"""
        user = query.from_user
        main_msg = (
            f"🤖 **Refer & Earn Bot**\n\n"
            f"👋 Welcome {user.first_name}!\n"
            f"💰 Earn {REFERRAL_REWARD} coins for each friend you refer!\n"
            f"💸 Minimum withdrawal: {MINIMUM_WITHDRAWAL} coins\n\n"
            f"Choose an option below:"
        )
        await query.edit_message_text(
            main_msg,
            reply_markup=self.create_main_menu_keyboard(),
            parse_mode='Markdown'
        )
    
    async def check_membership_callback(self, query, context):
        """Check user's channel membership"""
        user_id = query.from_user.id
        is_member = await self.check_channel_membership(user_id, context)
        
        if is_member:
            db.update_membership_status(user_id, True)
            success_msg = (
                f"✅ **Membership Confirmed!**\n\n"
                f"🎉 Welcome to the Refer & Earn Bot!\n"
                f"💰 Earn {REFERRAL_REWARD} coins for each referral\n\n"
                f"Choose an option below:"
            )
            await query.edit_message_text(
                success_msg,
                reply_markup=self.create_main_menu_keyboard(),
                parse_mode='Markdown'
            )
        else:
            error_msg = (
                f"❌ **Membership Not Found**\n\n"
                f"Please make sure you have joined our channel and try again.\n\n"
                f"📢 Join the channel first:"
            )
            await query.edit_message_text(
                error_msg,
                reply_markup=self.create_channel_join_keyboard()
            )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages"""
        user_id = update.effective_user.id
        user = db.get_user(user_id)
        
        if not user or not user[7]:  # Not a member
            await update.message.reply_text(
                "🔒 Please join our channel first to use the bot!",
                reply_markup=self.create_channel_join_keyboard()
            )
            return
        
        # If user is a member, show main menu
        await update.message.reply_text(
            "🤖 Use the buttons below to navigate:",
            reply_markup=self.create_main_menu_keyboard()
        )
    
    def run(self):
        """Start the bot"""
        logger.info("Starting Refer & Earn Bot...")
        self.app.run_polling(allowed_updates=Update.ALL_TYPES)

def main():
    """Main function to run the bot"""
    bot = TelegramBot()
    bot.run()

if __name__ == "__main__":
    main()