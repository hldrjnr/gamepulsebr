import os
import logging
from datetime import datetime, timedelta

from telegram import Bot
from telegram.error import TelegramError

from src.database import get_db, cleanup_old
from src.templates import render_weekly_digest

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")

if not BOT_TOKEN or not CHANNEL_ID:
    raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID must be set")

bot = Bot(token=BOT_TOKEN)

async def post_weekly_digest():
    """Generate and post weekly digest."""
    cutoff = datetime.now() - timedelta(days=7)
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM posted_items WHERE posted_at > ? ORDER BY posted_at DESC",
            (cutoff.isoformat(),)
        )
        rows = cursor.fetchall()
    
    posts = [dict(row) for row in rows]
    
    if not posts:
        logger.info("No posts for weekly digest")
        return
    
    week_start = (datetime.now() - timedelta(days=7)).strftime("%d/%m")
    week_end = datetime.now().strftime("%d/%m")
    
    text = render_weekly_digest(posts, week_start, week_end)
    
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode=None,
            disable_web_page_preview=False
        )
        logger.info("Weekly digest posted successfully")
    except TelegramError as e:
        logger.error(f"Failed to post weekly digest: {e}")

async def main():
    await post_weekly_digest()
    cleanup_old(30)
    logger.info("Weekly digest job complete")

if __name__ == "__main__":
    import asyncio
    asyncio.run(main())