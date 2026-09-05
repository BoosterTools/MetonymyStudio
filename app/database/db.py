from __future__ import annotations

import json
import sqlite3
import threading
from contextlib import contextmanager
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterator, List, Optional

from app.config import DEFAULT_SETTINGS
from app.models.models import ImportRecord

SCHEMA = """
CREATE TABLE IF NOT EXISTS import_history (
    id              INTEGER PRIMARY KEY AUTOINCREMENT,
    import_number   INTEGER NOT NULL,
    workbook_path   TEXT    NOT NULL,
    sheet_name      TEXT    NOT NULL,
    records_written INTEGER NOT NULL DEFAULT 0,
    records_skipped INTEGER NOT NULL DEFAULT 0,
    warnings        TEXT    NOT NULL DEFAULT '[]',
    timestamp       TEXT    NOT NULL
);

CREATE TABLE IF NOT EXISTS settings (
    key   TEXT PRIMARY KEY,
    value TEXT NOT NULL
);
"""


def _now() -> str:
    return datetime.now(timezone.utc).isoformat(timespec="seconds")


class Database:
    def __init__(self, db_path: Path | str):
        self._lock = threading.RLock()
        self._conn = sqlite3.connect(str(db_path), check_same_thread=False)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        with self._lock, self._conn:
            self._conn.executescript(SCHEMA)
            existing = {
                r["key"]
                for r in self._conn.execute("SELECT key FROM settings")
            }
            for key, value in DEFAULT_SETTINGS.items():
                if key not in existing:
                    self._conn.execute(
                        "INSERT OR IGNORE INTO settings(key,value) VALUES(?,?)",
                        (key, value),
                    )

    @contextmanager
    def _cur(self) -> Iterator[sqlite3.Cursor]:
        with self._lock, self._conn:
            yield self._conn.cursor()

    def close(self) -> None:
        with self._lock:
            self._conn.close()

    # ── Settings ──────────────────────────────────────────────────────────────
    def get_setting(self, key: str, default: str = "") -> str:
        with self._cur() as c:
            c.execute("SELECT value FROM settings WHERE key=?", (key,))
            row = c.fetchone()
        return row["value"] if row else default

    def set_setting(self, key: str, value: str) -> None:
        with self._cur() as c:
            c.execute(
                "INSERT INTO settings(key,value) VALUES(?,?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value",
                (key, value),
            )

    # ── Import history ────────────────────────────────────────────────────────
    def add_import(
        self,
        import_number:   int,
        workbook_path:   str,
        sheet_name:      str,
        records_written: int,
        records_skipped: int,
        warnings:        list,
    ) -> ImportRecord:
        ts = _now()
        with self._cur() as c:
            c.execute(
                """INSERT INTO import_history
                   (import_number, workbook_path, sheet_name,
                    records_written, records_skipped, warnings, timestamp)
                   VALUES(?,?,?,?,?,?,?)""",
                (
                    import_number, workbook_path, sheet_name,
                    records_written, records_skipped,
                    json.dumps(warnings), ts,
                ),
            )
            rid = c.lastrowid
        return ImportRecord(
            id=rid, import_number=import_number,
            workbook_path=workbook_path, sheet_name=sheet_name,
            records_written=records_written, records_skipped=records_skipped,
            warnings=json.dumps(warnings), timestamp=ts,
        )

    def list_imports(self, workbook_path: str = "") -> List[ImportRecord]:
        with self._cur() as c:
            if workbook_path:
                c.execute(
                    "SELECT * FROM import_history WHERE workbook_path=? "
                    "ORDER BY import_number ASC",
                    (workbook_path,),
                )
            else:
                c.execute(
                    "SELECT * FROM import_history ORDER BY import_number ASC"
                )
            rows = c.fetchall()
        return [self._row_to_record(r) for r in rows]

    def delete_last_import(self, workbook_path: str) -> Optional[ImportRecord]:
        recs = self.list_imports(workbook_path)
        if not recs:
            return None
        last = recs[-1]
        with self._cur() as c:
            c.execute("DELETE FROM import_history WHERE id=?", (last.id,))
        return last

    def clear_history(self, workbook_path: str) -> None:
        with self._cur() as c:
            c.execute(
                "DELETE FROM import_history WHERE workbook_path=?",
                (workbook_path,),
            )

    @staticmethod
    def _row_to_record(row: sqlite3.Row) -> ImportRecord:
        return ImportRecord(
            id=row["id"],
            import_number=row["import_number"],
            workbook_path=row["workbook_path"],
            sheet_name=row["sheet_name"],
            records_written=row["records_written"],
            records_skipped=row["records_skipped"],
            warnings=row["warnings"],
            timestamp=row["timestamp"],
        )
