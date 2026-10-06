import sqlite3
import hashlib
from datetime import datetime, timedelta
from contextlib import contextmanager
from pathlib import Path
from typing import Optional, List, Dict

from src.config import DB_PATH as DB_PATH_STR

DB_PATH = Path(DB_PATH_STR)

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
        conn.execute("""
            CREATE TABLE IF NOT EXISTS run_log (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                run_type TEXT NOT NULL,
                category TEXT,
                items_found INTEGER DEFAULT 0,
                items_posted INTEGER DEFAULT 0,
                error TEXT,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
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

def get_recent_posts(hours: int = 168, category: Optional[str] = None) -> List[Dict]:
    """Get recent posts for digest."""
    cutoff = datetime.now() - timedelta(hours=hours)
    with get_db() as conn:
        if category:
            cursor = conn.execute(
                "SELECT * FROM posted_items WHERE category = ? AND posted_at > ? ORDER BY posted_at DESC",
                (category, cutoff.isoformat())
            )
        else:
            cursor = conn.execute(
                "SELECT * FROM posted_items WHERE posted_at > ? ORDER BY posted_at DESC",
                (cutoff.isoformat(),)
            )
        return [dict(row) for row in cursor.fetchall()]

def log_run(run_type: str, category: str = None, items_found: int = 0, items_posted: int = 0, error: str = None):
    """Log a run for monitoring."""
    with get_db() as conn:
        conn.execute(
            "INSERT INTO run_log (run_type, category, items_found, items_posted, error) VALUES (?, ?, ?, ?, ?)",
            (run_type, category, items_found, items_posted, error)
        )

# Initialize on import
init_db()