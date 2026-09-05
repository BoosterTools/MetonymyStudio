from __future__ import annotations
from PySide6.QtCore import Signal
from PySide6.QtWidgets import QButtonGroup, QLabel, QPushButton, QVBoxLayout, QWidget
from app.config import APP_NAME

PAGES = [
    ("dashboard", "🏠  Dashboard"),
    ("import",    "⬆  Import JSON"),
    ("workbook",  "📊  Workbook Viewer"),
    ("history",   "🕐  Import History"),
    ("settings",  "⚙️  Settings"),
]


class Sidebar(QWidget):
    page_selected = Signal(str)

    def __init__(self, parent: QWidget | None = None):
        super().__init__(parent)
        self.setObjectName("Sidebar")

        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 12)
        layout.setSpacing(2)

        t = QLabel(APP_NAME)
        t.setObjectName("AppTitle")
        layout.addWidget(t)

        s = QLabel("JSON → Excel Workspace")
        s.setObjectName("AppSubtitle")
        layout.addWidget(s)

        self._wb_label = QLabel("No workbook open")
        self._wb_label.setObjectName("WorkbookLabel")
        self._wb_label.setWordWrap(True)
        layout.addWidget(self._wb_label)

        self._group   = QButtonGroup(self)
        self._group.setExclusive(True)
        self._buttons: dict[str, QPushButton] = {}

        for key, label in PAGES:
            btn = QPushButton(label)
            btn.setObjectName("SidebarButton")
            btn.setCheckable(True)
            btn.clicked.connect(lambda _c, k=key: self.page_selected.emit(k))
            layout.addWidget(btn)
            self._group.addButton(btn)
            self._buttons[key] = btn

        layout.addStretch(1)
        self._buttons["dashboard"].setChecked(True)

    def set_active(self, key: str) -> None:
        btn = self._buttons.get(key)
        if btn:
            btn.setChecked(True)

    def set_workbook(self, name: str) -> None:
        self._wb_label.setText(f"📁 {name}" if name else "No workbook open")
