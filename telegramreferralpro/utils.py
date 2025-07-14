import logging
import re
from typing import Optional
from telegram import Bot, ChatMember
from telegram.error import TelegramError

logger = logging.getLogger(__name__)

def setup_logging():
    """Setup logging configuration"""
    logging.basicConfig(
        level=logging.INFO,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[
            logging.FileHandler('bot.log'),
            logging.StreamHandler()
        ]
    )
    # Reduce telegram library logging
    logging.getLogger('telegram').setLevel(logging.WARNING)
    logging.getLogger('httpx').setLevel(logging.WARNING)

class TelegramUtils:
    def __init__(self, bot: Bot, channel_id: str, channel_username: str):
        self.bot = bot
        self.channel_id = channel_id
        self.channel_username = channel_username

    async def create_unique_invite_link(self, expire_date=None, member_limit=None, name=None) -> str:
        """Create a unique invite link for the channel using Telegram API"""
        try:
            params = {}
            if expire_date:
                params['expire_date'] = expire_date
            if member_limit:
                params['member_limit'] = member_limit
            if name:
                params['name'] = name
            invite_link = await self.bot.create_chat_invite_link(self.channel_id, **params)
            return invite_link.invite_link
        except Exception as e:
            logger.error(f"Error creating invite link: {e}")
            return self.get_channel_link()

    async def check_channel_membership(self, user_id: int) -> bool:
        """Check if a user is a member of the channel"""
        try:
            member = await self.bot.get_chat_member(self.channel_id, user_id)
            return member.status in [ChatMember.MEMBER, ChatMember.ADMINISTRATOR, ChatMember.OWNER]
        except TelegramError as e:
            logger.warning(f"Error checking membership for user {user_id}: {e}")
            return False

    def get_channel_link(self) -> str:
        """Get the channel invite link"""
        if self.channel_username.startswith('@'):
            return f"https://t.me/{self.channel_username[1:]}"
        else:
            return f"https://t.me/{self.channel_username}"

    async def get_chat_info(self) -> Optional[dict]:
        """Get information about the channel"""
        try:
            chat = await self.bot.get_chat(self.channel_id)
            return {
                'title': chat.title,
                'username': chat.username,


                'member_count': await self.bot.get_chat_member_count(self.channel_id) if hasattr(chat, 'member_count') else None
            }
        except TelegramError as e:
            logger.error(f"Error getting chat info: {e}")
            return None

    async def send_message_safe(self, user_id: int, text: str, **kwargs) -> bool:
        """Send a message with error handling"""
        try:
            await self.bot.send_message(user_id, text, **kwargs)
            return True
        except TelegramError as e:
            logger.warning(f"Failed to send message to user {user_id}: {e}")
            return False

    def is_admin(self, user_id: int, admin_user_ids: list) -> bool:
        """Check if user is an admin"""
        return user_id in admin_user_ids

def escape_markdown(text: str) -> str:
    """Escape Telegram Markdown special characters in a string."""
    if not isinstance(text, str):
        return text
    # Escape these characters: _ * [ ] ( ) ~ ` > # + - = | { } . !
    return re.sub(r'([_\*\[\]\(\)~`>#+\-=|{}.!])', r'\\\1', text)
