# scheduled.py


from config import admin_ids
from bot_instance import bot
from database.database import db
from apscheduler.schedulers.asyncio import AsyncIOScheduler

# Define an asynchronous function to send statistics
async def send_stats():
    # Retrieve statistics from the database
    statistic = await db.get_statistics()

    # Send statistics to each admin user
    for user_id in admin_ids:
        await bot.send_message(user_id, statistic)


scheduler = AsyncIOScheduler()

# Schedule the send_stats function to run daily at 23:59
scheduler.add_job(send_stats, 'cron', hour=23, minute=59)
