from __future__ import annotations
from typing import Callable
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QFrame, QGridLayout, QHBoxLayout, QLabel,
    QPushButton, QVBoxLayout, QWidget,
)


def _card(label: str) -> tuple[QFrame, QLabel]:
    frame = QFrame()
    frame.setObjectName("Card")
    lay = QVBoxLayout(frame)
    lay.setContentsMargins(20, 16, 20, 16)
    val = QLabel("—")
    val.setObjectName("CardValue")
    cap = QLabel(label)
    cap.setObjectName("CardLabel")
    lay.addWidget(val)
    lay.addWidget(cap)
    return frame, val


class DashboardPage(QWidget):
    def __init__(self, actions: dict[str, Callable], parent: QWidget | None = None):
        super().__init__(parent)
        self.actions = actions

        root = QVBoxLayout(self)
        root.setContentsMargins(32, 28, 32, 28)
        root.setSpacing(20)

        title = QLabel("Dashboard")
        title.setObjectName("PageTitle")
        sub   = QLabel("MetonymyStudio — open once, import endlessly, export once")
        sub.setObjectName("PageSubtitle")
        root.addWidget(title)
        root.addWidget(sub)

        # KPI cards
        grid = QGridLayout()
        grid.setSpacing(14)

        self._c_imports, self._v_imports = _card("JSON Imports This Session")
        self._c_rows,    self._v_rows    = _card("Total Rows in METONYMY CODING")
        self._c_wb,      self._v_wb      = _card("Active Workbook")
        self._c_status,  self._v_status  = _card("Session Status")

        grid.addWidget(self._c_imports, 0, 0)
        grid.addWidget(self._c_rows,    0, 1)
        grid.addWidget(self._c_wb,      1, 0)
        grid.addWidget(self._c_status,  1, 1)
        root.addLayout(grid)

        # Workflow
        wf_label = QLabel("Workflow")
        wf_label.setObjectName("PageSubtitle")
        root.addWidget(wf_label)

        wf_card = QFrame()
        wf_card.setObjectName("Card")
        wf_lay  = QHBoxLayout(wf_card)
        wf_lay.setContentsMargins(20, 14, 20, 14)
        wf_lay.setSpacing(8)
        for step in [
            "① Open Workbook",
            "→",
            "② Paste JSON",
            "→",
            "③ Import",
            "→",
            "④ Repeat",
            "→",
            "⑤ Export Final",
        ]:
            lbl = QLabel(step)
            lbl.setObjectName("CardLabel" if step == "→" else "")
            if step not in ("→",):
                lbl.setStyleSheet("font-weight: 600; font-size: 12px;")
            wf_lay.addWidget(lbl)
        wf_lay.addStretch(1)
        root.addWidget(wf_card)

        # Quick actions
        qa_label = QLabel("Quick Actions")
        qa_label.setObjectName("PageSubtitle")
        root.addWidget(qa_label)

        qa_row = QHBoxLayout()
        qa_row.setSpacing(10)
        for text, key, style in [
            ("📂 Open Workbook",  "open",    "Primary"),
            ("⬆ Import JSON",    "import",  "Primary"),
            ("📊 View Workbook",  "workbook",""),
            ("⬇ Export Final",   "export",  "Success"),
            ("↩ Undo Last",      "undo",    ""),
        ]:
            btn = QPushButton(text)
            if style:
                btn.setObjectName(style)
            btn.clicked.connect(actions.get(key, lambda: None))
            qa_row.addWidget(btn)
        qa_row.addStretch(1)
        root.addLayout(qa_row)

        root.addStretch(1)

    def refresh(self, imports: int, rows: int, filename: str, has_wb: bool) -> None:
        self._v_imports.setText(str(imports))
        self._v_rows.setText(str(rows) if has_wb else "—")
        self._v_wb.setText(filename if filename else "None")
        self._v_status.setText(
            "● Working" if has_wb else "○ No workbook"
        )
