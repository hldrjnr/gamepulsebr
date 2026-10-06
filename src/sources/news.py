# News sources - gaming news sites

import feedparser
from typing import List, Dict, Any
from src.config import SOURCES

def fetch_gaming_news(max_per_source: int = 5) -> List[Dict[str, Any]]:
    """Fetch gaming news from multiple RSS feeds."""
    items = []
    
    for source, url in SOURCES["news_sites"].items():
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:max_per_source]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", entry.get("description", ""))
                
                # Skip non-gaming content
                skip_keywords = ["review:", "review ", "opinion:", "editorial:", "video:", "podcast:", "hands-on:", "preview:"]
                if any(skip in title.lower() for skip in skip_keywords):
                    continue
                
                items.append({
                    "title": title,
                    "summary": summary[:300] if summary else "Nova notícia do mundo dos jogos.",
                    "url": link,
                    "source": f"news_{source}",
                })
        except Exception as e:
            print(f"Error fetching {source}: {e}")
    
    return items