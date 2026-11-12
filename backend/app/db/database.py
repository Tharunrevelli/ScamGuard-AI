"""
SQLite Persistence Layer with Privacy Isolation.
Strictly records metadata (timestamp, risk score, classification, latency) - NEVER raw message bodies.
Queries and deletions are isolated by anonymous client session token hash.
"""
import os
import sqlite3
import datetime
from typing import List, Dict, Any, Optional
from backend.app.config import settings


class DatabaseManager:
    """Manages SQLite connection and privacy-conscious audit schema."""

    def __init__(self, db_path: str = settings.DB_PATH):
        self.db_path = db_path
        try:
            db_dir = os.path.dirname(self.db_path)
            if db_dir:
                os.makedirs(db_dir, exist_ok=True)
            self._init_db()
        except Exception as e:
            print(f"[DatabaseManager] Database initialization warning: {e}")

    def _get_connection(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.db_path)
        conn.row_factory = sqlite3.Row
        # Enable Write-Ahead Logging for high concurrency
        conn.execute("PRAGMA journal_mode=WAL;")
        conn.execute("PRAGMA foreign_keys=ON;")
        return conn

    def _init_db(self):
        with self._get_connection() as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS detection_audit (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT UNIQUE NOT NULL,
                    session_hash TEXT NOT NULL,
                    timestamp TEXT NOT NULL,
                    source TEXT NOT NULL,
                    classification TEXT NOT NULL,
                    risk_score REAL NOT NULL,
                    model_version TEXT NOT NULL,
                    latency_ms REAL NOT NULL
                );
            """)
            conn.execute("""
                CREATE INDEX IF NOT EXISTS idx_audit_session ON detection_audit(session_hash);
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS user_feedback (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    request_id TEXT NOT NULL,
                    session_hash TEXT NOT NULL,
                    actual_label TEXT NOT NULL,
                    user_notes TEXT,
                    created_at TEXT NOT NULL,
                    FOREIGN KEY (request_id) REFERENCES detection_audit(request_id) ON DELETE CASCADE
                );
            """)
            conn.commit()

    def record_detection(
        self,
        request_id: str,
        session_hash: str,
        source: str,
        classification: str,
        risk_score: float,
        model_version: str,
        latency_ms: float
    ) -> bool:
        """Store ephemeral detection metadata (no raw text retained)."""
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO detection_audit (
                        request_id, session_hash, timestamp, source, classification, risk_score, model_version, latency_ms
                    ) VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (request_id, session_hash, now_iso, source, classification, risk_score, model_version, latency_ms))
                conn.commit()
                return True
        except Exception as e:
            print(f"[DB] Error recording audit record: {e}")
            return False

    def get_history_by_session(self, session_hash: str, limit: int = 50) -> List[Dict[str, Any]]:
        """Retrieve historical audits belonging exclusively to this session hash."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                SELECT id, request_id, timestamp, source, classification, risk_score, latency_ms
                FROM detection_audit
                WHERE session_hash = ?
                ORDER BY id DESC
                LIMIT ?
            """, (session_hash, limit))
            rows = cursor.fetchall()
            return [dict(row) for row in rows]

    def delete_history_by_session(self, session_hash: str) -> int:
        """Delete all stored records for this session."""
        with self._get_connection() as conn:
            cursor = conn.execute("""
                DELETE FROM detection_audit WHERE session_hash = ?
            """, (session_hash,))
            deleted = cursor.rowcount
            conn.commit()
            return deleted

    def record_feedback(self, request_id: str, session_hash: str, actual_label: str, user_notes: Optional[str]) -> bool:
        now_iso = datetime.datetime.now(datetime.timezone.utc).isoformat()
        try:
            with self._get_connection() as conn:
                conn.execute("""
                    INSERT INTO user_feedback (request_id, session_hash, actual_label, user_notes, created_at)
                    VALUES (?, ?, ?, ?, ?)
                """, (request_id, session_hash, actual_label, user_notes, now_iso))
                conn.commit()
                return True
        except Exception as e:
            print(f"[DB] Error recording feedback: {e}")
            return False


default_db_manager = DatabaseManager()
