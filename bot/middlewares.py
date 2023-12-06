# middlewares.py

from aiogram import BaseMiddleware
from aiogram.types import Message, CallbackQuery
from typing import Callable, Dict, Awaitable, Any
from database.database import db
from bot_instance import get_bot_id
from bot_instance import bot
from aiogram.utils.i18n import gettext as _


class ObservedFieldRestrictionMiddleware(BaseMiddleware):
    # Middleware for handling events in groups
    # It checks conditions for routers to handle the event
    # Do not use this middleware for routers with commands,
    # as it may make commands invisible in group chats.

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        if event.chat.type == "private":
            return await handler(event, data)
        elif event.reply_to_message and event.reply_to_message.from_user.id == await get_bot_id() or hasattr(event,
                                                                                                             "COMMAND"):
            return await handler(event, data)


class CallbackGroupRestrictionMiddleware(BaseMiddleware):
    # Middleware for restricting users from pressing buttons
    # under the bot's responses to other users in group chats.

    async def __call__(
            self,
            handler: Callable[[CallbackQuery, Dict[str, Any]], Awaitable[Any]],
            event: CallbackQuery,
            data: Dict[str, Any]
    ) -> Any:
        if event.message.chat.type == "private":
            return await handler(event, data)
        else:
            if event.from_user.id == data['callback_data'].user_id:
                return await handler(event, data)
            else:
                await bot.answer_callback_query(callback_query_id=event.id, text=_("This is not your request"))


class DatabaseMiddleware(BaseMiddleware):
    # Middleware for recording database entries
    def __init__(self, request_type) -> None:
        self.request_type = request_type

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        await db.log_request(user_id=event.from_user.id, request_type=self.request_type)
        return await handler(event, data)
