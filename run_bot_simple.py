#!/usr/bin/env python3
"""
Simplified bot runner to test core functionality
"""

import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.error import TelegramError

from telegramreferralpro.config import load_config
from telegramreferralpro.database import Database
from telegramreferralpro.referral_system import ReferralSystem
from telegramreferralpro.utils import TelegramUtils, setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

class SimpleBotHandlers:
    """Simplified bot handlers without problematic inline buttons"""
    
    def __init__(self, config, database, referral_system, telegram_utils):
        self.config = config
        self.db = database
        self.referral_system = referral_system
        self.telegram_utils = telegram_utils
        self.channel_username = None  # Will be set dynamically
    
    async def get_channel_username(self):
        """Get the correct channel username dynamically"""
        if self.channel_username is None:
            try:
                chat_info = await self.telegram_utils.get_chat_info()
                if chat_info and chat_info.get('username'):
                    self.channel_username = chat_info['username']
                else:
                    # Fallback to config username
                    self.channel_username = self.config.channel_username
            except Exception as e:
                logger.error(f"Error getting channel username: {e}")
                self.channel_username = self.config.channel_username
        return self.channel_username
    
    def get_correct_channel_link(self):
        """Get the correct channel link"""
        if self.channel_username and not self.channel_username.startswith('-100'):
            return f"https://t.me/{self.channel_username}"
        else:
            # Fallback to using channel ID
            return f"https://t.me/c/{self.config.channel_id[4:]}"
    
    async def start_command(self, update, context):
        """Handle /start command"""
        if not update.effective_user or not update.message:
            return
            
        user = update.effective_user
        user_id = user.id
        
        logger.info(f"User {user_id} ({user.username}) started the bot")
        
        # Get or create user
        existing_user = self.db.get_user(user_id)
        if not existing_user:
            # Create new user with referral code
            user_referral_code = self.referral_system.generate_referral_code(user_id)
            self.db.add_user(
                user_id=user_id,
                username=user.username or "",
                first_name=user.first_name or "",
                last_name=user.last_name or "",
                referral_code=user_referral_code
            )
            existing_user = self.db.get_user(user_id)
        
        # Check channel membership
        is_member = await self.telegram_utils.check_channel_membership(user_id)
        self.db.update_channel_membership(user_id, is_member)
        
        # Get correct channel username and link
        await self.get_channel_username()
        channel_link = self.get_correct_channel_link()
        
        # Send welcome message
        if is_member:
            referral_link = f"{channel_link}?start={existing_user['referral_code']}"
            message = f"""
🎉 **Welcome to the Referral Bot!**

You're already a member of our channel: {channel_link}

🔗 **Your Unique Referral Link:**
`{referral_link}`

📊 **Commands:**
• /status - Check your referral progress
• /claim - Claim your reward when ready
• /help - Show help message

Share your referral link with friends to earn rewards!
"""
        else:
            message = f"""
👋 **Welcome to the Referral Bot!**

To get started, please join our channel first:
{channel_link}

After joining, use /start again to get your referral link!
"""
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def status_command(self, update, context):
        """Handle /status command"""
        if not update.effective_user:
            return
            
        user_id = update.effective_user.id
        
        # Check if user exists
        user = self.db.get_user(user_id)
        if not user:
            await update.message.reply_text("❌ Please use /start first to register.")
            return
        
        # Check channel membership
        is_member = await self.telegram_utils.check_channel_membership(user_id)
        if not is_member:
            await self.get_channel_username()
            channel_link = self.get_correct_channel_link()
            await update.message.reply_text(f"❌ Please join our channel first: {channel_link}")
            return
        
        # Get referral progress
        progress = self.referral_system.get_referral_progress(user_id, self.config.referral_target)
        
        # Get user's referral link
        await self.get_channel_username()
        channel_link = self.get_correct_channel_link()
        referral_link = f"{channel_link}?start={user['referral_code']}"
        
        message = f"""
📊 **Your Referral Status**

✅ **Active Referrals:** {progress['active_referrals']}/{progress['target']}
📈 **Total Referrals:** {progress['total_referrals']}
🎯 **Target:** {progress['target']} referrals
📊 **Progress:** {int(progress['progress_percentage'])}%

🔗 **Your Referral Link:**
`{referral_link}`

"""
        
        if progress['target_reached']:
            message += "🎉 **Congratulations! You can claim your reward with /claim**"
        else:
            message += f"📝 **You need {progress['remaining']} more referrals to claim your reward**"
        
        await update.message.reply_text(message, parse_mode='Markdown')
    
    async def claim_command(self, update, context):
        """Handle /claim command"""
        if not update.effective_user:
            return
            
        user_id = update.effective_user.id
        
        # Check if user exists
        user = self.db.get_user(user_id)
        if not user:
            await update.message.reply_text("❌ Please use /start first to register.")
            return
        
        # Check if reward already claimed
        if user['reward_claimed']:
            await update.message.reply_text("🎉 You've already claimed your reward!")
            return
        
        # Check if target reached
        if not self.referral_system.check_referral_target_reached(user_id, self.config.referral_target):
            progress = self.referral_system.get_referral_progress(user_id, self.config.referral_target)
            await update.message.reply_text(f"❌ You need {progress['target'] - progress['active_referrals']} more referrals to claim your reward.")
            return
        
        # Claim reward
        self.db.mark_reward_claimed(user_id)
        await update.message.reply_text(f"🎉 {self.config.reward_message}")
        logger.info(f"User {user_id} claimed their reward")
    
    async def help_command(self, update, context):
        """Handle /help command"""
        message = """
🤖 **Referral Bot Help**

**Commands:**
• /start - Get your referral link
• /status - Check your referral progress  
• /claim - Claim your reward when ready
• /help - Show this help message

**How it works:**
1. Use /start to get your unique referral link
2. Share the link with friends
3. When they join using your link, you get credit
4. Reach your target to claim your reward!

**Need help?** Contact the bot administrator.
"""
        await update.message.reply_text(message, parse_mode='Markdown')

def main():
    """Main function to run the simplified bot"""
    try:
        # Load configuration
        config = load_config()
        logger.info("Configuration loaded successfully")
        
        # Initialize database
        database = Database(config.database_path)
        logger.info("Database initialized")
        
        # Initialize referral system
        referral_system = ReferralSystem(database)
        logger.info("Referral system initialized")
        
        # Create bot application
        application = Application.builder().token(config.bot_token).build()
        
        # Initialize telegram utils
        telegram_utils = TelegramUtils(application.bot, config.channel_id, config.channel_username)
        
        # Initialize simplified bot handlers
        bot_handlers = SimpleBotHandlers(config, database, referral_system, telegram_utils)
        
        # Add handlers to application
        application.add_handler(CommandHandler("start", bot_handlers.start_command))
        application.add_handler(CommandHandler("status", bot_handlers.status_command))
        application.add_handler(CommandHandler("claim", bot_handlers.claim_command))
        application.add_handler(CommandHandler("help", bot_handlers.help_command))
        
        logger.info("Bot handlers registered")
        
        # Start the bot in polling mode
        logger.info("Starting bot in polling mode")
        application.run_polling(allowed_updates=["message", "chat_member"])
    
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    main()
