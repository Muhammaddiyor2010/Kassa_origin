from aiogram import Bot

from config import Config, load_config
from tables.sqlite import Database

bot: Bot = Bot(token="8176163130:AAEE0NPybiiHDU_gPkpsLYDayaPPc5LoBpQ")

db = Database()

# Add start_count column to existing database if needed
db.add_start_count_column()

