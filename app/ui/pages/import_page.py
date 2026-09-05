from __future__ import annotations
import json
from typing import Callable
from PySide6.QtCore import Qt, QThread, Signal
from PySide6.QtWidgets import (
    QFrame, QHBoxLayout, QLabel, QMessageBox,
    QPlainTextEdit, QPushButton, QSizePolicy,
    QTableWidget, QTableWidgetItem, QVBoxLayout, QWidget,
)
from app.ui.theme import ACCENT, SUCCESS, DANGER, WARN


class _ImportWorker(QThread):
    done = Signal(dict)

    def __init__(self, service, entries):
        super().__init__()
        self._service = service
        self._entries = entries

    def run(self):
        result = self._service.import_entries(self._entries)
        self.done.emit(result)


class ImportPage(QWidget):
    import_finished = Signal(dict)   # emitted after every successful import

    def __init__(
        self,
        workbook_service,
        db,
        on_nav: Callable[[str], None],
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._svc    = workbook_service
        self._db     = db
        self._nav    = on_nav
        self._worker = None
        self._build()

    def _build(self):
        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 20)
        root.setSpacing(14)

        # Title
        title = QLabel("Import JSON")
        title.setObjectName("PageTitle")
        sub   = QLabel(
            "Paste JSON from your AI assistant → Validate → Import → Paste again"
        )
        sub.setObjectName("PageSubtitle")
        root.addWidget(title)
        root.addWidget(sub)

        # Status banner
        self._banner = QLabel("")
        self._banner.setObjectName("Card")
        self._banner.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self._banner.setVisible(False)
        self._banner.setFixedHeight(36)
        root.addWidget(self._banner)

        # Editor + preview — side by side
        split = QHBoxLayout()
        split.setSpacing(14)

        # ── Left: JSON editor ──────────────────────────────────────────────
        editor_frame = QFrame()
        editor_frame.setObjectName("Card")
        editor_lay = QVBoxLayout(editor_frame)
        editor_lay.setContentsMargins(16, 14, 16, 14)
        editor_lay.setSpacing(10)

        hdr_row = QHBoxLayout()
        hdr_row.addWidget(QLabel("JSON Input"))
        self._valid_label = QLabel("")
        self._valid_label.setAlignment(Qt.AlignmentFlag.AlignRight)
        hdr_row.addWidget(self._valid_label)
        editor_lay.addLayout(hdr_row)

        self._editor = QPlainTextEdit()
        self._editor.setPlaceholderText(
            'Paste JSON here  (Ctrl+V)\n\n'
            'Accepted formats:\n'
            '{ "entries": [ { ... }, { ... } ] }\n'
            '[ { ... }, { ... } ]\n'
            '{ "article_id": "A01", "expression": "...", ... }'
        )
        self._editor.setLineWrapMode(QPlainTextEdit.LineWrapMode.NoWrap)
        self._editor.textChanged.connect(self._on_text_changed)
        editor_lay.addWidget(self._editor)

        # Button row
        btn_row = QHBoxLayout()
        btn_row.setSpacing(8)
        self._paste_btn    = self._btn("📋 Paste",    self._paste,    "Toolbar")
        self._validate_btn = self._btn("✓ Validate",  self._validate, "Toolbar")
        self._preview_btn  = self._btn("👁 Preview",  self._preview,  "Toolbar")
        self._clear_btn    = self._btn("✕ Clear",     self._clear,    "Toolbar")
        self._import_btn   = self._btn("⬆  IMPORT",  self._do_import,"Primary")
        self._import_btn.setEnabled(False)

        for b in [self._paste_btn, self._validate_btn,
                  self._preview_btn, self._clear_btn]:
            btn_row.addWidget(b)
        btn_row.addStretch(1)
        btn_row.addWidget(self._import_btn)
        editor_lay.addLayout(btn_row)

        hint = QLabel("Ctrl+V = Paste   Ctrl+Return = Import   Ctrl+Z = Undo")
        hint.setObjectName("PageSubtitle")
        editor_lay.addWidget(hint)

        split.addWidget(editor_frame, 3)

        # ── Right: Preview table ───────────────────────────────────────────
        preview_frame = QFrame()
        preview_frame.setObjectName("Card")
        preview_lay = QVBoxLayout(preview_frame)
        preview_lay.setContentsMargins(16, 14, 16, 14)
        preview_lay.setSpacing(8)

        phdr = QHBoxLayout()
        phdr.addWidget(QLabel("Preview"))
        self._count_label = QLabel("0 entries")
        self._count_label.setObjectName("PageSubtitle")
        phdr.addStretch(1)
        phdr.addWidget(self._count_label)
        preview_lay.addLayout(phdr)

        self._table = QTableWidget(0, 4)
        self._table.setHorizontalHeaderLabels(
            ["Article ID", "Expression", "Type", "Occ."]
        )
        self._table.horizontalHeader().setStretchLastSection(False)
        self._table.setColumnWidth(0, 80)
        self._table.setColumnWidth(1, 200)
        self._table.setColumnWidth(2, 160)
        self._table.setColumnWidth(3, 50)
        self._table.setEditTriggers(
            QTableWidget.EditTrigger.NoEditTriggers
        )
        self._table.setSelectionBehavior(
            QTableWidget.SelectionBehavior.SelectRows
        )
        preview_lay.addWidget(self._table)
        split.addWidget(preview_frame, 2)

        root.addLayout(split, 1)

        # Result row at bottom
        result_row = QHBoxLayout()
        self._result_label = QLabel("")
        result_row.addWidget(self._result_label)
        result_row.addStretch(1)
        nav_wb = QPushButton("View Workbook →")
        nav_wb.setObjectName("Toolbar")
        nav_wb.clicked.connect(lambda: self._nav("workbook"))
        result_row.addWidget(nav_wb)
        root.addLayout(result_row)

        # Shortcuts
        from PySide6.QtGui import QKeySequence, QShortcut
        QShortcut(QKeySequence("Ctrl+Return"), self).activated.connect(
            self._do_import
        )

    # ── Helpers ───────────────────────────────────────────────────────────────
    @staticmethod
    def _btn(text, slot, obj="") -> QPushButton:
        b = QPushButton(text)
        if obj:
            b.setObjectName(obj)
        b.clicked.connect(slot)
        return b

    def _text(self) -> str:
        return self._editor.toPlainText().strip()

    def _on_text_changed(self):
        self._valid_label.setText("")
        self._import_btn.setEnabled(False)
        self._table.setRowCount(0)
        self._count_label.setText("0 entries")

    def _paste(self):
        cb = self._editor.createStandardContextMenu()
        self._editor.paste()

    def _clear(self):
        self._editor.clear()
        self._table.setRowCount(0)
        self._count_label.setText("0 entries")
        self._valid_label.setText("")
        self._import_btn.setEnabled(False)
        self._hide_banner()

    def _validate(self) -> list | None:
        txt = self._text()
        if not txt:
            self._valid_label.setText(
                f'<span style="color:{WARN}">⚠ No JSON pasted</span>'
            )
            return None

        entries, err = self._svc.parse_json(txt)
        if err:
            self._valid_label.setText(
                f'<span style="color:{DANGER}">✕ {err[:70]}</span>'
            )
            self._import_btn.setEnabled(False)
            return None

        n = len(entries)
        self._valid_label.setText(
            f'<span style="color:{SUCCESS}">✓ Valid — {n} entr{"y" if n==1 else "ies"}</span>'
        )
        self._import_btn.setEnabled(True)
        self._fill_preview(entries)
        return entries

    def _preview(self):
        self._validate()

    def _fill_preview(self, entries: list):
        self._table.setRowCount(len(entries))
        self._count_label.setText(f"{len(entries)} entr{'y' if len(entries)==1 else 'ies'}")
        for i, e in enumerate(entries):
            vals = [
                str(e.get("article_id",  "")),
                str(e.get("expression",   ""))[:60],
                str(e.get("type",        "")),
                str(e.get("occurrence",  "")),
            ]
            for col, val in enumerate(vals):
                item = QTableWidgetItem(val)
                item.setTextAlignment(
                    Qt.AlignmentFlag.AlignLeft | Qt.AlignmentFlag.AlignVCenter
                )
                self._table.setItem(i, col, item)

    def _do_import(self):
        if not self._svc.is_open():
            QMessageBox.warning(self, "No workbook",
                "Open a workbook first (Dashboard → Open Workbook).")
            return
        entries = self._validate()
        if not entries:
            return

        warnings = self._svc.validate_entries(entries)
        if warnings:
            reply = QMessageBox.question(
                self, "Warnings",
                f"{len(warnings)} warning(s):\n\n" +
                "\n".join(warnings[:8]) +
                "\n\nImport anyway?",
                QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No,
            )
            if reply != QMessageBox.StandardButton.Yes:
                return

        self._import_btn.setEnabled(False)
        self._show_banner("Importing…", WARN)

        self._worker = _ImportWorker(self._svc, entries)
        self._worker.done.connect(self._on_done)
        self._worker.start()

    def _on_done(self, result: dict):
        self._import_btn.setEnabled(True)
        if "error" in result:
            self._show_banner(f"✕ {result['error']}", DANGER)
            QMessageBox.critical(self, "Import failed", result["error"])
            return

        w = result["written"]
        s = result["skipped"]
        n = result["import_number"]

        # Log to DB
        self._db.add_import(
            import_number   = n,
            workbook_path   = self._svc.original_path,
            sheet_name      = result.get("sheet", "METONYMY CODING"),
            records_written = w,
            records_skipped = s,
            warnings        = result.get("warnings", []),
        )

        msg = f"✓  Import #{n} — {w} row{'s' if w != 1 else ''} added"
        if s:
            msg += f"  ({s} skipped)"
        self._show_banner(msg, SUCCESS)
        self._result_label.setText(
            f"Total rows in METONYMY CODING: {result['total_data_rows']}"
        )
        self._editor.clear()
        self._table.setRowCount(0)
        self._count_label.setText("0 entries")
        self._valid_label.setText("")
        self.import_finished.emit(result)

        if result.get("warnings"):
            QMessageBox.warning(
                self, "Import warnings",
                "\n".join(result["warnings"][:10]),
            )

    def _show_banner(self, msg: str, color: str):
        self._banner.setText(msg)
        self._banner.setStyleSheet(
            f"background: {color}22; border: 1px solid {color}; "
            f"color: {color}; border-radius: 8px; font-weight: 600;"
        )
        self._banner.setVisible(True)

    def _hide_banner(self):
        self._banner.setVisible(False)
