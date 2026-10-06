# Prime Gaming source - free games and loot

import feedparser
from typing import List, Dict, Any
from src.config import SOURCES

def fetch_prime_gaming() -> List[Dict[str, Any]]:
    """Fetch free games from Prime Gaming."""
    items = []
    try:
        feed = feedparser.parse(SOURCES["prime"]["rss"])
        
        for entry in feed.entries[:15]:
            title = entry.get("title", "")
            url = entry.get("link", "")
            summary = entry.get("summary", "")
            
            items.append({
                "title": title,
                "summary": summary[:300] if summary else "Conteúdo grátis no Prime Gaming.",
                "url": url,
                "source": "prime_gaming",
            })
    except Exception as e:
        print(f"Error fetching Prime Gaming: {e}")
    
    return items