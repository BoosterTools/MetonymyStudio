from __future__ import annotations
import os, sys
from pathlib import Path
from app.config import ORG_NAME

def get_app_data_dir() -> Path:
    override = os.environ.get("MS_DATA_DIR")
    if override:
        path = Path(override)
    elif sys.platform == "win32":
        base = os.environ.get("APPDATA") or str(Path.home())
        path = Path(base) / ORG_NAME
    else:
        path = Path.home() / f".{ORG_NAME.lower()}"
    path.mkdir(parents=True, exist_ok=True)
    return path

def get_database_path() -> Path:
    return get_app_data_dir() / "data.db"

def get_icon_path() -> Path:
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        base = Path(sys._MEIPASS)
    else:
        base = Path(__file__).resolve().parent.parent.parent
    return base / "assets" / "icons" / "app_icon.ico"
