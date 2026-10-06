# Mods category

from typing import List, Dict, Any
from src.sources.mods import fetch_mods

def fetch_mods_category() -> List[Dict[str, Any]]:
    """Fetch mod updates."""
    items = []
    
    for item in fetch_mods():
        item["category"] = "mods"
        items.append(item)
    
    return items