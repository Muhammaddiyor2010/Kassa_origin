"""
Production configuration for Kassa AI Bot
"""

import os
from pathlib import Path

# Base directory
BASE_DIR = Path(__file__).parent.parent

# Bot configuration
BOT_TOKEN = os.getenv('BOT_TOKEN')
WEBHOOK_URL = os.getenv('WEBHOOK_URL')
WEBHOOK_PATH = os.getenv('WEBHOOK_PATH', '/webhook')
WEBAPP_HOST = os.getenv('WEBAPP_HOST', '0.0.0.0')
WEBAPP_PORT = int(os.getenv('WEBAPP_PORT', 8080))

# Database configuration
DATABASE_URL = os.getenv('DATABASE_URL', 'sqlite:///main.db')
DATABASE_PATH = os.getenv('DATABASE_PATH', str(BASE_DIR / 'main.db'))

# Redis configuration (for production)
REDIS_URL = os.getenv('REDIS_URL', 'redis://localhost:6379/0')

# Logging configuration
LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
LOG_FILE = os.getenv('LOG_FILE', str(BASE_DIR / 'logs' / 'bot.log'))

# Admin configuration
MAIN_ADMIN_ID = int(os.getenv('MAIN_ADMIN_ID', '7231910736'))

# AI configuration
GEMINI_API_KEY = os.getenv('GEMINI_API_KEY')

# Security
SECRET_KEY = os.getenv('SECRET_KEY', 'your-secret-key-here')

# Environment
ENVIRONMENT = 'production'

# Server settings
DEBUG = False
RELOAD = False

# Database pool settings
DB_POOL_SIZE = int(os.getenv('DB_POOL_SIZE', '10'))
DB_MAX_OVERFLOW = int(os.getenv('DB_MAX_OVERFLOW', '20'))

# Rate limiting
RATE_LIMIT_PER_MINUTE = int(os.getenv('RATE_LIMIT_PER_MINUTE', '30'))

# File upload settings
MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', '20971520'))  # 20MB
UPLOAD_FOLDER = os.getenv('UPLOAD_FOLDER', str(BASE_DIR / 'uploads'))

# Monitoring
SENTRY_DSN = os.getenv('SENTRY_DSN')

# Backup settings
BACKUP_INTERVAL = int(os.getenv('BACKUP_INTERVAL', '3600'))  # 1 hour
BACKUP_RETENTION_DAYS = int(os.getenv('BACKUP_RETENTION_DAYS', '7'))
