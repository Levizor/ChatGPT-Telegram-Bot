# middlewares.py

from typing import Callable, Dict, Awaitable, Any
from typing import Optional

from aiogram import BaseMiddleware
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, CallbackQuery
from aiogram.utils.i18n import gettext as _

from bot_instance import get_bot_id
from database.database import db


class ChatGPTProvider(BaseMiddleware):
    def __init__(self, provider):
        self.key = 'provider'
        self.default_provider = provider

    async def __call__(
            self,
            handler: Callable[[Message, Dict[str, Any]], Awaitable[Any]],
            event: Message,
            data: Dict[str, Any]
    ) -> Any:
        fsm_context: Optional[FSMContext] = data.get("state")
        provider = None
        if fsm_context:
            fsm_data = await fsm_context.get_data()
            provider = fsm_data.get(self.key, None)
        if not provider:
            provider = self.default_provider
            if fsm_context:
                await fsm_context.update_data(data={self.key: provider})
        data.update(provider=provider)
        return await handler(event, data)


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

        if event.from_user.id == data['callback_data'].user_id:
            return await handler(event, data)

        bot = data.get('bot')
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
