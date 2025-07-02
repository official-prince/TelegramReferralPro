# Telegram Referral Bot

A Python Telegram bot that creates a referral system for channel growth. Users can generate unique referral links to invite friends and earn rewards when they reach their referral targets.

## Features

- **Automatic Channel Integration**: Bot checks channel membership automatically
- **Unique Referral Links**: Each user gets a personalized referral link
- **Progress Tracking**: Users can check their referral progress anytime
- **Real-time Updates**: Automatic notifications when people join or leave
- **Reward System**: Users can claim rewards when reaching their target
- **Admin Dashboard**: Statistics and management tools for administrators

## Quick Setup

### 1. Create Your Bot
1. Message [@BotFather](https://t.me/BotFather) on Telegram
2. Send `/newbot` and follow the instructions
3. Save the bot token you receive

### 2. Set Up Your Channel
1. Create or use an existing Telegram channel
2. Add your bot as an admin with these permissions:
   - Delete messages
   - Restrict members
   - Pin messages
   - Manage video chats
3. Note your channel username (e.g., if your channel is t.me/mychannel, the username is "mychannel")

### 3. Configure Environment Variables

Set these required environment variables:

```bash
BOT_TOKEN=your_bot_token_here
CHANNEL_ID=your_channel_id_here
CHANNEL_USERNAME=your_channel_username
ADMIN_USER_IDS=your_user_id,another_admin_id
```

Optional configuration:
```bash
REFERRAL_TARGET=5
REWARD_MESSAGE=Congratulations! You've earned your reward!
```

### 4. Run the Bot

```bash
python main.py
```

## How It Works

1. **User Starts Bot**: New users get instructions to join your channel
2. **Channel Join**: After joining, users receive their unique referral link
3. **Share & Refer**: Users share their link with friends
4. **Track Progress**: Real-time tracking of successful referrals
5. **Claim Rewards**: When target is reached, users can claim their reward

## Bot Commands

- `/start` - Get your referral link and instructions
- `/status` - Check your referral progress
- `/claim` - Claim your reward when target is reached
- `/help` - Show help message
- `/admin_stats` - Admin statistics (admins only)

## Environment Variables

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `BOT_TOKEN` | Yes | - | Your bot token from BotFather |
| `CHANNEL_ID` | Yes | - | Your channel ID (with -100 prefix) |
| `CHANNEL_USERNAME` | Yes | - | Channel username without @ |
| `ADMIN_USER_IDS` | Yes | - | Comma-separated admin user IDs |
| `REFERRAL_TARGET` | No | 5 | Referrals needed for reward |
| `REWARD_MESSAGE` | No | Default message | Custom reward message |
| `WEBHOOK_URL` | No | - | For webhook deployment |
| `PORT` | No | 8000 | Webhook server port |

## Getting Your Channel ID

1. Add your bot to the channel as admin
2. Send a message in the channel
3. Check the bot logs when it starts - it will show the channel ID
4. Or use [@userinfobot](https://t.me/userinfobot) - forward a message from your channel to it

## Architecture

The bot is built with a modular Python architecture:

- **Config Management**: Environment-based configuration
- **Database Layer**: SQLite for user and referral tracking
- **Referral System**: Core logic for managing referrarls
- **Bot Handlers**: Telegram command and event processing
- **Message Templates**: Centralized message management
- **Utilities**: Helper functions for Telegram operations

## Files Structure

```
├── main.py              # Bot entry point
├── config.py            # Configuration management
├── database.py          # Database operations
├── referral_system.py   # Referral logic
├── bot_handlers.py      # Telegram handlers
├── messages.py          # Message templates
├── utils.py             # Utility functions
└── README.md           # This file
```

## Support

The bot automatically handles:
- User joins and leaves
- Referral tracking
- Progress updates
- Reward eligibility
- Error handling

## License

This project is open source and available under the MIT License.