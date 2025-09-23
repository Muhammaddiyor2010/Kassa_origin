#!/usr/bin/env python3
"""
Startup script for Kassa AI Bot with environment loading
"""

import os
import sys
from pathlib import Path

def load_env_file():
    """
    Load environment variables from .env file
    """
    env_file = Path('.env')
    if env_file.exists():
        print("📁 Loading environment variables from .env file...")
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    os.environ[key] = value
        print("✅ Environment variables loaded")
    else:
        print("⚠️  No .env file found, using system environment variables")

def check_requirements():
    """
    Check if required environment variables are set
    """
    required_vars = ['BOT_TOKEN', 'GEMINI_API_KEY']
    missing_vars = []
    
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        print("\n💡 Please run: python setup_env.py")
        return False
    
    return True

def main():
    """
    Main startup function
    """
    print("🤖 Starting Kassa AI Bot...")
    
    # Load environment variables
    load_env_file()
    
    # Check requirements
    if not check_requirements():
        sys.exit(1)
    
    # Import and run the appropriate bot
    try:
        if len(sys.argv) > 1 and sys.argv[1] == '--webhook':
            print("🌐 Starting webhook server...")
            from webhook_server import main as webhook_main
            webhook_main()
        else:
            print("🏠 Starting local bot...")
            from bot import main as bot_main
            import asyncio
            asyncio.run(bot_main())
    except KeyboardInterrupt:
        print("\n👋 Bot stopped by user")
    except Exception as e:
        print(f"❌ Error starting bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()
