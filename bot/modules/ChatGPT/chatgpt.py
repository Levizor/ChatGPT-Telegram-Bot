# chatgpt.py

import g4f.models
import requests.exceptions
from openai import AsyncOpenAI
from aiogram import Router, F
from aiogram.types import Message
from bot.middlewares import DatabaseMiddleware, ObservedFieldRestrictionMiddleware
from config import OPEN_AI
from bot_instance import bot
from aiogram.utils.chat_action import ChatActionMiddleware, ChatActionSender
from g4f import ChatCompletion, Provider
from aiogram.utils.i18n import gettext as _
from main import logging

# Define the ChatGPT class for handling chat responses
class ChatGPT:
    def __init__(self):
        # Initialize message history and initial settings
        self.message_history = {}
        self.initial_settings = {"role": "system",
                                 "content": "You are a kind and sensible assistant. "
                                            "You must answer the questions with the language which user speaks."}
        # Initialize AsyncOpenAI instance
        self.openai = AsyncOpenAI(api_key=OPEN_AI)

    # Get or initialize user message history
    async def get_history(self, user_id):
        if user_id not in self.message_history:
            self.message_history[user_id] = [self.initial_settings]
        return self.message_history[user_id]

    # Erase user message history
    async def erase_history(self, user_id):
        if user_id in self.message_history:
            self.message_history[user_id] = [self.initial_settings]
            return True
        else:
            return False

    # Add response to message history
    async def add_response(self, user_id, message):
        history = await self.get_history(user_id)
        history.append(message)

    # Get response from ChatGPT
    async def get_response(self, user_id, text):
        # Adding user's message to the message history
        history = await self.get_history(user_id)
        history.append({"role": "user", "content": text})
        response = "0 content"
        try:
            # Create ChatCompletion using the GPT model
            response = await ChatCompletion.create_async(
                model=g4f.models.gpt_35_turbo,
                messages=history,
                provider=Provider.GeekGpt,
            )
            # Check for incomplete code blocks and fix them
            if "```" in response and response.count("```") % 2 != 0:
                response += "```"
        except requests.exceptions.HTTPError as e:
            # Handle HTTP errors from the GPT model
            if e.response.status_code == 401:
                response = await self.get_response(user_id, text)
            elif e.response.status_code == 429:
                response = _("Too many requests. Please be patient and retry a little later.")
            else:
                response = _("Sorry, your message wasn't handled properly. Please retry or try to clear your history.")
                logging.error(f"Exception occurred: {str(e)}")
        finally:
            # Add assistant's response to the message history
            history.append({'role': "assistant", 'content': response})
            return response


# Create an instance of the ChatGPT class
chatgpt = ChatGPT()
gptrouter = Router()

# Apply middlewares for chat handling
gptrouter.message.middleware(ObservedFieldRestrictionMiddleware())
gptrouter.message.middleware(ChatActionMiddleware())
gptrouter.message.middleware(DatabaseMiddleware(request_type="text_requests"))


# Define a handler for text messages
@gptrouter.message(F.text)
async def chat(msg: Message):
    # Send a "Generating..." message
    mes = await bot.send_message(msg.chat.id, _("Generating..."), parse_mode="Markdown",
                                 reply_to_message_id=msg.message_id)
    async with ChatActionSender(bot=bot, chat_id=msg.chat.id):
        # Get response from ChatGPT
        response = await chatgpt.get_response(msg.from_user.id, msg.text)

        try:
            # Delete the "Generating..." message and send the response
            await bot.delete_message(mes.chat.id, mes.message_id)
            await msg.answer(response, reply_to_message_id=msg.message_id)
        except Exception as e:
            # Handle exceptions, e.g., message too long
            if "MESSAGE_TOO_LONG" in str(e):
                await msg.answer(_("Sorry, the message was too long"), reply_to_message_id=msg.message_id)
            else:
                await msg.answer(_("Sorry, some problem occurred"), reply_to_message_id=msg.message_id)
