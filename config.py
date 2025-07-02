import os
from dataclasses import dataclass
from typing import Optional

@dataclass
class BotConfig:
    """Bot configuration class"""
    bot_token: str
    channel_id: str
    channel_username: str
    admin_user_ids: list
    referral_target: int = 5
    reward_message: str = "🎉 Congratulations! You've reached your referral target and earned your reward!"
    database_path: str = "bot_database.db"
    webhook_url: Optional[str] = None
    port: int = 8000

def load_config() -> BotConfig:
    """Load configuration from environment variables"""
    bot_token = os.getenv("BOT_TOKEN")
    if not bot_token:
        raise ValueError("BOT_TOKEN environment variable is required")
    
    channel_id = os.getenv("CHANNEL_ID")
    if not channel_id:
        raise ValueError("CHANNEL_ID environment variable is required")
    
    channel_username = os.getenv("CHANNEL_USERNAME", "")
    if not channel_username:
        raise ValueError("CHANNEL_USERNAME environment variable is required")
    
    admin_user_ids = os.getenv("ADMIN_USER_IDS", "").split(",")
    admin_user_ids = [int(uid.strip()) for uid in admin_user_ids if uid.strip().isdigit()]
    
    referral_target = int(os.getenv("REFERRAL_TARGET", "5"))
    reward_message = os.getenv("REWARD_MESSAGE", "🎉 Congratulations! You've reached your referral target and earned your reward!")
    
    return BotConfig(
        bot_token=bot_token,
        channel_id=channel_id,
        channel_username=channel_username,
        admin_user_ids=admin_user_ids,
        referral_target=referral_target,
        reward_message=reward_message,
        webhook_url=os.getenv("WEBHOOK_URL"),
        port=int(os.getenv("PORT", "8000"))
    )
