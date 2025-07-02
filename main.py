import asyncio
import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from telegram.error import TelegramError

from config import load_config
from database import Database
from referral_system import ReferralSystem
from bot_handlers import BotHandlers
from utils import TelegramUtils, setup_logging

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

async def main():
    """Main function to run the bot"""
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
        
        # Initialize bot handlers
        bot_handlers = BotHandlers(config, database, referral_system, telegram_utils)
        
        # Add handlers to application
        for handler in bot_handlers.get_handlers():
            application.add_handler(handler)
        
        logger.info("Bot handlers registered")
        
        # Start the bot
        if config.webhook_url:
            # Webhook mode
            logger.info(f"Starting bot in webhook mode on port {config.port}")
            await application.run_webhook(
                listen="0.0.0.0",
                port=config.port,
                webhook_url=config.webhook_url,
                url_path=config.bot_token
            )
        else:
            # Polling mode
            logger.info("Starting bot in polling mode")
            await application.run_polling(allowed_updates=["message", "chat_member"])
    
    except Exception as e:
        logger.error(f"Failed to start bot: {e}")
        raise

if __name__ == "__main__":
    asyncio.run(main())
