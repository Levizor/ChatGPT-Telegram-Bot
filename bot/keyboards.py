from aiogram.utils.keyboard import InlineKeyboardBuilder, KeyboardBuilder
from bot.filters import CallBackSettingsData
from aiogram.utils.keyboard import InlineKeyboardButton
from aiogram.utils.i18n import gettext as _

langs = {'en': 'Eng',
         'uk': 'Укр',
         'ru': 'Рус'}


async def settings_keyboard(user_id: int):
    builder = InlineKeyboardBuilder()

    builder.button(text=_("GPT Provider"), callback_data=CallBackSettingsData(user_id=user_id, button="provider").pack())
    builder.button(text=_("Language"), callback_data=CallBackSettingsData(user_id=user_id, button="lan").pack())
    builder.row(
        InlineKeyboardButton(text=_("❌Delete"),
                             callback_data=CallBackSettingsData(user_id=user_id, button="delete").pack()))
    return builder.as_markup()


async def settings_lang_keyboard(user_id: int, current: str):
    builder = InlineKeyboardBuilder()

    for key in langs.keys():
        text = langs[key]
        if current == key:
            text = f"●{text}●"
        builder.button(text=text, callback_data=CallBackSettingsData(user_id=user_id, button=key).pack())

    builder.adjust(3)

    builder.row(
        InlineKeyboardButton(text=_("↩️Back"),
                             callback_data=CallBackSettingsData(user_id=user_id, button="set").pack()))

    return builder.as_markup()


async def settings_provider_keyboard(user_id: int, providers: dict, current: str):
    builder = InlineKeyboardBuilder()

    for provider in providers.keys():
        builder.button(text=provider if provider != current else f"●{provider}●",
                       callback_data=CallBackSettingsData(user_id=user_id, button=provider))

    builder.adjust(3)
    builder.row(
        InlineKeyboardButton(text=_("↩️Back"),
                             callback_data=CallBackSettingsData(user_id=user_id, button="set").pack()))

    return builder.as_markup()
