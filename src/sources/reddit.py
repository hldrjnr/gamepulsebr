# Reddit sources - hardware deals and news

import feedparser
from typing import List, Dict, Any
from src.config import SOURCES

def fetch_reddit_hardware_sales() -> List[Dict[str, Any]]:
    """Fetch hardware deals from r/buildapcsales."""
    items = []
    try:
        feed = feedparser.parse(SOURCES["reddit"]["buildapcsales"])
        
        for entry in feed.entries[:20]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            
            # Must have price indicator
            if not any(c in title for c in ["$", "USD", "R$", "BRL", "%", "€", "£"]):
                continue
                
            items.append({
                "title": title,
                "summary": "Promoção de hardware no r/buildapcsales.",
                "url": link,
                "source": "reddit_buildapcsales",
            })
    except Exception as e:
        print(f"Error fetching Reddit hardware sales: {e}")
    
    return items

def fetch_reddit_hardware_news() -> List[Dict[str, Any]]:
    """Fetch hardware news from r/hardware."""
    items = []
    try:
        feed = feedparser.parse(SOURCES["reddit"]["hardware"])
        
        for entry in feed.entries[:10]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", entry.get("description", ""))
            
            # Filter for relevant hardware
            keywords = ["gpu", "cpu", "ssd", "ram", "memory", "monitor", "graphics", "processor", "ryzen", "intel core", "rtx", "radeon", "geforce", "nvidia", "amd"]
            if not any(kw in title.lower() for kw in keywords):
                continue
            
            # Skip rumors
            if any(skip in title.lower() for skip in ["rumor", "leak", "alleged", "supposedly", "may ", "could "]):
                continue
                
            items.append({
                "title": title,
                "summary": summary[:300] if summary else "Nova notícia de hardware.",
                "url": link,
                "source": "reddit_hardware",
            })
    except Exception as e:
        print(f"Error fetching Reddit hardware news: {e}")
    
    return items