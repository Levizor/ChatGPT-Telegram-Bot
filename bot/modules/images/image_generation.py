# image_generation.py


from aiogram import Router, flags
from aiogram.types import Message
from bot.middlewares import DatabaseMiddleware
from aiogram.utils.chat_action import ChatActionMiddleware
from bot_instance import bot
import aiohttp
from config import EDEN_AI
from aiogram.utils.i18n import gettext as _
from bot.commands import CommandArgs
from aiogram.filters import Command


# Define a function to generate an image using the specified prompt
async def generate_image(prompt):
    headers = {"Authorization": EDEN_AI}
    url = "https://api.edenai.run/v2/image/generation"
    payload = {
        "providers": "replicate",
        "text": prompt,
        "resolution": "1024x1024"
    }

    async with aiohttp.ClientSession() as session:
        async with session.post(url, json=payload, headers=headers) as response:
            result = await response.json()

    return result[payload["providers"]]['items'][0]['image_resource_url']


# Create an instance of the Router for image generation
imgenrouter = Router()

# Apply middlewares for image generation
imgenrouter.message.middleware(ChatActionMiddleware())
imgenrouter.message.middleware(DatabaseMiddleware("img_generation_requests"))


# Define a command handler for generating images with prompts
@imgenrouter.message(Command('draw'), CommandArgs(True))
@flags.chat_action("upload_photo")
async def cmd_generate(msg: Message):
    try:
        # Generate an image using the specified prompt and send it as a photo
        url = await generate_image(await CommandArgs.remove_first_word(msg.text))
        await bot.send_photo(chat_id=msg.chat.id, photo=url, reply_to_message_id=msg.message_id)
    except Exception:
        # Handle errors and inform the user
        await msg.answer(_("Sorry, some problem occurred"))


# Define a command handler for generating images with a reply prompt
@imgenrouter.message(Command('draw'), CommandArgs(False))
@flags.chat_action("upload_photo")
async def cmd_reply_generate(msg: Message):
    if msg.reply_to_message and msg.reply_to_message.text:
        try:
            # Generate an image using the reply prompt and send it as a photo
            url = await generate_image(msg.reply_to_message.text)
            await bot.send_photo(chat_id=msg.chat.id, photo=url, reply_to_message_id=msg.message_id)
        except Exception:
            # Handle errors and inform the user
            await msg.answer(_("Sorry, some problem occurred"))
    else:
        # Inform the user to provide a prompt
        await msg.answer(
            _("Please, provide a prompt. Add it after the command or just reply with this command to the prompt."),
            reply_to_message_id=msg.message_id)
