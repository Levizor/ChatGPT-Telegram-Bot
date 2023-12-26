from aiogram import Dispatcher
from aiogram.utils.i18n import I18n, middleware

from bot.middlewares import CallbackGroupRestrictionMiddleware, ChatGPTProvider
from bot.modules.ChatGPT.chatgpt import chatgpt

dp = Dispatcher()

i18n = I18n(path="bot/locales", default_locale="en", domain="messages")
locales=i18n.locales
fsmi18n=middleware.FSMI18nMiddleware(i18n)

dp.message.middleware(ChatGPTProvider(chatgpt.providers))
dp.callback_query.middleware(ChatGPTProvider(chatgpt.providers))
dp.message.middleware(fsmi18n)
dp.callback_query.middleware(fsmi18n)
dp.callback_query.middleware(CallbackGroupRestrictionMiddleware())
