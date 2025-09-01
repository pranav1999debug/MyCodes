import paypalrestsdk
import logging
import requests
import time
from typing import Dict, Any, Optional
from config import PAYPAL_CLIENT_ID, PAYPAL_CLIENT_SECRET, PAYPAL_MODE, PAYMENT_AMOUNT, PAYMENT_CURRENCY

class PayPalManager:
    def __init__(self):
        self.client_id = PAYPAL_CLIENT_ID
        self.client_secret = PAYPAL_CLIENT_SECRET
        self.mode = PAYPAL_MODE
        
        # Configure PayPal SDK
        paypalrestsdk.configure({
            "mode": self.mode,
            "client_id": self.client_id,
            "client_secret": self.client_secret
        })
        
        self.base_url = "https://api.sandbox.paypal.com" if self.mode == "sandbox" else "https://api.paypal.com"
        self.access_token = None
        self.token_expires_at = None
    
    def get_access_token(self) -> Optional[str]:
        """Get PayPal access token"""
        try:
            url = f"{self.base_url}/v1/oauth2/token"
            headers = {
                "Accept": "application/json",
                "Accept-Language": "en_US"
            }
            data = {
                "grant_type": "client_credentials"
            }
            
            response = requests.post(
                url,
                headers=headers,
                data=data,
                auth=(self.client_id, self.client_secret)
            )
            
            if response.status_code == 200:
                token_data = response.json()
                self.access_token = token_data["access_token"]
                self.token_expires_at = token_data.get("expires_in", 3600)
                return self.access_token
            else:
                logging.error(f"Failed to get access token: {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error getting PayPal access token: {e}")
            return None
    
    def create_payment(self, user_id: int, description: str = "Telegram Group Access") -> Optional[Dict[str, Any]]:
        """Create a PayPal payment"""
        try:
            if not self.access_token:
                self.get_access_token()
            
            payment_data = {
                "intent": "sale",
                "payer": {
                    "payment_method": "paypal"
                },
                "transactions": [{
                    "amount": {
                        "total": str(PAYMENT_AMOUNT),
                        "currency": PAYMENT_CURRENCY
                    },
                    "description": description,
                    "custom": str(user_id)  # Store user ID in custom field
                }],
                "redirect_urls": {
                    "return_url": "https://your-domain.com/success",  # You'll need to set this up
                    "cancel_url": "https://your-domain.com/cancel"    # You'll need to set this up
                }
            }
            
            payment = paypalrestsdk.Payment(payment_data)
            
            if payment.create():
                logging.info(f"Payment created successfully: {payment.id}")
                return {
                    "payment_id": payment.id,
                    "approval_url": payment.links[1].href,  # PayPal approval URL
                    "status": payment.state
                }
            else:
                logging.error(f"Payment creation failed: {payment.error}")
                return None
                
        except Exception as e:
            logging.error(f"Error creating PayPal payment: {e}")
            return None
    
    def execute_payment(self, payment_id: str, payer_id: str) -> Optional[Dict[str, Any]]:
        """Execute a PayPal payment after user approval"""
        try:
            if not self.access_token:
                self.get_access_token()
            
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if payment.execute({"payer_id": payer_id}):
                logging.info(f"Payment executed successfully: {payment.id}")
                return {
                    "payment_id": payment.id,
                    "status": payment.state,
                    "transaction_id": payment.transactions[0].related_resources[0].sale.id
                }
            else:
                logging.error(f"Payment execution failed: {payment.error}")
                return None
                
        except Exception as e:
            logging.error(f"Error executing PayPal payment: {e}")
            return None
    
    def verify_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Verify a PayPal payment status"""
        try:
            if not self.access_token:
                self.get_access_token()
            
            payment = paypalrestsdk.Payment.find(payment_id)
            
            if payment:
                return {
                    "payment_id": payment.id,
                    "status": payment.state,
                    "amount": payment.transactions[0].amount.total,
                    "currency": payment.transactions[0].amount.currency,
                    "custom": payment.transactions[0].custom  # User ID
                }
            else:
                logging.error(f"Payment not found: {payment_id}")
                return None
                
        except Exception as e:
            logging.error(f"Error verifying PayPal payment: {e}")
            return None
    
    def get_payment_details(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Get detailed payment information"""
        try:
            if not self.access_token:
                self.get_access_token()
            
            url = f"{self.base_url}/v1/payments/payment/{payment_id}"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Content-Type": "application/json"
            }
            
            response = requests.get(url, headers=headers)
            
            if response.status_code == 200:
                return response.json()
            else:
                logging.error(f"Failed to get payment details: {response.text}")
                return None
                
        except Exception as e:
            logging.error(f"Error getting payment details: {e}")
            return None

# Alternative implementation for USDT payments (since PayPal doesn't directly support USDT)
class USDTPaymentManager:
    """
    Since PayPal doesn't directly support USDT, this is a placeholder for USDT payment integration.
    You would need to integrate with a crypto payment processor like:
    - Coinbase Commerce
    - BitPay
    - Crypto.com Pay
    - Or implement your own USDT wallet integration
    """
    
    def __init__(self):
        self.payment_amount = PAYMENT_AMOUNT
        self.currency = "USDT"
    
    def create_payment(self, user_id: int, description: str = "Telegram Group Access") -> Optional[Dict[str, Any]]:
        """Create a USDT payment request"""
        # This is a placeholder implementation
        # In a real implementation, you would:
        # 1. Generate a unique payment address
        # 2. Set up webhook monitoring for incoming transactions
        # 3. Verify the payment amount and confirmations
        
        payment_id = f"usdt_{user_id}_{int(time.time())}"
        
        return {
            "payment_id": payment_id,
            "amount": self.payment_amount,
            "currency": self.currency,
            "address": "0x742d35Cc6634C0532925a3b8D4C9db96C4b4d8b6",  # Placeholder address
            "status": "pending",
            "instructions": f"Send exactly {self.payment_amount} USDT to the provided address"
        }
    
    def verify_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Verify USDT payment"""
        # This is a placeholder implementation
        # In a real implementation, you would:
        # 1. Check blockchain for transactions to the payment address
        # 2. Verify the amount matches exactly
        # 3. Check for sufficient confirmations
        
        return {
            "payment_id": payment_id,
            "status": "verified",  # Placeholder - always returns verified
            "amount": self.payment_amount,
            "currency": self.currency
        }