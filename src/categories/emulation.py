# Emulation category

from typing import List, Dict, Any
from src.sources.github import fetch_emulator_releases

def fetch_emulation() -> List[Dict[str, Any]]:
    """Fetch emulator releases."""
    items = []
    
    for item in fetch_emulator_releases():
        item["category"] = "emulation"
        items.append(item)
    
    return items