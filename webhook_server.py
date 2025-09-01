"""
Webhook server for handling PayPal payment notifications
This is optional - you can also check payment status manually or use polling
"""
import logging
import json
from datetime import datetime
from flask import Flask, request, jsonify
from telegram import Bot

from config import TELEGRAM_BOT_TOKEN
from database import DatabaseManager
from paypal_handler import PayPalHandler

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
db = DatabaseManager()
paypal_handler = PayPalHandler()
telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)

@app.route('/webhook/paypal', methods=['POST'])
async def paypal_webhook():
    """Handle PayPal webhook notifications"""
    try:
        # Get the webhook data
        webhook_data = request.get_json()
        
        if not webhook_data:
            return jsonify({'error': 'No data received'}), 400
        
        event_type = webhook_data.get('event_type')
        resource = webhook_data.get('resource', {})
        
        logger.info(f"Received PayPal webhook: {event_type}")
        
        # Handle payment completion
        if event_type == 'PAYMENT.SALE.COMPLETED':
            payment_id = resource.get('parent_payment')
            
            if payment_id:
                # Verify the payment
                if paypal_handler.verify_payment(payment_id):
                    # Find user by payment session
                    # This would require storing payment_id in payment_sessions table
                    # For now, we'll handle this in the return URL flow
                    logger.info(f"Payment verified: {payment_id}")
                else:
                    logger.warning(f"Payment verification failed: {payment_id}")
        
        return jsonify({'status': 'success'}), 200
        
    except Exception as e:
        logger.error(f"Webhook error: {e}")
        return jsonify({'error': 'Internal server error'}), 500

@app.route('/payment/success')
async def payment_success():
    """Handle successful payment return from PayPal"""
    try:
        payment_id = request.args.get('paymentId')
        payer_id = request.args.get('PayerID')
        session_id = request.args.get('session_id')
        
        if not all([payment_id, payer_id, session_id]):
            return "Missing payment parameters", 400
        
        # Get payment session
        session = db.get_payment_session(session_id)
        if not session:
            return "Invalid session", 400
        
        user_id = session['user_id']
        
        # Execute the payment
        success, payment_details = paypal_handler.execute_payment(payment_id, payer_id)
        
        if success:
            # Mark user as paid
            db.mark_user_paid(user_id)
            
            # Complete payment session
            db.complete_payment_session(session_id)
            
            # Add payment record
            db.add_payment(
                user_id=user_id,
                payment_id=payment_details['payment_id'],
                payer_id=payer_id,
                amount=payment_details['amount'],
                currency=payment_details['currency'],
                status='approved'
            )
            
            # Send invite link via Telegram
            from config import TELEGRAM_GROUP_INVITE_LINK
            
            invite_text = f"""
🎉 **Payment Successful!**

Thank you for your payment! Your access to the premium group has been activated.

Here's your exclusive invite link:
{TELEGRAM_GROUP_INVITE_LINK}

Welcome to our community! 🚀
            """
            
            await telegram_bot.send_message(
                chat_id=user_id,
                text=invite_text,
                parse_mode='Markdown',
                disable_web_page_preview=True
            )
            
            # Mark invite as sent
            db.mark_invite_sent(user_id)
            
            return """
            <html>
            <head><title>Payment Successful</title></head>
            <body>
                <h1>✅ Payment Successful!</h1>
                <p>Thank you for your payment! You should receive your Telegram group invite link shortly.</p>
                <p>Please check your Telegram bot chat for the invite link.</p>
                <p>You can now close this window.</p>
            </body>
            </html>
            """
        else:
            return """
            <html>
            <head><title>Payment Failed</title></head>
            <body>
                <h1>❌ Payment Failed</h1>
                <p>There was an issue processing your payment. Please try again.</p>
                <p>If the problem persists, please contact support.</p>
            </body>
            </html>
            """, 400
            
    except Exception as e:
        logger.error(f"Payment success handler error: {e}")
        return "Internal server error", 500

@app.route('/payment/cancel')
def payment_cancel():
    """Handle cancelled payment return from PayPal"""
    return """
    <html>
    <head><title>Payment Cancelled</title></head>
    <body>
        <h1>❌ Payment Cancelled</h1>
        <p>Your payment was cancelled. No charges have been made.</p>
        <p>You can try again anytime by returning to the Telegram bot.</p>
        <p>You can now close this window.</p>
    </body>
    </html>
    """

@app.route('/health')
def health_check():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'timestamp': datetime.now().isoformat()
    })

if __name__ == '__main__':
    # For development only - use a proper WSGI server for production
    app.run(host='0.0.0.0', port=5000, debug=False)