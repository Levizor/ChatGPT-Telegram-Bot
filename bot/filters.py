# filters.py

from aiogram.filters.callback_data import CallbackData
from aiogram.filters import Filter
from aiogram.types import Message
from config import USERNAME


# Define CallbackData classes for handling callback data
class CallbackUser(CallbackData, prefix="id", sep="|"):
    user_id: int


class CallBackYTdata(CallbackUser, prefix="y", sep="|"):
    audio: bool
    itag: int


class CallBackTRdata(CallbackUser, prefix="tr", sep="|"):
    pass


class CallBackSettingsData(CallbackUser, prefix="set", sep="|"):
    button: str



# Define custom filters
class BotName(Filter):
    def __init__(self):
        self.name = USERNAME

    async def __call__(self, msg):
        # Check if the bot's username is mentioned in the message text or caption
        if msg.text:
            return True if self.name in msg.text else False
        elif msg.caption:
            return True if self.name in msg.caption else False


class CommandArgs(Filter):
    def __init__(self, condition: bool):
        self.condition = condition

    async def __call__(self, msg: Message):
        # Check if the message contains command arguments based on the condition
        return self.condition == await self.check_for_text(msg.text)

    @staticmethod
    async def check_for_text(text: str):
        # Check if the message text contains more than one word
        return True if len(text.split(" ")) > 1 else False

    @staticmethod
    async def remove_first_word(input_string):
        # Remove the first word from a given input string
        words = input_string.split()
        words.pop(0)
        result_string = ' '.join(words)

        return result_string
