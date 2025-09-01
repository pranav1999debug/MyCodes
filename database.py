import sqlite3
import logging
from datetime import datetime
from typing import Optional, Dict, Any

class DatabaseManager:
    def __init__(self, db_file: str = "bot_database.db"):
        self.db_file = db_file
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        payment_status TEXT DEFAULT 'pending',
                        payment_id TEXT,
                        payment_verified_at TIMESTAMP
                    )
                ''')
                
                # Payments table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS payments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        payment_id TEXT UNIQUE,
                        amount REAL,
                        currency TEXT,
                        status TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        verified_at TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                conn.commit()
                logging.info("Database initialized successfully")
                
        except Exception as e:
            logging.error(f"Error initializing database: {e}")
            raise
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> bool:
        """Add a new user to the database"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error adding user {user_id}: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict[str, Any]]:
        """Get user information from database"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logging.error(f"Error getting user {user_id}: {e}")
            return None
    
    def update_user_payment_status(self, user_id: int, status: str, payment_id: str = None) -> bool:
        """Update user's payment status"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                if status == 'verified':
                    cursor.execute('''
                        UPDATE users 
                        SET payment_status = ?, payment_id = ?, payment_verified_at = CURRENT_TIMESTAMP
                        WHERE user_id = ?
                    ''', (status, payment_id, user_id))
                else:
                    cursor.execute('''
                        UPDATE users 
                        SET payment_status = ?, payment_id = ?
                        WHERE user_id = ?
                    ''', (status, payment_id, user_id))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error updating payment status for user {user_id}: {e}")
            return False
    
    def add_payment(self, user_id: int, payment_id: str, amount: float, currency: str, status: str) -> bool:
        """Add a payment record"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO payments (user_id, payment_id, amount, currency, status)
                    VALUES (?, ?, ?, ?, ?)
                ''', (user_id, payment_id, amount, currency, status))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error adding payment {payment_id}: {e}")
            return False
    
    def update_payment_status(self, payment_id: str, status: str) -> bool:
        """Update payment status"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                cursor = conn.cursor()
                if status == 'verified':
                    cursor.execute('''
                        UPDATE payments 
                        SET status = ?, verified_at = CURRENT_TIMESTAMP
                        WHERE payment_id = ?
                    ''', (status, payment_id))
                else:
                    cursor.execute('''
                        UPDATE payments 
                        SET status = ?
                        WHERE payment_id = ?
                    ''', (status, payment_id))
                conn.commit()
                return True
        except Exception as e:
            logging.error(f"Error updating payment status {payment_id}: {e}")
            return False
    
    def get_payment(self, payment_id: str) -> Optional[Dict[str, Any]]:
        """Get payment information"""
        try:
            with sqlite3.connect(self.db_file) as conn:
                conn.row_factory = sqlite3.Row
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM payments WHERE payment_id = ?', (payment_id,))
                row = cursor.fetchone()
                return dict(row) if row else None
        except Exception as e:
            logging.error(f"Error getting payment {payment_id}: {e}")
            return None