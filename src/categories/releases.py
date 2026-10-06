# Releases category - new game releases

from typing import List, Dict, Any
from src.sources.steam import fetch_steamdb_releases, fetch_steamdb_demos

def fetch_releases() -> List[Dict[str, Any]]:
    """Fetch new game releases."""
    items = []
    
    for item in fetch_steamdb_releases():
        item["category"] = "releases"
        items.append(item)
    
    return items

def fetch_demos() -> List[Dict[str, Any]]:
    """Fetch new demos."""
    items = []
    
    for item in fetch_steamdb_demos():
        item["category"] = "demos"
        items.append(item)
    
    return items

def fetch_updates() -> List[Dict[str, Any]]:
    """Fetch major game updates."""
    items = []
    
    from src.sources.steam import fetch_steamdb_updates
    for item in fetch_steamdb_updates():
        item["category"] = "updates"
        items.append(item)
    
    return items