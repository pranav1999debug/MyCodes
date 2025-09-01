# Telegram Invite Member Bot - Multi-Payment Support

A comprehensive Telegram bot that manages paid access to your premium Telegram group with support for multiple payment methods including PayPal, Bitcoin, TON Coin, Bank Transfer, and UPI payments.

## 🚀 Features

- 🤖 **Telegram Bot Integration** - Seamless user interaction via Telegram
- 💳 **Multiple Payment Methods** - PayPal, Bitcoin, TON, Bank Transfer, UPI
- 🔄 **Automated PayPal Processing** - Instant verification and access
- 📱 **Manual Payment Verification** - Admin approval system for crypto/bank payments
- 🗄️ **SQLite Database** - User and payment tracking
- 👥 **User Management** - Track payments and invite status
- 📊 **Admin Dashboard** - Statistics and payment management
- 🔐 **Secure** - Payment verification and user authentication
- 🌐 **Production Ready** - Configured for live deployment

## 💰 Supported Payment Methods

### Automated Payments (Instant Access)
- **💳 PayPal** - $10.00 USD (Instant verification)

### Manual Payments (Admin Verification Required)
- **₿ Bitcoin** - $10.00 USD equivalent in BTC
- **🪙 TON Coin** - $10.00 USD equivalent in TON
- **🏦 Bank Transfer** - ₹830.00 INR (Indian Bank Transfer)
- **📱 UPI** - ₹830.00 INR (Indian UPI Payment)

## 🛠️ Setup Instructions

### 1. Prerequisites

