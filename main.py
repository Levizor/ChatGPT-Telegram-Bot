# main.py

# Import necessary modules and libraries
import asyncio
import datetime
import logging

import aiogram
from aiogram import Dispatcher
from aiogram.webhook.aiohttp_server import SimpleRequestHandler, setup_application
from aiohttp import web

from bot.modules.ChatGPT.chatgpt import chatgpt
from bot.scheduled import scheduler
from bot_instance import bot
from config import BASE_WEBHOOK_URL, WEBHOOK_PATH, test
from database.database import db
from dispatcher_instance import dp

# Configure logging
if not test:
    logging.basicConfig(
        filename='bot.log',  # Specify the log file
        level=logging.ERROR,  # Set the logging level to capture ERROR and above
        format='%(asctime)s - %(levelname)s - %(message)s',
    )


def register_routers(dp: Dispatcher) -> None:
    """Registers routers"""
    # Import routers from different modules
    from bot.modules.yt.youtube import ytrouter
    from bot.modules.tiktok.tiktok import ttrouter
    from bot.commands import cmdrouter
    from bot.modules.ChatGPT.chatgpt import gptrouter
    from bot.modules.images.image_generation import imgenrouter
    from bot.modules.audio.audio import avrouter
    from bot.modules.images.images_handler import imgrouter
    from bot.modules.images.text_recognition import txtrcgrouter
    from bot.settings import settings

    # Append routers with commands in a specific order
    dp.include_routers(imgenrouter, settings, cmdrouter, ytrouter, ttrouter, imgrouter, gptrouter,
                       avrouter, txtrcgrouter)


async def on_startup(bot: aiogram.Bot):
    # Start the scheduler and create database tables on bot startup
    scheduler.start()
    await db.create_tables()
    await chatgpt.update_providers()

    # Set webhook if not in test mode
    if not test:
        await bot.set_webhook(f"{BASE_WEBHOOK_URL}{WEBHOOK_PATH}")
    print(f"{datetime.datetime.now().strftime('(%Y-%m-%d)  %H:%M.%S')} >> Bot Started")


async def polling(dp, bot):
    # Start polling in test mode
    await dp.start_polling(bot)


def main(dp) -> None:
    # Register routers and set up startup logic
    register_routers(dp)
    dp.startup.register(on_startup)

    # Run polling or set up webhook based on test mode
    if test:
        asyncio.run(polling(dp, bot))
    else:
        print("Establishing WebHook")
        app = web.Application()

        # Set up webhook request handler
        webhook_request_handler = SimpleRequestHandler(
            dispatcher=dp,
            bot=bot
        )

        webhook_request_handler.register(app, path=WEBHOOK_PATH)

        # Set up application with webhook configuration
        setup_application(app, dp, bot=bot)

        # Run the web application
        web.run_app(
            app,
            host='0.0.0.0',
            port=8080
        )


if __name__ == "__main__":
    main(dp)
