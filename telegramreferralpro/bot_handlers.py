import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import ContextTypes, CommandHandler, MessageHandler, filters, ChatMemberHandler, CallbackQueryHandler
from telegram.constants import ParseMode
from .database import Database
from .referral_system import ReferralSystem
from .messages import Messages
from .utils import TelegramUtils, setup_logging, escape_markdown
from .config import BotConfig
from .languages import LanguageManager, MultilingualMessages, SupportedLanguage

logger = logging.getLogger(__name__)

class BotHandlers:
    def __init__(self, config: BotConfig, database: Database, referral_system: ReferralSystem, telegram_utils: TelegramUtils):
        self.config = config
        self.db = database
        self.referral_system = referral_system
        self.telegram_utils = telegram_utils
        self.messages = Messages()
        self.language_manager = LanguageManager(database)
        self.multilingual_messages = MultilingualMessages()
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /start command with multilingual support"""
        if not update.effective_user or not update.message:
            return
            
        user = update.effective_user
        user_id = user.id
        
        logger.info(f"User {user_id} ({user.username}) started the bot")
        
        # Detect and set user language
        message_text = update.message.text if update.message.text else ""
        user_lang = self.language_manager.detect_and_set_language(user_id, user, message_text)
        
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
                username=user.username or "",
                first_name=user.first_name or "",
                last_name=user.last_name or "",
                referral_code=user_referral_code
            )
            existing_user = self.db.get_user(user_id)
        
        # Check channel membership
        is_member = await self.telegram_utils.check_channel_membership(user_id)
        self.db.update_channel_membership(user_id, is_member)
        
        # Process referral if provided
        if referral_code and existing_user and not existing_user['referred_by']:
            success, message = self.referral_system.process_referral(referral_code, user_id)
            if success:
                await update.message.reply_text(f"✅ {message}")
            else:
                logger.warning(f"Referral failed for user {user_id}: {message}")
        
        # Send appropriate welcome message
        if is_member:
            await self._send_member_welcome_multilingual(update, existing_user, user_lang)
        else:
            if referral_code:
                await self._send_referral_welcome_multilingual(update, user_lang)
            else:
                await self._send_new_user_welcome_multilingual(update, user_lang)
    
    async def _send_new_user_welcome_multilingual(self, update: Update, user_lang: str) -> None:
        """Send multilingual welcome message to new users"""
        if not update.message:
            return
        channel_link = escape_markdown(self.telegram_utils.get_channel_link())
        message = self.multilingual_messages.get_message(
            user_lang, "welcome_new_user", channel_link=channel_link
        )
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def _send_referral_welcome_multilingual(self, update: Update, user_lang: str) -> None:
        """Send multilingual welcome message to referred users"""
        if not update.message:
            return
        channel_link = escape_markdown(self.telegram_utils.get_channel_link())
        message = self.multilingual_messages.get_message(
            user_lang, "referral_welcome", channel_link=channel_link
        )
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def _send_member_welcome_multilingual(self, update: Update, user_data, user_lang: str) -> None:
        """Send multilingual welcome message to existing channel members"""
        if not update.message or not user_data:
            return
        chat_info = await self.telegram_utils.get_chat_info()
        channel_name = escape_markdown(chat_info['title']) if chat_info else "our channel"
        
        # Get or create unique invite link for this user
        stored_invite_link = self.db.get_invite_link(user_data['user_id'])
        if stored_invite_link:
            invite_link = escape_markdown(stored_invite_link)
        else:
            # Create new unique invite link
            referral_code = user_data['referral_code']
            invite_link_name = f"Referral-{referral_code}"
            raw_invite_link = await self.telegram_utils.create_unique_invite_link(name=invite_link_name)
            invite_link = escape_markdown(raw_invite_link)
            
            # Store the invite link in database
            self.db.store_invite_link(user_data['user_id'], referral_code, raw_invite_link, invite_link_name)
        
        message = self.multilingual_messages.get_message(
            user_lang, "welcome_existing_member",
            channel_name=channel_name,
            referral_link=invite_link,
            target=self.config.referral_target
        )
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)

    # Keep the old methods for backward compatibility
    async def _send_new_user_welcome(self, update: Update) -> None:
        """Send welcome message to new users"""
        if not update.message:
            return
        channel_link = self.telegram_utils.get_channel_link()
        message = self.messages.WELCOME_NEW_USER.format(
            channel_link=channel_link
        )
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def _send_referral_welcome(self, update: Update) -> None:
        """Send welcome message to referred users"""
        if not update.message:
            return
        channel_link = self.telegram_utils.get_channel_link()
        message = self.messages.REFERRAL_WELCOME.format(
            channel_link=channel_link
        )
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def _send_member_welcome(self, update: Update, user_data) -> None:
        """Send welcome message to existing channel members"""
        if not update.message or not user_data:
            return
        chat_info = await self.telegram_utils.get_chat_info()
        channel_name = chat_info['title'] if chat_info else "our channel"
        
        # Get or create unique invite link for this user
        stored_invite_link = self.db.get_invite_link(user_data['user_id'])
        if stored_invite_link:
            invite_link = stored_invite_link
        else:
            # Create new unique invite link
            referral_code = user_data['referral_code']
            invite_link_name = f"Referral-{referral_code}"
            invite_link = await self.telegram_utils.create_unique_invite_link(name=invite_link_name)
            
            # Store the invite link in database
            self.db.store_invite_link(user_data['user_id'], referral_code, invite_link, invite_link_name)
        
        message = self.messages.WELCOME_EXISTING_MEMBER.format(
            channel_name=channel_name,
            referral_link=invite_link,
            target=self.config.referral_target
        )
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /status command with multilingual support"""
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        user_lang = self.language_manager.get_user_language(user_id)
        
        # Check if user exists
        user = self.db.get_user(user_id)
        if not user:
            message = self.multilingual_messages.get_message(user_lang, "error_register_first", fallback="❌ Please use /start first to register.")
            await update.message.reply_text(message)
            return
        
        # Check channel membership
        is_member = await self.telegram_utils.check_channel_membership(user_id)
        if not is_member:
            channel_link = self.telegram_utils.get_channel_link()
            message = self.multilingual_messages.get_message(
                user_lang, "error_not_channel_member", channel_link=channel_link
            )
            await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
            return
        
        # Get referral progress
        progress = self.referral_system.get_referral_progress(user_id, self.config.referral_target)
        
        # Generate progress bar
        progress_bar_full = self.multilingual_messages.get_message(user_lang, "progress_bar_full")
        progress_bar_empty = self.multilingual_messages.get_message(user_lang, "progress_bar_empty")
        filled = int((progress['progress_percentage'] / 100) * 10)
        empty = 10 - filled
        progress_bar = progress_bar_full * filled + progress_bar_empty * empty
        
        # Get status text
        if progress['target_reached']:
            status_text = self.multilingual_messages.get_message(user_lang, "status_target_reached")
        elif progress['active_referrals'] == 0:
            status_text = self.multilingual_messages.get_message(user_lang, "status_no_referrals")
        else:
            status_text = self.multilingual_messages.get_message(
                user_lang, "status_progress", remaining=progress['remaining']
            )
        
        message = self.multilingual_messages.get_message(
            user_lang, "status_message",
            active_referrals=progress['active_referrals'],
            target=progress['target'],
            total_referrals=progress['total_referrals'],
            remaining=progress['remaining'],
            progress=int(progress['progress_percentage']),
            progress_bar=progress_bar,
            status_text=status_text
        )
        
        keyboard = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_status"),
                InlineKeyboardButton("📊 My Link", callback_data="my_link"),
            ],
            [
                InlineKeyboardButton("🏆 Claim Reward", callback_data="claim_reward"),
                InlineKeyboardButton("❓ Help", callback_data="help"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    async def language_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        # ...existing code for language selection...
        pass

    async def button_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle inline keyboard button callbacks"""
        query = update.callback_query
        if not query:
            logger.warning("Received button callback with no query")
            return
            
        user_id = query.from_user.id
        user_lang = self.language_manager.get_user_language(user_id)
        
        logger.info(f"Button callback received: {query.data} from user {user_id}")
        await query.answer()
        
        if query.data == "my_status":
            # Show current status
            await self._show_status_inline(query, user_id, user_lang)
        elif query.data == "refresh_status":
            # Refresh and show updated status
            await self._show_status_inline(query, user_id, user_lang)
        elif query.data == "claim_reward":
            # Handle reward claiming
            await self._handle_claim_inline(query, user_id, user_lang)
        elif query.data == "help":
            # Show help message
            message = self.multilingual_messages.get_message(user_lang, "help_message")
            
            # Create back button
            keyboard = [[InlineKeyboardButton("🔙 Back to Status", callback_data="refresh_status")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        elif query.data == "my_link":
            # Show user's referral link
            await self._show_referral_link_inline(query, user_id, user_lang)
        elif query.data == "share_success":
            # Handle success sharing
            await self._show_status_inline(query, user_id, user_lang)
        else:
            logger.warning(f"Unknown callback data: {query.data}")
            await query.edit_message_text("Unknown action.")
    
    async def _show_status_inline(self, query, user_id: int, user_lang: str) -> None:
        """Show status message inline"""
        try:
        # Check if user exists
        user = self.db.get_user(user_id)
        if not user:
            message = self.multilingual_messages.get_message(user_lang, "error_register_first", fallback="❌ Please use /start first to register.")
            await query.edit_message_text(message)
            return
        
        # Check channel membership
        is_member = await self.telegram_utils.check_channel_membership(user_id)
        if not is_member:
            channel_link = self.telegram_utils.get_channel_link()
            message = self.multilingual_messages.get_message(
                user_lang, "error_not_channel_member", channel_link=channel_link
            )
            await query.edit_message_text(message, parse_mode=ParseMode.MARKDOWN)
            return
        
        # Get referral progress
        progress = self.referral_system.get_referral_progress(user_id, self.config.referral_target)
        
        # Generate progress bar
        progress_bar_full = self.multilingual_messages.get_message(user_lang, "progress_bar_full")
        progress_bar_empty = self.multilingual_messages.get_message(user_lang, "progress_bar_empty")
        filled = int((progress['progress_percentage'] / 100) * 10)
        empty = 10 - filled
        progress_bar = progress_bar_full * filled + progress_bar_empty * empty
        
        # Get status text
        if progress['target_reached']:
            status_text = self.multilingual_messages.get_message(user_lang, "status_target_reached")
        elif progress['active_referrals'] == 0:
            status_text = self.multilingual_messages.get_message(user_lang, "status_no_referrals")
        else:
            status_text = self.multilingual_messages.get_message(
                user_lang, "status_progress", remaining=progress['remaining']
            )
        
        message = self.multilingual_messages.get_message(
            user_lang, "status_message",
            active_referrals=progress['active_referrals'],
            target=progress['target'],
            total_referrals=progress['total_referrals'],
            remaining=progress['remaining'],
            progress=int(progress['progress_percentage']),
            progress_bar=progress_bar,
            status_text=status_text
        )
        
        # Create keyboard with updated buttons
        keyboard = [
            [
                InlineKeyboardButton("🔄 Refresh", callback_data="refresh_status"),
                InlineKeyboardButton("📊 My Link", callback_data="my_link"),
            ],
            [
                InlineKeyboardButton("🏆 Claim Reward", callback_data="claim_reward"),
                InlineKeyboardButton("❓ Help", callback_data="help"),
            ]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        except Exception as e:
            logger.error(f"Error in _show_status_inline: {e}")
            await query.edit_message_text("❌ An error occurred. Please try again.")
    
    async def _handle_claim_inline(self, query, user_id: int, user_lang: str) -> None:
        """Handle reward claiming inline"""
        try:
        # Check if user exists
        user = self.db.get_user(user_id)
        if not user:
            message = self.multilingual_messages.get_message(user_lang, "error_register_first", fallback="❌ Please use /start first to register.")
            await query.edit_message_text(message)
            return
        
        # Check if reward already claimed
        if user['reward_claimed']:
            # Get user's stored invite link
            stored_invite_link = self.db.get_invite_link(user_id)
            invite_link = stored_invite_link or self.telegram_utils.get_channel_link()
            message = self.multilingual_messages.get_message(
                user_lang, "error_reward_already_claimed", referral_link=invite_link
            )
            
            # Create back button
            keyboard = [[InlineKeyboardButton("🔙 Back to Status", callback_data="refresh_status")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            return
        
        # Check if target reached
        if not self.referral_system.check_referral_target_reached(user_id, self.config.referral_target):
            progress = self.referral_system.get_referral_progress(user_id, self.config.referral_target)
            message = self.multilingual_messages.get_message(
                user_lang, "error_reward_not_available",
                active_referrals=progress['active_referrals'],
                target=progress['target']
            )
            
            # Create back button
            keyboard = [[InlineKeyboardButton("🔙 Back to Status", callback_data="refresh_status")]]
            reply_markup = InlineKeyboardMarkup(keyboard)
            
            await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
            return
        
        # Claim reward
        self.db.mark_reward_claimed(user_id)
        
        # Get user's stored invite link
        stored_invite_link = self.db.get_invite_link(user_id)
        invite_link = stored_invite_link or self.telegram_utils.get_channel_link()
        
        message = self.multilingual_messages.get_message(
            user_lang, "reward_claimed",
            reward_message=self.config.reward_message,
            referral_link=invite_link
        )
        
        # Create celebration keyboard
        keyboard = [
            [InlineKeyboardButton("🎉 Share Success", callback_data="share_success")],
            [InlineKeyboardButton("📊 View Status", callback_data="refresh_status")]
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
        logger.info(f"User {user_id} claimed their reward via inline button")
        except Exception as e:
            logger.error(f"Error in _handle_claim_inline: {e}")
            await query.edit_message_text("❌ An error occurred. Please try again.")
    
    async def _show_referral_link_inline(self, query, user_id: int, user_lang: str) -> None:
        """Show user's referral link inline"""
        try:
        user = self.db.get_user(user_id)
        if not user:
            message = self.multilingual_messages.get_message(user_lang, "error_register_first", fallback="❌ Please use /start first to register.")
            await query.edit_message_text(message)
            return
        
        # Get user's stored invite link
        stored_invite_link = self.db.get_invite_link(user_id)
        if stored_invite_link:
            invite_link = stored_invite_link
        else:
            # Create new unique invite link if not exists
            referral_code = user['referral_code']
            invite_link_name = f"Referral-{referral_code}"
            invite_link = await self.telegram_utils.create_unique_invite_link(name=invite_link_name)
            
            # Store the invite link in database
            self.db.store_invite_link(user_id, referral_code, invite_link, invite_link_name)
        
        message = f"""
🔗 **Your Unique Referral Link**

{invite_link}

📋 **How to use:**
1. Copy the link above
2. Share it with friends
3. When they join using your link, you get credit
4. Reach {self.config.referral_target} referrals to claim your reward!

💡 **Tip:** Share this link in groups, social media, or directly with friends!
"""
        
        # Create back button
        keyboard = [[InlineKeyboardButton("🔙 Back to Status", callback_data="refresh_status")]]
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        await query.edit_message_text(message, reply_markup=reply_markup, parse_mode=ParseMode.MARKDOWN)
    
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
            # Get user's stored invite link
            stored_invite_link = self.db.get_invite_link(user_id)
            invite_link = stored_invite_link or self.telegram_utils.get_channel_link()
            message = self.messages.ERROR_REWARD_ALREADY_CLAIMED.format(
                referral_link=invite_link
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
        # Get user's stored invite link
        stored_invite_link = self.db.get_invite_link(user_id)
        invite_link = stored_invite_link or self.telegram_utils.get_channel_link()
        message = self.messages.REWARD_CLAIMED.format(
            reward_message=self.config.reward_message,
            referral_link=invite_link
        )
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
        logger.info(f"User {user_id} claimed their reward")
    
    async def language_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /language command to change language settings"""
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        user_lang = self.language_manager.get_user_language(user_id)
        
        # Create language selection keyboard
        available_languages = self.multilingual_messages.get_available_languages()
        keyboard = []
        
        # Create rows of 2 languages each
        row = []
        for lang_code, lang_name in available_languages.items():
            button = InlineKeyboardButton(lang_name, callback_data=f"lang_{lang_code}")
            row.append(button)
            if len(row) == 2:
                keyboard.append(row)
                row = []
        
        # Add remaining button if exists
        if row:
            keyboard.append(row)
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message = self.multilingual_messages.get_message(user_lang, "language_selection")
        await update.message.reply_text(message, reply_markup=reply_markup)
    
    async def language_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle language selection callback"""
        query = update.callback_query
        if not query or not query.data or not update.effective_user:
            return
            
        await query.answer()
        
        user_id = update.effective_user.id
        lang_code = query.data.replace("lang_", "")
        
        # Set the new language
        self.language_manager.set_user_language(user_id, lang_code)
        
        # Send confirmation in the new language
        message = self.multilingual_messages.get_message(lang_code, "language_changed")
        await query.edit_message_text(message)
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
        """Handle /help command with multilingual support"""
        if not update.effective_user or not update.message:
            return
            
        user_id = update.effective_user.id
        user_lang = self.language_manager.get_user_language(user_id)
        
        message = self.multilingual_messages.get_message(user_lang, "help_message")
        await update.message.reply_text(message, parse_mode=ParseMode.MARKDOWN)
    
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
                    # Get or create unique invite link for this user
                    stored_invite_link = self.db.get_invite_link(user_id)
                    if stored_invite_link:
                        referral_link = stored_invite_link
                    else:
                        # Create new unique invite link
                        referral_code = user['referral_code']
                        invite_link_name = f"Referral-{referral_code}"
                        referral_link = await self.telegram_utils.create_unique_invite_link(name=invite_link_name)
                        
                        # Store the invite link in database
                        self.db.store_invite_link(user_id, referral_code, referral_link, invite_link_name)
                    
                    chat_info = await self.telegram_utils.get_chat_info()
                    channel_name = chat_info['title'] if chat_info else "our channel"
                    # Multilingual welcome message
                    user_lang = self.language_manager.get_user_language(user_id)
                    message = self.multilingual_messages.get_message(
                        user_lang,
                        "channel_joined_success",
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
        except Exception as e:
            logger.error(f"Error in _show_referral_link_inline: {e}")
            await query.edit_message_text("❌ An error occurred. Please try again.")
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
            CommandHandler("language", self.language_command),
            CommandHandler("admin_stats", self.admin_stats_command),
            # Handle all button callbacks first
            CallbackQueryHandler(self.button_callback, pattern="^(refresh_status|claim_reward|help|my_link|share_success)$"),
            # Handle language selection callbacks
            CallbackQueryHandler(self.language_callback, pattern="^lang_"),
            # Handle chat member updates
            ChatMemberHandler(self.chat_member_updated, ChatMemberHandler.CHAT_MEMBER)
        ]
