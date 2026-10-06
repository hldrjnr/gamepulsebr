# GamePulse Bot Configuration

import os
from dataclasses import dataclass
from typing import Dict, List, Set
from datetime import time

# Telegram
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "")
TELEGRAM_CHANNEL_ID = os.getenv("TELEGRAM_CHANNEL_ID", "@gamepulse_br")

# Database
DB_PATH = os.getenv("DB_PATH", "data/gamepulse.db")

# Scheduling - which categories run at which frequency
HOURLY_CATEGORIES: Set[str] = {
    "freebies",    # Epic, GOG, Prime, itch, SteamDB free
    "news",        # Gaming news sites
    "sales",       # CheapShark, Nuuvem
}

DAILY_CATEGORIES: Set[str] = HOURLY_CATEGORIES | {
    "releases",    # SteamDB releases, upcoming
    "updates",     # SteamDB major patches
    "demos",       # SteamDB demos
    "emulation",   # Emulator releases
    "hardware",    # Hardware news + deals
}

WEEKLY_CATEGORIES: Set[str] = DAILY_CATEGORIES | {
    "mods",        # NexusMods, ModDB
    "ports",       # PCGamingWiki, GitHub ports
    "repacks",     # FitGirl, DODI, ElAmigos announcements
}

# Rate limiting
MAX_POSTS_PER_CATEGORY = 5
MAX_TOTAL_POSTS_PER_RUN = 25
MIN_INTERVAL_SECONDS = 3

# Source configs
SOURCES = {
    "steamdb": {
        "releases_rss": "https://steamdb.info/rss/",
        "updates_rss": "https://steamdb.info/rss/patches/",
        "free_rss": "https://steamdb.info/rss/free/",
        "demos_rss": "https://steamdb.info/rss/demos/",
    },
    "epic": {
        "free_api": "https://api.epicgames.dev/epic/free-games",
    },
    "gog": {
        "rss": "https://www.gog.com/rss",
    },
    "prime": {
        "rss": "https://gaming.amazon.com/rss",
    },
    "itch": {
        "free_rss": "https://itch.io/games/free.rss",
    },
    "cheapshark": {
        "api": "https://www.cheapshark.com/api/1.0/deals",
    },
    "nuuvem": {
        "sale_url": "https://www.nuuvem.com/br-pt/sale",
    },
    "news_sites": {
        "vgc": "https://www.videogameschronicle.com/feed/",
        "eurogamer": "https://www.eurogamer.net/rss.xml",
        "gematsu": "https://gematsu.com/feed",
        "theverge": "https://www.theverge.com/gaming/rss/index.xml",
        "kotaku": "https://kotaku.com/rss",
        "pcgamer": "https://www.pcgamer.com/rss",
        "rockpapershotgun": "https://www.rockpapershotgun.com/rss",
        "ign": "https://feeds.ign.com/ign/games-all",
    },
    "emulators": {
        "ryujinx": "https://github.com/Ryujinx/Ryujinx/releases.atom",
        "sudachi": "https://github.com/sudachi-emu/sudachi/releases.atom",
        "pcsx2": "https://github.com/PCSX2/pcsx2/releases.atom",
        "duckstation": "https://github.com/stenzek/duckstation/releases.atom",
        "ppsspp": "https://github.com/hrydgard/ppsspp/releases.atom",
        "dolphin": "https://github.com/dolphin-emu/dolphin/releases.atom",
        "rpcs3": "https://github.com/RPCS3/rpcs3/releases.atom",
    },
    "pcgamingwiki": {
        "feed": "https://www.pcgamingwiki.com/api.php?action=feedrecentchanges&feedformat=atom",
    },
    "mods": {
        "nexus_skyrim": "https://www.nexusmods.com/skyrimspecialedition/rss/mods/updated",
        "nexus_cyberpunk": "https://www.nexusmods.com/cyberpunk2077/rss/mods/updated",
        "nexus_baldursgate3": "https://www.nexusmods.com/baldursgate3/rss/mods/updated",
        "nexus_eldenring": "https://www.nexusmods.com/eldenring/rss/mods/updated",
        "nexus_stardew": "https://www.nexusmods.com/stardewvalley/rss/mods/updated",
        "moddb": "https://www.moddb.com/rss.xml",
    },
    "repacks": {
        "fitgirl": "https://fitgirl-repacks.site/feed/",
        "dodi": "https://dodi-repacks.site/feed/",
        "elamigos": "https://elamigos.site/feed/",
    },
    "reddit": {
        "buildapcsales": "https://www.reddit.com/r/buildapcsales/.rss",
        "hardware": "https://www.reddit.com/r/hardware/.rss",
    },
}

# Category emojis and tags
CATEGORY_EMOJIS = {
    "freebies": "🆓",
    "releases": "🆕",
    "updates": "🔄",
    "demos": "🎮",
    "news": "📰",
    "sales": "🔥",
    "emulation": "📟",
    "hardware": "⚙️",
    "mods": "🛠",
    "ports": "🔧",
    "repacks": "🔓",
}

CATEGORY_TAGS = {
    "freebies": ["#grátis", "#freebie", "#free"],
    "releases": ["#lançamento", "#novojogo", "#steam"],
    "updates": ["#atualização", "#patch", "#changelog"],
    "demos": ["#demo", "#testegrátis", "#steamdemo"],
    "news": ["#notícias", "#gamingnews", "#indústria"],
    "sales": ["#promoção", "#desconto", "#steamsale"],
    "emulation": ["#emulação", "#emulator", "#retrogaming"],
    "hardware": ["#hardware", "#gpu", "#pcgaming"],
    "mods": ["#mod", "#modding", "#comunidade"],
    "ports": ["#port", "#recompilação", "#linuxgaming"],
    "repacks": ["#repack", "#fitgirl", "#dodi"],
}

DISCLAIMER = "\n⚠️ Emulação/repacks/ports: apenas notícia + link para projeto oficial. Não hospedamos arquivos."