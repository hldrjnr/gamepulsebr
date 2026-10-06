# Repacks sources - FitGirl, DODI, ElAmigos announcements

import feedparser
from typing import List, Dict, Any
from src.config import SOURCES

def fetch_repack_announcements() -> List[Dict[str, Any]]:
    """Fetch repack announcements (info only, no direct links)."""
    items = []
    
    for name, url in SOURCES["repacks"].items():
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:5]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", entry.get("description", ""))
                
                items.append({
                    "title": title,
                    "summary": f"Novo repack {name.title()}: {summary[:200] if summary else 'Disponível.'}",
                    "url": link,
                    "source": f"repack_{name}",
                })
        except Exception as e:
            print(f"Error fetching {name}: {e}")
    
    return items