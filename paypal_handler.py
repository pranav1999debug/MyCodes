import paypalrestsdk
import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple
from config import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_MODE, PAYMENT_AMOUNT, PAYMENT_CURRENCY

class PayPalHandler:
    def __init__(self):
        # Configure PayPal SDK
        paypalrestsdk.configure({
            "mode": PAYPAL_MODE,  # sandbox or live
            "client_id": PAYPAL_CLIENT_ID,
            "client_secret": PAYPAL_CLIENT_SECRET
        })
        logging.info(f"PayPal configured in {PAYPAL_MODE} mode")
    
    def create_payment(self, user_id: int, return_url: str, cancel_url: str) -> Tuple[Optional[str], Optional[str]]:
        """
        Create a PayPal payment
        Returns: (payment_url, payment_id) or (None, None) if failed
        """
        try:
            payment = paypalrestsdk.Payment({
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "redirect_urls": {
                    "return_url": return_url,
                    "cancel_url": cancel_url
                },
                "transactions": [{
                    "item_list": {
                        "items": [{
                            "name": "Telegram Group Access",
                            "sku": f"tg_access_{user_id}",
                            "price": str(PAYMENT_AMOUNT),
                            "currency": PAYMENT_CURRENCY,
                            "quantity": 1
                        }]
                    },
                    "amount": {
                        "total": str(PAYMENT_AMOUNT),
                        "currency": PAYMENT_CURRENCY
                    },
                    "description": f"Payment for Telegram group access - User ID: {user_id}"
                }]
            })
            
            if payment.create():
                logging.info(f"Payment created successfully for user {user_id}: {payment.id}")
                
                # Get the approval URL
                for link in payment.links:
                    if link.rel == "approval_url":
                        return link.href, payment.id
                
                logging.error("No approval URL found in payment links")
                return None, None
            else:
                logging.error(f"Payment creation failed: {payment.error}")
                return None, None
                
        except Exception as e:
            logging.error(f"Exception creating PayPal payment: {e}")
            return None, None
    
    def execute_payment(self, payment_id: str, payer_id: str) -> Tuple[bool, Optional[Dict]]:
        """
        Execute a PayPal payment after user approval
        Returns: (success, payment_details)
        """
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if payment.execute({"payer_id": payer_id}):
                logging.info(f"Payment executed successfully: {payment_id}")
                
                # Extract payment details
                payment_details = {
                    'payment_id': payment.id,
                    'payer_id': payer_id,
                    'state': payment.state,
                    'amount': float(payment.transactions[0].amount.total),
                    'currency': payment.transactions[0].amount.currency,
                    'create_time': payment.create_time,
                    'update_time': payment.update_time
                }
                
                return True, payment_details
            else:
                logging.error(f"Payment execution failed: {payment.error}")
                return False, None
                
        except Exception as e:
            logging.error(f"Exception executing PayPal payment: {e}")
            return False, None
    
    def get_payment_details(self, payment_id: str) -> Optional[Dict]:
        """Get details of a PayPal payment"""
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            
            payment_details = {
                'payment_id': payment.id,
                'state': payment.state,
                'intent': payment.intent,
                'amount': float(payment.transactions[0].amount.total) if payment.transactions else 0,
                'currency': payment.transactions[0].amount.currency if payment.transactions else '',
                'create_time': payment.create_time,
                'update_time': payment.update_time,
                'payer_info': payment.payer.payer_info.__dict__ if hasattr(payment.payer, 'payer_info') else {}
            }
            
            return payment_details
            
        except Exception as e:
            logging.error(f"Exception getting PayPal payment details: {e}")
            return None
    
    def verify_payment(self, payment_id: str) -> bool:
        """Verify that a payment was completed successfully"""
        try:
            payment = paypalrestsdk.Payment.find(payment_id)
            return payment.state == "approved"
        except Exception as e:
            logging.error(f"Exception verifying PayPal payment: {e}")
            return False
    
    def generate_webhook_url(self, base_url: str) -> str:
        """Generate webhook URL for PayPal notifications"""
        return f"{base_url}/webhook/paypal"
    
    @staticmethod
    def generate_session_id() -> str:
        """Generate a unique session ID for payment tracking"""
        return str(uuid.uuid4())
    
    def create_return_urls(self, base_url: str, session_id: str) -> Tuple[str, str]:
        """Create return and cancel URLs for PayPal"""
        return_url = f"{base_url}/payment/success?session_id={session_id}"
        cancel_url = f"{base_url}/payment/cancel?session_id={session_id}"
        return return_url, cancel_url