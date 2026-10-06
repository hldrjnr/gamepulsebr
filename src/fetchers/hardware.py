import feedparser
import requests
from typing import List, Dict, Any

from src.database import make_item_id, is_posted

HARDWARE_FEEDS = {
    "tomshardware": "https://www.tomshardware.com/feeds/all",
    "gamersnexus": "https://www.gamersnexus.net/rss.xml",
    "hardwareunboxed": "https://www.youtube.com/feeds/videos.xml?channel_id=UCEkQRfnaG17WVT5d85-vqYQ",  # Hardware Unboxed
    "techpowerup": "https://www.techpowerup.com/rss.php",
    "videocardz": "https://videocardz.com/feed",
}

REDDIT_HARDWARE_SALES = "https://www.reddit.com/r/buildapcsales/.rss"
REDDIT_HARDWARE = "https://www.reddit.com/r/hardware/.rss"

def fetch_hardware_news(max_per_source: int = 3) -> List[Dict[str, Any]]:
    """Fetch hardware news and reviews."""
    items = []
    
    for source, url in HARDWARE_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:max_per_source]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", entry.get("description", ""))
                
                # Filter for relevant hardware (GPU, CPU, SSD, RAM, Monitor)
                keywords = ["gpu", "cpu", "ssd", "ram", "memory", "monitor", "graphics", "processor", "ryzen", "intel core", "rtx", "radeon", "geforce", "nvidia", "amd"]
                if not any(kw in title.lower() for kw in keywords):
                    continue
                
                # Skip rumors/leaks unless confirmed
                if any(skip in title.lower() for skip in ["rumor", "leak", "alleged", "supposedly", "may", "could"]):
                    continue
                
                item_id = make_item_id(f"hardware_{source}", link, title)
                if is_posted(item_id):
                    continue
                
                items.append({
                    "category": "hardware",
                    "title": title,
                    "summary": summary[:200] if summary else "Nova notícia de hardware.",
                    "date_info": "Recente",
                    "price_info": "Ver review",
                    "platforms": "PC Hardware",
                    "url": link,
                    "source": f"hardware_{source}",
                })
        except Exception as e:
            print(f"Error fetching {source}: {e}")
    
    # Reddit buildapcsales for deals
    try:
        feed = feedparser.parse(REDDIT_HARDWARE_SALES)
        for entry in feed.entries[:10]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            
            # Must have price indicator
            if not any(c in title for c in ["$", "USD", "R$", "BRL", "%"]):
                continue
                
            item_id = make_item_id("hardware_reddit_sales", link, title)
            if is_posted(item_id):
                continue
            
            items.append({
                "category": "hardware",
                "title": title,
                "summary": "Promoção de hardware no r/buildapcsales.",
                "date_info": "Enquanto durar",
                "price_info": "Ver post",
                "platforms": "PC Hardware",
                "url": link,
                "source": "hardware_reddit_sales",
            })
    except Exception as e:
        print(f"Error fetching Reddit hardware sales: {e}")
    
    return items