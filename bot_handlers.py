import logging
from telegram import Update
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ChatMemberHandler
from telegram.constants import ParseMode
from database import Database
from referral_system import ReferralSystem
from messages import Messages
from utils import TelegramUtils
from config import BotConfig

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self, config: BotConfig, database: Database, referral_system: ReferralSystem, telegram_utils: TelegramUtils):
        self.config = config
        self.db = database
        self.referral_system = referral_system
        self.telegram_utils = telegram_utils
        self.messages = Messages()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command"""
        user = update.effective_user
        user_id = user.id
        
        logger.info(f"User {user_id} ({user.username}) started the bot")
        
        # Check if this is a referral start
        referral_code = None
        if context.args:
            referral_code = context.args[0]
        
        # Get or create user
        existing_user = self.db.get_user(user_id)
        if not existing_user:
            # Create new user with referral code
            user_referral_code = self.referral_system.generate_referral_code(user_id)
            self.db.add_user(
                user_id=user_id,
                username=user.username,
                first_name=user.first_name,
                last_name=user.last_name,
                referral_code=user_referral_code
            )
            existing_user = self.db.get_user(user_id)
        
        # Check channel membership
        is_member = await self.telegram_utils.check_channel_membership(user_id)
        self.db.update_channel_membership(user_id, is_member)
        
        # Process referral if provided
        if referral_code and not existing_user['referred_by']:
            success, message = self.referral_system.process_referral(referral_code, user_id)
            if success:
                await update.message.reply_text(f"✅ {message}")
            else:
                logger.warning(f"Referral failed for user {user_id}: {message}")
        
        # Send appropriate welcome message
        if is_member:
            await self._send_member_welcome(update, existing_user)
        else:
            if referral_code:
                await self._send_referral_welcome(update)
            else:
                await self._send_new_user_welcome(update)
    
    async def _send_new_user_welcome(self, update: Update) -> None:
        """Send welcome message to new users"""
        channel_link = self.telegram_utils.get_channel_link()
        message = self.messages.WELCOME_NEW_USER.format(
            channel_link=channel_link
        )
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def _send_referral_welcome(self, update: Update) -> None:
        """Send welcome message to referred users"""
        channel_link = self.telegram_utils.get_channel_link()
        message = self.messages.REFERRAL_WELCOME.format(
            channel_link=channel_link
        )
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def _send_member_welcome(self, update: Update, user_data) -> None:
        """Send welcome message to existing channel members"""
        bot_info = await update.get_bot()
        referral_link = self.referral_system.create_referral_link(
            bot_info.username, user_data['referral_code']
        )
        
        chat_info = await self.telegram_utils.get_chat_info()
        channel_name = chat_info['title'] if chat_info else "our channel"
        
        message = self.messages.WELCOME_EXISTING_MEMBER.format(
            channel_name=channel_name,
            referral_link=referral_link,
            target=self.config.referral_target
        )
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command"""
        user_id = update.effective_user.id
        
        # Check if user exists
        user = self.db.get_user(user_id)
        if not user:
            await update.message.reply_text("❌ Please use /start first to register.")
            return
        
        # Check channel membership
        is_member = await self.telegram_utils.check_channel_membership(user_id)
        if not is_member:
            channel_link = self.telegram_utils.get_channel_link()
            message = self.messages.ERROR_NOT_CHANNEL_MEMBER.format(
                channel_link=channel_link
            )
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            return
        
        # Get referral progress
        progress = self.referral_system.get_referral_progress(user_id, self.config.referral_target)
        progress_bar = self.messages.get_progress_bar(progress['progress_percentage'])
        status_text = self.messages.get_status_text(progress)
        
        message = self.messages.STATUS_MESSAGE.format(
            active_referrals=progress['active_referrals'],
            target=progress['target'],
            total_referrals=progress['total_referrals'],
            remaining=progress['remaining'],
            progress=int(progress['progress_percentage']),
            progress_bar=progress_bar,
            status_text=status_text
        )
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def claim_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /claim command"""
        user_id = update.effective_user.id
        
        # Check if user exists
        user = self.db.get_user(user_id)
        if not user:
            await update.message.reply_text("❌ Please use /start first to register.")
            return
        
        # Check if reward already claimed
        if user['reward_claimed']:
            bot_info = await update.get_bot()
            referral_link = self.referral_system.create_referral_link(
                bot_info.username, user['referral_code']
            )
            message = self.messages.ERROR_REWARD_ALREADY_CLAIMED.format(
                referral_link=referral_link
            )
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            return
        
        # Check if target reached
        if not self.referral_system.check_referral_target_reached(user_id, self.config.referral_target):
            progress = self.referral_system.get_referral_progress(user_id, self.config.referral_target)
            message = self.messages.ERROR_REWARD_NOT_AVAILABLE.format(
                active_referrals=progress['active_referrals'],
                target=progress['target']
            )
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            return
        
        # Claim reward
        self.db.mark_reward_claimed(user_id)
        
        bot_info = await update.get_bot()
        referral_link = self.referral_system.create_referral_link(
            bot_info.username, user['referral_code']
        )
        
        message = self.messages.REWARD_CLAIMED.format(
            reward_message=self.config.reward_message,
            referral_link=referral_link
        )
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        logger.info(f"User {user_id} claimed their reward")
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command"""
        await update.message.reply_text(self.messages.HELP_MESSAGE, parse_mode=ParseMode.MARKDOWN)
    
    async def admin_stats_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /admin_stats command"""
        user_id = update.effective_user.id
        
        if not self.telegram_utils.is_admin(user_id, self.config.admin_user_ids):
            await update.message.reply_text("❌ You don't have permission to use this command.")
            return
        
        # Get statistics
        total_users = self.db.get_all_users_count()
        channel_members = self.db.get_channel_members_count()
        
        # Get total referrals and rewards claimed
        with self.db.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute('SELECT COUNT(*) FROM referrals WHERE is_active = TRUE')
            total_referrals = cursor.fetchone()[0]
            
            cursor.execute('SELECT COUNT(*) FROM users WHERE reward_claimed = TRUE')
            rewards_claimed = cursor.fetchone()[0]
        
        message = self.messages.ADMIN_STATS.format(
            total_users=total_users,
            channel_members=channel_members,
            total_referrals=total_referrals,
            rewards_claimed=rewards_claimed
        )
        
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def chat_member_updated(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle chat member updates (join/leave events)"""
        result = update.chat_member
        
        # Only process events for our target channel
        if str(result.chat.id) != self.config.channel_id:
            return
        
        user_id = result.new_chat_member.user.id
        old_status = result.old_chat_member.status
        new_status = result.new_chat_member.status
        
        # User joined the channel
        if old_status in ['left', 'kicked'] and new_status in ['member', 'administrator', 'creator']:
            logger.info(f"User {user_id} joined the channel")
            
            # Update database and check for referral
            referrer_id = self.referral_system.handle_user_joined_channel(user_id)
            
            # Send welcome message if user exists in our system
            user = self.db.get_user(user_id)
            if user:
                try:
                    bot_info = await context.bot.get_me()
                    referral_link = self.referral_system.create_referral_link(
                        bot_info.username, user['referral_code']
                    )
                    
                    chat_info = await self.telegram_utils.get_chat_info()
                    channel_name = chat_info['title'] if chat_info else "our channel"
                    
                    message = self.messages.CHANNEL_JOINED_SUCCESS.format(
                        channel_name=channel_name,
                        referral_link=referral_link,
                        target=self.config.referral_target
                    )
                    
                    await self.telegram_utils.send_message_safe(user_id, message)
                    
                    # Notify referrer if applicable
                    if referrer_id:
                        referrer = self.db.get_user(referrer_id)
                        if referrer:
                            progress = self.referral_system.get_referral_progress(referrer_id, self.config.referral_target)
                            
                            if progress['target_reached'] and not referrer['reward_claimed']:
                                notify_message = self.messages.REWARD_AVAILABLE
                                await self.telegram_utils.send_message_safe(referrer_id, notify_message)
                            else:
                                notify_message = f"🎉 Great news! Someone joined using your referral link!\n\nYour progress: {progress['active_referrals']}/{progress['target']}"
                                await self.telegram_utils.send_message_safe(referrer_id, notify_message)
                
                except Exception as e:
                    logger.error(f"Error sending welcome message to user {user_id}: {e}")
        
        # User left the channel
        elif old_status in ['member', 'administrator', 'creator'] and new_status in ['left', 'kicked']:
            logger.info(f"User {user_id} left the channel")
            
            # Update database and notify affected referrers
            affected_referrers = self.referral_system.handle_user_left_channel(user_id)
            
            # Notify referrers about the change
            for referrer_id in affected_referrers:
                try:
                    progress = self.referral_system.get_referral_progress(referrer_id, self.config.referral_target)
                    notify_message = f"📉 One of your referrals left the channel.\n\nYour current progress: {progress['active_referrals']}/{progress['target']}"
                    await self.telegram_utils.send_message_safe(referrer_id, notify_message)
                except Exception as e:
                    logger.error(f"Error notifying referrer {referrer_id}: {e}")
    
    def get_handlers(self) -> list:
        """Get all bot handlers"""
        return [
            CommandHandler("start", self.start_command),
            CommandHandler("status", self.status_command),
            CommandHandler("claim", self.claim_command),
            CommandHandler("help", self.help_command),
            CommandHandler("admin_stats", self.admin_stats_command),
            ChatMemberHandler(self.chat_member_updated, ChatMemberHandler.CHAT_MEMBER)
        ]
