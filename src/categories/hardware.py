# Hardware category - news and deals

from typing import List, Dict, Any
from src.sources.reddit import fetch_reddit_hardware_sales, fetch_reddit_hardware_news
from src.sources.github import fetch_pcgamingwiki_updates

def fetch_hardware() -> List[Dict[str, Any]]:
    """Fetch hardware news and deals."""
    items = []
    
    # Reddit hardware sales
    for item in fetch_reddit_hardware_sales():
        item["category"] = "hardware"
        items.append(item)
    
    # Reddit hardware news
    for item in fetch_reddit_hardware_news():
        item["category"] = "hardware"
        items.append(item)
    
    return items