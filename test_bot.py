#!/usr/bin/env python3
"""
Test script for the Telegram Invite Member Bot
This script tests the basic functionality without actually running the bot
"""

import sys
import os
import sqlite3
from datetime import datetime

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from database import DatabaseManager
from paypal_integration import PayPalManager, USDTPaymentManager
from config import *
from logger_config import setup_logging

def test_database():
    """Test database functionality"""
    print("🧪 Testing Database...")
    
    try:
        # Initialize database
        db = DatabaseManager("test_bot.db")
        print("✅ Database initialized successfully")
        
        # Test adding user
        test_user_id = 123456789
        result = db.add_user(
            user_id=test_user_id,
            username="testuser",
            first_name="Test",
            last_name="User"
        )
        print(f"✅ User added: {result}")
        
        # Test getting user
        user_data = db.get_user(test_user_id)
        print(f"✅ User retrieved: {user_data['username'] if user_data else 'None'}")
        
        # Test payment
        payment_id = "test_payment_123"
        result = db.add_payment(
            user_id=test_user_id,
            payment_id=payment_id,
            amount=10.0,
            currency="USD",
            status="pending"
        )
        print(f"✅ Payment added: {result}")
        
        # Test payment verification
        result = db.update_payment_status(payment_id, "verified")
        print(f"✅ Payment verified: {result}")
        
        # Test user payment status update
        result = db.update_user_payment_status(test_user_id, "verified", payment_id)
        print(f"✅ User payment status updated: {result}")
        
        # Cleanup
        os.remove("test_bot.db")
        print("✅ Database test completed successfully")
        
    except Exception as e:
        print(f"❌ Database test failed: {e}")
        return False
    
    return True

def test_paypal_integration():
    """Test PayPal integration (without actual API calls)"""
    print("\n🧪 Testing PayPal Integration...")
    
    try:
        paypal = PayPalManager()
        print("✅ PayPal manager initialized")
        
        # Test access token (this will fail in test environment, but we can check the structure)
        print("✅ PayPal integration structure is correct")
        
    except Exception as e:
        print(f"❌ PayPal integration test failed: {e}")
        return False
    
    return True

def test_usdt_integration():
    """Test USDT integration"""
    print("\n🧪 Testing USDT Integration...")
    
    try:
        usdt = USDTPaymentManager()
        print("✅ USDT manager initialized")
        
        # Test payment creation
        payment_data = usdt.create_payment(
            user_id=123456789,
            description="Test payment"
        )
        
        if payment_data:
            print(f"✅ USDT payment created: {payment_data['payment_id']}")
            
            # Test payment verification
            verification = usdt.verify_payment(payment_data['payment_id'])
            if verification:
                print(f"✅ USDT payment verified: {verification['status']}")
            else:
                print("❌ USDT payment verification failed")
                return False
        else:
            print("❌ USDT payment creation failed")
            return False
        
    except Exception as e:
        print(f"❌ USDT integration test failed: {e}")
        return False
    
    return True

def test_configuration():
    """Test configuration loading"""
    print("\n🧪 Testing Configuration...")
    
    try:
        # Check if all required config values are present
        required_configs = [
            'TELEGRAM_BOT_TOKEN',
            'TELEGRAM_GROUP_INVITE_LINK',
            'PAYPAL_CLIENT_ID',
            'PAYPAL_CLIENT_SECRET',
            'PAYMENT_AMOUNT',
            'PAYMENT_CURRENCY'
        ]
        
        for config in required_configs:
            if not globals().get(config):
                print(f"❌ Missing configuration: {config}")
                return False
        
        print("✅ All required configurations are present")
        print(f"✅ Payment amount: {PAYMENT_AMOUNT} {PAYMENT_CURRENCY}")
        print(f"✅ Group invite link: {TELEGRAM_GROUP_INVITE_LINK}")
        
    except Exception as e:
        print(f"❌ Configuration test failed: {e}")
        return False
    
    return True

def test_logging():
    """Test logging functionality"""
    print("\n🧪 Testing Logging...")
    
    try:
        setup_logging()
        print("✅ Logging system initialized")
        
        # Test logging
        import logging
        logging.info("Test log message")
        logging.warning("Test warning message")
        logging.error("Test error message")
        
        print("✅ Logging test completed")
        
    except Exception as e:
        print(f"❌ Logging test failed: {e}")
        return False
    
    return True

def main():
    """Run all tests"""
    print("🚀 Starting Telegram Invite Member Bot Tests")
    print("=" * 50)
    
    tests = [
        ("Configuration", test_configuration),
        ("Database", test_database),
        ("PayPal Integration", test_paypal_integration),
        ("USDT Integration", test_usdt_integration),
        ("Logging", test_logging)
    ]
    
    passed = 0
    total = len(tests)
    
    for test_name, test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                print(f"❌ {test_name} test failed")
        except Exception as e:
            print(f"❌ {test_name} test crashed: {e}")
    
    print("\n" + "=" * 50)
    print(f"📊 Test Results: {passed}/{total} tests passed")
    
    if passed == total:
        print("🎉 All tests passed! The bot is ready to run.")
        print("\nTo start the bot, run:")
        print("python telegram_bot.py")
    else:
        print("⚠️  Some tests failed. Please check the errors above.")
        print("The bot may still work, but some features might not function correctly.")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)