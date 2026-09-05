from __future__ import annotations
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class ImportRecord:
    id:              Optional[int]
    import_number:   int
    workbook_path:   str
    sheet_name:      str
    records_written: int
    records_skipped: int
    warnings:        str   # JSON-encoded list
    timestamp:       str

    @property
    def label(self) -> str:
        return (f"#{self.import_number:03d}  "
                f"+{self.records_written} rows  "
                f"{self.sheet_name}  "
                f"{self.timestamp[-8:][:8]}")   # HH:MM:SS


@dataclass
class MetonymyEntry:
    article_id:         str
    expression:         str
    occurrence:         int
    metonymy_type:      str
    context:            str  = ""
    source_page:        str  = ""
    literal_referent:   str  = ""
    metonymic_referent: str  = ""
    interpretation:     str  = ""
    notes:              str  = ""
