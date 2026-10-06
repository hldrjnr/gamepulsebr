# GitHub sources - emulator releases, PCGamingWiki

import feedparser
import re
from typing import List, Dict, Any
from src.config import SOURCES

def fetch_emulator_releases() -> List[Dict[str, Any]]:
    """Fetch emulator releases from GitHub."""
    items = []
    
    for name, url in SOURCES["emulators"].items():
        try:
            feed = feedparser.parse(url)
            
            for entry in feed.entries[:3]:
                title = entry.get("title", "")
                link = entry.get("link", "")
                summary = entry.get("summary", entry.get("description", ""))
                
                # Skip pre-releases, drafts
                if any(skip in title.lower() for skip in ["draft", "pre-release", "alpha", "beta", "rc"]):
                    continue
                
                # Extract version
                version_match = re.search(r'v?(\d+\.\d+(\.\d+)?)', title)
                version = version_match.group(1) if version_match else ""
                
                display_title = f"{name.title()} {version}".strip() if version else name.title()
                
                items.append({
                    "title": display_title,
                    "summary": f"Nova versão do emulador {name.title()}. {summary[:200] if summary else ''}",
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
        feed = feedparser.parse(SOURCES["pcgamingwiki"]["feed"])
        
        for entry in feed.entries[:15]:
            title = entry.get("title", "")
            link = entry.get("link", "")
            summary = entry.get("summary", entry.get("description", ""))
            
            # Filter for port/fix related updates
            keywords = ["port", "patch", "fix", "fan patch", "recompilation", "source port", "mod", "translation", "remaster", "wrapper"]
            if not any(kw in title.lower() or kw in summary.lower() for kw in keywords):
                continue
            
            # Determine category
            cat = "ports"
            if "mod" in title.lower() or "mod" in summary.lower():
                cat = "mods"
            elif "emulation" in title.lower() or "emulator" in title.lower():
                cat = "emulation"
            
            items.append({
                "title": title,
                "summary": summary[:300] if summary else "Atualização no PCGamingWiki.",
                "url": link,
                "source": "pcgamingwiki",
                "_extra": {"pcgw_category": cat}
            })
    except Exception as e:
        print(f"Error fetching PCGamingWiki: {e}")
    
    return items