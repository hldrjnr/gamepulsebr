# Epic Games Store source - free games

import requests
from datetime import datetime
from typing import List, Dict, Any
from src.config import SOURCES

def fetch_epic_free() -> List[Dict[str, Any]]:
    """Fetch free games from Epic Games Store."""
    items = []
    try:
        resp = requests.get(SOURCES["epic"]["free_api"], timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        for game in data.get("freeGames", {}).get("current", []):
            title = game.get("title", "")
            product_slug = game.get("productSlug", "")
            url = f"https://store.epicgames.com/p/{product_slug}" if product_slug else ""
            description = game.get("description", "")
            
            # Get end date
            end_date = ""
            offers = game.get("promotionalOffers", [])
            if offers:
                promo_offers = offers[0].get("promotionalOffers", [])
                if promo_offers:
                    end_date = promo_offers[0].get("endDate", "")
            
            original_price = game.get("price", {}).get("totalPrice", {}).get("fmtPrice", {}).get("originalPrice", "Desconhecido")
            
            items.append({
                "title": title,
                "summary": description[:300] if description else "Jogo grátis na Epic Games Store.",
                "url": url,
                "source": "epic_free",
                "_extra": {
                    "end_date": end_date,
                    "original_price": original_price,
                }
            })
    except Exception as e:
        print(f"Error fetching Epic free games: {e}")
    
    return items