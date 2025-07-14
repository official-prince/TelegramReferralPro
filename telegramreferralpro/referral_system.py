import hashlib
import secrets
import logging
from typing import Optional, Tuple, List
from .database import Database

logger = logging.getLogger(__name__)

class ReferralSystem:
    def __init__(self, database: Database):
        self.db = database
    
    def generate_referral_code(self, user_id: int) -> str:
        """Generate a unique referral code for a user"""
        # Create a unique code based on user ID and random salt
        salt = secrets.token_hex(8)
        raw_code = f"{user_id}_{salt}"
        hash_code = hashlib.sha256(raw_code.encode()).hexdigest()[:12]
        return f"ref_{hash_code}"
    
    def create_referral_link(self, bot_username: str, referral_code: str) -> str:
        """Create a referral link for sharing"""
        return f"https://t.me/{bot_username}?start={referral_code}"
    
    def process_referral(self, referrer_code: str, new_user_id: int) -> Tuple[bool, str]:
        """Process a new referral"""
        try:
            # Find the referrer
            referrer = self.db.get_user_by_referral_code(referrer_code)
            if not referrer:
                return False, "Invalid referral code"
            
            referrer_id = referrer['user_id']
            
            # Check if user is trying to refer themselves
            if referrer_id == new_user_id:
                return False, "You cannot refer yourself"
            
            # Check if this referral already exists
            existing_user = self.db.get_user(new_user_id)
            if existing_user and existing_user['referred_by']:
                return False, "You were already referred by someone else"
            
            # Add the referral
            success = self.db.add_referral(referrer_id, new_user_id)
            if success:
                # Update the new user's referrer
                self.db.add_user(
                    new_user_id, 
                    referred_by=referrer_id
                )
                return True, f"Successfully referred by {referrer['first_name'] or referrer['username'] or 'User'}"
            else:
                return False, "Failed to process referral"
                
        except Exception as e:
            logger.error(f"Error processing referral: {e}")
            return False, "An error occurred while processing the referral"
    
    def check_referral_target_reached(self, user_id: int, target: int) -> bool:
        """Check if user has reached their referral target"""
        active_referrals, _ = self.db.get_referral_stats(user_id)
        return active_referrals >= target
    
    def get_referral_progress(self, user_id: int, target: int) -> dict:
        """Get detailed referral progress for a user"""
        active_referrals, total_referrals = self.db.get_referral_stats(user_id)
        
        return {
            'active_referrals': active_referrals,
            'total_referrals': total_referrals,
            'target': target,
            'remaining': max(0, target - active_referrals),
            'target_reached': active_referrals >= target,
            'progress_percentage': min(100, (active_referrals / target) * 100) if target > 0 else 0
        }
    
    def handle_user_left_channel(self, user_id: int) -> List[int]:
        """Handle when a user leaves the channel - notify their referrer"""
        try:
            # Update user's channel membership
            self.db.update_channel_membership(user_id, False)
            self.db.log_channel_event(user_id, 'left')
            
            # Find who referred this user and deactivate the referral
            user = self.db.get_user(user_id)
            affected_referrers = []
            
            if user and user['referred_by']:
                referrer_id = user['referred_by']
                self.db.deactivate_referral(referrer_id, user_id)
                affected_referrers.append(referrer_id)
            
            # Also deactivate any referrals this user made
            # This is handled by the database query in get_referral_stats
            
            return affected_referrers
            
        except Exception as e:
            logger.error(f"Error handling user left channel: {e}")
            return []
    
    def handle_user_joined_channel(self, user_id: int) -> Optional[int]:
        """Handle when a user joins the channel"""
        try:
            # Update user's channel membership
            self.db.update_channel_membership(user_id, True)
            self.db.log_channel_event(user_id, 'joined')
            
            # If this user was referred, activate the referral
            user = self.db.get_user(user_id)
            if user and user['referred_by']:
                referrer_id = user['referred_by']
                # Referral is automatically active when user is channel member
                return referrer_id
            
            return None
            
        except Exception as e:
            logger.error(f"Error handling user joined channel: {e}")
            return None
