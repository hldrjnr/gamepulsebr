import requests
from datetime import datetime
from typing import List, Dict, Any

from src.database import make_item_id, is_posted
from src.templates import render_post

EPIC_FREE_API = "https://api.epicgames.dev/epic/free-games"
GOG_RSS = "https://www.gog.com/rss"
PRIME_RSS = "https://gaming.amazon.com/rss"
ITCH_FREE_RSS = "https://itch.io/games/free.rss"

def fetch_epic_free() -> List[Dict[str, Any]]:
    """Fetch free games from Epic Games Store."""
    items = []
    try:
        resp = requests.get(EPIC_FREE_API, timeout=15)
        resp.raise_for_status()
        data = resp.json()
        
        for game in data.get("freeGames", {}).get("current", []):
            title = game.get("title", "")
            url = f"https://store.epicgames.com/p/{game.get('productSlug', '')}"
            description = game.get("description", "")
            
            # Get end date
            end_date = game.get("promotionalOffers", [{}])[0].get("promotionalOffers", [{}])[0].get("endDate", "")
            if end_date:
                try:
                    dt = datetime.fromisoformat(end_date.replace("Z", "+00:00"))
                    date_info = f"Até {dt.strftime('%d/%m/%Y')}"
                except:
                    date_info = "Por tempo limitado"
            else:
                date_info = "Por tempo limitado"
            
            original_price = game.get("price", {}).get("totalPrice", {}).get("fmtPrice", {}).get("originalPrice", "Desconhecido")
            price_info = f"Grátis (era {original_price})"
            
            item_id = make_item_id("epic_free", url, title)
            if is_posted(item_id):
                continue
            
            items.append({
                "category": "freebie",
                "title": title,
                "summary": description[:200] if description else "Jogo grátis na Epic Games Store.",
                "date_info": date_info,
                "price_info": price_info,
                "platforms": "PC (Epic Games)",
                "url": url,
                "source": "epic_free",
            })
    except Exception as e:
        print(f"Error fetching Epic free games: {e}")
    
    return items

def fetch_gog_free() -> List[Dict[str, Any]]:
    """Fetch free games from GOG."""
    items = []
    try:
        import feedparser
        feed = feedparser.parse(GOG_RSS)
        
        for entry in feed.entries[:15]:
            title = entry.get("title", "")
            url = entry.get("link", "")
            summary = entry.get("summary", "")
            
            # Filter for free games
            if "free" not in title.lower() and "grátis" not in title.lower() and "gratis" not in title.lower():
                continue
            
            item_id = make_item_id("gog_free", url, title)
            if is_posted(item_id):
                continue
            
            items.append({
                "category": "freebie",
                "title": title,
                "summary": summary[:200] if summary else "Jogo grátis no GOG.",
                "date_info": "Por tempo limitado",
                "price_info": "Grátis",
                "platforms": "PC (GOG)",
                "url": url,
                "source": "gog_free",
            })
    except Exception as e:
        print(f"Error fetching GOG free games: {e}")
    
    return items

def fetch_prime_gaming() -> List[Dict[str, Any]]:
    """Fetch free games from Prime Gaming."""
    items = []
    try:
        import feedparser
        feed = feedparser.parse(PRIME_RSS)
        
        for entry in feed.entries[:10]:
            title = entry.get("title", "")
            url = entry.get("link", "")
            summary = entry.get("summary", "")
            
            item_id = make_item_id("prime_gaming", url, title)
            if is_posted(item_id):
                continue
            
            items.append({
                "category": "freebie",
                "title": title,
                "summary": summary[:200] if summary else "Conteúdo grátis no Prime Gaming.",
                "date_info": "Ver na página",
                "price_info": "Grátis (Prime)",
                "platforms": "PC (Prime Gaming)",
                "url": url,
                "source": "prime_gaming",
            })
    except Exception as e:
        print(f"Error fetching Prime Gaming: {e}")
    
    return items

def fetch_itch_free() -> List[Dict[str, Any]]:
    """Fetch free games from itch.io."""
    items = []
    try:
        import feedparser
        feed = feedparser.parse(ITCH_FREE_RSS)
        
        for entry in feed.entries[:15]:
            title = entry.get("title", "")
            url = entry.get("link", "")
            summary = entry.get("summary", "")
            
            item_id = make_item_id("itch_free", url, title)
            if is_posted(item_id):
                continue
            
            items.append({
                "category": "freebie",
                "title": title,
                "summary": summary[:200] if summary else "Jogo grátis no itch.io.",
                "date_info": "Por tempo limitado",
                "price_info": "Grátis",
                "platforms": "PC (itch.io)",
                "url": url,
                "source": "itch_free",
            })
    except Exception as e:
        print(f"Error fetching itch.io free: {e}")
    
    return items