# MetonymyStudio

**A persistent JSON → Excel workspace for Kurdish–English metonymy research.**

Built in the same architecture as the Personal Text Manager — PySide6, SQLite, modular structure, dark/light theme.

> Open once. Import endlessly. Export once.

---

## Installation

**1. Install Python 3.11+** from https://python.org  
   *(tick "Add Python to PATH" during installation)*

**2. Install dependencies:**
```
pip install PySide6 openpyxl
```

---

## Run

**Double-click `run.bat`**

Or from Command Prompt:
```
python -m app.main
```

---

## Workflow

| Step | Action |
|------|--------|
| ① | Click **Open Workbook** (or Ctrl+O) → select `.xlsm` file |
| ② | Go to **Import JSON** → paste your JSON (Ctrl+V) |
| ③ | Click **IMPORT** (or Ctrl+Enter) |
| ④ | Paste next JSON → Import again |
| ⑤ | Repeat 10, 50, 100+ times — same workbook stays open |
| ⑥ | Click **Export** (Ctrl+E) → save final `.xlsm` |

---

## Pages

| Page | Purpose |
|------|---------|
| 🏠 Dashboard | Overview — KPI cards, quick actions, workflow guide |
| ⬆ Import JSON | Paste JSON, validate, preview, import |
| 📊 Workbook Viewer | Browse all sheets, filter rows |
| 🕐 Import History | Full log of every import; undo last |
| ⚙️ Settings | Theme, import/export preferences |

---

## Keyboard shortcuts

| Shortcut | Action |
|----------|--------|
| Ctrl+O | Open workbook |
| Ctrl+V | Paste JSON |
| Ctrl+Enter | Import JSON |
| Ctrl+Z | Undo last import |
| Ctrl+S | Save working copy |
| Ctrl+E | Export final workbook |

---

## JSON format

```json
{
  "entries": [
    {
      "article_id":         "A01",
      "expression":         "بانکی ناوەندیی عێراق",
      "occurrence":         4,
      "type":               "Institution for People",
      "context":            "فرۆشتنی دراوی بیانی لە لایەن بانکی ناوەندیی عێراقەوە",
      "literal_referent":   "The Central Bank of Iraq",
      "metonymic_referent": "The officials and policymakers of the Central Bank",
      "interpretation":     "Institution name refers to its human agents.",
      "notes":              ""
    }
  ]
}
```

**Required:** `article_id`, `expression`, `occurrence`, `type`

Also accepted: bare array `[{...}, {...}]` or single entry `{...}`

---

## Files created

| File | Purpose |
|------|---------|
| `YourFile_working.xlsm` | Safe working copy (all imports go here) |
| `YourFile_FINAL.xlsm` | Exported final file |
| `~/.MetonymyStudio/data.db` | SQLite — settings + import history |

The original file is **never modified**.

---

## Build Windows .exe

```
pip install pyinstaller
python build.py
```

Produces `dist/MetonymyStudio.exe` — no Python installation required on target PC.

---

## Project structure

```
MS2/
├── app/
│   ├── main.py                  Entry point
│   ├── config.py                Constants, metonymy types
│   ├── database/db.py           SQLite — history & settings
│   ├── models/models.py         Data classes
│   ├── services/
│   │   ├── workbook_service.py  All Excel operations
│   │   └── settings_service.py  Settings helpers
│   └── ui/
│       ├── theme.py             Dark/light QSS theme
│       ├── main_window.py       Main window + toolbar
│       ├── widgets/sidebar.py   Navigation sidebar
│       └── pages/
│           ├── dashboard_page.py
│           ├── import_page.py
│           ├── workbook_page.py
│           ├── history_page.py
│           └── settings_page.py
├── tests/
│   └── test_workbook_service.py
├── requirements.txt
├── build.py
└── run.bat
```
