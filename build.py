"""
Build a standalone Windows executable with PyInstaller.

Usage (on Windows, with requirements-dev.txt installed):
    python build.py

Produces dist/MetonymyStudio.exe
"""
from __future__ import annotations
import shutil, sys
from pathlib import Path

ROOT       = Path(__file__).resolve().parent
APP_NAME   = "MetonymyStudio"
ENTRY      = ROOT / "app" / "main.py"
ASSETS_DIR = ROOT / "assets"
ICON_PATH  = ROOT / "assets" / "icons" / "app_icon.ico"


def main() -> int:
    try:
        import PyInstaller.__main__
    except ImportError:
        print("Run: pip install pyinstaller", file=sys.stderr)
        return 1

    for stale in ("build", "dist", f"{APP_NAME}.spec"):
        p = ROOT / stale
        if p.is_dir():  shutil.rmtree(p, ignore_errors=True)
        elif p.is_file(): p.unlink(missing_ok=True)

    sep = ";" if sys.platform == "win32" else ":"

    args = [
        str(ENTRY),
        "--name",        APP_NAME,
        "--onefile",
        "--windowed",
        "--noconfirm",
        "--add-data",    f"{ASSETS_DIR}{sep}assets",
        "--hidden-import", "openpyxl",
        "--hidden-import", "PySide6.QtSvg",
    ]
    if ICON_PATH.exists():
        args += ["--icon", str(ICON_PATH)]

    PyInstaller.__main__.run(args)
    print(f"\nBuilt: dist/{APP_NAME}.exe")
    return 0


if __name__ == "__main__":
    sys.exit(main())
