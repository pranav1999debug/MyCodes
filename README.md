# Telegram Refer & Earn Bot

A comprehensive Telegram bot for referral and earning programs with a beautiful 2x2 button layout, channel membership verification, and robust database management.

## Features

- ✅ **Channel Membership Check**: Users must join your channel before accessing bot features
- 🔗 **Referral System**: Unique referral links for each user
- 💰 **Balance Management**: Track user earnings and withdrawals
- 📱 **2x2 Button Layout**: Clean and intuitive user interface
- 🔙 **Navigation**: Back button functionality for easy navigation
- 📊 **Database**: SQLite database for data persistence
- 🎯 **Callback System**: Enhanced callback handling for all features

## Bot Features

### Main Menu (2x2 Layout)
- 💰 **Balance**: Check current coin balance
- 👥 **Referrals**: View referral stats and get referral link
- 💸 **Withdraw**: Request withdrawals (minimum threshold)
- 📖 **Earning Guide**: Complete guide on how to earn

### Additional Features
- 🔗 **Get Referral Link**: Generate and share unique referral links
- ✅ **Channel Verification**: Automatic membership verification
- 🔙 **Back Button**: Easy navigation back to main menu

## Setup Instructions

### 1. Prerequisites

```bash
# Install Python 3.8+
python --version

# Install required packages
pip install -r requirements.txt
```

### 2. Bot Configuration

1. **Create a Telegram Bot**:
   - Message @BotFather on Telegram
   - Use `/newbot` command
   - Follow instructions to create your bot
   - Save the bot token

2. **Get Channel ID**:
   ```bash
   python get_channel_id.py
   ```
   Follow the instructions to get your channel's actual ID.

3. **Update Configuration**:
   Edit `config.py` with your details:
   ```python
   BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
   CHANNEL_ID = -1001234567890  # Your actual channel ID
   CHANNEL_LINK = "https://t.me/+YOUR_CHANNEL_INVITE_LINK"
   ```

### 3. Database Setup

The bot automatically creates the SQLite database on first run. No manual setup required.

### 4. Running the Bot

```bash
python main.py
```

## Bot Usage

### For Users

1. **Start the Bot**: Send `/start` to the bot
2. **Join Channel**: Click "Join Channel" and join the required channel
3. **Verify Membership**: Click "Check Membership" to verify
4. **Get Referral Link**: Use "Get Referral Link" to get your unique link
5. **Share & Earn**: Share your link to earn coins for each referral
6. **Withdraw**: Once you reach the minimum threshold, request withdrawal

### Referral Process

1. User gets their unique referral link
2. They share it with friends
3. Friends click the link and start the bot
4. Friends must join the channel to complete registration
5. Original user gets rewarded with coins

## Configuration Options

### Rewards & Limits

```python
REFERRAL_REWARD = 10.0      # Coins per referral
MINIMUM_WITHDRAWAL = 100.0  # Minimum coins to withdraw
```

### Database

- `users`: Store user information, balances, referral codes
- `referrals`: Track all referral relationships
- `withdrawals`: Manage withdrawal requests

## Bot Commands

- `/start` - Start the bot (with optional referral code)
- `/help` - Show help information

## File Structure

```
├── main.py              # Main bot application
├── database.py          # Database management
├── config.py           # Configuration settings
├── get_channel_id.py   # Utility to get channel ID
├── requirements.txt    # Python dependencies
├── README.md          # This file
└── bot_database.db    # SQLite database (created automatically)
```

## Important Notes

### Channel Setup

1. **Add Bot to Channel**: Add your bot to the channel as an administrator
2. **Channel Type**: 
   - For public channels: Use `@channel_username`
   - For private channels: Use numeric chat ID (e.g., `-1001234567890`)
3. **Permissions**: Bot needs permission to see channel members

### Security

- Keep your bot token secure
- Don't share the bot token publicly
- Consider using environment variables for production

### Database

- SQLite database is created automatically
- Backup your database regularly for production use
- Consider migrating to PostgreSQL for large-scale deployment

## Customization

### Changing Rewards

Edit `config.py`:
```python
REFERRAL_REWARD = 25.0      # Change to your desired amount
MINIMUM_WITHDRAWAL = 200.0  # Change minimum withdrawal
```

### Button Layout

Modify the `create_main_menu_keyboard()` function in `main.py` to customize the button layout.

### Messages

Update the message templates in `main.py` to customize the bot's language and style.

## Troubleshooting

### Common Issues

1. **"Chat not found" error**:
   - Make sure the bot is added to the channel
   - Verify the channel ID is correct
   - For private channels, use numeric ID instead of username

2. **Database errors**:
   - Check file permissions
   - Ensure the directory is writable

3. **Bot not responding**:
   - Verify the bot token is correct
   - Check internet connection
   - Look at console logs for errors

### Getting Channel ID

If you're having trouble getting the channel ID:

1. **Method 1**: Add @userinfobot to your channel
2. **Method 2**: Use @chatid_echo_bot
3. **Method 3**: Check bot logs when users join

## Support

For support and questions:
- Check the console logs for error messages
- Verify all configuration settings
- Ensure bot has proper permissions in the channel

## License

This project is open source. Feel free to modify and use for your own projects.

---

**Happy Earning! 🚀**