# GOG source - free games and deals

import feedparser
from typing import List, Dict, Any
from src.config import SOURCES

def fetch_gog_free() -> List[Dict[str, Any]]:
    """Fetch free games from GOG."""
    items = []
    try:
        feed = feedparser.parse(SOURCES["gog"]["rss"])
        
        for entry in feed.entries[:20]:
            title = entry.get("title", "")
            url = entry.get("link", "")
            summary = entry.get("summary", "")
            
            # Filter for free games
            if not any(kw in title.lower() for kw in ["free", "grátis", "gratis", "gratuito"]):
                continue
            
            items.append({
                "title": title,
                "summary": summary[:300] if summary else "Jogo grátis no GOG.",
                "url": url,
                "source": "gog_free",
            })
    except Exception as e:
        print(f"Error fetching GOG free games: {e}")
    
    return items