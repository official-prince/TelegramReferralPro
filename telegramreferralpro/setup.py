"""
Telegram Referral Bot Setup Instructions

This bot creates a referral system for Telegram channels to promote growth.

Features:
- Automatic channel join link generation
- Unique referral links for each user
- Progress tracking and rewards
- Real-time membership monitoring
- Admin statistics

Setup Steps:

1. Create a Telegram Bot:
   - Go to @BotFather on Telegram
   - Send /newbot and follow instructions
   - Save your bot token

2. Set up your channel:
   - Create a Telegram channel
   - Add your bot as an admin with these permissions:
     * Delete messages
     * Restrict members
     * Pin messages
     * Manage video chats
   - Get your channel ID (use @userinfobot or check logs when bot runs)

3. Configure environment variables:
   - BOT_TOKEN: Your bot token from BotFather
   - CHANNEL_ID: Your channel ID (with -100 prefix for supergroups)
   - CHANNEL_USERNAME: Your channel username (without @)
   - ADMIN_USER_IDS: Comma-separated list of admin user IDs
   
   Optional settings:
   - REFERRAL_TARGET: Number of referrals needed (default: 5)
   - REWARD_MESSAGE: Custom reward message
   - WEBHOOK_URL: For production webhook deployment
   - PORT: Server port for webhook mode (default: 8000)

4. Run the bot:
   python main.py

Bot Commands:
- /start - Get referral link and instructions
- /status - Check referral progress
- /claim - Claim reward when target is reached
- /help - Show help message
- /admin_stats - Admin-only statistics (must be in ADMIN_USER_IDS)

How it works:
1. Users start the bot and get instructions to join the channel
2. After joining, they receive a unique referral link
3. They share this link to get others to join
4. When they reach the target (default 5 referrals), they can claim rewards
5. The system tracks joins/leaves automatically
"""

if __name__ == "__main__":
    print(__doc__)