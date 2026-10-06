# Ports category - PCGamingWiki ports, recompilation

from typing import List, Dict, Any
from src.sources.github import fetch_pcgamingwiki_updates

def fetch_ports() -> List[Dict[str, Any]]:
    """Fetch ports and recompilation news."""
    items = []
    
    for item in fetch_pcgamingwiki_updates():
        # Use the category determined by PCGamingWiki
        cat = item.get("_extra", {}).get("pcgw_category", "ports")
        item["category"] = cat
        items.append(item)
    
    return items