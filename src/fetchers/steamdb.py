import feedparser
import requests
from datetime import datetime, timedelta
from typing import List, Dict, Any
import re

from src.database import make_item_id, is_posted, mark_posted
from src.templates import render_post

STEAMDB_RSS = "https://steamdb.info/rss/"
STEAMDB_UPCOMING = "https://steamdb.info/upcoming/"
STEAMDB_FREE = "https://steamdb.info/free/"

def fetch_steamdb_releases() -> List[Dict[str, Any]]:
    """Fetch new releases from SteamDB RSS."""
    items = []
    feed = feedparser.parse(STEAMDB_RSS)
    
    for entry in feed.entries[:30]:  # Limit to recent
        title = entry.get("title", "")
        url = entry.get("link", "")
        summary = entry.get("summary", "")
        
        # Filter for actual game releases (not DLC, soundtracks, etc.)
        if any(skip in title.lower() for skip in ["soundtrack", "dlc", "demo", "beta", "test", "pack", "bundle"]):
            continue
            
        item_id = make_item_id("steamdb_releases", url, title)
        if is_posted(item_id):
            continue
        
        # Extract date from summary if possible
        date_match = re.search(r'(\d{1,2} \w+ \d{4})', summary)
        date_info = date_match.group(1) if date_match else "Lançamento recente"
        
        items.append({
            "category": "release",
            "title": title,
            "summary": summary[:200] if summary else "Novo jogo lançado no Steam.",
            "date_info": date_info,
            "price_info": "Ver na loja",
            "platforms": "PC (Steam)",
            "url": url,
            "source": "steamdb_releases",
        })
    
    return items

def fetch_steamdb_updates() -> List[Dict[str, Any]]:
    """Fetch major game updates from SteamDB."""
    items = []
    feed = feedparser.parse("https://steamdb.info/rss/patches/")
    
    for entry in feed.entries[:20]:
        title = entry.get("title", "")
        url = entry.get("link", "")
        summary = entry.get("summary", "")
        
        # Filter for significant updates (large size or major version)
        size_match = re.search(r'(\d+(?:\.\d+)?)\s*(GB|MB)', summary, re.IGNORECASE)
        is_major = False
        if size_match:
            size = float(size_match.group(1))
            unit = size_match.group(2).upper()
            if unit == "GB" or (unit == "MB" and size > 500):
                is_major = True
        
        # Also check for version numbers like v1.0, v2.0, etc.
        if re.search(r'v\d+\.\d+\.\d+|Version \d+\.\d+|Update \d+', title, re.IGNORECASE):
            is_major = True
            
        if not is_major:
            continue
            
        item_id = make_item_id("steamdb_updates", url, title)
        if is_posted(item_id):
            continue
        
        items.append({
            "category": "update",
            "title": title.replace("Patch: ", "").replace("Update: ", ""),
            "summary": summary[:200] if summary else "Atualização significativa liberada.",
            "date_info": "Disponível agora",
            "price_info": "Grátis (atualização)",
            "platforms": "PC (Steam)",
            "url": url,
            "source": "steamdb_updates",
        })
    
    return items

def fetch_steamdb_free() -> List[Dict[str, Any]]:
    """Fetch free games from SteamDB."""
    items = []
    feed = feedparser.parse("https://steamdb.info/rss/free/")
    
    for entry in feed.entries[:15]:
        title = entry.get("title", "")
        url = entry.get("link", "")
        summary = entry.get("summary", "")
        
        # Extract price info
        price_match = re.search(r'was \$?([\d,.]+)', summary, re.IGNORECASE)
        price_info = f"Grátis (era ${price_match.group(1)})" if price_match else "Grátis por tempo limitado"
        
        # Extract end date
        date_match = re.search(r'until (\d{1,2} \w+ \d{4})', summary, re.IGNORECASE)
        date_info = f"Até {date_match.group(1)}" if date_match else "Por tempo limitado"
        
        item_id = make_item_id("steamdb_free", url, title)
        if is_posted(item_id):
            continue
        
        items.append({
            "category": "freebie",
            "title": title,
            "summary": summary[:200] if summary else "Jogo grátis no Steam por tempo limitado.",
            "date_info": date_info,
            "price_info": price_info,
            "platforms": "PC (Steam)",
            "url": url,
            "source": "steamdb_free",
        })
    
    return items

def fetch_steamdb_demos() -> List[Dict[str, Any]]:
    """Fetch new demos from SteamDB."""
    items = []
    feed = feedparser.parse("https://steamdb.info/rss/demos/")
    
    for entry in feed.entries[:15]:
        title = entry.get("title", "")
        url = entry.get("link", "")
        summary = entry.get("summary", "")
        
        item_id = make_item_id("steamdb_demos", url, title)
        if is_posted(item_id):
            continue
        
        items.append({
            "category": "demo",
            "title": title,
            "summary": summary[:200] if summary else "Nova demo disponível no Steam.",
            "date_info": "Disponível agora",
            "price_info": "Grátis (demo)",
            "platforms": "PC (Steam)",
            "url": url,
            "source": "steamdb_demos",
        })
    
    return items