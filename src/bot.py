import os
import logging
from typing import List, Dict, Any
from datetime import datetime

from telegram import Bot
from telegram.error import TelegramError, RetryAfter
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.database import mark_posted, cleanup_old, get_recent_count
from src.templates import render_post, render_weekly_digest
from src.fetchers.steamdb import fetch_steamdb_releases, fetch_steamdb_updates, fetch_steamdb_free, fetch_steamdb_demos
from src.fetchers.freebies import fetch_epic_free, fetch_gog_free, fetch_prime_gaming, fetch_itch_free
from src.fetchers.sales import fetch_cheapshark_sales, fetch_nuuvem_sales
from src.fetchers.news import fetch_gaming_news
from src.fetchers.emulation import fetch_emulation_releases, fetch_pcgamingwiki_updates
from src.fetchers.mods import fetch_mods
from src.fetchers.hardware import fetch_hardware_news
from src.fetchers.repacks import fetch_repack_announcements

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID")  # e.g., "@gamepulse_br"

if not BOT_TOKEN or not CHANNEL_ID:
    raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID must be set")

bot = Bot(token=BOT_TOKEN)

# Rate limiting: max 30 messages per minute, but we'll be conservative
MAX_POSTS_PER_RUN = 10
MIN_INTERVAL_SECONDS = 3

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((RetryAfter, TelegramError))
)
async def send_message(text: str) -> bool:
    """Send message to Telegram channel with retry logic."""
    try:
        await bot.send_message(
            chat_id=CHANNEL_ID,
            text=text,
            parse_mode=None,  # Plain text, no markdown parsing issues
            disable_web_page_preview=False
        )
        return True
    except RetryAfter as e:
        logger.warning(f"Rate limited, waiting {e.retry_after}s")
        raise
    except TelegramError as e:
        logger.error(f"Telegram error: {e}")
        raise

async def post_items(items: List[Dict[str, Any]], max_posts: int = MAX_POSTS_PER_RUN) -> int:
    """Post items to channel with rate limiting."""
    posted = 0
    
    for item in items[:max_posts]:
        try:
            text = render_post(item)
            await send_message(text)
            
            # Mark as posted in database
            from src.database import make_item_id
            item_id = make_item_id(item["source"], item["url"], item["title"])
            mark_posted(item_id, item["category"], item["title"], item["url"], item["source"])
            
            logger.info(f"Posted: [{item['category']}] {item['title'][:50]}")
            posted += 1
            
            # Small delay between posts
            import asyncio
            await asyncio.sleep(MIN_INTERVAL_SECONDS)
            
        except Exception as e:
            logger.error(f"Failed to post {item.get('title', 'unknown')}: {e}")
    
    return posted

async def run_fetcher_job(job_name: str, fetcher_func, max_posts: int = MAX_POSTS_PER_RUN):
    """Run a fetcher job and post results."""
    logger.info(f"Starting job: {job_name}")
    try:
        items = fetcher_func()
        if items:
            count = await post_items(items, max_posts)
            logger.info(f"Job {job_name}: posted {count}/{len(items)} items")
        else:
            logger.info(f"Job {job_name}: no new items")
    except Exception as e:
        logger.error(f"Job {job_name} failed: {e}")

async def run_all_jobs():
    """Run all fetcher jobs in sequence."""
    logger.info("=== Starting GamePulse bot run ===")
    
    jobs = [
        ("steamdb_releases", fetch_steamdb_releases, 5),
        ("steamdb_updates", fetch_steamdb_updates, 3),
        ("steamdb_free", fetch_steamdb_free, 5),
        ("steamdb_demos", fetch_steamdb_demos, 3),
        ("epic_free", fetch_epic_free, 3),
        ("gog_free", fetch_gog_free, 2),
        ("prime_gaming", fetch_prime_gaming, 2),
        ("itch_free", fetch_itch_free, 3),
        ("cheapshark_sales", fetch_cheapshark_sales, 5),
        ("nuuvem_sales", fetch_nuuvem_sales, 3),
        ("gaming_news", fetch_gaming_news, 5),
        ("emulation_releases", fetch_emulation_releases, 3),
        ("pcgamingwiki", fetch_pcgamingwiki_updates, 2),
        ("mods", fetch_mods, 3),
        ("hardware", fetch_hardware_news, 3),
        ("repacks", fetch_repack_announcements, 2),
    ]
    
    total_posted = 0
    for job_name, fetcher, max_posts in jobs:
        await run_fetcher_job(job_name, fetcher, max_posts)
        total_posted += get_recent_count(hours=1)  # Approximate
    
    # Cleanup old entries
    cleanup_old(30)
    
    logger.info(f"=== Run complete. Total posted this hour: ~{total_posted} ===")

async def post_weekly_digest():
    """Generate and post weekly digest."""
    from src.database import get_db
    from datetime import timedelta
    
    cutoff = datetime.now() - timedelta(days=7)
    with get_db() as conn:
        cursor = conn.execute(
            "SELECT * FROM posted_items WHERE posted_at > ? ORDER BY posted_at DESC",
            (cutoff.isoformat(),)
        )
        rows = cursor.fetchall()
    
    posts = [dict(row) for row in rows]
    
    week_start = (datetime.now() - timedelta(days=7)).strftime("%d/%m")
    week_end = datetime.now().strftime("%d/%m")
    
    text = render_weekly_digest(posts, week_start, week_end)
    await send_message(text)
    logger.info("Weekly digest posted")

if __name__ == "__main__":
    import asyncio
    asyncio.run(run_all_jobs())