from __future__ import annotations
import json
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QHBoxLayout, QLabel, QListWidget, QListWidgetItem,
    QPushButton, QTextEdit, QVBoxLayout, QWidget, QFrame,
)
from app.ui.theme import SUCCESS, DANGER


class HistoryPage(QWidget):
    def __init__(self, db, workbook_service, parent: QWidget | None = None):
        super().__init__(parent)
        self._db  = db
        self._svc = workbook_service
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 20)
        root.setSpacing(14)

        title = QLabel("Import History")
        title.setObjectName("PageTitle")
        sub   = QLabel("Every JSON import is logged here for this workbook session")
        sub.setObjectName("PageSubtitle")
        root.addWidget(title)
        root.addWidget(sub)

        split = QHBoxLayout()
        split.setSpacing(14)

        # Left: list
        left = QFrame()
        left.setObjectName("Card")
        left_lay = QVBoxLayout(left)
        left_lay.setContentsMargins(14, 14, 14, 14)

        lhdr = QHBoxLayout()
        lhdr.addWidget(QLabel("Imports"))
        self._total_label = QLabel("")
        self._total_label.setObjectName("PageSubtitle")
        lhdr.addStretch(1)
        lhdr.addWidget(self._total_label)
        left_lay.addLayout(lhdr)

        self._list = QListWidget()
        self._list.currentRowChanged.connect(self._on_select)
        left_lay.addWidget(self._list)

        split.addWidget(left, 1)

        # Right: detail
        right = QFrame()
        right.setObjectName("Card")
        right_lay = QVBoxLayout(right)
        right_lay.setContentsMargins(14, 14, 14, 14)
        right_lay.setSpacing(8)
        right_lay.addWidget(QLabel("Detail"))
        self._detail = QTextEdit()
        self._detail.setReadOnly(True)
        self._detail.setPlaceholderText("Select an import to see details…")
        right_lay.addWidget(self._detail)
        split.addWidget(right, 1)

        root.addLayout(split, 1)

        # Buttons
        btn_row = QHBoxLayout()
        self._undo_btn = QPushButton("↩ Undo Last Import")
        self._undo_btn.clicked.connect(self._undo)
        btn_row.addWidget(self._undo_btn)
        btn_row.addStretch(1)
        root.addLayout(btn_row)

        self._records = []

    def refresh(self) -> None:
        if not self._svc.is_open():
            self._list.clear()
            self._records = []
            self._total_label.setText("")
            return

        self._records = self._db.list_imports(self._svc.original_path)
        self._list.clear()
        for rec in reversed(self._records):
            item = QListWidgetItem(rec.label)
            self._list.addItem(item)
        n = len(self._records)
        total_written = sum(r.records_written for r in self._records)
        self._total_label.setText(
            f"{n} import{'s' if n!=1 else ''}  ·  {total_written} rows total"
        )

    def _on_select(self, idx: int):
        if idx < 0 or idx >= len(self._records):
            return
        # list is reversed, so reverse the index
        rec = list(reversed(self._records))[idx]
        warnings = json.loads(rec.warnings or "[]")
        detail = (
            f"Import #{rec.import_number}\n"
            f"Time:     {rec.timestamp}\n"
            f"Sheet:    {rec.sheet_name}\n"
            f"Written:  {rec.records_written}\n"
            f"Skipped:  {rec.records_skipped}\n"
            f"Warnings: {len(warnings)}\n"
        )
        if warnings:
            detail += "\nWarnings:\n" + "\n".join(f"  • {w}" for w in warnings)
        self._detail.setPlainText(detail)

    def _undo(self):
        from PySide6.QtWidgets import QMessageBox
        if not self._svc.is_open():
            return
        msg = self._svc.undo()
        if msg is None:
            QMessageBox.information(self, "Nothing to undo",
                "No snapshots available to restore.")
            return
        self._db.delete_last_import(self._svc.original_path)
        self.refresh()
        QMessageBox.information(self, "Undone", msg)
