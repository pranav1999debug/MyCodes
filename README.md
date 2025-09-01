# Telegram Invite Member Bot

A Telegram bot that manages group invite access through payment verification. Users must pay 10 USDT to receive an invite link to an exclusive Telegram group.

## Features

- 🤖 **Telegram Bot Integration**: Full Telegram Bot API integration
- 💳 **Multiple Payment Methods**: Support for PayPal and USDT payments
- 🗄️ **Database Management**: SQLite database for user and payment tracking
- 🔒 **Payment Verification**: Automatic payment verification system
- 📊 **User Management**: Track user status and payment history
- 🛡️ **Error Handling**: Comprehensive error handling and logging
- 📝 **Audit Trail**: Complete logging of all user actions and payments

## Configuration

### Required API Keys

1. **Telegram Bot Token**: `8270681359:AAF1TcTLkbqM9DlloE_-1ThzirSWgVpceyI`
2. **PayPal Client ID**: `AYoXO1m62hxQZJ5Kvi64723cNFYABj4_6cThvEQGwzSssMw7inZb_Zw8oujLX77kKpXSgbGDwaezdQ7M`
3. **PayPal Client Secret**: `ELzXi6pbH-6xGA46w04NRcE1yAw1Wo2Y8WUbA7iAEimk4QezR-wYrkdRXxUmsyP5BQaYmAAVO0LqHxUA`
4. **Telegram Group Invite Link**: `https://t.me/+xOBgxKDODnUzYjI1`

### Payment Settings

- **Amount**: 10 USDT
- **Currency**: USD (for PayPal), USDT (for crypto)
- **Payment Methods**: PayPal, USDT (Ethereum ERC-20)

## Installation

1. **Clone the repository**:
   ```bash
   git clone <repository-url>
   cd telegram-invite-bot
   ```

2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure the bot**:
   - Update `config.py` with your API keys and settings
   - Modify payment amounts and group invite link as needed

4. **Run the bot**:
   ```bash
   python telegram_bot.py
   ```

## Project Structure

```
telegram-invite-bot/
├── telegram_bot.py          # Main bot application
├── config.py                # Configuration settings
├── database.py              # Database management
├── paypal_integration.py    # PayPal payment integration
├── error_handler.py         # Error handling utilities
├── logger_config.py         # Logging configuration
├── requirements.txt         # Python dependencies
├── README.md               # This file
└── logs/                   # Log files (created automatically)
    ├── bot_YYYYMMDD.log    # Daily bot logs
    └── errors_YYYYMMDD.log # Error logs
```

## Bot Commands

- `/start` - Start the bot and begin payment process
- `/help` - Show help information
- `/status` - Check your payment status

## How It Works

1. **User starts the bot** with `/start` command
2. **User selects payment method** (PayPal or USDT)
3. **Payment is processed**:
   - PayPal: Redirects to PayPal for payment
   - USDT: Provides wallet address for crypto payment
4. **Payment verification**:
   - PayPal: Checks payment status via API
   - USDT: Verifies blockchain transaction (placeholder implementation)
5. **Access granted**: User receives group invite link upon successful payment

## Database Schema

### Users Table
- `user_id` (INTEGER, PRIMARY KEY)
- `username` (TEXT)
- `first_name` (TEXT)
- `last_name` (TEXT)
- `created_at` (TIMESTAMP)
- `payment_status` (TEXT)
- `payment_id` (TEXT)
- `payment_verified_at` (TIMESTAMP)

### Payments Table
- `id` (INTEGER, PRIMARY KEY)
- `user_id` (INTEGER, FOREIGN KEY)
- `payment_id` (TEXT, UNIQUE)
- `amount` (REAL)
- `currency` (TEXT)
- `status` (TEXT)
- `created_at` (TIMESTAMP)
- `verified_at` (TIMESTAMP)

## Security Features

- Input validation and sanitization
- Rate limiting for user actions
- Comprehensive error handling
- Security event logging
- SQL injection protection
- XSS protection

## Logging

The bot includes comprehensive logging:

- **Daily logs**: `logs/bot_YYYYMMDD.log`
- **Error logs**: `logs/errors_YYYYMMDD.log`
- **User actions**: All user interactions are logged
- **Payment events**: All payment-related events are tracked
- **Security events**: Suspicious activities are logged

## PayPal Integration

The bot uses PayPal REST API for payment processing:

- **Sandbox Mode**: Currently configured for testing
- **Production Mode**: Change `PAYPAL_MODE` to "live" for production
- **Webhook Support**: Can be extended for real-time payment notifications

## USDT Integration

**Note**: The current USDT integration is a placeholder. For production use, you need to:

1. **Integrate with a crypto payment processor**:
   - Coinbase Commerce
   - BitPay
   - Crypto.com Pay
   - Or implement your own wallet integration

2. **Set up blockchain monitoring**:
   - Monitor incoming transactions
   - Verify payment amounts
   - Check confirmation requirements

## Deployment

### Local Development
```bash
python telegram_bot.py
```

### Production Deployment

1. **Use a process manager** (PM2, systemd, etc.)
2. **Set up reverse proxy** (nginx, Apache)
3. **Configure SSL/TLS** for webhook endpoints
4. **Set up monitoring** and alerting
5. **Regular backups** of database and logs

### Environment Variables

For production, consider using environment variables:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export PAYPAL_CLIENT_ID="your_paypal_client_id"
export PAYPAL_CLIENT_SECRET="your_paypal_secret"
export PAYPAL_MODE="live"
```

## Troubleshooting

### Common Issues

1. **Bot not responding**:
   - Check if bot token is correct
   - Verify internet connection
   - Check logs for errors

2. **Payment verification failing**:
   - Verify PayPal credentials
   - Check payment status in PayPal dashboard
   - Review payment logs

3. **Database errors**:
   - Check database file permissions
   - Verify SQLite installation
   - Review database logs

### Log Analysis

Check the log files for detailed error information:

```bash
# View recent bot logs
tail -f logs/bot_$(date +%Y%m%d).log

# View error logs
tail -f logs/errors_$(date +%Y%m%d).log
```

## Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests if applicable
5. Submit a pull request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

For support and questions:

1. Check the troubleshooting section
2. Review the logs
3. Create an issue in the repository
4. Contact the development team

## Disclaimer

This bot is for educational and legitimate business purposes only. Ensure compliance with:

- Local laws and regulations
- Telegram's Terms of Service
- PayPal's Terms of Service
- Cryptocurrency regulations in your jurisdiction

## Future Enhancements

- [ ] Real-time USDT payment verification
- [ ] Multiple group support
- [ ] Admin dashboard
- [ ] Payment analytics
- [ ] Webhook support for instant notifications
- [ ] Multi-language support
- [ ] Subscription management
- [ ] Refund system