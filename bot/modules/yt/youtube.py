# youtube.py


import os
import time
import asyncio
from pytube import YouTube
from aiogram.types import FSInputFile
from aiogram.utils.chat_action import ChatActionSender, ChatActionMiddleware
from aiogram import Router, types, flags, F
from bot_instance import bot
from aiogram.utils.keyboard import InlineKeyboardBuilder
from pydub import AudioSegment
from bot.middlewares import DatabaseMiddleware, ObservedFieldRestrictionMiddleware
from aiogram.utils.i18n import gettext as _
from bot.filters import CallBackYTdata


# Define the action for ChatActionSender based on whether it's audio or video
async def action(cd):
    return str("upload_audio") if cd.audio is True else str("upload_video")


# Function to convert a file to MP3 format
async def convert_to_mp3(path):
    audio = AudioSegment.from_file(path)
    os.remove(path)
    path = audio.export(path.split('.')[0] + '.mp3', format('mp3'), bitrate='128k')
    return path.name


# Function to send a video
async def send_video(path, chat_id):
    video = FSInputFile(path)
    await bot.send_video(chat_id=chat_id, video=video)
    os.remove(path)


# Function to send an audio file
async def send_audio(path, chat_id):
    audio = FSInputFile(path)
    await bot.send_audio(chat_id=chat_id, audio=audio)
    os.remove(path)


# Function to download a YouTube video
async def download(link, itag):
    yt = await asyncio.to_thread(YouTube, link, use_oauth=True, allow_oauth_cache=True)
    stream = yt.streams.get_by_itag(itag)
    path = await asyncio.to_thread(stream.download, output_path=f'bot/modules/yt/cache',
                                   filename_prefix=str(time.time()))
    return path


# Function to send options for video type and resolution
async def send_var(msg):
    link = msg.text
    text = _("Choose type/resolution")
    yt = await asyncio.to_thread(YouTube, link, use_oauth=False, allow_oauth_cache=True)

    builder = InlineKeyboardBuilder()
    tasks = []

    # Process video streams
    async def process_stream(stream):
        nonlocal builder
        if stream.filesize / (1024 * 1024) < 50:
            builder.button(
                text=stream.resolution,
                callback_data=CallBackYTdata(audio=False, itag=stream.itag, user_id=msg.from_user.id).pack()
            )

    for stream in yt.streams.filter(progressive=True, file_extension='mp4', type='video'):
        tasks.append(process_stream(stream))

    # Process audio stream
    async def process_audio_stream():
        nonlocal builder
        audio_stream = yt.streams.filter(type='audio').order_by('abr')[-1]
        text = _("Choose type/resolution")

        if audio_stream.filesize / (1024 * 1024) < 50:
            builder.button(
                text="mp3",
                callback_data=CallBackYTdata(audio=True, itag=audio_stream.itag, user_id=msg.from_user.id).pack()
            )
        else:
            text = _("Sorry, filesize of this video is greater than the limit (50 Mb)")

    tasks.append(process_audio_stream())

    await asyncio.gather(*tasks)

    await bot.send_message(
        chat_id=msg.chat.id,
        text=text,
        reply_to_message_id=msg.message_id,
        reply_markup=builder.as_markup()
    )


# Create an instance of the Router for YouTube handling
ytrouter = Router()
# Apply middlewares for YouTube handling
ytrouter.message.outer_middleware(ObservedFieldRestrictionMiddleware())
ytrouter.message.middleware(ChatActionMiddleware())
ytrouter.message.middleware(DatabaseMiddleware(request_type="yt_download_requests"))


# Define a handler for YouTube links
@ytrouter.message(F.text.regexp(r'^(https?\:\/\/)?(www\.)?(youtube\.com|youtu\.?be)\/.+'))
@flags.chat_action(initial_sleep=0, action="typing", interval=0)
async def yt_handler(msg: types.Message):
    await send_var(msg)


# Define a handler for YouTube callback queries
@ytrouter.callback_query(CallBackYTdata.filter())
@flags.chat_action(initial_sleep=0, action="upload_video", interval=0)
async def yt_cq(cq: types.CallbackQuery, callback_data: CallBackYTdata):
    async with ChatActionSender(bot=bot, chat_id=cq.message.chat.id,
                                action=await action(callback_data)):
        await bot.delete_message(chat_id=cq.message.chat.id, message_id=cq.message.message_id)

        path = await download(link=cq.message.reply_to_message.text, itag=callback_data.itag)
        if callback_data.audio:
            path = await convert_to_mp3(path)
            await send_audio(path, cq.message.chat.id)
        else:
            await send_video(path, cq.message.chat.id)
