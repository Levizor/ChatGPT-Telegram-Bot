# database.py
from datetime import datetime

import aiogram.types
import aiosqlite
from aiogram.types import Message


class BotDatabase:
    def __init__(self, database_name='database/database.db'):
        # Initialize BotDatabase with a default or provided database name
        self.database_name = database_name

    async def create_tables(self):
        # Create necessary tables if they don't exist in the database
        async with aiosqlite.connect(self.database_name) as db_conn:
            await db_conn.execute('''
                CREATE TABLE IF NOT EXISTS requests (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    date DATE,
                    user_id INTEGER,
                    request_type TEXT
                )
            ''')

            await db_conn.execute('''
                CREATE TABLE IF NOT EXISTS messages (
                    chat_id INTEGER,
                    message_id INTEGER,
                    date INTEGER,
                    text TEXT, 
                    PRIMARY KEY (chat_id, message_id)
                )
                ''')


            await db_conn.commit()

    async def get_message(self, chat: aiogram.types.Chat, message_id: int, user: aiogram.types.User) -> Message:
        async with aiosqlite.connect(self.database_name) as db_conn:
            row = await self.select_message(chat.id, message_id)

            if row:
                date, text = row
                return Message(message_id=message_id, date=date, text=text, chat=chat, from_user=user)

    async def select_message(self, chat_id, message_id):
        async with aiosqlite.connect(self.database_name) as db_conn:
            cursor = await db_conn.execute('SELECT date, text FROM messages WHERE chat_id=? AND message_id=?',
                                           (chat_id, message_id))

            return await cursor.fetchone()

    async def log_message(self, msg: Message) -> None:
        if await self.select_message(msg.chat.id, msg.message_id):
            return
        async with aiosqlite.connect(self.database_name) as db_conn:
            await db_conn.execute('INSERT INTO messages (chat_id, message_id, date, text) VALUES (?, ?, ?, ?)',
                                  (msg.chat.id, msg.message_id, msg.date, msg.text))
            await db_conn.commit()

    async def log_request(self, user_id, request_type):
        # Log user requests with the current date
        current_date = datetime.now().date()
        async with aiosqlite.connect(self.database_name) as db_conn:
            await db_conn.execute('INSERT INTO requests (date, user_id, request_type) VALUES (?, ?, ?)',
                                  (current_date, user_id, request_type))
            await db_conn.commit()

    async def get_total_requests(self, date=None):
        # Get the total number of requests for a specific date
        async with aiosqlite.connect(self.database_name) as db_conn:
            if date is None:
                date = datetime.now().date()
            cursor = await db_conn.execute('SELECT COUNT(*) FROM requests WHERE date = ?', (date,))
            return (await cursor.fetchone())[0]

    async def get_total_requests_by_type(self, request_type, date=None):
        # Get the total number of requests for a specific type and date
        async with aiosqlite.connect(self.database_name) as db_conn:
            if date is None:
                date = datetime.now().date()
            cursor = await db_conn.execute('SELECT COUNT(*) FROM requests WHERE request_type = ? AND date = ?',
                                           (request_type, date))
            return (await cursor.fetchone())[0]

    async def get_total_unique_users(self):
        # Get the total number of unique users
        async with aiosqlite.connect(self.database_name) as db_conn:
            cursor = await db_conn.execute('SELECT COUNT(DISTINCT user_id) FROM requests')
            users = await cursor.fetchall()
            return users[0][0]

    async def clear_table_data(self, table_name: str):
        async with aiosqlite.connect(self.database_name) as db_conn:
            await db_conn.execute('DELETE FROM ?', table_name)


    async def get_statistics(self, date=None):
        # Get statistics for a specific date or the current date
        if date is None:
            current_date = datetime.now().date()
        else:
            current_date = datetime.strptime(date, '%Y-%m-%d').date()

        # Retrieve various statistics from the database
        async with aiosqlite.connect(self.database_name) as db_conn:
            cursor = await db_conn.execute('SELECT COUNT(DISTINCT user_id) FROM requests WHERE date = ?',
                                           (current_date,))
            unique_users_today = (await cursor.fetchone())[0]
            unique_users = await self.get_total_unique_users()
            cursor = await db_conn.execute('SELECT COUNT(*) FROM requests WHERE date = ?', (current_date,))
            total_requests = (await cursor.fetchone())[0]

            text_requests = await self.get_total_requests_by_type("text_requests", current_date)
            img_generation_requests = await self.get_total_requests_by_type("img_generation_requests", current_date)
            audio_recognition_requests = await self.get_total_requests_by_type("audio_text_recognition_requests",
                                                                               current_date)
            yt_download_requests = await self.get_total_requests_by_type("yt_download_requests", current_date)
            tt_download_requests = await self.get_total_requests_by_type("tt_download_requests", current_date)
            image_text_recognition_requests = await self.get_total_requests_by_type("image_text_recognition_requests",
                                                                                    current_date)

        # Construct and return the statistics string
        statistics = f"📊 Statistics"
        if date:
            statistics += f" for {current_date}"
        else:
            statistics += f" for {current_date}"
        statistics += " 📊\n\n"
        statistics += f"👥 Unique Users Today: {unique_users_today}\n"
        statistics += f"📈 Total amount of unique users: {unique_users}\n"
        statistics += f"📥 Total Requests: {total_requests}\n\n"
        statistics += f"📝 Text Requests: {text_requests}\n"
        statistics += f"🖼 Img Generation Requests: {img_generation_requests}\n"
        statistics += f"📖 Image Text Recognition Requests: {image_text_recognition_requests}\n"
        statistics += f"🔉 Audio Text Recognition Requests: {audio_recognition_requests}\n"
        statistics += f"🎵 YouTube Download Requests: {yt_download_requests}\n"
        statistics += f"📹 TikTok Download Requests: {tt_download_requests}\n"

        return statistics

db = BotDatabase()
