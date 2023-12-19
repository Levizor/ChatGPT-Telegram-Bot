# chatgpt.py
import asyncio
import logging

import g4f.models
import requests.exceptions
from aiogram import Router, F
from aiogram.types import Message
from aiogram.utils.chat_action import ChatActionMiddleware, ChatActionSender
from aiogram.utils.i18n import gettext as _
from g4f import ChatCompletion, Provider
from openai import AsyncOpenAI

from bot.middlewares import ChatGPTProvider
from bot.middlewares import DatabaseMiddleware, ObservedFieldRestrictionMiddleware
from bot_instance import bot
from config import OPEN_AI

logging.basicConfig(
    filename='chatgpt.log',  # Specify the log file
    level=logging.ERROR,  # Set the logging level to capture ERROR and above
    format='%(asctime)s - %(levelname)s - %(message)s',
)


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

        self.providers = {}

    async def update_providers(self):

        tasks=[self.check_provider(provider) for provider in Provider.__providers__ if provider.working]

        results = await asyncio.gather(*tasks)

        for provider, works in results:
            if works:
                self.providers[provider.__name__]= provider



    checking_list = [{"role": "user", "content": "Hi, reply shortly if you hear me."}]

    async def check_provider(self, provider: Provider):

        async def step():
            try:
                response = await self.make_request(self.checking_list, provider)
                print(f"Response of {provider.__name__} --> {response}")
            except Exception:
                return False
            return True if response!="" else False


        if await step() and await step():
            return provider, True
        return provider, False

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

    # Create ChatCompletion using the GPT model
    async def make_request(self, messages, provider: Provider):
        response = await ChatCompletion.create_async(
            model=g4f.models.gpt_35_turbo,
            messages=messages,
            provider=provider,
        )
        return response

    # Get response from ChatGPT
    async def get_response(self, user_id, text, provider: str):

        # Adding user's message to the message history
        history = await self.get_history(user_id)
        history.append({"role": "user", "content": text})
        response = None
        try:
            response = await self.make_request(history, self.providers[provider]) if provider in self.providers else "Sorry, your provider doesn't work now, choose another one"
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
        except Exception as e:
            print(e)
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
gptrouter.message.middleware(ChatGPTProvider("GeekGpt"))
gptrouter.message.middleware(DatabaseMiddleware(request_type="text_requests"))


# Define a handler for text messages
@gptrouter.message(F.text)
async def chat(msg: Message, provider: str):
    # Send a "Generating..." message
    mes = await bot.send_message(msg.chat.id, _("Generating..."), parse_mode="Markdown",
                                 reply_to_message_id=msg.message_id)
    async with ChatActionSender(bot=bot, chat_id=msg.chat.id):
        # Get response from ChatGPT

        try:
            response = await chatgpt.get_response(msg.from_user.id, msg.text, provider)
            # Delete the "Generating..." message and send the response
            await bot.delete_message(mes.chat.id, mes.message_id)
            await msg.answer(response, reply_to_message_id=msg.message_id)
        except Exception as e:

            # Handle exceptions, e.g., message too long
            if "MESSAGE_TOO_LONG" in str(e):
                await msg.answer(_("Sorry, the message was too long"), reply_to_message_id=msg.message_id)
            else:
                await msg.answer(_("Sorry, some problem occurred"), reply_to_message_id=msg.message_id)
