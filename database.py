import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Dict
from config import DATABASE_PATH

class DatabaseManager:
    def __init__(self):
        self.db_path = DATABASE_PATH
        self.init_database()
    
    def init_database(self):
        """Initialize the database with required tables"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Users table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS users (
                        user_id INTEGER PRIMARY KEY,
                        username TEXT,
                        first_name TEXT,
                        last_name TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        has_paid BOOLEAN DEFAULT FALSE,
                        invite_sent BOOLEAN DEFAULT FALSE
                    )
                ''')
                
                # Payments table
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS payments (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        payment_id TEXT UNIQUE,
                        payer_id TEXT,
                        amount REAL,
                        currency TEXT,
                        status TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        completed_at TIMESTAMP,
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                # Payment sessions table (for tracking pending payments)
                cursor.execute('''
                    CREATE TABLE IF NOT EXISTS payment_sessions (
                        id INTEGER PRIMARY KEY AUTOINCREMENT,
                        user_id INTEGER,
                        session_id TEXT UNIQUE,
                        payment_url TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                        expires_at TIMESTAMP,
                        status TEXT DEFAULT 'pending',
                        FOREIGN KEY (user_id) REFERENCES users (user_id)
                    )
                ''')
                
                conn.commit()
                logging.info("Database initialized successfully")
        except sqlite3.Error as e:
            logging.error(f"Database initialization error: {e}")
            raise
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, last_name: str = None) -> bool:
        """Add a new user or update existing user info"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users (user_id, username, first_name, last_name)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logging.error(f"Error adding user: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[Dict]:
        """Get user information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
        except sqlite3.Error as e:
            logging.error(f"Error getting user: {e}")
            return None
    
    def user_has_paid(self, user_id: int) -> bool:
        """Check if user has completed payment"""
        user = self.get_user(user_id)
        return user and user.get('has_paid', False)
    
    def user_has_invite(self, user_id: int) -> bool:
        """Check if user has been sent the invite link"""
        user = self.get_user(user_id)
        return user and user.get('invite_sent', False)
    
    def mark_user_paid(self, user_id: int) -> bool:
        """Mark user as having completed payment"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET has_paid = TRUE WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logging.error(f"Error marking user as paid: {e}")
            return False
    
    def mark_invite_sent(self, user_id: int) -> bool:
        """Mark that invite link has been sent to user"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET invite_sent = TRUE WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logging.error(f"Error marking invite as sent: {e}")
            return False
    
    def add_payment_session(self, user_id: int, session_id: str, payment_url: str, expires_at: datetime) -> bool:
        """Add a payment session"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO payment_sessions (user_id, session_id, payment_url, expires_at)
                    VALUES (?, ?, ?, ?)
                ''', (user_id, session_id, payment_url, expires_at))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logging.error(f"Error adding payment session: {e}")
            return False
    
    def get_payment_session(self, session_id: str) -> Optional[Dict]:
        """Get payment session information"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM payment_sessions WHERE session_id = ?', (session_id,))
                row = cursor.fetchone()
                if row:
                    columns = [description[0] for description in cursor.description]
                    return dict(zip(columns, row))
                return None
        except sqlite3.Error as e:
            logging.error(f"Error getting payment session: {e}")
            return None
    
    def complete_payment_session(self, session_id: str) -> bool:
        """Mark payment session as completed"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE payment_sessions SET status = 'completed' WHERE session_id = ?
                ''', (session_id,))
                conn.commit()
                return cursor.rowcount > 0
        except sqlite3.Error as e:
            logging.error(f"Error completing payment session: {e}")
            return False
    
    def add_payment(self, user_id: int, payment_id: str, payer_id: str, amount: float, currency: str, status: str) -> bool:
        """Add a payment record"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO payments (user_id, payment_id, payer_id, amount, currency, status, completed_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?)
                ''', (user_id, payment_id, payer_id, amount, currency, status, datetime.now()))
                conn.commit()
                return True
        except sqlite3.Error as e:
            logging.error(f"Error adding payment: {e}")
            return False
    
    def get_user_stats(self) -> Dict:
        """Get user statistics"""
        try:
            with sqlite3.connect(self.db_path) as conn:
                cursor = conn.cursor()
                
                # Total users
                cursor.execute('SELECT COUNT(*) FROM users')
                total_users = cursor.fetchone()[0]
                
                # Paid users
                cursor.execute('SELECT COUNT(*) FROM users WHERE has_paid = TRUE')
                paid_users = cursor.fetchone()[0]
                
                # Users with invites sent
                cursor.execute('SELECT COUNT(*) FROM users WHERE invite_sent = TRUE')
                invited_users = cursor.fetchone()[0]
                
                # Total revenue
                cursor.execute('SELECT SUM(amount) FROM payments WHERE status = "approved"')
                total_revenue = cursor.fetchone()[0] or 0
                
                return {
                    'total_users': total_users,
                    'paid_users': paid_users,
                    'invited_users': invited_users,
                    'total_revenue': total_revenue
                }
        except sqlite3.Error as e:
            logging.error(f"Error getting user stats: {e}")
            return {
                'total_users': 0,
                'paid_users': 0,
                'invited_users': 0,
                'total_revenue': 0
            }