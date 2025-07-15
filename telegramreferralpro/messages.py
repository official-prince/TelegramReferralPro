"""Message templates for the bot"""

class Messages:
    WELCOME_NEW_USER = """
🎉 Welcome to the referral system!

To get started:
1. First, join our channel: {channel_link}
2. Once you join, I'll give you your unique referral link
3. Share your link with friends to earn rewards!

Click the link above to join the channel, then come back here.
"""
    
    WELCOME_EXISTING_MEMBER = """
🎉 Welcome back! I can see you're already a member of {channel_name}.


Here's your unique referral link:
{referral_link}

📋 **Your Mission:**
Share this link with friends and get {target} people to join the channel using your link to earn your reward!

🔗 **How it works:**
1. Copy and share your referral link with friends
2. When they click it and join the channel, you get credit
3. Reach {target} successful referrals to claim your reward

Use /status to check your progress anytime!
"""
    
    CHANNEL_JOINED_SUCCESS = """
✅ Great! You've successfully joined {channel_name}!


Here's your unique referral link:
{referral_link}

📋 **Your Mission:**
Copy and share this link with friends and get {target} people to join the channel using your link to earn your reward!

🔗 **How it works:**
1. Copy and share your referral link with friends
2. When they click it and join the channel, you get credit
3. Reach {target} successful referrals to claim your reward

Use /status to check your progress anytime!
"""
    
    REFERRAL_WELCOME = """
👋 Welcome! You were referred by a friend.

Please join our channel to continue: {channel_link}

After joining, you'll get your own referral link to start earning rewards too!
"""
    
    STATUS_MESSAGE = """
📊 **Your Referral Status**

👥 Active Referrals: {active_referrals}/{target}
📈 Total Referrals Made: {total_referrals}
🎯 Target: {target} referrals
🔥 Remaining: {remaining}
📊 Progress: {progress}%

{progress_bar}

{status_text}
"""
    
    PROGRESS_BAR_FULL = "🟩"
    PROGRESS_BAR_EMPTY = "⬜"
    
    REWARD_AVAILABLE = """
🎉 **CONGRATULATIONS!** 🎉

You've reached your referral target! Your reward is ready to claim.

Use /claim to get your reward!
"""
    
    REWARD_CLAIMED = """
🏆 **REWARD CLAIMED!** 🏆

{reward_message}

Thank you for helping grow our community! Keep sharing your referral link to help even more people discover our channel.

Your referral link is still active: {referral_link}
"""
    
    HELP_MESSAGE = """
🤖 **Referral Bot Commands**

/start - Get your referral link and instructions
/status - Check your referral progress
/claim - Claim your reward (when target is reached)
/help - Show this help message

📋 **How the referral system works:**
1. Get your unique referral link from /start
2. Copy the link and share it with friends
3. When friends join using your link, you get credit
4. Reach the target number of referrals to earn rewards
5. Use /claim to get your reward

💡 **Tips:**
- Share your link in groups, social media, or with friends
- Only active channel members count towards your target
- If someone leaves the channel, they won't count anymore
- You can check your progress anytime with /status
"""
    
    ERROR_NOT_CHANNEL_MEMBER = """
❌ You need to be a member of the channel first!

Join here: {channel_link}

After joining, come back and use /start again.
"""
    
    ERROR_REWARD_ALREADY_CLAIMED = """
✅ You've already claimed your reward!

Your referral link is still active if you want to keep helping grow the community: {referral_link}
"""
    
    ERROR_REWARD_NOT_AVAILABLE = """
❌ You haven't reached the referral target yet.

Current progress: {active_referrals}/{target}

Use /status to see your detailed progress.
"""
    
    ADMIN_STATS = """
📊 **Bot Statistics**

👥 Total Users: {total_users}
🔗 Channel Members: {channel_members}
📈 Total Referrals: {total_referrals}
⭐ Rewards Claimed: {rewards_claimed}
"""
    
    def get_progress_bar(self, progress_percentage: float, length: int = 10) -> str:
        """Generate a visual progress bar"""
        filled = int((progress_percentage / 100) * length)
        empty = length - filled
        return self.PROGRESS_BAR_FULL * filled + self.PROGRESS_BAR_EMPTY * empty
    
    def get_status_text(self, progress: dict) -> str:
        """Get status text based on progress"""
        if progress['target_reached']:
            return "🎉 Target reached! Use /claim to get your reward!"
        elif progress['active_referrals'] == 0:
            return "🚀 Start sharing your referral link to earn rewards!"
        else:
            return f"🔥 Great progress! Just {progress['remaining']} more referrals to go!"
