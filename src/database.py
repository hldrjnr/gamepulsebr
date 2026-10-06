import os
import sqlite3
import hashlib
from datetime import datetime, timedelta
from contextlib import contextmanager
from pathlib import Path

DB_PATH = Path(__file__).parent.parent / "data" / "gamepulse.db"

def init_db():
    """Initialize SQLite database with required tables."""
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with sqlite3.connect(DB_PATH) as conn:
        conn.execute("""
            CREATE TABLE IF NOT EXISTS posted_items (
                id TEXT PRIMARY KEY,
                category TEXT NOT NULL,
                title TEXT NOT NULL,
                url TEXT NOT NULL,
                source TEXT NOT NULL,
                posted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_posted_category 
            ON posted_items(category)
        """)
        conn.execute("""
            CREATE INDEX IF NOT EXISTS idx_posted_date 
            ON posted_items(posted_at)
        """)
        conn.commit()

@contextmanager
def get_db():
    """Context manager for database connections."""
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    try:
        yield conn
        conn.commit()
    finally:
        conn.close()

def make_item_id(source: str, url: str, title: str) -> str:
    """Generate deterministic ID for deduplication."""
    normalized = f"{source}|{url}|{title.lower().strip()}"
    return hashlib.sha256(normalized.encode()).hexdigest()[:32]

def is_posted(item_id: str) -> bool:
    """Check if item was already posted."""
    with get_db() as conn:
        cursor = conn.execute("SELECT 1 FROM posted_items WHERE id = ?", (item_id,))
        return cursor.fetchone() is not None

def mark_posted(item_id: str, category: str, title: str, url: str, source: str):
    """Mark item as posted."""
    with get_db() as conn:
        conn.execute(
            "INSERT OR IGNORE INTO posted_items (id, category, title, url, source) VALUES (?, ?, ?, ?, ?)",
            (item_id, category, title, url, source)
        )

def cleanup_old(days: int = 30):
    """Remove entries older than specified days."""
    cutoff = datetime.now() - timedelta(days=days)
    with get_db() as conn:
        conn.execute("DELETE FROM posted_items WHERE posted_at < ?", (cutoff.isoformat(),))

def get_recent_count(category: str = None, hours: int = 24) -> int:
    """Get count of recent posts."""
    cutoff = datetime.now() - timedelta(hours=hours)
    with get_db() as conn:
        if category:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM posted_items WHERE category = ? AND posted_at > ?",
                (category, cutoff.isoformat())
            )
        else:
            cursor = conn.execute(
                "SELECT COUNT(*) FROM posted_items WHERE posted_at > ?",
                (cutoff.isoformat(),)
            )
        return cursor.fetchone()[0]

# Initialize on import
init_db()