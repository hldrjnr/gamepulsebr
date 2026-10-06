CATEGORY_EMOJIS = {
    "release": "🆕",
    "update": "🔄",
    "freebie": "🆓",
    "demo": "🎮",
    "news": "📰",
    "ranking": "📊",
    "mod": "🛠",
    "hardware": "⚙️",
    "sale": "🔥",
    "trailer": "🎬",
    "event": "📅",
    "emulation": "📟",
    "repack": "🔓",
    "port": "🔧",
}

CATEGORY_TAGS = {
    "release": ["#lançamento", "#novojogo", "#steam"],
    "update": ["#atualização", "#patch", "#changelog"],
    "freebie": ["#grátis", "#freebie", "#free"],
    "demo": ["#demo", "#testegrátis", "#steamdemo"],
    "news": ["#notícias", "#gamingnews", "#indústria"],
    "ranking": ["#ranking", "#topjogos", "#estatísticas"],
    "mod": ["#mod", "#modding", "#comunidade"],
    "hardware": ["#hardware", "#gpu", "#pcgaming"],
    "sale": ["#promoção", "#desconto", "#steamsale"],
    "trailer": ["#trailer", "#gameplay", "#reveal"],
    "event": ["#evento", "#gamescom", "#summergamefest"],
    "emulation": ["#emulação", "#emulator", "#retrogaming"],
    "repack": ["#repack", "#fitgirl", "#dodi"],
    "port": ["#port", "#recompilação", "#linuxgaming"],
}

DISCLAIMER = "\n⚠️ Emulação/repacks/ports: apenas notícia + link para projeto oficial. Não hospedamos arquivos."

def render_post(item: dict) -> str:
    """Render a post using the standard template."""
    category = item.get("category", "news")
    emoji = CATEGORY_EMOJIS.get(category, "📰")
    tags = " ".join(CATEGORY_TAGS.get(category, ["#gaming", "#gamepulsebr"]))
    
    title = item.get("title", "Sem título")
    summary = item.get("summary", "")
    date_info = item.get("date_info", "")
    price_info = item.get("price_info", "")
    platforms = item.get("platforms", "")
    url = item.get("url", "")
    source = item.get("source", "")
    
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

def render_weekly_digest(posts: list, week_start: str, week_end: str) -> str:
    """Render weekly digest post."""
    lines = [
        f"📋 DIGEST SEMANAL {week_start} a {week_end}",
        "━━━━━━━━━━━━━━━━━━━━━━━━",
        "",
        "Melhores da semana por categoria:",
        "",
    ]
    
    by_cat = {}
    for p in posts:
        cat = p.get("category", "news")
        if cat not in by_cat:
            by_cat[cat] = []
        by_cat[cat].append(p)
    
    for cat, items in sorted(by_cat.items()):
        emoji = CATEGORY_EMOJIS.get(cat, "📰")
        lines.append(f"{emoji} {cat.upper()}")
        for item in items[:2]:  # top 2 per category
            title = item.get("title", "Sem título")[:60]
            url = item.get("url", "")
            lines.append(f"  • {title} — {url}")
        lines.append("")
    
    lines.append("#digest #semanal #gamepulsebr")
    lines.append(DISCLAIMER)
    
    return "\n".join(lines)