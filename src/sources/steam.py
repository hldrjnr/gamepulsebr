# SteamDB source - releases, updates, freebies, demos

import feedparser
import re
from typing import List, Dict, Any
from src.config import SOURCES

def fetch_steamdb_releases() -> List[Dict[str, Any]]:
    """Fetch new releases from SteamDB RSS."""
    items = []
    feed = feedparser.parse(SOURCES["steamdb"]["releases_rss"])
    
    for entry in feed.entries[:30]:
        title = entry.get("title", "")
        url = entry.get("link", "")
        summary = entry.get("summary", "")
        
        # Filter out DLCs, soundtracks, etc.
        skip_keywords = ["soundtrack", "dlc", "demo", "beta", "test", "pack", "bundle", "edition upgrade", "wallpaper", "avatar", "artbook"]
        if any(skip in title.lower() for skip in skip_keywords):
            continue
            
        items.append({
            "title": title,
            "summary": summary[:300] if summary else "Novo jogo lançado no Steam.",
            "url": url,
            "source": "steamdb_releases",
        })
    
    return items

def fetch_steamdb_updates() -> List[Dict[str, Any]]:
    """Fetch major game updates from SteamDB."""
    items = []
    feed = feedparser.parse(SOURCES["steamdb"]["updates_rss"])
    
    for entry in feed.entries[:20]:
        title = entry.get("title", "")
        url = entry.get("link", "")
        summary = entry.get("summary", "")
        
        items.append({
            "title": title.replace("Patch: ", "").replace("Update: ", ""),
            "summary": summary[:300] if summary else "Atualização liberada.",
            "url": url,
            "source": "steamdb_updates",
        })
    
    return items

def fetch_steamdb_free() -> List[Dict[str, Any]]:
    """Fetch free games from SteamDB."""
    items = []
    feed = feedparser.parse(SOURCES["steamdb"]["free_rss"])
    
    for entry in feed.entries[:20]:
        title = entry.get("title", "")
        url = entry.get("link", "")
        summary = entry.get("summary", "")
        
        items.append({
            "title": title,
            "summary": summary[:300] if summary else "Jogo grátis no Steam por tempo limitado.",
            "url": url,
            "source": "steamdb_free",
        })
    
    return items

def fetch_steamdb_demos() -> List[Dict[str, Any]]:
    """Fetch new demos from SteamDB."""
    items = []
    feed = feedparser.parse(SOURCES["steamdb"]["demos_rss"])
    
    for entry in feed.entries[:15]:
        title = entry.get("title", "")
        url = entry.get("link", "")
        summary = entry.get("summary", "")
        
        items.append({
            "title": title,
            "summary": summary[:300] if summary else "Nova demo disponível no Steam.",
            "url": url,
            "source": "steamdb_demos",
        })
    
    return items