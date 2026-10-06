# Freebies category - combines all free game sources

from typing import List, Dict, Any
from src.sources.steam import fetch_steamdb_free
from src.sources.epic import fetch_epic_free
from src.sources.gog import fetch_gog_free
from src.sources.amazon import fetch_prime_gaming
from src.sources.itch import fetch_itch_free

def fetch_freebies() -> List[Dict[str, Any]]:
    """Fetch all freebies from all sources."""
    items = []
    
    # SteamDB free
    for item in fetch_steamdb_free():
        item["category"] = "freebies"
        items.append(item)
    
    # Epic Games
    for item in fetch_epic_free():
        item["category"] = "freebies"
        items.append(item)
    
    # GOG
    for item in fetch_gog_free():
        item["category"] = "freebies"
        items.append(item)
    
    # Prime Gaming
    for item in fetch_prime_gaming():
        item["category"] = "freebies"
        items.append(item)
    
    # itch.io
    for item in fetch_itch_free():
        item["category"] = "freebies"
        items.append(item)
    
    return items