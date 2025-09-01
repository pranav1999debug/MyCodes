# Telegram Invite Member Bot

A Telegram bot that manages paid access to your premium Telegram group. Users must complete a $10 USD PayPal payment before receiving the group invite link.

## Features

- 🤖 **Telegram Bot Integration** - Seamless user interaction via Telegram
- 💳 **PayPal Payment Processing** - Secure payment handling via PayPal API
- 🗄️ **SQLite Database** - User and payment tracking
- 👥 **User Management** - Track payments and invite status
- 📊 **Admin Dashboard** - Statistics and user management
- 🔐 **Secure** - Payment verification and user authentication
- 🚀 **Easy Deployment** - Simple setup and configuration

## Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- PayPal Developer Account
- Telegram Bot Token
- Telegram Group Admin Access

### 2. Installation

```bash
# Clone the repository
git clone <your-repo-url>
cd telegram-invite-bot

# Install dependencies
pip install -r requirements.txt
```

### 3. Configuration

1. **Copy and edit the environment file:**
   ```bash
   cp .env.example .env
   ```

2. **Update `.env` with your credentials:**
   ```env
   # Telegram Bot Configuration
   TELEGRAM_BOT_TOKEN=your_bot_token_here
   TELEGRAM_GROUP_INVITE_LINK=your_group_invite_link
   
   # PayPal Configuration
   PAYPAL_CLIENT_ID=your_paypal_client_id
   PAYPAL_CLIENT_SECRET=your_paypal_client_secret
   PAYPAL_MODE=sandbox  # Change to 'live' for production
   
   # Bot Configuration
   PAYMENT_AMOUNT=10.00
   PAYMENT_CURRENCY=USD
   ADMIN_USER_ID=your_telegram_user_id
   ```

3. **Get your Telegram User ID:**
   - Message @userinfobot on Telegram to get your user ID
   - Add this ID to `ADMIN_USER_ID` in `.env`

### 4. PayPal Setup

1. **Create PayPal App:**
   - Go to [PayPal Developer](https://developer.paypal.com/)
   - Create a new app
   - Get your Client ID and Client Secret
   - Add them to your `.env` file

2. **Set PayPal Mode:**
   - Use `sandbox` for testing
   - Use `live` for production

### 5. Telegram Bot Setup

1. **Create Bot:**
   - Message @BotFather on Telegram
   - Create a new bot with `/newbot`
   - Get your bot token
   - Add it to your `.env` file

2. **Get Group Invite Link:**
   - Create a Telegram group
   - Make your bot an admin (optional)
   - Generate an invite link
   - Add it to your `.env` file

## Running the Bot

### Development Mode (Polling)

```bash
python bot.py
```

### Production Mode (Webhooks)

1. **Set up your webhook URL in `bot.py`:**
   ```python
   self.webhook_base_url = "https://your-domain.com"
   ```

2. **Run the webhook server:**
   ```bash
   python webhook_server.py
   ```

3. **Set up reverse proxy (nginx example):**
   ```nginx
   server {
       listen 443 ssl;
       server_name your-domain.com;
       
       location /webhook/ {
           proxy_pass http://127.0.0.1:5000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
       }
   }
   ```

## Bot Commands

### User Commands

- `/start` - Start the bot and see payment options
- `/help` - Show help information
- `/status` - Check payment status
- `/pay` - Initiate payment process

### Admin Commands

- `/admin` - Show admin panel
- `/stats` - View bot statistics

## File Structure

```
telegram-invite-bot/
├── bot.py              # Main bot application
├── config.py           # Configuration management
├── database.py         # Database operations
├── paypal_handler.py   # PayPal integration
├── webhook_server.py   # Webhook server (optional)
├── requirements.txt    # Python dependencies
├── .env               # Environment variables
└── README.md          # This file
```

## Database Schema

The bot uses SQLite with the following tables:

- **users** - User information and payment status
- **payments** - Payment records
- **payment_sessions** - Temporary payment sessions

## Security Considerations

1. **Environment Variables** - Keep your `.env` file secure
2. **PayPal Verification** - All payments are verified with PayPal
3. **User Authentication** - Admin commands require user ID verification
4. **HTTPS** - Use HTTPS for webhook endpoints in production

## Troubleshooting

### Common Issues

1. **Bot not responding:**
   - Check your bot token
   - Ensure the bot is not blocked
   - Check internet connection

2. **PayPal errors:**
   - Verify client ID and secret
   - Check PayPal mode (sandbox/live)
   - Ensure PayPal app permissions

3. **Database errors:**
   - Check file permissions
   - Ensure SQLite is installed
   - Check disk space

### Logs

The bot logs important events. Check the console output for error messages.

## Production Deployment

### Using Docker (Recommended)

1. **Create Dockerfile:**
   ```dockerfile
   FROM python:3.9-slim
   WORKDIR /app
   COPY requirements.txt .
   RUN pip install -r requirements.txt
   COPY . .
   CMD ["python", "bot.py"]
   ```

2. **Build and run:**
   ```bash
   docker build -t invite-bot .
   docker run -d --env-file .env invite-bot
   ```

### Using systemd

1. **Create service file:**
   ```ini
   [Unit]
   Description=Telegram Invite Bot
   After=network.target
   
   [Service]
   Type=simple
   User=botuser
   WorkingDirectory=/path/to/bot
   ExecStart=/usr/bin/python3 bot.py
   Restart=always
   
   [Install]
   WantedBy=multi-user.target
   ```

2. **Enable and start:**
   ```bash
   sudo systemctl enable invite-bot.service
   sudo systemctl start invite-bot.service
   ```

## Support

If you encounter any issues:

1. Check the troubleshooting section
2. Review the logs for error messages
3. Ensure all configuration is correct
4. Test with PayPal sandbox first

## License

This project is licensed under the MIT License.

## Disclaimer

This bot is for educational purposes. Ensure compliance with:
- Telegram Terms of Service
- PayPal Acceptable Use Policy
- Local laws and regulations
- Data protection requirements

---

**Note:** Always test thoroughly with PayPal sandbox before going live with real payments.