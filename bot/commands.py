# commands.py
import aiogram.fsm.context
from aiogram.filters import Command, or_f, CommandStart
from aiogram import Router, types, F, flags
from aiogram.types.message import Message
from bot.keyboards import settings_keyboard
from config import admin_ids
from aiogram.utils.i18n import gettext as _
from dispatcher_instance import dp
from bot_instance import bot
from bot.modules.ChatGPT.chatgpt import chatgpt
from database.database import db
from bot.filters import BotName, CommandArgs, CallBackSettingsData

# Create a Router instance for commands
cmdrouter = Router()


# Define command handlers using the cmdrouter
@cmdrouter.message(F.text, or_f(Command('call'), BotName()), CommandArgs(False))
async def cmd_call(msg: Message, state:aiogram.fsm.context.FSMContext):
    # Handle 'call' command with a reply
    if msg.reply_to_message:
        message = msg.reply_to_message.model_copy(update={"COMMAND": True, "from_user": msg.from_user})
        await dp.feed_raw_update(bot=bot, update={"update_id": 2, "message": message})
    else:
        await msg.answer(_("At your service."), reply_to_message_id=msg.message_id)


@cmdrouter.message(F.text, or_f(Command('call'), BotName()), CommandArgs(True))
async def direct_gpt_call_request(msg: Message):
    # Handle 'call' command with direct GPT request
    message = msg.model_copy(update={"COMMAND": True, "text": await CommandArgs.remove_first_word(msg.text)})
    await dp.feed_raw_update(bot=bot, update={"update_id": 1, "message": message})


@cmdrouter.message(F.caption_entities, or_f(Command('call'), BotName()))
async def cmd_caption_call(msg: Message):
    # Handle 'call' command with caption
    message = msg.model_copy(update={"COMMAND": True, "caption": None, "from_user": msg.from_user})
    await dp.feed_raw_update(bot=bot, update={"update_id": 3, "message": message})


@cmdrouter.message(Command('clear'), CommandArgs(False))
async def clear_history(msg: Message):
    # Handle 'clear' command to erase chat history with assistant
    cond = await chatgpt.erase_history(msg.from_user.id)
    if cond:
        await msg.answer(_("Your chat history with assistant was erased."), reply_to_message_id=msg.message_id)
    else:
        await msg.answer(_("You have no chat history with assistant to erase."), reply_to_message_id=msg.message_id)


@cmdrouter.message(CommandStart())
async def cmd_start(msg: types.Message) -> None:
    # Handle 'start' command
    await msg.answer(_("Hello *{0}*!").format(msg.from_user.first_name), parse_mode="Markdown")
    await cmd_help(msg)


@cmdrouter.message(Command('help'))
async def cmd_help(msg: Message) -> None:
    # Handle 'help' command
    await msg.answer(_("help_message"))


@cmdrouter.message(Command('stats'), F.from_user.id.in_(admin_ids))
@flags.chat_action("typing")
async def cmd_stats(msg: Message) -> None:
    # Handle 'stats' command for admin users
    date_arg = msg.text[len("/stats "):].strip()
    statistics = "NO DATA"
    if date_arg:
        statistics = await db.get_statistics(date_arg)
    else:
        statistics = await db.get_statistics()
    await msg.answer(statistics)

