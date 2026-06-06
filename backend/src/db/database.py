"""SQLite database setup for user authentication."""
import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).parent.parent.parent / "data" / "auth.db"


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(exist_ok=True)
    conn = sqlite3.connect(str(DB_PATH), check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn


def init_db() -> None:
    """Create users table if it doesn't exist, migrate columns for existing DBs."""
    conn = get_connection()
    conn.execute("""
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT UNIQUE NOT NULL,
            name TEXT NOT NULL,
            code_id TEXT NOT NULL,
            hashed_password TEXT NOT NULL,
            software_background TEXT DEFAULT '',
            hardware_background TEXT DEFAULT '',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    # Migrate existing databases that lack background columns
    for col in ("software_background", "hardware_background"):
        try:
            conn.execute(f"ALTER TABLE users ADD COLUMN {col} TEXT DEFAULT ''")
        except Exception:
            pass  # Column already exists
    conn.commit()
    conn.close()
