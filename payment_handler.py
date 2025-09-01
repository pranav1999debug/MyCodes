import logging
import uuid
from datetime import datetime, timedelta
from typing import Optional, Dict, Tuple, List
from config import PAYMENT_METHODS, PAYMENT_AMOUNT_USD, PAYMENT_AMOUNT_INR
from paypal_handler import PayPalHandler

logger = logging.getLogger(__name__)

# QR code functionality (optional)
try:
    import qrcode
    import io
    import base64
    QR_AVAILABLE = True
except ImportError:
    QR_AVAILABLE = False
    logger.warning("QR code libraries not available. QR codes will be disabled.")

class PaymentHandler:
    def __init__(self):
        # Initialize PayPal handler
        self.paypal_handler = PayPalHandler()
        
    def get_available_payment_methods(self) -> Dict:
        """Get all available payment methods"""
        return PAYMENT_METHODS
    
    def generate_payment_reference(self, user_id: int, method: str) -> str:
        """Generate a unique payment reference"""
        timestamp = datetime.now().strftime("%Y%m%d%H%M%S")
        return f"PAY_{method.upper()}_{user_id}_{timestamp}"
    
    def create_payment_instructions(self, method: str, user_id: int) -> Dict:
        """Create payment instructions for a specific method"""
        if method not in PAYMENT_METHODS:
            return None
        
        payment_method = PAYMENT_METHODS[method]
        payment_ref = self.generate_payment_reference(user_id, method)
        
        if method == 'paypal':
            return self._create_paypal_payment(user_id, payment_ref)
        elif method == 'bitcoin':
            return self._create_bitcoin_payment(payment_method, payment_ref)
        elif method == 'ton':
            return self._create_ton_payment(payment_method, payment_ref)
        elif method == 'bank_transfer':
            return self._create_bank_transfer_payment(payment_method, payment_ref)
        elif method == 'upi':
            return self._create_upi_payment(payment_method, payment_ref)
        
        return None
    
    def _create_paypal_payment(self, user_id: int, payment_ref: str) -> Dict:
        """Create PayPal payment"""
        try:
            # Generate session ID
            session_id = PayPalHandler.generate_session_id()
            
            # Create return URLs (update base URL for production)
            webhook_base_url = "https://your-domain.com"  # Update this
            return_url, cancel_url = self.paypal_handler.create_return_urls(
                webhook_base_url, 
                session_id
            )
            
            # Create PayPal payment
            payment_url, payment_id = self.paypal_handler.create_payment(
                user_id=user_id,
                return_url=return_url,
                cancel_url=cancel_url
            )
            
            if payment_url and payment_id:
                return {
                    'method': 'paypal',
                    'payment_ref': payment_ref,
                    'session_id': session_id,
                    'payment_url': payment_url,
                    'payment_id': payment_id,
                    'amount': PAYMENT_AMOUNT_USD,
                    'currency': 'USD',
                    'instructions': f"Click the PayPal button to complete your ${PAYMENT_AMOUNT_USD} USD payment.",
                    'type': 'automated'
                }
            else:
                return None
                
        except Exception as e:
            logger.error(f"Error creating PayPal payment: {e}")
            return None
    
    def _create_bitcoin_payment(self, payment_method: Dict, payment_ref: str) -> Dict:
        """Create Bitcoin payment instructions"""
        wallet_address = payment_method['wallet']
        amount = payment_method['amount']
        
        # Generate QR code for Bitcoin payment
        bitcoin_uri = f"bitcoin:{wallet_address}?amount={amount}&label=TelegramGroupAccess&message={payment_ref}"
        qr_code = self._generate_qr_code(bitcoin_uri)
        
        instructions = f"""
**Bitcoin Payment Instructions:**

💰 **Amount:** ${amount} USD worth of Bitcoin
📧 **Wallet Address:** `{wallet_address}`
🔖 **Reference:** `{payment_ref}`

**Steps:**
1. Send the equivalent of ${amount} USD in Bitcoin to the above address
2. Include the reference in transaction memo (if possible)
3. Send screenshot of transaction to admin for verification
4. Wait for 1 confirmation before access is granted

**Important:** Make sure to send the exact USD equivalent in Bitcoin at current market rates.
        """
        
        return {
            'method': 'bitcoin',
            'payment_ref': payment_ref,
            'wallet_address': wallet_address,
            'amount': amount,
            'currency': 'USD',
            'network': payment_method['network'],
            'qr_code': qr_code,
            'bitcoin_uri': bitcoin_uri,
            'instructions': instructions,
            'type': 'manual'
        }
    
    def _create_ton_payment(self, payment_method: Dict, payment_ref: str) -> Dict:
        """Create TON payment instructions"""
        wallet_address = payment_method['wallet']
        amount = payment_method['amount']
        
        # Generate QR code for TON payment
        ton_uri = f"ton://transfer/{wallet_address}?amount={amount}&text={payment_ref}"
        qr_code = self._generate_qr_code(wallet_address)
        
        instructions = f"""
**TON Payment Instructions:**

💰 **Amount:** ${amount} USD worth of TON
📧 **Wallet Address:** `{wallet_address}`
🔖 **Reference:** `{payment_ref}`

**Steps:**
1. Send the equivalent of ${amount} USD in TON to the above address
2. Include the reference in transaction comment: `{payment_ref}`
3. Send screenshot of transaction to admin for verification
4. Wait for confirmation before access is granted

**Important:** Make sure to send the exact USD equivalent in TON at current market rates.
        """
        
        return {
            'method': 'ton',
            'payment_ref': payment_ref,
            'wallet_address': wallet_address,
            'amount': amount,
            'currency': 'USD',
            'network': payment_method['network'],
            'qr_code': qr_code,
            'ton_uri': ton_uri,
            'instructions': instructions,
            'type': 'manual'
        }
    
    def _create_bank_transfer_payment(self, payment_method: Dict, payment_ref: str) -> Dict:
        """Create bank transfer payment instructions"""
        amount = payment_method['amount']
        
        instructions = f"""
**Bank Transfer Instructions (India):**

💰 **Amount:** ₹{amount}
🏦 **Bank:** {payment_method['bank_name']}
👤 **Account Name:** {payment_method['account_name']}
🔢 **Account Number:** `{payment_method['account_number']}`
🏛️ **IFSC Code:** `{payment_method['ifsc']}`
🔖 **Reference:** `{payment_ref}`

**Steps:**
1. Transfer exactly ₹{amount} to the above account
2. Use reference `{payment_ref}` in transaction remarks
3. Send screenshot of successful transfer to admin
4. Wait for verification before access is granted

**Important:** Include the reference in your transfer remarks for quick verification.
        """
        
        return {
            'method': 'bank_transfer',
            'payment_ref': payment_ref,
            'bank_name': payment_method['bank_name'],
            'account_name': payment_method['account_name'],
            'account_number': payment_method['account_number'],
            'ifsc': payment_method['ifsc'],
            'amount': amount,
            'currency': 'INR',
            'instructions': instructions,
            'type': 'manual'
        }
    
    def _create_upi_payment(self, payment_method: Dict, payment_ref: str) -> Dict:
        """Create UPI payment instructions"""
        amount = payment_method['amount']
        upi_id = payment_method['upi_id']
        
        # Generate UPI payment link
        upi_link = f"upi://pay?pa={upi_id}&pn=Pranav Ranjan Singh&am={amount}&cu=INR&tn={payment_ref}"
        qr_code = self._generate_qr_code(upi_link)
        
        instructions = f"""
**UPI Payment Instructions:**

💰 **Amount:** ₹{amount}
📱 **UPI ID:** `{upi_id}`
🔖 **Reference:** `{payment_ref}`

**Steps:**
1. Pay exactly ₹{amount} to the UPI ID above
2. Use reference `{payment_ref}` in transaction note
3. Send screenshot of successful payment to admin
4. Wait for verification before access is granted

**Quick Pay:** You can also scan the QR code below with any UPI app.
        """
        
        return {
            'method': 'upi',
            'payment_ref': payment_ref,
            'upi_id': upi_id,
            'amount': amount,
            'currency': 'INR',
            'upi_link': upi_link,
            'qr_code': qr_code,
            'instructions': instructions,
            'type': 'manual'
        }
    
    def _generate_qr_code(self, data: str) -> str:
        """Generate QR code and return as base64 string"""
        if not QR_AVAILABLE:
            return None
            
        try:
            qr = qrcode.QRCode(
                version=1,
                error_correction=qrcode.constants.ERROR_CORRECT_L,
                box_size=10,
                border=4,
            )
            qr.add_data(data)
            qr.make(fit=True)
            
            img = qr.make_image(fill_color="black", back_color="white")
            
            # Convert to base64
            buffer = io.BytesIO()
            img.save(buffer, format='PNG')
            buffer.seek(0)
            
            return base64.b64encode(buffer.getvalue()).decode()
        except Exception as e:
            logger.error(f"Error generating QR code: {e}")
            return None
    
    def verify_paypal_payment(self, payment_id: str, payer_id: str) -> Tuple[bool, Optional[Dict]]:
        """Verify PayPal payment"""
        return self.paypal_handler.execute_payment(payment_id, payer_id)
    
    def get_payment_method_display_name(self, method: str) -> str:
        """Get display name for payment method"""
        if method in PAYMENT_METHODS:
            return PAYMENT_METHODS[method]['name']
        return method.title()
    
    def get_payment_amount_display(self, method: str) -> str:
        """Get formatted payment amount for display"""
        if method not in PAYMENT_METHODS:
            return ""
        
        payment_method = PAYMENT_METHODS[method]
        symbol = payment_method['symbol']
        amount = payment_method['amount']
        currency = payment_method['currency']
        
        return f"{symbol}{amount} {currency}"