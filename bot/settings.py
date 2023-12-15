from aiogram import Router
from aiogram.types import CallbackQuery
from bot_instance import bot
from bot.filters import CallBackSettingsData
from aiogram import F
from aiogram.utils.i18n import gettext as _
from dispatcher_instance import fsmi18n
from dispatcher_instance import locales
import bot.keyboards as kb
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from aiogram.filters.command import Command
from bot.modules.ChatGPT.chatgpt import chatgpt

settings = Router()


@settings.message(Command('settings'))
async def send_settings(msg: Message) -> None:
    await bot.send_message(msg.chat.id, _("Settings⚙️"), reply_markup=await kb.settings_keyboard(msg.from_user.id))


@settings.callback_query(CallBackSettingsData.filter(F.button == 'set'))
async def send_back_settings(cq: CallbackQuery):
    await bot.edit_message_text(chat_id=cq.message.chat.id, message_id=cq.message.message_id, text=_("Settings⚙️"),
                                reply_markup=await kb.settings_keyboard(cq.from_user.id))


@settings.callback_query(CallBackSettingsData.filter(F.button == "provider"))
async def send_provider(cq: CallbackQuery, provider: str):
    await bot.edit_message_text(
        message_id=cq.message.message_id,
        chat_id=cq.message.chat.id,
        text=_("Choose your GPT provider. By default AiChatOnline is enabled."),
        reply_markup=await kb.settings_provider_keyboard(cq.from_user.id, chatgpt.providers, current=provider)
    )


@settings.callback_query(CallBackSettingsData.filter(F.button.in_(chatgpt.providers)))
async def change_provider(cq: CallbackQuery, state: FSMContext, callback_data: CallBackSettingsData, provider: str):
    if provider == callback_data.button:
        await cq.answer(_("You chose the same provider."))
        return
    await state.update_data(provider=callback_data.button)
    await cq.answer(_("Provider was changed"))
    await send_provider(cq, callback_data.button)


@settings.callback_query(CallBackSettingsData.filter(F.button == "lan"))
async def send_language(cq: CallbackQuery, state: FSMContext):
    await state.update_data(first="lan")
    await bot.edit_message_text(
        message_id=cq.message.message_id, chat_id=cq.message.chat.id,
        text=(_("Choose your language:")),
        reply_markup=await kb.settings_lang_keyboard(cq.from_user.id,
                                                     current=(await state.get_data())['locale'])
    )


@settings.callback_query(CallBackSettingsData.filter(F.button.in_(locales)))
async def change_language(cq: CallbackQuery, state: FSMContext, callback_data: CallBackSettingsData):
    if (await state.get_data())['locale'] == callback_data.button:
        await cq.answer(_("You chose the same language"))
        return
    await fsmi18n.set_locale(state=state, locale=callback_data.button)
    await cq.answer(_("Language have been changed."))
    await send_language(cq, state)


@settings.callback_query(CallBackSettingsData.filter(F.button == "delete"))
async def settings_delete(cq: CallbackQuery):
    await cq.answer(_("Settings were deleted."))
    await bot.delete_message(cq.message.chat.id, cq.message.message_id)
