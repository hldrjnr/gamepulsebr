# Mods sources - NexusMods, ModDB

import feedparser
from typing import List, Dict, Any
from src.config import SOURCES

def fetch_mods(max_per_source: int = 3) -> List[Dict[str, Any]]:
    """Fetch popular mod updates from NexusMods and ModDB."""
    items = []
    
    for source, url in SOURCES["mods"].items():
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:max_per_source]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", entry.get("description", ""))
                
                # Skip trivial updates
                if any(skip in title.lower() for skip in ["hotfix", "minor", "typo", "readme", "changelog only"]):
                    continue
                
                game = source.replace("nexus_", "").replace("_", " ").title()
                if source == "moddb":
                    game = "Vários jogos"
                
                items.append({
                    "title": title,
                    "summary": f"Mod para {game}: {summary[:200] if summary else 'Atualização de mod.'}",
                    "url": link,
                    "source": f"mods_{source}",
                })
        except Exception as e:
            print(f"Error fetching {source}: {e}")
    
    return items