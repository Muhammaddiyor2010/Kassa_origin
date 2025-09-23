"""
Webhook server for production deployment
"""

import asyncio
import logging
from aiohttp import web
from aiohttp.web import Request, Response, json_response
from aiogram import Bot, Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiogram.types import Update
import os
import sys
from pathlib import Path

# Add project root to path
project_root = Path(__file__).parent
sys.path.append(str(project_root))

from config.production import (
    BOT_TOKEN, WEBHOOK_URL, WEBHOOK_PATH, WEBAPP_HOST, WEBAPP_PORT,
    LOG_LEVEL, LOG_FILE, MAIN_ADMIN_ID, ENVIRONMENT
)

# Import bot components
from handlers.start import start_router
from handlers.chiqim import chiqim_router
from handlers.harajatlar import harajatlar_router
from handlers.daromadlar import daromadlar_router
from handlers.hisobot import hisobot_router
from handlers.sozlamalar import sozlamalar_router
from handlers.admin import admin_router
from loader import db

# Create logs directory if it doesn't exist
log_dir = Path(LOG_FILE).parent
log_dir.mkdir(exist_ok=True)

# Configure logging
logging.basicConfig(
    level=getattr(logging, LOG_LEVEL),
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)

logger = logging.getLogger(__name__)

async def on_startup(bot: Bot) -> None:
    """
    Startup handler
    """
    logger.info("Starting webhook server...")
    
    # Initialize database
    try:
        db.create_table_users()
        db.create_table_chiqim()
        db.create_table_kirim()
        db.create_table_tokens()
        db.create_admin_table()
        db.create_admin_tokens_table()
        # Note: plan, pro_token, ai_usage_count, is_admin columns are already in create_table_users()
        db.add_pro_token_created_by_column()
        db.add_pro_token_is_active_column()
        
        # Set main admin
        if not db.is_admin(MAIN_ADMIN_ID):
            db.add_admin(MAIN_ADMIN_ID, added_by=None, username="Main Admin")
            logger.info(f"Main admin {MAIN_ADMIN_ID} added successfully")
        
        logger.info("Database initialized successfully")
    except Exception as e:
        logger.error(f"Database initialization error: {e}")
    
    # Set webhook
    try:
        webhook_url = f"{WEBHOOK_URL}{WEBHOOK_PATH}"
        await bot.set_webhook(
            url=webhook_url,
            drop_pending_updates=True
        )
        logger.info(f"Webhook set to: {webhook_url}")
    except Exception as e:
        logger.error(f"Webhook setup error: {e}")

async def on_shutdown(bot: Bot) -> None:
    """
    Shutdown handler
    """
    logger.info("Shutting down webhook server...")
    await bot.delete_webhook(drop_pending_updates=True)
    logger.info("Webhook deleted")

async def health_check(request: Request) -> Response:
    """
    Health check endpoint
    """
    return json_response({
        "status": "healthy",
        "environment": ENVIRONMENT,
        "bot_token_set": bool(BOT_TOKEN),
        "webhook_url": WEBHOOK_URL
    })

async def stats_endpoint(request: Request) -> Response:
    """
    Statistics endpoint
    """
    try:
        total_users = db.get_user_count()
        pro_users = db.get_pro_user_count()
        free_users = db.get_free_user_count()
        total_admins = len(db.get_all_admins())
        
        return json_response({
            "total_users": total_users,
            "pro_users": pro_users,
            "free_users": free_users,
            "total_admins": total_admins,
            "environment": ENVIRONMENT
        })
    except Exception as e:
        logger.error(f"Stats endpoint error: {e}")
        return json_response({"error": str(e)}, status=500)

def create_app() -> web.Application:
    """
    Create web application
    """
    # Create bot and dispatcher
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher()
    
    # Include routers
    dp.include_routers(
        start_router,
        admin_router,
        sozlamalar_router,
        harajatlar_router,
        chiqim_router,
        daromadlar_router,
        hisobot_router,
    )
    
    # Create web application
    app = web.Application()
    
    # Setup webhook handler
    webhook_requests_handler = SimpleRequestHandler(
        dispatcher=dp,
        bot=bot,
    )
    webhook_requests_handler.register(app, path=WEBHOOK_PATH)
    
    # Setup application
    setup_application(app, dp, bot=bot)
    
    # Add routes
    app.router.add_get('/health', health_check)
    app.router.add_get('/stats', stats_endpoint)
    
    # Add startup and shutdown handlers
    app.on_startup.append(lambda app: on_startup(bot))
    app.on_shutdown.append(lambda app: on_shutdown(bot))
    
    return app

def main():
    """
    Main function
    """
    if not BOT_TOKEN:
        logger.error("BOT_TOKEN is not set!")
        sys.exit(1)
    
    if not WEBHOOK_URL:
        logger.error("WEBHOOK_URL is not set!")
        sys.exit(1)
    
    # Create necessary directories
    log_dir = Path(LOG_FILE).parent
    log_dir.mkdir(exist_ok=True)
    
    upload_dir = Path("uploads")
    upload_dir.mkdir(exist_ok=True)
    
    data_dir = Path("data")
    data_dir.mkdir(exist_ok=True)
    
    logger.info(f"Starting server on {WEBAPP_HOST}:{WEBAPP_PORT}")
    logger.info(f"Environment: {ENVIRONMENT}")
    logger.info(f"Webhook URL: {WEBHOOK_URL}{WEBHOOK_PATH}")
    
    # Run server
    app = create_app()
    web.run_app(
        app,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
        access_log=logger
    )

if __name__ == '__main__':
    main()
