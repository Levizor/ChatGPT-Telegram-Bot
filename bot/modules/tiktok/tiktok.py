# tiktok.py


import os
import asyncio
from aiogram import Router, F
from aiogram.types import Message, FSInputFile
from bot_instance import bot
from bot.modules.tiktok.ttdownloader.downloader import TiktokDownloader
from bot.middlewares import DatabaseMiddleware, ObservedFieldRestrictionMiddleware
from aiogram.utils.chat_action import ChatActionSender
from aiogram.utils.i18n import gettext as _

# Create an instance of the Router for TikTok handling
ttrouter = Router()

# Apply middlewares for TikTok handling
ttrouter.message.outer_middleware(ObservedFieldRestrictionMiddleware())
ttrouter.message.middleware(DatabaseMiddleware(request_type='tt_download_requests'))


# Define a handler for TikTok links
@ttrouter.message(F.text.regexp(
    r'^.*https:\/\/(?:m|www|vm)?\.?tiktok\.com\/((?:.*\b(?:(?:usr|v|embed|user|video)\/|\?shareId=|\&item_id=)(\d+))|\w+)'))

async def tiktok_handler(msg: Message):
    # Send a message indicating that the video is being downloaded
    await_msg = await bot.send_message(msg.chat.id, _("Downloading the video..."),
                                       reply_to_message_id=msg.message_id)
    async with ChatActionSender(action="upload_video", bot=bot, chat_id=msg.chat.id):
        # Define the path to save the downloaded video
        path = 'bot/modules/tiktok/cache/' + msg.text.rsplit('/', 1)[-1] + ".mp4"

        # Download the TikTok video using Tiktok_downloader
        getvideo = await asyncio.to_thread(TiktokDownloader().musicaldown, url=msg.text, output_name=path)

        # Check if the video is downloaded successfully
        if getvideo and os.path.exists(path):
            # Send the downloaded video
            await bot.send_video(msg.chat.id, video=FSInputFile(path))

            os.remove(path)

            # Delete the initial downloading message
            await bot.delete_message(msg.chat.id, await_msg.message_id)
        else:
            # If there is an error, edit the message with an error text
            err_text = _("Couldn't download the video")
            await bot.edit_message_text(err_text, msg.chat.id, await_msg.message_id)
