# images_handler.py

from aiogram import Router, flags, F
from bot_instance import bot
from aiogram.types import Message
from aiogram.utils.keyboard import InlineKeyboardBuilder
from bot.filters import CallBackTRdata
from aiogram.utils.i18n import gettext as _
from bot.middlewares import ObservedFieldRestrictionMiddleware
from aiogram.utils.chat_action import ChatActionMiddleware

# Create an instance of the Router for image handling
imgrouter = Router()

# Apply middlewares for image handling
imgrouter.message.outer_middleware(ObservedFieldRestrictionMiddleware())
imgrouter.message.middleware(ChatActionMiddleware())


# Define a handler for messages with photos
@flags.chat_action("typing")
@imgrouter.message(F.photo)
async def recognize_text(msg: Message):
    # Build an inline keyboard with a "Recognize text" button
    builder = InlineKeyboardBuilder()
    builder.button(text=_("Recognize text"), callback_data=CallBackTRdata(user_id=msg.from_user.id))

    # Send a message asking the user what they want to do with the image
    await bot.send_message(chat_id=msg.chat.id, text=_("What do you want to do with the image?"),
                           reply_to_message_id=msg.message_id,
                           reply_markup=builder.as_markup())
