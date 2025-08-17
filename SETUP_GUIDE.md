# 🚀 Telegram Referral Bot Setup Guide

This guide will help you set up your Telegram bot and channel credentials for the referral bot.

## 📋 Prerequisites

- A Telegram account
- Access to create/manage a Telegram channel
- Basic understanding of Telegram bots

## 🔧 Step-by-Step Setup

### 1. Create Your Bot Token

1. **Open Telegram** and search for `@BotFather`
2. **Start a chat** with BotFather
3. **Send the command**: `/newbot`
4. **Follow the instructions**:
   - Enter a name for your bot (e.g., "My Referral Bot")
   - Enter a username for your bot (must end with 'bot', e.g., "myreferralbot")
5. **Save the bot token** - BotFather will give you a token like:
   ```
   1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   ```

### 2. Get Your Channel Information

#### Option A: Create a New Channel
1. **In Telegram**, tap the menu (☰) → "New Channel"
2. **Choose a name** and description for your channel
3. **Set it as public** and choose a username (e.g., "mychannel")
4. **Add your bot as an admin** with these permissions:
   - ✅ Delete messages
   - ✅ Restrict members
   - ✅ Pin messages
   - ✅ Manage video chats

#### Option B: Use Existing Channel
1. **Open your existing channel**
2. **Add your bot as an admin** with the permissions listed above

### 3. Get Your Channel ID

#### Method 1: Using @userinfobot (Recommended)
1. **Search for `@userinfobot`** in Telegram
2. **Start a chat** with it
3. **Forward a message** from your channel to @userinfobot
4. **Look for the "Forward from" section** - it will show your channel ID
5. **Add -100 prefix** to the ID (e.g., if it shows 1234567890, use -1001234567890)

#### Method 2: Using Bot Logs
1. **Add your bot to the channel** as admin
2. **Send a message** in the channel
3. **Run the bot** - it will log the channel ID in the console

### 4. Get Your User ID

1. **Search for `@userinfobot`** in Telegram
2. **Start a chat** with it
3. **Send any message** to it
4. **It will reply** with your user ID (e.g., 123456789)

### 5. Configure Environment Variables

1. **Copy the template file**:
   ```bash
   cp env_template.txt .env
   ```

2. **Edit the `.env` file** and fill in your credentials:
   ```env
   BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
   CHANNEL_ID=-1001234567890
   CHANNEL_USERNAME=mychannel
   ADMIN_USER_IDS=123456789
   ```

## 🔍 Verification Steps

### Test Your Bot Token
1. **Open your browser** and go to:
   ```
   https://api.telegram.org/bot<YOUR_BOT_TOKEN>/getMe
   ```
2. **Replace `<YOUR_BOT_TOKEN>`** with your actual token
3. **You should see** a JSON response with your bot's information

### Test Your Channel Access
1. **Make sure your bot is an admin** in your channel
2. **Try sending a message** in the channel
3. **Check that the bot can read** the message

## 🚨 Common Issues & Solutions

### "Bot token is invalid"
- Double-check your bot token from BotFather
- Make sure there are no extra spaces or characters

### "Channel not found"
- Verify your channel username (without @ symbol)
- Make sure the channel is public
- Check that your bot is an admin in the channel

### "Access denied"
- Ensure your bot has admin permissions in the channel
- Check that the channel ID includes the -100 prefix

### "User ID not found"
- Use @userinfobot to get the correct user ID
- Make sure you're using your personal user ID, not the bot's ID

## 📝 Example Configuration

Here's what a complete `.env` file should look like:

```env
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrsTUVwxyz
CHANNEL_ID=-1001234567890
CHANNEL_USERNAME=myreferralchannel
ADMIN_USER_IDS=123456789,987654321
REFERRAL_TARGET=5
REWARD_MESSAGE=🎉 Congratulations! You've earned your reward!
```

## ✅ Next Steps

Once you've configured your `.env` file:

1. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

2. **Run the bot**:
   ```bash
   python -m telegramreferralpro.main
   ```

3. **Test the bot** by sending `/start` to your bot

## 🆘 Need Help?

If you encounter any issues:
1. Check the bot logs for error messages
2. Verify all credentials are correct
3. Ensure your bot has proper permissions in the channel
4. Make sure your channel is public and accessible
