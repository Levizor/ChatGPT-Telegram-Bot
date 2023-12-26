# audio.py


import os

import aiogram.exceptions
import aiohttp
from aiogram import Router, types, flags, F
from aiogram.utils.chat_action import ChatActionMiddleware
from aiogram.utils.i18n import gettext as _

from bot.middlewares import DatabaseMiddleware, ObservedFieldRestrictionMiddleware
from bot_instance import bot
from config import EDEN_AI


# Define the VoiceRecognition class for handling audio recognition
class VoiceRecognition:
    def __init__(self, provider):
        # API URLs for audio recognition
        self.api_url = "https://api.edenai.run/v2/audio/speech_to_text_async"
        self.transcription_url = "https://api.edenai.run/v2/audio/speech_to_text_async/{public_id}"

        # Headers for API requests
        self.headers = {"Authorization": EDEN_AI}

        # Audio recognition provider
        self.provider = provider

    async def recognize(self, file_id):
        # Retrieve the file information from the bot
        file = await bot.get_file(file_id)

        # Download the audio file
        path = await self.download_file(file)

        # Get text from the audio file
        text = await self.get_text(path)

        # Remove the downloaded audio file
        os.remove(path)

        # If no text is recognized, return a message
        if text == '':
            return _("Couldn't recognize anything.")

        return text

    async def perform_async_post(self, audio_path):
        # Perform an asynchronous POST request to the audio recognition API
        async with aiohttp.ClientSession() as session:
            form_data = aiohttp.formdata.FormData()
            form_data.add_field('file', open(audio_path, 'rb'))
            form_data.add_field('providers', self.provider)

            async with session.post(self.api_url, data=form_data, headers=self.headers) as response:
                return await response.json()

    async def perform_async_get(self, url):
        # Perform an asynchronous GET request to the audio recognition API
        async with aiohttp.ClientSession() as session:
            async with session.get(url, headers=self.headers) as response:
                "GOT IT"
                return await response.json()

    @staticmethod
    async def download_file(file):
        # Download the audio file from the bot
        path = f"bot/modules/audio/cache/{file.file_id}.mp3"
        await bot.download_file(file.file_path, path)
        return path

    async def get_text(self, audio_path):
        # Get text from the audio file using the recognition API
        post = await self.perform_async_post(audio_path)
        transcription_url = self.transcription_url.format(public_id=post['public_id'])
        data = await self.perform_async_get(transcription_url)
        # Handle errors during transcription
        if data['error'] is not None:
            return _("Sorry, some problem occurred during transcription.")

        return data['results'][self.provider]['text']


# Create a Router instance for audio-related commands
avrouter = Router()

# Apply middlewares for audio handling
avrouter.message.outer_middleware(ObservedFieldRestrictionMiddleware())
avrouter.message.middleware(DatabaseMiddleware(request_type="audio_text_recognition_requests"))
avrouter.message.middleware(ChatActionMiddleware())

# Create an instance of the VoiceRecognition class
vr = VoiceRecognition(provider="openai")


# Define handlers for voice and audio messages
@flags.chat_action("typing")
@avrouter.message(F.voice)
async def voice_handler(msg: types.Message):
    text = await vr.recognize(msg.voice.file_id)
    try:
        await msg.answer(text, reply_to_message_id=msg.message_id)
    except aiogram.exceptions.TelegramBadRequest:
        parts = await split_text(text)
        for text in parts:
            await msg.answer(text, reply_to_message_id=msg.message_id)
@flags.chat_action("typing")
@avrouter.message(F.audio)
async def audio_handler(msg: types.Message):
    text = await vr.recognize(msg.audio.file_id)
    try:
        await msg.answer(text, reply_to_message_id=msg.message_id)
    except aiogram.exceptions.TelegramBadRequest:
        parts=await split_text(text)
        for text in parts:
            await msg.answer(text, reply_to_message_id=msg.message_id)


async def split_text(text:str) -> list:
    length=len(text)
    amount=int(length/4000)+(length%4000!=0)
    list=[]
    for i in range(amount):
        list.append(text[i*4000:(i+1)*4000])

    return list