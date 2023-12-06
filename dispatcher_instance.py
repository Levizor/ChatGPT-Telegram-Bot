from aiogram import Dispatcher
from aiogram.utils.i18n import I18n, middleware
from bot.middlewares import CallbackGroupRestrictionMiddleware

dp = Dispatcher()

i18n = I18n(path="bot/locales", default_locale="en", domain="messages")
dp.message.middleware(middleware.SimpleI18nMiddleware(i18n))
dp.callback_query.middleware(middleware.SimpleI18nMiddleware(i18n))
dp.callback_query.middleware(CallbackGroupRestrictionMiddleware())
