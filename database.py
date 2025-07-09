import sqlite3
import hashlib
import random
import string
from config import DATABASE_FILE, REFERRAL_REWARD

class Database:
    def __init__(self):
        self.db_file = DATABASE_FILE
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Users table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                username TEXT,
                first_name TEXT,
                balance REAL DEFAULT 0.0,
                referral_code TEXT UNIQUE,
                referred_by INTEGER,
                total_referrals INTEGER DEFAULT 0,
                is_member BOOLEAN DEFAULT FALSE,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        ''')
        
        # Referrals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS referrals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                referrer_id INTEGER,
                referred_id INTEGER,
                reward_amount REAL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (referrer_id) REFERENCES users (user_id),
                FOREIGN KEY (referred_id) REFERENCES users (user_id)
            )
        ''')
        
        # Withdrawals table
        cursor.execute('''
            CREATE TABLE IF NOT EXISTS withdrawals (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                user_id INTEGER,
                amount REAL,
                status TEXT DEFAULT 'pending',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (user_id) REFERENCES users (user_id)
            )
        ''')
        
        conn.commit()
        conn.close()
    
    def generate_referral_code(self, user_id):
        """Generate a unique referral code for user"""
        base_string = f"{user_id}{random.randint(1000, 9999)}"
        return hashlib.md5(base_string.encode()).hexdigest()[:8].upper()
    
    def add_user(self, user_id, username, first_name, referred_by=None):
        """Add a new user to the database"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Check if user already exists
        cursor.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        if cursor.fetchone():
            conn.close()
            return False
        
        # Generate referral code
        referral_code = self.generate_referral_code(user_id)
        
        # Insert new user
        cursor.execute('''
            INSERT INTO users (user_id, username, first_name, referral_code, referred_by)
            VALUES (?, ?, ?, ?, ?)
        ''', (user_id, username, first_name, referral_code, referred_by))
        
        # If user was referred, add referral record and reward
        if referred_by:
            # Add referral record
            cursor.execute('''
                INSERT INTO referrals (referrer_id, referred_id, reward_amount)
                VALUES (?, ?, ?)
            ''', (referred_by, user_id, REFERRAL_REWARD))
            
            # Update referrer's balance and referral count
            cursor.execute('''
                UPDATE users 
                SET balance = balance + ?, total_referrals = total_referrals + 1
                WHERE user_id = ?
            ''', (REFERRAL_REWARD, referred_by))
        
        conn.commit()
        conn.close()
        return True
    
    def get_user(self, user_id):
        """Get user information"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM users WHERE user_id = ?", (user_id,))
        user = cursor.fetchone()
        conn.close()
        return user
    
    def get_user_by_referral_code(self, referral_code):
        """Get user by referral code"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT user_id FROM users WHERE referral_code = ?", (referral_code,))
        user = cursor.fetchone()
        conn.close()
        return user[0] if user else None
    
    def update_membership_status(self, user_id, is_member):
        """Update user's channel membership status"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("UPDATE users SET is_member = ? WHERE user_id = ?", (is_member, user_id))
        conn.commit()
        conn.close()
    
    def get_user_balance(self, user_id):
        """Get user's current balance"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute("SELECT balance FROM users WHERE user_id = ?", (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else 0.0
    
    def get_user_referrals(self, user_id):
        """Get user's referral information"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        cursor.execute('''
            SELECT total_referrals, referral_code 
            FROM users WHERE user_id = ?
        ''', (user_id,))
        result = cursor.fetchone()
        conn.close()
        return result if result else (0, "")
    
    def create_withdrawal_request(self, user_id, amount):
        """Create a withdrawal request"""
        conn = sqlite3.connect(self.db_file)
        cursor = conn.cursor()
        
        # Check if user has sufficient balance
        current_balance = self.get_user_balance(user_id)
        if current_balance < amount:
            conn.close()
            return False
        
        # Create withdrawal request
        cursor.execute('''
            INSERT INTO withdrawals (user_id, amount)
            VALUES (?, ?)
        ''', (user_id, amount))
        
        # Deduct amount from user balance
        cursor.execute('''
            UPDATE users SET balance = balance - ? WHERE user_id = ?
        ''', (amount, user_id))
        
        conn.commit()
        conn.close()
        return True