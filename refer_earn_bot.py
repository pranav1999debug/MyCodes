import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (Application, CommandHandler, CallbackQueryHandler, ContextTypes, MessageHandler, filters)
import aiosqlite
import asyncio

API_TOKEN = '7822214244:AAGLYV2Qy2WZxGsKwU_wD_dbPibBJzGmj68'
CHANNEL_ID = '@G6VMGeXQ0ENmNDQ1'  # Use @username or channel ID
CHANNEL_LINK = 'https://t.me/+G6VMGeXQ0ENmNDQ1'

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

DB_PATH = 'referral_bot.db'

MAIN_MENU_BUTTONS = [
    [InlineKeyboardButton('💰 Balance', callback_data='balance'), InlineKeyboardButton('👥 Referrals', callback_data='referrals')],
    [InlineKeyboardButton('💸 Withdraw', callback_data='withdraw'), InlineKeyboardButton('📖 Earning Guide', callback_data='guide')]
]

BACK_BUTTON = [[InlineKeyboardButton('🔙 Back', callback_data='back')]]

async def init_db():
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('''CREATE TABLE IF NOT EXISTS users (
            user_id INTEGER PRIMARY KEY,
            referred_by INTEGER,
            balance INTEGER DEFAULT 0
        )''')
        await db.execute('''CREATE TABLE IF NOT EXISTS referrals (
            user_id INTEGER,
            referred_id INTEGER,
            PRIMARY KEY (user_id, referred_id)
        )''')
        await db.commit()

async def is_user_in_channel(user_id, context: ContextTypes.DEFAULT_TYPE):
    try:
        member = await context.bot.get_chat_member(CHANNEL_ID, user_id)
        return member.status in ['member', 'administrator', 'creator']
    except Exception as e:
        logger.error(f'Error checking channel membership: {e}')
        return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    args = context.args
    referred_by = int(args[0]) if args and args[0].isdigit() and int(args[0]) != user.id else None
    await init_db()
    async with aiosqlite.connect(DB_PATH) as db:
        await db.execute('INSERT OR IGNORE INTO users (user_id, referred_by) VALUES (?, ?)', (user.id, referred_by))
        await db.commit()
        if referred_by:
            # Add referral if not already present
            await db.execute('INSERT OR IGNORE INTO referrals (user_id, referred_id) VALUES (?, ?)', (referred_by, user.id))
            await db.commit()
    if not await is_user_in_channel(user.id, context):
        await send_join_channel(update, context)
        return
    await send_main_menu(update, context)

def get_referral_link(user_id):
    return f'https://t.me/{context.bot.username}?start={user_id}'

async def send_join_channel(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton('✅ Join Channel', url=CHANNEL_LINK)],
                [InlineKeyboardButton('🔄 I Joined', callback_data='check_join')]]
    reply_markup = InlineKeyboardMarkup(keyboard)
    text = '🚨 To use this bot, please join our channel first!'
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup)
    else:
        await update.message.reply_text(text, reply_markup=reply_markup)

async def send_main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    reply_markup = InlineKeyboardMarkup(MAIN_MENU_BUTTONS)
    text = f'👋 Welcome, {user.first_name}!
\nYour referral link:\n<code>https://t.me/{context.bot.username}?start={user.id}</code>'
    if update.callback_query:
        await update.callback_query.edit_message_text(text, reply_markup=reply_markup, parse_mode='HTML')
    else:
        await update.message.reply_text(text, reply_markup=reply_markup, parse_mode='HTML')

async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    user_id = query.from_user.id
    data = query.data
    if data == 'check_join':
        if await is_user_in_channel(user_id, context):
            await send_main_menu(update, context)
        else:
            await query.answer('Please join the channel first!', show_alert=True)
    elif data == 'balance':
        await show_balance(update, context)
    elif data == 'referrals':
        await show_referrals(update, context)
    elif data == 'withdraw':
        await show_withdraw(update, context)
    elif data == 'guide':
        await show_guide(update, context)
    elif data == 'back':
        await send_main_menu(update, context)
    else:
        await query.answer('Unknown action.')

async def show_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT balance FROM users WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            balance = row[0] if row else 0
    text = f'💰 Your Balance: <b>{balance}</b> points.'
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(BACK_BUTTON), parse_mode='HTML')

async def show_referrals(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.callback_query.from_user.id
    async with aiosqlite.connect(DB_PATH) as db:
        async with db.execute('SELECT COUNT(*) FROM referrals WHERE user_id = ?', (user_id,)) as cursor:
            row = await cursor.fetchone()
            count = row[0] if row else 0
    text = f'👥 You have <b>{count}</b> referrals.\nShare your link to earn more!\n\n<code>https://t.me/{context.bot.username}?start={user_id}</code>'
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(BACK_BUTTON), parse_mode='HTML')

async def show_withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '💸 Withdrawals are processed manually. Please contact admin with your details.'
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(BACK_BUTTON))

async def show_guide(update: Update, context: ContextTypes.DEFAULT_TYPE):
    text = '📖 <b>Earning Guide:</b>\n1. Share your referral link.\n2. Earn points when friends join and use the bot.\n3. Withdraw when you reach the minimum balance.'
    await update.callback_query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(BACK_BUTTON), parse_mode='HTML')

async def main():
    await init_db()
    application = Application.builder().token(API_TOKEN).build()
    application.add_handler(CommandHandler('start', start))
    application.add_handler(CallbackQueryHandler(button_handler))
    print('Bot is running...')
    await application.run_polling()

if __name__ == '__main__':
    asyncio.run(main())