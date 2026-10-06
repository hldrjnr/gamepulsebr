import feedparser
import requests
from typing import List, Dict, Any

from src.database import make_item_id, is_posted

MOD_FEEDS = {
    "nexusmods_skyrim": "https://www.nexusmods.com/skyrimspecialedition/rss/mods/updated",
    "nexusmods_cyberpunk": "https://www.nexusmods.com/cyberpunk2077/rss/mods/updated",
    "nexusmods_baldursgate3": "https://www.nexusmods.com/baldursgate3/rss/mods/updated",
    "nexusmods_eldenring": "https://www.nexusmods.com/eldenring/rss/mods/updated",
    "nexusmods_stardew": "https://www.nexusmods.com/stardewvalley/rss/mods/updated",
    "moddb": "https://www.moddb.com/rss.xml",
}

def fetch_mods(max_per_source: int = 3) -> List[Dict[str, Any]]:
    """Fetch popular mod updates from NexusMods and ModDB."""
    items = []
    
    for source, url in MOD_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:max_per_source]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", entry.get("description", ""))
                
                # Skip trivial updates
                if any(skip in title.lower() for skip in ["hotfix", "minor", "typo", "readme", "changelog only"]):
                    continue
                
                item_id = make_item_id(f"mods_{source}", link, title)
                if is_posted(item_id):
                    continue
                
                game = source.replace("nexusmods_", "").replace("_", " ").title()
                if source == "moddb":
                    game = "Vários jogos"
                
                items.append({
                    "category": "mod",
                    "title": title,
                    "summary": f"Mod para {game}: {summary[:150] if summary else 'Atualização de mod.'}",
                    "date_info": "Disponível agora",
                    "price_info": "Grátis",
                    "platforms": "PC",
                    "url": link,
                    "source": f"mods_{source}",
                })
        except Exception as e:
            print(f"Error fetching {source}: {e}")
    
    return items