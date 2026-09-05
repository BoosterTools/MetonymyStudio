from __future__ import annotations
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QComboBox, QHBoxLayout, QLabel, QLineEdit,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)


class WorkbookPage(QWidget):
    def __init__(self, workbook_service, parent: QWidget | None = None):
        super().__init__(parent)
        self._svc = workbook_service
        self._all_rows: list = []
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 20)
        root.setSpacing(14)

        title = QLabel("Workbook Viewer")
        title.setObjectName("PageTitle")
        sub   = QLabel("Browse sheets and inspect imported data")
        sub.setObjectName("PageSubtitle")
        root.addWidget(title)
        root.addWidget(sub)

        # Toolbar
        tb = QHBoxLayout()
        tb.setSpacing(10)
        tb.addWidget(QLabel("Sheet:"))
        self._sheet_combo = QComboBox()
        self._sheet_combo.setMinimumWidth(220)
        self._sheet_combo.currentTextChanged.connect(self._load_sheet)
        tb.addWidget(self._sheet_combo)

        tb.addWidget(QLabel("Search:"))
        self._search = QLineEdit()
        self._search.setPlaceholderText("Filter rows…")
        self._search.setMinimumWidth(200)
        self._search.textChanged.connect(self._filter)
        tb.addWidget(self._search)

        tb.addStretch(1)
        self._info_label = QLabel("")
        self._info_label.setObjectName("PageSubtitle")
        tb.addWidget(self._info_label)
        root.addLayout(tb)

        # Table
        self._table = QTableWidget(0, 0)
        self._table.setEditTriggers(QTableWidget.EditTrigger.NoEditTriggers)
        self._table.setSelectionBehavior(QTableWidget.SelectionBehavior.SelectRows)
        self._table.horizontalHeader().setStretchLastSection(True)
        self._table.setAlternatingRowColors(True)
        root.addWidget(self._table, 1)

    def refresh(self) -> None:
        if not self._svc.is_open():
            self._sheet_combo.clear()
            self._table.setRowCount(0)
            self._table.setColumnCount(0)
            self._info_label.setText("")
            return

        info = self._svc.info()
        current = self._sheet_combo.currentText()
        self._sheet_combo.blockSignals(True)
        self._sheet_combo.clear()
        self._sheet_combo.addItems(info.get("sheets", []))
        # Prefer METONYMY CODING
        target = "METONYMY CODING"
        if target in info.get("sheets", []):
            self._sheet_combo.setCurrentText(target)
        elif current in info.get("sheets", []):
            self._sheet_combo.setCurrentText(current)
        self._sheet_combo.blockSignals(False)
        self._load_sheet(self._sheet_combo.currentText())

    def _load_sheet(self, name: str):
        if not name or not self._svc.is_open():
            return
        headers, rows = self._svc.sheet_data(name, max_rows=500, max_cols=15)
        self._all_rows = rows[1:] if (headers and rows) else rows

        ncols = len(headers) if headers else (len(rows[0]) if rows else 0)
        self._table.setColumnCount(ncols)
        col_labels = [str(h)[:30] if h is not None else f"Col{i+1}"
                      for i, h in enumerate(headers)] if headers else [
                      f"Col{i+1}" for i in range(ncols)]
        self._table.setHorizontalHeaderLabels(col_labels)

        self._render(self._all_rows)
        for col in range(ncols):
            self._table.setColumnWidth(col, max(100, 180))

    def _render(self, rows: list):
        self._table.setRowCount(len(rows))
        for r, row in enumerate(rows):
            for c, val in enumerate(row):
                text = str(val)[:120] if val is not None else ""
                item = QTableWidgetItem(text)
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                )
                self._table.setItem(r, c, item)
        n = len(rows)
        total = len(self._all_rows)
        self._info_label.setText(
            f"{n} row{'s' if n!=1 else ''}" +
            (f" (filtered from {total})" if n != total else "")
        )

    def _filter(self, term: str):
        if not term:
            self._render(self._all_rows)
            return
        t = term.lower()
        filtered = [
            row for row in self._all_rows
            if any(t in str(v).lower() for v in row if v is not None)
        ]
        self._render(filtered)
