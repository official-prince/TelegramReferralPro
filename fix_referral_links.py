#!/usr/bin/env python3
"""
Script to fix referral link issues and test channel connectivity
"""

import asyncio
import logging
from telegramreferralpro.config import load_config
from telegramreferralpro.database import Database
from telegramreferralpro.referral_system import ReferralSystem
from telegramreferralpro.utils import TelegramUtils, setup_logging
from telegram.ext import Application

# Setup logging
setup_logging()
logger = logging.getLogger(__name__)

async def fix_referral_links():
    """Fix referral link issues"""
    try:
        print("🔧 Fixing Referral Link Issues...")
        
        # Load configuration
        config = load_config()
        print(f"✅ Configuration loaded")
        print(f"📺 Channel ID: {config.channel_id}")
        print(f"👤 Channel Username: {config.channel_username}")
        
        # Create bot application
        application = Application.builder().token(config.bot_token).build()
        
        # Initialize telegram utils
        telegram_utils = TelegramUtils(application.bot, config.channel_id, config.channel_username)
        
        # Get channel information
        print("\n🔍 Getting channel information...")
        chat_info = await telegram_utils.get_chat_info()
        
        if chat_info:
            print(f"✅ Channel Title: {chat_info.get('title', 'Unknown')}")
            print(f"✅ Channel Username: {chat_info.get('username', 'None')}")
            
            # Update the channel username if we got it from the API
            if chat_info.get('username'):
                correct_username = chat_info['username']
                print(f"🎯 Correct channel username: {correct_username}")
                print(f"⚠️  Current config username: {config.channel_username}")
                
                if config.channel_username != correct_username:
                    print(f"❌ Channel username mismatch! Update your .env file:")
                    print(f"   CHANNEL_USERNAME={correct_username}")
            else:
                print("⚠️  Channel doesn't have a public username")
        else:
            print("❌ Could not get channel information")
        
        # Test creating invite links
        print("\n🔗 Testing invite link creation...")
        
        # Test 1: Create a simple invite link
        try:
            simple_link = await telegram_utils.create_unique_invite_link()
            print(f"✅ Simple invite link created: {simple_link}")
        except Exception as e:
            print(f"❌ Failed to create simple invite link: {e}")
        
        # Test 2: Create a named invite link
        try:
            named_link = await telegram_utils.create_unique_invite_link(name="Test-Referral")
            print(f"✅ Named invite link created: {named_link}")
        except Exception as e:
            print(f"❌ Failed to create named invite link: {e}")
        
        # Test 3: Test channel membership check
        print("\n👥 Testing channel membership check...")
        try:
            # Test with your user ID
            test_user_id = config.admin_user_ids[0] if config.admin_user_ids else 6754566064
            is_member = await telegram_utils.check_channel_membership(test_user_id)
            print(f"✅ User {test_user_id} membership check: {'Member' if is_member else 'Not a member'}")
        except Exception as e:
            print(f"❌ Failed to check membership: {e}")
        
        # Test 4: Test referral link generation
        print("\n🎯 Testing referral link generation...")
        try:
            # Initialize database and referral system
            database = Database(config.database_path)
            referral_system = ReferralSystem(database)
            
            # Generate a test referral code
            test_user_id = 123456789
            referral_code = referral_system.generate_referral_code(test_user_id)
            print(f"✅ Referral code generated: {referral_code}")
            
            # Create referral link
            if chat_info and chat_info.get('username'):
                correct_channel_link = f"https://t.me/{chat_info['username']}?start={referral_code}"
                print(f"✅ Correct referral link: {correct_channel_link}")
            else:
                # Fallback to using channel ID
                fallback_link = f"https://t.me/c/{config.channel_id[4:]}/?start={referral_code}"
                print(f"⚠️  Fallback referral link: {fallback_link}")
                
        except Exception as e:
            print(f"❌ Failed to generate referral link: {e}")
        
        print("\n🎉 Referral link testing completed!")
        
    except Exception as e:
        print(f"❌ Error during testing: {e}")
        logger.error(f"Error: {e}")

if __name__ == "__main__":
    asyncio.run(fix_referral_links())
