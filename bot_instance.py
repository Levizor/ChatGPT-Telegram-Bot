from aiogram import Bot
from config import TOKEN
from aiogram.enums import ParseMode
bot = Bot(
    token=TOKEN,
    parse_mode=ParseMode.MARKDOWN
)

async def get_bot_id():
    id=await bot.me()
    return id.id
