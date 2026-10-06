# Repacks category - FitGirl, DODI, ElAmigos

from typing import List, Dict, Any
from src.sources.repacks import fetch_repack_announcements

def fetch_repacks() -> List[Dict[str, Any]]:
    """Fetch repack announcements."""
    items = []
    
    for item in fetch_repack_announcements():
        item["category"] = "repacks"
        items.append(item)
    
    return items