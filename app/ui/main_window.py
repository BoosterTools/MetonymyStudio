from __future__ import annotations
import os, sys
from PySide6.QtCore import QSize, Qt
from PySide6.QtGui import QCloseEvent, QColor, QIcon, QKeySequence, QPainter, QPixmap, QShortcut
from PySide6.QtWidgets import (
    QApplication, QFileDialog, QHBoxLayout, QLabel,
    QMainWindow, QMessageBox, QPushButton, QStackedWidget, QWidget,
)
from app.config import APP_NAME
from app.database.db import Database
from app.services.workbook_service import WorkbookService
from app.services.settings_service import SettingsService
from app.ui.pages.dashboard_page import DashboardPage
from app.ui.pages.import_page import ImportPage
from app.ui.pages.workbook_page import WorkbookPage
from app.ui.pages.history_page import HistoryPage
from app.ui.pages.settings_page import SettingsPage
from app.ui.theme import apply_theme, SUCCESS, DANGER, WARN
from app.ui.widgets.sidebar import Sidebar


def _build_icon() -> QIcon:
    pix = QPixmap(64, 64)
    pix.fill(Qt.GlobalColor.transparent)
    p = QPainter(pix)
    p.setRenderHint(QPainter.RenderHint.Antialiasing)
    p.setBrush(QColor("#6C5CE7"))
    p.setPen(Qt.PenStyle.NoPen)
    p.drawRoundedRect(0, 0, 64, 64, 16, 16)
    p.setPen(QColor("white"))
    f = p.font(); f.setBold(True); f.setPointSize(24); p.setFont(f)
    p.drawText(pix.rect(), Qt.AlignmentFlag.AlignCenter, "M")
    p.end()
    return QIcon(pix)


