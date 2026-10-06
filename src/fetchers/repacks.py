import feedparser
import requests
from typing import List, Dict, Any

from src.database import make_item_id, is_posted

REPACK_SITES = {
    "fitgirl": "https://fitgirl-repacks.site/feed/",
    "dodi": "https://dodi-repacks.site/feed/",
    "elamigos": "https://elamigos.site/feed/",
}

def fetch_repack_announcements() -> List[Dict[str, Any]]:
    """Fetch repack announcements (info only, no direct links)."""
    items = []
    
    for name, url in REPACK_SITES.items():
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:5]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", entry.get("description", ""))
                
                item_id = make_item_id(f"repack_{name}", link, title)
                if is_posted(item_id):
                    continue
                
                items.append({
                    "category": "repack",
                    "title": title,
                    "summary": f"Novo repack {name.title()}: {summary[:150] if summary else 'Disponível.'}",
                    "date_info": "Lançado recentemente",
                    "price_info": "Repack (informativo)",
                    "platforms": "PC",
                    "url": link,
                    "source": f"repack_{name}",
                })
        except Exception as e:
            print(f"Error fetching {name}: {e}")
    
    return items