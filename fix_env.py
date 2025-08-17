#!/usr/bin/env python3
"""
Script to fix the .env file with correct channel username
"""

import os
import re

def fix_env_file():
    """Fix the .env file with correct channel username"""
    env_file = '.env'
    
    if not os.path.exists(env_file):
        print("❌ .env file not found!")
        return
    
    # Read the current .env file
    with open(env_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Replace the incorrect channel username
    old_username = "CHANNEL_USERNAME=-1002713207409"
    new_username = "CHANNEL_USERNAME=EarnPro_org"
    
    if old_username in content:
        content = content.replace(old_username, new_username)
        
        # Write the fixed content back
        with open(env_file, 'w', encoding='utf-8') as f:
            f.write(content)
        
        print("✅ Fixed .env file!")
        print(f"   Changed: {old_username}")
        print(f"   To: {new_username}")
    else:
        print("⚠️  Channel username line not found or already correct")
        print("   Please manually update your .env file:")
        print("   CHANNEL_USERNAME=EarnPro_org")

if __name__ == "__main__":
    fix_env_file()
