# Telegram Referral Bot

## Overview

This is a Telegram bot that implements a referral system for channel growth. Users can generate unique referral links to invite friends to join a specific Telegram channel. When users successfully refer a target number of people, they become eligible for rewards. The bot tracks channel membership, manages referral relationships, and provides progress tracking.

## System Architecture

The application follows a modular Python architecture with clear separation of concerns:

- **Bot Layer**: Handles Telegram interactions and user commands
- **Business Logic Layer**: Manages referral system logic and user rewards
- **Data Layer**: SQLite database for persistent storage
- **Configuration Layer**: Environment-based configuration management
- **Utility Layer**: Helper functions for Telegram API operations

## Key Components

### 1. Bot Handlers (`bot_handlers.py`)
- Processes all Telegram bot commands and messages
- Handles user registration and referral code processing
- Manages channel membership verification
- Coordinates between different system components

### 2. Database Layer (`database.py`)
- SQLite-based data persistence
- Manages three main tables: users, referrals, and channel events
- Provides CRUD operations for user and referral management
- Handles referral tracking and reward eligibility

### 3. Referral System (`referral_system.py`)
- Generates unique referral codes using SHA256 hashing
- Creates shareable referral links
- Processes new referrals with validation (prevents self-referrals and duplicate referrals)
- Tracks referral success and eligibility

### 4. Configuration Management (`config.py`)
- Environment variable-based configuration
- Supports both webhook and polling modes
- Configurable referral targets and reward messages
- Admin user management

### 5. Telegram Utilities (`utils.py`)
- Channel membership verification
- Safe message sending with error handling
- Channel information retrieval
- Link generation utilities

### 6. Message Templates (`messages.py`)
- Centralized message management
- Welcome messages for new and existing users
- Referral success notifications
- User progress updates

## Data Flow

1. **User Registration**: New users start the bot and receive a unique referral code
2. **Channel Verification**: Bot checks if user has joined the required channel
3. **Referral Processing**: When users join via referral links, the system tracks the relationship
4. **Progress Tracking**: Users can check their referral progress anytime
5. **Reward Distribution**: When target referrals are reached, users become eligible for rewards

## External Dependencies

- **python-telegram-bot**: Core Telegram bot functionality
- **SQLite**: Local database storage (no external database required)
- **Telegram Channel**: Target channel that users must join
- **Environment Variables**: Configuration through system environment

## Deployment Strategy

The bot supports two deployment modes:

### Polling Mode (Default)
- Simple deployment without webhook setup
- Suitable for development and small-scale deployments
- Bot actively polls Telegram servers for updates

### Webhook Mode
- Production-ready deployment option
- Requires WEBHOOK_URL environment variable
- More efficient for high-traffic bots
- Configurable port (default: 8000)

### Environment Variables Required:
- `BOT_TOKEN`: Telegram bot token from BotFather
- `CHANNEL_ID`: Target channel ID (with -100 prefix for supergroups)
- `CHANNEL_USERNAME`: Channel username for link generation
- `ADMIN_USER_IDS`: Comma-separated list of admin user IDs

### Optional Configuration:
- `REFERRAL_TARGET`: Number of referrals needed for reward (default: 5)
- `REWARD_MESSAGE`: Custom reward message
- `WEBHOOK_URL`: For webhook deployment mode
- `PORT`: Server port for webhook mode

## Changelog

- July 02, 2025. Initial setup and full bot implementation completed
- Fixed import issues and verified bot functionality
- Created comprehensive documentation and setup guides

## Recent Updates

The Telegram referral bot is now fully functional with all requested features:
- Channel join verification system
- Unique referral link generation for each user
- Real-time progress tracking with /status command
- Reward system with /claim command
- Automatic handling of users joining/leaving the channel
- Admin statistics dashboard
- Complete database system for tracking users and referrals
- **NEW: Multilingual support for 15 languages** for international channel growth
- **NEW: Automatic language detection** from Telegram user settings
- **NEW: Interactive language selector** with /language command
- **NEW: Localized user experience** with native language messages

## User Preferences

Preferred communication style: Simple, everyday language.