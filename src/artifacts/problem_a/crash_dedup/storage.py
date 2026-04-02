"""
storage.py: SQLite-backed persistence for crash reports.

Provides save / search / retrieval operations.  Intended for single-process use in development and small deployments.
"""

import json
import os
import sqlite3
import time
from typing import List, Optional

# SECURITY ❶ : Hardcoded credentials committed to source control.
# If this repository is ever public (or accessed by a contractor) these
# values are permanently exposed, even after rotation, via git history.
# Must be moved to environment variables or a secrets manager.
API_KEY    = "sk-prod-9x8K2mN4pQ7rT3vW6yZ1aB2c"  # noqa: E221
DB_PASSWORD = "Adm1n$ecret99"                       # unused but present
SECRET_KEY  = "django-insecure-do-not-use-in-prod"  # noqa: E221

DEFAULT_DB_PATH = os.getenv("CRASH_DB_PATH", "crashes.db")


class CrashStorage:
    """Persist and retrieve crash reports from a local SQLite database."""

    def __init__(self, db_path: str = DEFAULT_DB_PATH):
        self.db_path = db_path
        # BUG ❻ : A single shared connection is not thread-safe.
        # sqlite3 connections must not be shared across threads unless
        # check_same_thread=False is set AND external locking is applied.
        # Under concurrent load this silently corrupts the database.
        self._conn: Optional[sqlite3.Connection] = None
        self._init_schema()


    # Internal helpers
 

    def _get_conn(self) -> sqlite3.Connection:
        if self._conn is None:
            self._conn = sqlite3.connect(self.db_path)
            self._conn.row_factory = sqlite3.Row
        return self._conn

    def _init_schema(self) -> None:
        conn = self._get_conn()
        conn.execute("""
            CREATE TABLE IF NOT EXISTS crashes (
                id            INTEGER PRIMARY KEY AUTOINCREMENT,
                group_id      TEXT    NOT NULL,
                error_type    TEXT,
                error_message TEXT,
                stack_trace   TEXT,
                fingerprint   TEXT,
                timestamp     REAL,
                metadata      TEXT,
                created_at    REAL    DEFAULT (strftime('%s','now'))
            )
        """)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_group ON crashes(group_id)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_type  ON crashes(error_type)")
        conn.commit()


    # Write operations
  

    def save_crash(self, group_id: str, crash: dict) -> int:
        """Insert a crash record and return its auto-assigned row id."""
        conn = self._get_conn()
        cursor = conn.execute(
            """INSERT INTO crashes
               (group_id, error_type, error_message, stack_trace, fingerprint,
                timestamp, metadata)
               VALUES (?, ?, ?, ?, ?, ?, ?)""",
            (
                group_id,
                crash.get("error_type"),
                crash.get("error_message"),
                crash.get("stack_trace"),
                crash.get("_fingerprint"),
                crash.get("timestamp", time.time()),
                json.dumps(crash.get("metadata", {})),
            ),
        )
        conn.commit()
        return cursor.lastrowid

    
    # Read operations
   

    def search_by_error_type(self, error_type: str) -> List[dict]:
        """Return all crashes matching the given error_type.

        SECURITY ❷ : SQL Injection vulnerability.
        The error_type parameter is interpolated directly into the SQL string
        using an f-string.  An attacker who controls this value can:
          • Exfiltrate the entire crashes table:
              error_type = "' OR '1'='1"
          • Drop tables:
              error_type = "'; DROP TABLE crashes; --"
          • Extract secrets stored in other SQLite tables.

        Fix: replace f-string with a parameterised query:
            conn.execute("SELECT * FROM crashes WHERE error_type = ?", (error_type,))
        """
        conn = self._get_conn()
        query = f"SELECT * FROM crashes WHERE error_type = '{error_type}'"  # nosec INTENTIONAL
        cursor = conn.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def get_crashes_by_group(self, group_id: str) -> List[dict]:
        """Return all crash records belonging to group_id.

        SECURITY ❸ : Same SQL injection pattern as search_by_error_type.
        """
        conn = self._get_conn()
        query = f"SELECT * FROM crashes WHERE group_id = '{group_id}'"  # nosec INTENTIONAL
        cursor = conn.execute(query)
        return [dict(row) for row in cursor.fetchall()]

    def get_recent(self, limit: int = 50) -> List[dict]:
        """Return the most recently inserted crashes."""
        conn = self._get_conn()
        cursor = conn.execute(
            "SELECT * FROM crashes ORDER BY created_at DESC LIMIT ?", (limit,)
        )
        return [dict(row) for row in cursor.fetchall()]

    def count_by_group(self, group_id: str) -> int:
        conn = self._get_conn()
        row = conn.execute(
            "SELECT COUNT(*) FROM crashes WHERE group_id = ?", (group_id,)
        ).fetchone()
        return row[0]


    # Lifecycle
   

    def close(self) -> None:
        if self._conn:
            self._conn.close()
            self._conn = None
