# Normalize and enrich items

import re
from datetime import datetime
from typing import Dict, Any, Optional

def normalize_title(title: str) -> str:
    """Clean up title."""
    if not title:
        return ""
    # Remove common prefixes
    title = re.sub(r'^(Patch|Update|Release|Free|Demo|Hotfix):\s*', '', title, flags=re.IGNORECASE)
    # Remove excess whitespace
    title = re.sub(r'\s+', ' ', title).strip()
    return title

def extract_price_info(text: str, category: str) -> str:
    """Extract price information from text."""
    if category == "freebies":
        # Look for original price
        match = re.search(r'(?:was|era|originalmente)\s*\$?([\d,.]+)', text, re.IGNORECASE)
        if match:
            return f"Grátis (era ${match.group(1)})"
        return "Grátis por tempo limitado"
    
    elif category == "sales":
        # Look for discount percentage
        match = re.search(r'(\d+)%\s*(?:off|desconto|OFF)', text, re.IGNORECASE)
        if match:
            return f"{match.group(1)}% OFF"
        # Look for price
        match = re.search(r'\$?([\d,.]+)\s*(?:\(era|\(was|era|was)\s*\$?([\d,.]+)', text, re.IGNORECASE)
        if match:
            return f"${match.group(1)} (era ${match.group(2)})"
    
    elif category in ("releases", "updates", "demos"):
        return "Ver na loja"
    
    elif category in ("emulation", "mods", "ports", "repacks"):
        return "Grátis"
    
    return "—"

def extract_date_info(text: str) -> str:
    """Extract date/availability info from text."""
    # Look for "until", "até", "ends", "expires"
    patterns = [
        r'(?:until|até|ends?|expires?|válid[ao]?)\s+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})',
        r'(?:until|até|ends?|expires?)\s+(\w+\s+\d{1,2},?\s+\d{4})',
        r'(?:until|até)\s+(\d{1,2}\s+\w+\s+\d{4})',
    ]
    for pattern in patterns:
        match = re.search(pattern, text, re.IGNORECASE)
        if match:
            return f"Até {match.group(1)}"
    
    # Look for release date
    match = re.search(r'(?:released?|lançad[ao]|launch)\s+(\d{1,2}[\/\-]\d{1,2}[\/\-]\d{2,4})', text, re.IGNORECASE)
    if match:
        return match.group(1)
    
    return "Disponível agora"

def extract_platforms(text: str, source: str) -> str:
    """Extract platform information."""
    platforms = []
    text_lower = text.lower()
    
    platform_keywords = {
        "steam": "PC (Steam)",
        "epic": "PC (Epic Games)",
        "gog": "PC (GOG)",
        "itch": "PC (itch.io)",
        "prime": "PC (Prime Gaming)",
        "microsoft": "PC (Microsoft Store)",
        "ubisoft": "PC (Ubisoft Connect)",
        "ea app": "PC (EA App)",
        "origin": "PC (Origin)",
        "playstation": "PlayStation",
        "xbox": "Xbox",
        "nintendo": "Nintendo Switch",
        "android": "Android",
        "ios": "iOS",
        "linux": "Linux",
        "mac": "macOS",
        "windows": "Windows",
    }
    
    for keyword, platform in platform_keywords.items():
        if keyword in text_lower or keyword in source.lower():
            if platform not in platforms:
                platforms.append(platform)
    
    if not platforms:
        # Default based on source
        if "steam" in source.lower():
            return "PC (Steam)"
        elif "epic" in source.lower():
            return "PC (Epic Games)"
        elif "gog" in source.lower():
            return "PC (GOG)"
        elif "itch" in source.lower():
            return "PC (itch.io)"
        elif "prime" in source.lower():
            return "PC (Prime Gaming)"
        else:
            return "Multiplataforma"
    
    return " | ".join(platforms)

def normalize_item(raw_item: Dict[str, Any], category: str) -> Dict[str, Any]:
    """Normalize a raw item into standard format."""
    title = normalize_title(raw_item.get("title", ""))
    summary = raw_item.get("summary", raw_item.get("description", ""))
    url = raw_item.get("url", raw_item.get("link", ""))
    source = raw_item.get("source", "unknown")
    
    return {
        "category": category,
        "title": title,
        "summary": summary[:200] if summary else "",
        "date_info": extract_date_info(summary or title),
        "price_info": extract_price_info(summary or title, category),
        "platforms": extract_platforms(summary or title, source),
        "url": url,
        "source": source,
    }

def filter_relevant(item: Dict[str, Any], category: str) -> bool:
    """Filter out irrelevant items."""
    title = item.get("title", "").lower()
    summary = item.get("summary", "").lower()
    text = f"{title} {summary}"
    
    # Always skip
    skip_keywords = ["soundtrack", "dlc", "wallpaper", "avatar", "theme", "artbook", "ost"]
    if any(skip in text for skip in skip_keywords):
        return False
    
    # Category-specific filters
    if category == "releases":
        # Skip DLCs, soundtracks, betas
        if any(skip in title for skip in ["dlc", "soundtrack", "beta", "test", "demo", "pack", "bundle", "edition upgrade"]):
            return False
    
    elif category == "updates":
        # Only major updates
        size_match = re.search(r'(\d+(?:\.\d+)?)\s*(GB|MB)', text, re.IGNORECASE)
        is_major = False
        if size_match:
            size = float(size_match.group(1))
            unit = size_match.group(2).upper()
            if unit == "GB" or (unit == "MB" and size > 500):
                is_major = True
        if re.search(r'v\d+\.\d+\.\d+|Version \d+\.\d+|Update \d+|Major|Patch \d+\.\d+', text, re.IGNORECASE):
            is_major = True
        if not is_major:
            return False
    
    elif category == "news":
        # Allow all news - don't filter out reviews, opinions, videos, podcasts
        pass
    
    elif category == "hardware":
        # Only relevant hardware
        keywords = ["gpu", "cpu", "ssd", "ram", "memory", "monitor", "graphics", "processor", "ryzen", "intel core", "rtx", "radeon", "geforce", "nvidia", "amd"]
        if not any(kw in text for kw in keywords):
            return False
        # Skip rumors unless confirmed
        if any(skip in title for skip in ["rumor", "leak", "alleged", "supposedly", "may ", "could "]):
            return False
    
    elif category == "emulation":
        # Skip pre-releases, alphas, betas unless stable
        if any(skip in title for skip in ["draft", "pre-release", "alpha", "beta", "rc"]):
            return False
    
    return True