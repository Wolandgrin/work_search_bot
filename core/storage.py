import sqlite3
from pathlib import Path

DB_PATH = Path(__file__).resolve().parent.parent / "seen_jobs.db"


class SeenJobsStore:
    def __init__(self, db_path: Path = DB_PATH):
        self.db_path = db_path
        self._init_db()

    def _init_db(self) -> None:
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS seen_jobs ("
                "dedup_key TEXT PRIMARY KEY, "
                "seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP"
                ")"
            )

    def filter_new(self, dedup_keys: list[str]) -> list[str]:
        if not dedup_keys:
            return []
        with sqlite3.connect(self.db_path) as conn:
            placeholders = ",".join("?" for _ in dedup_keys)
            rows = conn.execute(
                f"SELECT dedup_key FROM seen_jobs WHERE dedup_key IN ({placeholders})",
                dedup_keys,
            ).fetchall()
            existing = {row[0] for row in rows}
        return [key for key in dedup_keys if key not in existing]

    def mark_seen(self, dedup_keys: list[str]) -> None:
        if not dedup_keys:
            return
        with sqlite3.connect(self.db_path) as conn:
            conn.executemany(
                "INSERT OR IGNORE INTO seen_jobs (dedup_key) VALUES (?)",
                [(key,) for key in dedup_keys],
            )