- Python 3.8 or higher
- PayPal Developer Account (for PayPal payments)
- Cryptocurrency wallets (for Bitcoin/TON)
- Indian bank account (for Bank/UPI payments)
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
   
   # PayPal Configuration (for PayPal payments)
   PAYPAL_CLIENT_ID=your_paypal_client_id
   PAYPAL_CLIENT_SECRET=your_paypal_client_secret
   PAYPAL_MODE=live  # 'sandbox' for testing, 'live' for production
   
   # Payment Configuration
   PAYMENT_AMOUNT_USD=10.00
   PAYMENT_AMOUNT_INR=830.00
   
   # Cryptocurrency Wallet Addresses
   BITCOIN_WALLET=your_bitcoin_wallet_address
   TON_WALLET=your_ton_wallet_address
   
   # Bank Transfer Details (Indian Bank)
   BANK_NAME=Your Bank Name
   BANK_ACCOUNT_NAME=Your Account Name
   BANK_ACCOUNT_NUMBER=your_account_number
   BANK_IFSC=your_ifsc_code
   UPI_ID=your_upi_id
   
   # Bot Configuration
   ADMIN_USER_ID=your_telegram_user_id
   BOT_MODE=production
   ```

3. **Get your Telegram User ID:**
   - Message @userinfobot on Telegram to get your user ID
   - Add this ID to `ADMIN_USER_ID` in `.env`

### 4. Payment Method Setup

#### PayPal Setup
1. Go to [PayPal Developer](https://developer.paypal.com/)
2. Create a new app
3. Get your Client ID and Client Secret
4. Set `PAYPAL_MODE=live` for production

#### Cryptocurrency Setup
1. Set up Bitcoin and TON wallets
2. Add wallet addresses to `.env`
3. Monitor these wallets for incoming payments

#### Bank/UPI Setup (India)
1. Add your bank account details to `.env`
2. Set up UPI ID for UPI payments
3. Monitor bank account for transfers

### 5. Telegram Bot Setup

1. **Create Bot:**
   - Message @BotFather on Telegram
   - Create a new bot with `/newbot`
   - Get your bot token
   - Add it to your `.env` file

2. **Get Group Invite Link:**
   - Create a Telegram group
   - Generate an invite link
   - Add it to your `.env` file

## 🚀 Running the Bot

### Development Mode
```bash
python run.py --mode polling
```

### Production Mode
```bash
python run.py --mode polling --verbose
```

### Using Docker
```bash
docker-compose up -d
```

## 🎮 Bot Commands

### User Commands
- `/start` - Start the bot and see payment options
- `/help` - Show help information and payment methods
- `/status` - Check payment status
- `/pay` - Choose payment method

### Admin Commands
- `/admin` - Show admin panel
- `/stats` - View bot statistics
- `/pending` - View pending payments awaiting verification
- `/approve <payment_ref>` - Approve a manual payment
- `/reject <payment_ref>` - Reject a manual payment

## 🔄 Payment Flow

### PayPal Payments (Automated)
1. User clicks "💳 PayPal" button
2. Redirected to PayPal for payment
3. Payment automatically verified
4. Invite link sent immediately

### Manual Payments (Crypto/Bank/UPI)
1. User selects payment method
2. Bot shows payment details and QR code
3. User makes payment and uploads screenshot
4. Admin reviews and approves/rejects
5. Invite link sent upon approval

## 📁 File Structure

```
telegram-invite-bot/
├── bot.py                  # Main bot application
├── config.py               # Configuration management
├── database.py             # Database operations
├── payment_handler.py      # Multi-payment integration
├── paypal_handler.py       # PayPal specific handler
├── webhook_server.py       # Webhook server (optional)
├── run.py                  # Main entry point
├── requirements.txt        # Python dependencies
├── .env                    # Environment variables (your config)
├── .env.example           # Environment template
├── Dockerfile             # Docker configuration
├── docker-compose.yml     # Docker Compose setup
└── README.md              # This file
```

## 💾 Database Schema

The bot uses SQLite with the following tables:

- **users** - User information and payment status
- **payments** - Payment records with method and verification status
- **payment_sessions** - Temporary payment sessions for PayPal

## 🔧 Admin Panel Features

### Statistics Dashboard
- Total users and conversion rates
- Payment method breakdown
- Revenue tracking
- User engagement metrics

### Payment Management
- View pending payments
- Approve/reject manual payments
- User notification system
- Payment history tracking

## 🛡️ Security Considerations

1. **Environment Variables** - Keep your `.env` file secure
2. **PayPal Verification** - All PayPal payments are verified with PayPal API
3. **Manual Verification** - Crypto and bank payments require admin approval
4. **User Authentication** - Admin commands require user ID verification
5. **Screenshot Verification** - Payment proofs are forwarded to admin
6. **HTTPS** - Use HTTPS for webhook endpoints in production

## 🚨 Important Production Notes

### Current Configuration
- **PayPal Mode:** LIVE (Production)
- **Bot Mode:** Production
- **Payment Amounts:** 
  - USD: $10.00 (PayPal, Bitcoin, TON)
  - INR: ₹830.00 (Bank Transfer, UPI)

### Your Configured Payment Details
- **Bitcoin Wallet:** `18poFePnQdphmtS9V2gweviWkX2Nha4mKv`
- **TON Wallet:** `UQBDvIbxKNzlkdJdb3djBoF0rNVJuCOKSDMf8hafPtZVrPwt`
- **Bank Account:** Pranav Ranjan Singh - HDFC Bank
- **UPI ID:** `12spranavranjan-3@okhdfcbank`

## 🔍 Troubleshooting

### Common Issues

1. **Bot not responding:**
   - Check your bot token in `.env`
   - Verify bot is not blocked
   - Check internet connection

2. **PayPal errors:**
   - Verify PayPal credentials
   - Check PayPal mode (sandbox/live)
   - Ensure PayPal app permissions

3. **Payment verification issues:**
   - Check admin user ID configuration
   - Verify screenshot forwarding works
   - Ensure database permissions

4. **Crypto payment issues:**
   - Verify wallet addresses are correct
   - Check QR code generation
   - Monitor wallet for incoming transactions

### Logs

The bot logs important events. Check console output for error messages.

## 📈 Usage Examples

### For Users
1. Start bot with `/start`
2. Choose payment method (PayPal for instant access)
3. Complete payment
4. Receive invite link automatically (PayPal) or after admin approval (others)

### For Admins
1. Monitor payments with `/pending`
2. Review screenshots forwarded by bot
3. Approve payments with `/approve PAY_XXX_XXX`
4. View statistics with `/stats`

## 🚀 Production Deployment

### Using systemd
```bash
# Create service file
sudo nano /etc/systemd/system/invite-bot.service

# Add service configuration
[Unit]
Description=Telegram Invite Bot
After=network.target

[Service]
Type=simple
User=botuser
WorkingDirectory=/path/to/bot
ExecStart=/usr/bin/python3 run.py
Restart=always

[Install]
WantedBy=multi-user.target

# Enable and start
sudo systemctl enable invite-bot.service
sudo systemctl start invite-bot.service
```

### Using Docker
```bash
docker-compose up -d
```

## 📞 Support

If you encounter any issues:

1. Check the troubleshooting section
2. Review the logs for error messages
3. Verify all configuration is correct
4. Test with PayPal sandbox first (if using PayPal)
5. Monitor your crypto wallets and bank accounts

## ⚖️ Legal Disclaimer

This bot is for educational and business purposes. Ensure compliance with:
- Telegram Terms of Service
- PayPal Acceptable Use Policy
- Local cryptocurrency regulations
- Banking regulations in your jurisdiction
- Data protection requirements (GDPR, etc.)
- Tax reporting requirements

## 📝 License

This project is licensed under the MIT License.

---

**🔴 Production Mode Active**
**💰 Ready to accept real payments**
**🚀 Bot is configured and ready to use!**

**Next Steps:**
1. Get your Telegram User ID and add it to `ADMIN_USER_ID` in `.env`
2. Run the bot with `python run.py`
3. Test with a small payment first
4. Monitor your wallets and bank account for incoming payments