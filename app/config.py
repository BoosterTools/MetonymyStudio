from __future__ import annotations

APP_NAME    = "MetonymyStudio"
APP_ID      = "com.metonymystudio.app"
ORG_NAME    = "MetonymyStudio"
APP_VERSION = "1.0.0"

METONYMY_TYPES = [
    "Part for Whole",
    "Whole for Part",
    "Institution for People",
    "Place for People",
    "Instrument for Action",
    "Cause for Effect",
    "Effect for Cause",
    "Product for Producer",
    "Container for Content",
    "Material for Object",
    "Object for User",
    "Author for Work",
    "Possessor for Possessed",
    "Possessed for Possessor",
    "Controller for Controlled",
    "Time for Event",
    "Place for Institution",
    "Toponymic (Place for Object)",
    "Person for Object",
    "Place for Person",
    "Numerical Metonymy",
    "Event for People",
    "People for Event",
    "Institution for Members",
    "Person for Concept",
    "Institution for Person",
    "Other",
]

DEFAULT_SETTINGS = {
    "appearance.theme":       "Dark",
    "import.target_sheet":    "METONYMY CODING",
    "import.show_preview":    "true",
    "import.clear_after":     "true",
    "export.suffix":          "_FINAL",
    "workbook.last_path":     "",
}
