# text_recognition.py


import os
import aiohttp
from aiogram import Router, flags
from aiogram.types import CallbackQuery
from bot.middlewares import DatabaseMiddleware
from aiogram.utils.chat_action import ChatActionMiddleware
from bot.modules.images.images_handler import CallBackTRdata
from bot_instance import bot
from config import EDEN_AI
from aiogram.utils.i18n import gettext as _


# Define a class for text recognition
class TextRecognition:
    def __init__(self, provider):
        self.api_url = "https://api.edenai.run/v2/ocr/ocr"
        self.headers = {"Authorization": EDEN_AI}
        self.provider = provider

    async def recognize(self, file_id):
        file = await bot.get_file(file_id)
        path = await self.download_file(file)
        text = await self.get_text(path)
        if text == '':
            return _("Couldn't recognize anything.")
        return text

    async def perform_async_post(self, img_path):
        async with aiohttp.ClientSession() as session:
            form_data = aiohttp.formdata.FormData()
            form_data.add_field('file', open(img_path, 'rb'))
            form_data.add_field('providers', self.provider)

            async with session.post(self.api_url, data=form_data, headers=self.headers) as response:
                return await response.json()

    async def perform_async_get(self, url):
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                return await response.json()

    @staticmethod
    async def download_file(file):
        path = f"bot/modules/images/cache/{file.file_id}.png"
        await bot.download_file(file.file_path, path)

        return path

    async def get_text(self, img_path):
        post = await self.perform_async_post(img_path)
        data = post[self.provider]
        os.remove(img_path)

        if 'error' in data:
            return _("Sorry, some problem occurred during recognition.")

        return data['text']


# Create an instance of the Router for text recognition
txtrcgrouter = Router()

# Apply middlewares for text recognition
txtrcgrouter.message.middleware(ChatActionMiddleware())
txtrcgrouter.message.middleware(DatabaseMiddleware(request_type="image_text_recognition_requests"))
tr = TextRecognition(provider="google")


# Define a callback query handler for text recognition
@flags.chat_action("typing")
@txtrcgrouter.callback_query(CallBackTRdata.filter())
async def tr_cq(cq: CallbackQuery):
    msg = cq.message.reply_to_message
    text = await tr.recognize(msg.photo[len(msg.photo) - 1].file_id)

    await bot.edit_message_text(chat_id=cq.message.chat.id, message_id=cq.message.message_id, text=text,
                                parse_mode=None)
