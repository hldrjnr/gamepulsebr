# Main entry point - orchestrates fetching, filtering, normalizing, and posting

import asyncio
import logging
import sys
from datetime import datetime
from typing import Dict, List, Set, Callable

from src.config import (
    HOURLY_CATEGORIES, DAILY_CATEGORIES, WEEKLY_CATEGORIES,
    MAX_POSTS_PER_CATEGORY, MAX_TOTAL_POSTS_PER_RUN, MIN_INTERVAL_SECONDS
)
from src.database import is_posted, mark_posted, make_item_id, cleanup_old, get_recent_posts, log_run
from src.telegram import send_messages
from src.normalize import normalize_item, filter_relevant
from src.formatter import render_post, render_weekly_digest

# Category fetcher functions
CATEGORY_FETCHERS: Dict[str, Callable[[], List[Dict]]] = {}

def register_fetchers():
    """Import and register all category fetchers."""
    global CATEGORY_FETCHERS
    
    from src.categories.freebies import fetch_freebies
    from src.categories.releases import fetch_releases, fetch_demos, fetch_updates
    from src.categories.news import fetch_news
    from src.categories.sales import fetch_sales
    from src.categories.mods import fetch_mods_category
    from src.categories.emulation import fetch_emulation
    from src.categories.ports import fetch_ports
    from src.categories.repacks import fetch_repacks
    from src.categories.hardware import fetch_hardware
    
    CATEGORY_FETCHERS = {
        "freebies": fetch_freebies,
        "releases": fetch_releases,
        "demos": fetch_demos,
        "updates": fetch_updates,
        "news": fetch_news,
        "sales": fetch_sales,
        "mods": fetch_mods_category,
        "emulation": fetch_emulation,
        "ports": fetch_ports,
        "repacks": fetch_repacks,
        "hardware": fetch_hardware,
    }

def get_categories_for_run(run_type: str) -> Set[str]:
    """Get categories to run based on run type."""
    if run_type == "hourly":
        return HOURLY_CATEGORIES
    elif run_type == "daily":
        return DAILY_CATEGORIES
    elif run_type == "weekly":
        return WEEKLY_CATEGORIES
    else:
        return set()

async def process_category(category: str, run_type: str) -> int:
    """Process a single category: fetch, filter, normalize, deduplicate, post."""
    if category not in CATEGORY_FETCHERS:
        logging.warning(f"No fetcher for category: {category}")
        return 0
    
    fetcher = CATEGORY_FETCHERS[category]
    logging.info(f"[{run_type}] Fetching {category}...")
    
    try:
        raw_items = fetcher()
    except Exception as e:
        logging.error(f"[{run_type}] Fetcher error for {category}: {e}")
        log_run(run_type, category, error=str(e))
        return 0
    
    if not raw_items:
        log_run(run_type, category, items_found=0, items_posted=0)
        return 0
    
    # Normalize and filter
    processed = []
    for raw in raw_items:
        try:
            normalized = normalize_item(raw, category)
            if filter_relevant(normalized, category):
                processed.append(normalized)
        except Exception as e:
            logging.warning(f"Failed to normalize item: {e}")
    
    logging.info(f"[{run_type}] {category}: RAW={len(raw_items)} RELEVANT={len(processed)}")
    
    # Deduplicate and prepare for posting
    to_post = []
    for item in processed:
        item_id = make_item_id(item["source"], item["url"], item["title"])
        if not is_posted(item_id):
            to_post.append((item_id, item))
    
    logging.info(f"[{run_type}] {category}: NEW={len(to_post)} (after dedup)")
    
    # Limit per category
    to_post = to_post[:MAX_POSTS_PER_CATEGORY]
    
    if not to_post:
        log_run(run_type, category, items_found=len(raw_items), items_posted=0)
        logging.info(f"[{run_type}] {category}: SKIP (nothing new to post)")
        return 0
    
    # Render posts
    texts = [render_post(item) for _, item in to_post]
    
    # Send to Telegram
    sent = await send_messages(texts)
    
    # Mark as posted
    for item_id, item in to_post[:sent]:
        mark_posted(item_id, category, item["title"], item["url"], item["source"])
    
    log_run(run_type, category, items_found=len(raw_items), items_posted=sent)
    logging.info(f"[{run_type}] {category}: POSTED={sent}/{len(to_post)}")
    
    return sent

async def run_job(run_type: str) -> int:
    """Run a complete job for the given run type."""
    register_fetchers()
    
    categories = get_categories_for_run(run_type)
    logging.info(f"=== Starting {run_type} run: {sorted(categories)} ===")
    
    total_posted = 0
    for category in sorted(categories):
        if total_posted >= MAX_TOTAL_POSTS_PER_RUN:
            logging.warning(f"Hit max posts per run ({MAX_TOTAL_POSTS_PER_RUN}), stopping")
            break
        
        posted = await process_category(category, run_type)
        total_posted += posted
        
        # Small delay between categories
        await asyncio.sleep(1)
    
    # Cleanup old entries
    cleanup_old(30)
    
    logging.info(f"=== {run_type} run complete: {total_posted} posted ===")
    return total_posted

async def run_weekly_digest():
    """Generate and post weekly digest."""
    logging.info("Generating weekly digest...")
    
    posts = get_recent_posts(hours=168)  # Last 7 days
    
    if not posts:
        logging.info("No posts for weekly digest")
        return
    
    week_start = (datetime.now()).strftime("%d/%m")
    # Actually we want last week
    from datetime import timedelta
    week_start = (datetime.now() - timedelta(days=7)).strftime("%d/%m")
    week_end = datetime.now().strftime("%d/%m")
    
    text = render_weekly_digest(posts, week_start, week_end)
    
    from src.telegram import send_message
    await send_message(text)
    
    logging.info("Weekly digest posted")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description="GamePulse Bot")
    parser.add_argument("run_type", choices=["hourly", "daily", "weekly", "digest"],
                       help="Type of run to execute")
    args = parser.parse_args()
    
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
        handlers=[logging.StreamHandler(sys.stdout)]
    )
    
    if args.run_type == "digest":
        asyncio.run(run_weekly_digest())
    else:
        asyncio.run(run_job(args.run_type))

if __name__ == "__main__":
    main()