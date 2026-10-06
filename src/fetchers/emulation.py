import feedparser
import requests
from typing import List, Dict, Any
import re

from src.database import make_item_id, is_posted

EMULATION_FEEDS = {
    "ryujinx": "https://github.com/Ryujinx/Ryujinx/releases.atom",
    "sudachi": "https://github.com/sudachi-emu/sudachi/releases.atom",
    "pcsx2": "https://github.com/PCSX2/pcsx2/releases.atom",
    "duckstation": "https://github.com/stenzek/duckstation/releases.atom",
    "ppsspp": "https://github.com/hrydgard/ppsspp/releases.atom",
    "dolphin": "https://github.com/dolphin-emu/dolphin/releases.atom",
    "rpcs3": "https://github.com/RPCS3/rpcs3/releases.atom",
    "yuzu_fork": "https://github.com/pineappleEA/yuzu-mainline/releases.atom",
}

PCGAMINGWIKI_FEED = "https://www.pcgamingwiki.com/api.php?action=feedrecentchanges&feedformat=atom"

def fetch_emulation_releases() -> List[Dict[str, Any]]:
    """Fetch emulator releases from GitHub."""
    items = []
    
    for name, url in EMULATION_FEEDS.items():
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:3]:  # Latest 3 per emulator
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", entry.get("description", ""))
                published = entry.get("published", "")
                
                # Skip pre-releases, drafts, very old
                if any(skip in title.lower() for skip in ["draft", "pre-release", "alpha", "beta", "rc"]):
                    continue
                
                item_id = make_item_id(f"emulation_{name}", link, title)
                if is_posted(item_id):
                    continue
                
                date_info = "Lançado recentemente"
                if published:
                    try:
                        from datetime import datetime
                        dt = datetime(*entry.published_parsed[:6])
                        date_info = dt.strftime("%d/%m/%Y")
                    except:
                        pass
                
                # Extract version
                version_match = re.search(r'v?(\d+\.\d+(\.\d+)?)', title)
                version = version_match.group(1) if version_match else ""
                
                display_title = f"{name.title()} {version}".strip() if version else name.title()
                
                items.append({
                    "category": "emulation",
                    "title": display_title,
                    "summary": f"Nova versão do emulador {name.title()}. {summary[:150] if summary else ''}",
                    "date_info": date_info,
                    "price_info": "Grátis (open source)",
                    "platforms": "PC (Windows/Linux/macOS)",
                    "url": link,
                    "source": f"emulation_{name}",
                })
        except Exception as e:
            print(f"Error fetching {name}: {e}")
    
    return items

def fetch_pcgamingwiki_updates() -> List[Dict[str, Any]]:
    """Fetch PCGamingWiki updates (ports, fixes, patches)."""
    items = []
    try:
        feed = feedparser.parse(PCGAMINGWIKI_FEED)
        
        for entry in feed.entries[:10]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", entry.get("description", ""))
            
            # Filter for port/fix related updates
            keywords = ["port", "patch", "fix", "fan patch", "recompilation", "source port", "mod", "translation"]
            if not any(kw in title.lower() or kw in summary.lower() for kw in keywords):
                continue
            
            item_id = make_item_id("pcgamingwiki", link, title)
            if is_posted(item_id):
                continue
            
            # Determine category
            cat = "port"
            if "mod" in title.lower() or "mod" in summary.lower():
                cat = "mod"
            elif "emulation" in title.lower() or "emulator" in title.lower():
                cat = "emulation"
            
            items.append({
                "category": cat,
                "title": title,
                "summary": summary[:200] if summary else "Atualização no PCGamingWiki.",
                "date_info": "Recente",
                "price_info": "Grátis",
                "platforms": "PC",
                "url": link,
                "source": "pcgamingwiki",
            })
    except Exception as e:
        print(f"Error fetching PCGamingWiki: {e}")
    
    return items