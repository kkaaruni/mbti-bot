import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parents[2] / "data" / "server_mbti_stats.db"


def get_db():
    return sqlite3.connect(DB_PATH)


def init_db():
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    with get_db() as conn:
        conn.execute(
            """
            CREATE TABLE IF NOT EXISTS mbti_results (
                guild_id TEXT NOT NULL,
                user_id TEXT NOT NULL,
                mbti TEXT NOT NULL,
                PRIMARY KEY (guild_id, user_id)
            )
            """
        )
        conn.commit()


def load_server_stats():
    init_db()

    with get_db() as conn:
        rows = conn.execute("SELECT guild_id, user_id, mbti FROM mbti_results").fetchall()

    stats = {}
    for guild_id, user_id, mbti in rows:
        stats.setdefault(guild_id, {})[user_id] = mbti

    return stats


def record_server_mbti(guild_id, user_id, mbti):
    init_db()

    with get_db() as conn:
        conn.execute(
            "INSERT OR REPLACE INTO mbti_results (guild_id, user_id, mbti) VALUES (?, ?, ?)",
            (str(guild_id), str(user_id), str(mbti)),
        )
        conn.commit()


def get_server_member_mbti(guild_id, user_id):
    init_db()

    with get_db() as conn:
        row = conn.execute(
            "SELECT mbti FROM mbti_results WHERE guild_id = ? AND user_id = ?",
            (str(guild_id), str(user_id)),
        ).fetchone()

    return row[0] if row else None
