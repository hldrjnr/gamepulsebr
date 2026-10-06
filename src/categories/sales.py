# Sales category - game deals

from typing import List, Dict, Any
from src.sources.deals import fetch_cheapshark_sales, fetch_nuuvem_sales

def fetch_sales() -> List[Dict[str, Any]]:
    """Fetch game sales from all deal sources."""
    items = []
    
    for item in fetch_cheapshark_sales():
        item["category"] = "sales"
        items.append(item)
    
    for item in fetch_nuuvem_sales():
        item["category"] = "sales"
        items.append(item)
    
    return items