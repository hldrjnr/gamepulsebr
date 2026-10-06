# Formatter - renders posts for Telegram

from typing import Dict, Any, List
from src.config import CATEGORY_EMOJIS, CATEGORY_TAGS, DISCLAIMER

def render_post(item: Dict[str, Any]) -> str:
    """Render a single post using the standard template."""
    category = item.get("category", "news")
    emoji = CATEGORY_EMOJIS.get(category, "📰")
    tags = " ".join(CATEGORY_TAGS.get(category, ["#gaming", "#gamepulsebr"]))
    
    title = item.get("title", "Sem título")
    summary = item.get("summary", "")
    date_info = item.get("date_info", "")
    price_info = item.get("price_info", "")
    platforms = item.get("platforms", "")
    url = item.get("url", "")
    
    lines = [
        f"{emoji} [{category.upper()}] {title}",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
    ]
    
    if summary:
        lines.append(f"📝 {summary}")
    
    meta_parts = []
    if date_info:
        meta_parts.append(f"📅 {date_info}")
    if price_info:
        meta_parts.append(f"💰 {price_info}")
    if platforms:
        meta_parts.append(f"🖥 {platforms}")
    
    if meta_parts:
        lines.append(" | ".join(meta_parts))
    
    if url:
        lines.append(f"🔗 {url}")
    
    lines.append(f"{tags} #gamepulsebr")
    lines.append(DISCLAIMER)
    
    return "\n".join(lines)

def render_posts(items: List[Dict[str, Any]]) -> List[str]:
    """Render multiple posts."""
    return [render_post(item) for item in items]

def render_weekly_digest(posts: List[Dict[str, Any]], week_start: str, week_end: str) -> str:
    """Render weekly digest post."""
    lines = [
        f"📋 DIGEST SEMANAL {week_start} a {week_end}",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        "Melhores da semana por categoria:",
        "",
    ]
    
    # Group by category
    by_cat = {}
    for p in posts:
        cat = p.get("category", "news")
        if cat not in by_cat:
            by_cat[cat] = []
        by_cat[cat].append(p)
    
    # Sort categories by emoji order
    category_order = ["freebies", "releases", "sales", "news", "updates", "demos", 
                     "emulation", "hardware", "mods", "ports", "repacks"]
    
    for cat in category_order:
        if cat not in by_cat:
            continue
        items = by_cat[cat]
        emoji = CATEGORY_EMOJIS.get(cat, "📰")
        lines.append(f"{emoji} {cat.upper()}")
        for item in items[:3]:  # top 3 per category
            title = item.get("title", "Sem título")[:70]
            url = item.get("url", "")
            lines.append(f"  • {title} — {url}")
        lines.append("")
    
    # Any remaining categories not in order
    for cat, items in by_cat.items():
        if cat in category_order:
            continue
        emoji = CATEGORY_EMOJIS.get(cat, "📰")
        lines.append(f"{emoji} {cat.upper()}")
        for item in items[:2]:
            title = item.get("title", "Sem título")[:70]
            url = item.get("url", "")
            lines.append(f"  • {title} — {url}")
        lines.append("")
    
    lines.append("#digest #semanal #gamepulsebr")
    lines.append(DISCLAIMER)
    
    return "\n".join(lines)