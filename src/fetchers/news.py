import feedparser
import requests
from typing import List, Dict, Any
from datetime import datetime

from src.database import make_item_id, is_posted

NEWS_FEEDS = {
    "vgc": "https://www.videogameschronicle.com/feed/",
    "eurogamer": "https://www.eurogamer.net/rss.xml",
    "gematsu": "https://gematsu.com/feed",
    "theverge_gaming": "https://www.theverge.com/gaming/rss/index.xml",
    "kotaku": "https://kotaku.com/rss",
    "pcgamer": "https://www.pcgamer.com/rss",
    "rockpapershotgun": "https://www.rockpapershotgun.com/rss",
    "ign": "https://feeds.ign.com/ign/games-all",
}

def fetch_gaming_news(max_per_source: int = 5) -> List[Dict[str, Any]]:
    """Fetch gaming news from multiple RSS feeds."""
    items = []
    
    for source, url in NEWS_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:max_per_source]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", entry.get("description", ""))
                published = entry.get("published", "")
                
                # Skip non-gaming content
                skip_keywords = ["review:", "review ", "opinion:", "editorial:", "video:", "podcast:"]
                if any(skip in title.lower() for skip in skip_keywords):
                    continue
                
                item_id = make_item_id(f"news_{source}", link, title)
                if is_posted(item_id):
                    continue
                
                # Format date
                date_info = "Hoje"
                if published:
                    try:
                        dt = datetime(*entry.published_parsed[:6])
                        date_info = dt.strftime("%d/%m/%Y")
                    except:
                        pass
                
                items.append({
                    "category": "news",
                    "title": title,
                    "summary": summary[:200] if summary else "Nova notícia do mundo dos jogos.",
                    "date_info": date_info,
                    "price_info": "—",
                    "platforms": "Multiplataforma",
                    "url": link,
                    "source": f"news_{source}",
                })
        except Exception as e:
            print(f"Error fetching {source}: {e}")
    
    return items