class MainWindow(QMainWindow):
    def __init__(self, db: Database, wb_service: WorkbookService,
                 settings: SettingsService):
        super().__init__()
        self._db       = db
        self._svc      = wb_service
        self._settings = settings

        self.setWindowTitle(APP_NAME)
        self.resize(1260, 820)
        self.setMinimumSize(960, 640)
        self.setWindowIcon(_build_icon())

        self._build_ui()
        self._refresh_all()

        # Global shortcuts
        QShortcut(QKeySequence("Ctrl+O"), self).activated.connect(self._open_workbook)
        QShortcut(QKeySequence("Ctrl+E"), self).activated.connect(self._export)
        QShortcut(QKeySequence("Ctrl+S"), self).activated.connect(self._save)
        QShortcut(QKeySequence("Ctrl+Z"), self).activated.connect(self._undo)

    # ── UI construction ───────────────────────────────────────────────────────
    def _build_ui(self):
        central = QWidget()
        central.setObjectName("centralWidget")
        self.setCentralWidget(central)

        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # Sidebar
        self._sidebar = Sidebar()
        self._sidebar.page_selected.connect(self._on_page)
        root.addWidget(self._sidebar)

        # Right area: toolbar + stack
        right = QWidget()
        right_lay = QHBoxLayout(right)
        right_lay.setContentsMargins(0, 0, 0, 0)
        right_lay.setSpacing(0)

        from PySide6.QtWidgets import QVBoxLayout
        right_col = QWidget()
        right_col_lay = QVBoxLayout(right_col)
        right_col_lay.setContentsMargins(0, 0, 0, 0)
        right_col_lay.setSpacing(0)

        right_col_lay.addWidget(self._build_toolbar())
        right_col_lay.addWidget(self._build_stack(), 1)

        right_lay.addWidget(right_col)
        root.addWidget(right, 1)

    def _build_toolbar(self) -> QWidget:
        tb = QWidget()
        tb.setFixedHeight(50)
        tb.setStyleSheet(
            "background: #1B1C24; border-bottom: 1px solid #2A2B34;"
        )
        lay = QHBoxLayout(tb)
        lay.setContentsMargins(16, 0, 16, 0)
        lay.setSpacing(8)

        self._wb_indicator = QLabel("No workbook open")
        self._wb_indicator.setStyleSheet("color: #93939F; font-size: 12px;")
        lay.addWidget(self._wb_indicator)

        self._status_dot = QLabel("●")
        self._status_dot.setObjectName("StatusDot")
        self._status_dot.setStyleSheet(f"color: #93939F;")
        lay.addWidget(self._status_dot)

        lay.addStretch(1)

        for text, slot, tip in [
            ("📂 Open",     self._open_workbook, "Ctrl+O"),
            ("💾 Save",     self._save,          "Ctrl+S"),
            ("↩ Undo",     self._undo,          "Ctrl+Z"),
            ("⬇ Export",   self._export,        "Ctrl+E"),
        ]:
            btn = QPushButton(text)
            btn.setObjectName("Toolbar")
            btn.setToolTip(f"{tip}")
            btn.clicked.connect(slot)
            lay.addWidget(btn)

        return tb

    def _build_stack(self) -> QStackedWidget:
        self._stack = QStackedWidget()

        dashboard_actions = {
            "open":    self._open_workbook,
            "import":  lambda: self._on_page("import"),
            "workbook":lambda: self._on_page("workbook"),
            "export":  self._export,
            "undo":    self._undo,
        }
        self._dashboard_page = DashboardPage(dashboard_actions)
        self._import_page    = ImportPage(
            self._svc, self._db, self._on_page
        )
        self._import_page.import_finished.connect(self._on_import_finished)
        self._workbook_page  = WorkbookPage(self._svc)
        self._history_page   = HistoryPage(self._db, self._svc)
        self._settings_page  = SettingsPage(
            self._settings,
            {"theme_changed": self._on_theme},
        )

        self._pages = {
            "dashboard": self._dashboard_page,
            "import":    self._import_page,
            "workbook":  self._workbook_page,
            "history":   self._history_page,
            "settings":  self._settings_page,
        }
        for page in self._pages.values():
            self._stack.addWidget(page)

        self._stack.setCurrentWidget(self._dashboard_page)
        return self._stack

    # ── Navigation ────────────────────────────────────────────────────────────
    def _on_page(self, key: str) -> None:
        page = self._pages.get(key)
        if page is None:
            return
        if key == "workbook":
            self._workbook_page.refresh()
        elif key == "history":
            self._history_page.refresh()
        elif key == "dashboard":
            self._refresh_dashboard()
        self._stack.setCurrentWidget(page)
        self._sidebar.set_active(key)

    # ── Actions ───────────────────────────────────────────────────────────────
    def _open_workbook(self) -> None:
        last = self._settings.get("workbook.last_path", "")
        path, _ = QFileDialog.getOpenFileName(
            self, "Open Workbook",
            os.path.dirname(last) if last else "",
            "Excel Files (*.xlsm *.xlsx);;All Files (*.*)",
        )
        if not path:
            return
        try:
            info = self._svc.open(path)
            self._settings.set("workbook.last_path", path)
            self._sidebar.set_workbook(info.get("filename", ""))
            self._refresh_all()
            self._on_page("import")
            self._flash_status(f"✓ Opened {info['filename']}", SUCCESS)
        except Exception as e:
            QMessageBox.critical(self, "Error opening workbook", str(e))

    def _save(self) -> None:
        if not self._svc.is_open():
            return
        self._svc.save_working()
        self._flash_status("💾 Saved", SUCCESS)
        self._update_toolbar()

    def _undo(self) -> None:
        if not self._svc.is_open():
            return
        msg = self._svc.undo()
        if msg is None:
            QMessageBox.information(self, "Nothing to undo",
                "No previous state to restore.")
            return
        self._db.delete_last_import(self._svc.original_path)
        self._refresh_all()
        self._flash_status(f"↩ {msg}", WARN)

    def _export(self) -> None:
        if not self._svc.is_open():
            QMessageBox.warning(self, "No workbook", "Open a workbook first.")
            return
        base, ext = os.path.splitext(self._svc.original_path)
        suffix = self._settings.get("export.suffix", "_FINAL")
        default_name = os.path.basename(base) + suffix + ext
        path, _ = QFileDialog.getSaveFileName(
            self, "Export Final Workbook",
            os.path.join(os.path.dirname(self._svc.original_path), default_name),
            "Excel Macro Workbook (*.xlsm);;Excel Workbook (*.xlsx)",
        )
        if not path:
            return
        try:
            self._svc.export(path)
            info = self._svc.info()
            QMessageBox.information(
                self, "Export complete",
                f"Saved: {os.path.basename(path)}\n\n"
                f"Total imports: {self._svc.import_count}\n"
                f"Data rows: {info.get('data_rows', '?')}",
            )
            self._flash_status(f"⬇ Exported: {os.path.basename(path)}", SUCCESS)
        except Exception as e:
            QMessageBox.critical(self, "Export failed", str(e))

    def _on_import_finished(self, result: dict) -> None:
        self._refresh_all()
        self._workbook_page.refresh()
        self._history_page.refresh()

    # ── Refresh helpers ───────────────────────────────────────────────────────
    def _refresh_all(self) -> None:
        self._refresh_dashboard()
        self._update_toolbar()

    def _refresh_dashboard(self) -> None:
        info = self._svc.info() if self._svc.is_open() else {}
        self._dashboard_page.refresh(
            imports  = self._svc.import_count,
            rows     = info.get("data_rows", 0),
            filename = info.get("filename", ""),
            has_wb   = self._svc.is_open(),
        )

    def _update_toolbar(self) -> None:
        if self._svc.is_open():
            info = self._svc.info()
            fname = info.get("filename", "")
            self._wb_indicator.setText(
                f"{fname}  ·  {info.get('data_rows', 0)} rows  ·  "
                f"{self._svc.import_count} import(s)"
            )
            self._wb_indicator.setStyleSheet("color: #EDEDF2; font-size: 12px;")
            color = WARN if self._svc.unsaved else SUCCESS
            self._status_dot.setStyleSheet(f"color: {color};")
            self._sidebar.set_workbook(fname)
        else:
            self._wb_indicator.setText("No workbook open  (Ctrl+O)")
            self._wb_indicator.setStyleSheet("color: #93939F; font-size: 12px;")
            self._status_dot.setStyleSheet("color: #93939F;")
            self._sidebar.set_workbook("")

    def _flash_status(self, msg: str, color: str) -> None:
        # Temporarily show a message in the toolbar indicator
        orig_text  = self._wb_indicator.text()
        orig_style = self._wb_indicator.styleSheet()
        self._wb_indicator.setText(msg)
        self._wb_indicator.setStyleSheet(
            f"color: {color}; font-size: 12px; font-weight: 600;"
        )
        from PySide6.QtCore import QTimer
        QTimer.singleShot(3000, lambda: (
            self._wb_indicator.setText(orig_text),
            self._wb_indicator.setStyleSheet(orig_style),
        ))

    # ── Theme ─────────────────────────────────────────────────────────────────
    def _on_theme(self, mode: str) -> None:
        app = QApplication.instance()
        if app:
            apply_theme(app, mode)

    # ── Close ─────────────────────────────────────────────────────────────────
    def closeEvent(self, event: QCloseEvent) -> None:
        if self._svc.is_open() and self._svc.unsaved:
            reply = QMessageBox.question(
                self, "Unsaved session",
                "Save working copy before closing?",
                QMessageBox.StandardButton.Yes |
                QMessageBox.StandardButton.No  |
                QMessageBox.StandardButton.Cancel,
            )
            if reply == QMessageBox.StandardButton.Cancel:
                event.ignore()
                return
            if reply == QMessageBox.StandardButton.Yes:
                self._svc.save_working()
        self._db.close()
        event.accept()
