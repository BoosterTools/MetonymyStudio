from __future__ import annotations
from app.database.db import Database


class SettingsService:
    def __init__(self, db: Database):
        self._db = db

    def get(self, key: str, default: str = "") -> str:
        return self._db.get_setting(key, default)

    def get_bool(self, key: str, default: bool = False) -> bool:
        v = self._db.get_setting(key, "true" if default else "false")
        return v.lower() in ("true", "1", "yes")

    def set(self, key: str, value: str) -> None:
        self._db.set_setting(key, value)

    def set_bool(self, key: str, value: bool) -> None:
        self._db.set_setting(key, "true" if value else "false")
