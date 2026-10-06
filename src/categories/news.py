# News category - gaming news

from typing import List, Dict, Any
from src.sources.news import fetch_gaming_news

def fetch_news() -> List[Dict[str, Any]]:
    """Fetch gaming news."""
    items = []
    
    for item in fetch_gaming_news():
        item["category"] = "news"
        items.append(item)
    
    return items