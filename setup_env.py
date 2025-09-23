#!/usr/bin/env python3
"""
Environment setup script for Kassa AI Bot
"""

import os
from pathlib import Path

def setup_environment():
    """
    Setup environment variables and directories
    """
    print("🚀 Setting up Kassa AI Bot environment...")
    
    # Create necessary directories
    directories = ['logs', 'uploads', 'data']
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
        print(f"✅ Created directory: {directory}")
    
    # Check for environment variables
    required_vars = ['BOT_TOKEN', 'GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"\n⚠️  Missing environment variables: {', '.join(missing_vars)}")
        print("\n📝 Please set the following environment variables:")
        for var in missing_vars:
            if var == 'BOT_TOKEN':
                print(f"   export {var}='your_telegram_bot_token_here'")
            elif var == 'GEMINI_API_KEY':
                print(f"   export {var}='your_google_gemini_api_key_here'")
        
        print("\n💡 Or create a .env file with:")
        print("   BOT_TOKEN=your_telegram_bot_token_here")
        print("   GEMINI_API_KEY=your_google_gemini_api_key_here")
        print("   WEBHOOK_URL=https://yourdomain.com")
        print("   MAIN_ADMIN_ID=7231910736")
        
        return False
    else:
        print("✅ All required environment variables are set!")
        return True

def create_env_file():
    """
    Create a sample .env file
    """
    env_content = """# Bot Configuration
BOT_TOKEN=your_telegram_bot_token_here
GEMINI_API_KEY=your_google_gemini_api_key_here

# Webhook Configuration (for production)
WEBHOOK_URL=https://yourdomain.com
WEBHOOK_PATH=/webhook
WEBAPP_HOST=0.0.0.0
WEBAPP_PORT=8080

# Admin Configuration
MAIN_ADMIN_ID=7231910736

# Database Configuration
DATABASE_URL=sqlite:///main.db
DATABASE_PATH=./main.db

# Logging
LOG_LEVEL=INFO
LOG_FILE=./logs/bot.log

# Environment
ENVIRONMENT=production
"""
    
    env_file = Path('.env')
    if not env_file.exists():
        with open(env_file, 'w') as f:
            f.write(env_content)
        print("✅ Created .env file template")
        print("📝 Please edit .env file with your actual values")
    else:
        print("ℹ️  .env file already exists")

if __name__ == "__main__":
    print("=" * 50)
    print("🤖 Kassa AI Bot Environment Setup")
    print("=" * 50)
    
    # Create directories
    setup_environment()
    
    # Create .env file template
    create_env_file()
    
    print("\n" + "=" * 50)
    print("🎉 Setup complete!")
    print("=" * 50)
    print("\n📋 Next steps:")
    print("1. Set your environment variables or edit .env file")
    print("2. Run: python bot.py (for local development)")
    print("3. Run: python webhook_server.py (for production)")
    print("\n📚 For more information, see README.md")
