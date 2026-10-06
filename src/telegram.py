# Telegram bot client with rate limiting and retry logic

import os
import logging
import asyncio
from typing import Optional
from telegram import Bot
from telegram.error import TelegramError, RetryAfter
from tenacity import retry, stop_after_attempt, wait_exponential, retry_if_exception_type

from src.config import TELEGRAM_BOT_TOKEN, TELEGRAM_CHANNEL_ID, MIN_INTERVAL_SECONDS

logger = logging.getLogger(__name__)

if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHANNEL_ID:
    raise ValueError("TELEGRAM_BOT_TOKEN and TELEGRAM_CHANNEL_ID must be set")

bot = Bot(token=TELEGRAM_BOT_TOKEN)

_last_post_time = 0

@retry(
    wait=wait_exponential(multiplier=1, min=2, max=60),
    stop=stop_after_attempt(3),
    retry=retry_if_exception_type((RetryAfter, TelegramError))
)
async def send_message(text: str) -> bool:
    """Send message to Telegram channel with rate limiting and retry logic."""
    global _last_post_time
    
    # Rate limiting
    elapsed = asyncio.get_event_loop().time() - _last_post_time
    if elapsed < MIN_INTERVAL_SECONDS:
        await asyncio.sleep(MIN_INTERVAL_SECONDS - elapsed)
    
    try:
        await bot.send_message(
            chat_id=TELEGRAM_CHANNEL_ID,
            text=text,
            parse_mode=None,
            disable_web_page_preview=False
        )
        _last_post_time = asyncio.get_event_loop().time()
        return True
    except RetryAfter as e:
        logger.warning(f"Rate limited, waiting {e.retry_after}s")
        await asyncio.sleep(e.retry_after)
        raise
    except TelegramError as e:
        logger.error(f"Telegram error: {e}")
        raise

async def send_messages(texts: list) -> int:
    """Send multiple messages with rate limiting."""
    sent = 0
    for text in texts:
        try:
            await send_message(text)
            sent += 1
        except Exception as e:
            logger.error(f"Failed to send message: {e}")
    return sent