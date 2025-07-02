import sqlite3
import logging
from datetime import datetime
from typing import Optional, List, Tuple
from contextlib import contextmanager

logger = logging.getLogger(__name__)

class Database:
    def __init__(self, db_path: str):
        self.db_path = db_path
        self.init_database()
    
    def init_database(self):
        """Initialize database tables"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            
            # Users table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    referral_code TEXT UNIQUE,
                    referred_by INTEGER,
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_channel_member BOOLEAN DEFAULT FALSE,
                    reward_claimed BOOLEAN DEFAULT FALSE,
                    FOREIGN KEY (referred_by) REFERENCES users (user_id)
                )
            ''')
            
            # Referrals table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS referrals (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    referrer_id INTEGER,
                    referred_user_id INTEGER,
                    join_date TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    is_active BOOLEAN DEFAULT TRUE,
                    FOREIGN KEY (referrer_id) REFERENCES users (user_id),
                    FOREIGN KEY (referred_user_id) REFERENCES users (user_id),
                    UNIQUE(referrer_id, referred_user_id)
                )
            ''')
            
            # Channel events table
            cursor.execute('''
                CREATE TABLE IF NOT EXISTS channel_events (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    event_type TEXT,
                    timestamp TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            ''')
            
            conn.commit()
            logger.info("Database initialized successfully")
    
    @contextmanager
    def get_connection(self):
        """Context manager for database connections"""
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        try:
            yield conn
        except Exception as e:
            conn.rollback()
            logger.error(f"Database error: {e}")
            raise
        finally:
            conn.close()
    
    def add_user(self, user_id: int, username: str = None, first_name: str = None, 
                 last_name: str = None, referral_code: str = None, referred_by: int = None) -> bool:
        """Add a new user to the database"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR REPLACE INTO users 
                    (user_id, username, first_name, last_name, referral_code, referred_by)
                    VALUES (?, ?, ?, ?, ?, ?)
                ''', (user_id, username, first_name, last_name, referral_code, referred_by))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error adding user {user_id}: {e}")
            return False
    
    def get_user(self, user_id: int) -> Optional[sqlite3.Row]:
        """Get user by ID"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE user_id = ?', (user_id,))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting user {user_id}: {e}")
            return None
    
    def get_user_by_referral_code(self, referral_code: str) -> Optional[sqlite3.Row]:
        """Get user by referral code"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT * FROM users WHERE referral_code = ?', (referral_code,))
                return cursor.fetchone()
        except Exception as e:
            logger.error(f"Error getting user by referral code {referral_code}: {e}")
            return None
    
    def update_channel_membership(self, user_id: int, is_member: bool) -> bool:
        """Update user's channel membership status"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET is_channel_member = ? WHERE user_id = ?
                ''', (is_member, user_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error updating channel membership for user {user_id}: {e}")
            return False
    
    def add_referral(self, referrer_id: int, referred_user_id: int) -> bool:
        """Add a referral relationship"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT OR IGNORE INTO referrals (referrer_id, referred_user_id)
                    VALUES (?, ?)
                ''', (referrer_id, referred_user_id))
                conn.commit()
                return cursor.rowcount > 0
        except Exception as e:
            logger.error(f"Error adding referral: {e}")
            return False
    
    def get_referral_stats(self, user_id: int) -> Tuple[int, int]:
        """Get referral statistics for a user (active referrals, total referrals)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                
                # Active referrals (users still in channel)
                cursor.execute('''
                    SELECT COUNT(*) FROM referrals r
                    JOIN users u ON r.referred_user_id = u.user_id
                    WHERE r.referrer_id = ? AND r.is_active = TRUE AND u.is_channel_member = TRUE
                ''', (user_id,))
                active_count = cursor.fetchone()[0]
                
                # Total referrals ever made
                cursor.execute('''
                    SELECT COUNT(*) FROM referrals WHERE referrer_id = ?
                ''', (user_id,))
                total_count = cursor.fetchone()[0]
                
                return active_count, total_count
        except Exception as e:
            logger.error(f"Error getting referral stats for user {user_id}: {e}")
            return 0, 0
    
    def deactivate_referral(self, referrer_id: int, referred_user_id: int) -> bool:
        """Deactivate a referral when user leaves channel"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE referrals SET is_active = FALSE 
                    WHERE referrer_id = ? AND referred_user_id = ?
                ''', (referrer_id, referred_user_id))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error deactivating referral: {e}")
            return False
    
    def mark_reward_claimed(self, user_id: int) -> bool:
        """Mark reward as claimed for a user"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    UPDATE users SET reward_claimed = TRUE WHERE user_id = ?
                ''', (user_id,))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error marking reward claimed for user {user_id}: {e}")
            return False
    
    def log_channel_event(self, user_id: int, event_type: str) -> bool:
        """Log channel events (join/leave)"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('''
                    INSERT INTO channel_events (user_id, event_type)
                    VALUES (?, ?)
                ''', (user_id, event_type))
                conn.commit()
                return True
        except Exception as e:
            logger.error(f"Error logging channel event: {e}")
            return False
    
    def get_all_users_count(self) -> int:
        """Get total number of users"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM users')
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting user count: {e}")
            return 0
    
    def get_channel_members_count(self) -> int:
        """Get number of active channel members"""
        try:
            with self.get_connection() as conn:
                cursor = conn.cursor()
                cursor.execute('SELECT COUNT(*) FROM users WHERE is_channel_member = TRUE')
                return cursor.fetchone()[0]
        except Exception as e:
            logger.error(f"Error getting channel members count: {e}")
            return 0
