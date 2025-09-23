import asyncio
import logging

from aiogram import  Dispatcher

from handlers.echo import router
from handlers.start import start_router
from handlers.chiqim import chiqim_router
from handlers.harajatlar import harajatlar_router
from handlers.daromadlar import daromadlar_router
from handlers.hisobot import hisobot_router
from handlers.sozlamalar import sozlamalar_router
from handlers.admin import admin_router
from loader import bot,  db

logger = logging.getLogger(__name__)


async def main():
    logging.basicConfig(
        level=logging.INFO,
       
    )
    db.create_table_users()
    db.create_table_chiqim()
    db.create_table_kirim()
    db.create_table_tokens()
    db.create_admin_table()
    db.create_admin_tokens_table()
    db.add_plan_columns()
    db.add_admin_columns()
    db.add_ai_usage_column()
    db.add_pro_token_created_by_column()
    db.add_pro_token_is_active_column()
    
    # Set main admin (7231910736)
    main_admin_id = 7231910736
    if not db.is_admin(main_admin_id):
        db.add_admin(main_admin_id, added_by=None, username="Main Admin")
        print(f"Main admin {main_admin_id} added successfully")
    
    logger.info("Starting bot")


    dp: Dispatcher = Dispatcher()

    dp.include_routers( 
        start_router,
        admin_router,  # Admin router first to handle admin buttons
        sozlamalar_router,  # Settings router before chiqim to handle settings buttons
        harajatlar_router,
        chiqim_router,
        daromadlar_router,
        hisobot_router,
        # router
    )



        
    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except (KeyboardInterrupt, SystemExit):
        logger.info("Bot stopped")
