#!/usr/bin/env python3
"""
Check bot status and recent activity
"""
import os
from database import DatabaseManager

def main():
    print("🔍 **Bot Status Check**\n")
    
    # Check if database exists
    if os.path.exists('bot_database.db'):
        print("✅ Database: Found")
        
        # Check database contents
        db = DatabaseManager()
        stats = db.get_user_stats()
        
        print(f"👥 Total Users: {stats['total_users']}")
        print(f"💰 Paid Users: {stats['paid_users']}")
        print(f"📧 Invited Users: {stats['invited_users']}")
        print(f"💵 Total Revenue: ${stats['total_revenue']}")
        
        # Check pending payments
        pending = db.get_pending_payments()
        print(f"⏳ Pending Payments: {len(pending)}")
        
    else:
        print("❌ Database: Not found (will be created on first use)")
    
    # Check if bot process is running
    import subprocess
    try:
        result = subprocess.run(['ps', 'aux'], capture_output=True, text=True)
        if 'python3 run.py' in result.stdout:
            print("✅ Bot Process: Running")
        else:
            print("❌ Bot Process: Not found")
    except:
        print("❓ Bot Process: Cannot check")
    
    print(f"\n🤖 **Your Bot:** @JustfanRequest_bot")
    print(f"🔗 **Bot Link:** https://t.me/JustfanRequest_bot")
    print(f"👨‍💼 **Admin:** @Suzume1299 (ID: 7208394340)")

if __name__ == "__main__":
    main()