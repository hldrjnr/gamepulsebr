# itch.io source - free games

import feedparser
from typing import List, Dict, Any
from src.config import SOURCES

def fetch_itch_free() -> List[Dict[str, Any]]:
    """Fetch free games from itch.io."""
    items = []
    try:
        feed = feedparser.parse(SOURCES["itch"]["free_rss"])
        
        for entry in feed.entries[:20]:
            title = entry.get("title", "")
            url = entry.get("link", "")
            summary = entry.get("summary", "")
            
            items.append({
                "title": title,
                "summary": summary[:300] if summary else "Jogo grátis no itch.io.",
                "url": url,
                "source": "itch_free",
            })
    except Exception as e:
        print(f"Error fetching itch.io free games: {e}")
    
    return items