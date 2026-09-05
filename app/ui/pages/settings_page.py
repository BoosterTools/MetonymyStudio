from __future__ import annotations
from typing import Callable
from PySide6.QtWidgets import (
    QCheckBox, QComboBox, QGroupBox, QHBoxLayout,
    QLabel, QPushButton, QScrollArea, QVBoxLayout, QWidget, QFrame,
)


class SettingsPage(QWidget):
    def __init__(
        self,
        settings_service,
        callbacks: dict[str, Callable],
        parent: QWidget | None = None,
    ):
        super().__init__(parent)
        self._svc       = settings_service
        self._callbacks = callbacks
        self._build()

    def _build(self):
        outer = QVBoxLayout(self)
        outer.setContentsMargins(0, 0, 0, 0)

        scroll = QScrollArea()
        scroll.setWidgetResizable(True)
        scroll.setFrameShape(QFrame.Shape.NoFrame)
        outer.addWidget(scroll)

        content = QWidget()
        scroll.setWidget(content)
        lay = QVBoxLayout(content)
        lay.setContentsMargins(32, 28, 32, 28)
        lay.setSpacing(16)

        title = QLabel("Settings")
        title.setObjectName("PageTitle")
        lay.addWidget(title)

        lay.addWidget(self._build_appearance())
        lay.addWidget(self._build_import())
        lay.addWidget(self._build_export())
        lay.addStretch(1)

    def _build_appearance(self) -> QGroupBox:
        box = QGroupBox("Appearance")
        v   = QVBoxLayout(box)
        row = QHBoxLayout()
        row.addWidget(QLabel("Theme:"))
        self._theme_combo = QComboBox()
        self._theme_combo.addItems(["Dark", "Light", "System"])
        self._theme_combo.setCurrentText(
            self._svc.get("appearance.theme", "Dark")
        )
        self._theme_combo.currentTextChanged.connect(self._on_theme_changed)
        row.addWidget(self._theme_combo)
        row.addStretch(1)
        v.addLayout(row)
        return box

    def _build_import(self) -> QGroupBox:
        box = QGroupBox("Import")
        v   = QVBoxLayout(box)
        self._preview_check = QCheckBox(
            "Show preview table before import"
        )
        self._preview_check.setChecked(
            self._svc.get_bool("import.show_preview", True)
        )
        self._preview_check.toggled.connect(
            lambda c: self._svc.set_bool("import.show_preview", c)
        )
        v.addWidget(self._preview_check)

        self._clear_check = QCheckBox(
            "Clear JSON editor after successful import"
        )
        self._clear_check.setChecked(
            self._svc.get_bool("import.clear_after", True)
        )
        self._clear_check.toggled.connect(
            lambda c: self._svc.set_bool("import.clear_after", c)
        )
        v.addWidget(self._clear_check)
        return box

    def _build_export(self) -> QGroupBox:
        box = QGroupBox("Export")
        v   = QVBoxLayout(box)
        row = QHBoxLayout()
        row.addWidget(QLabel("Default filename suffix:"))
        from PySide6.QtWidgets import QLineEdit
        self._suffix_edit = QLineEdit(self._svc.get("export.suffix", "_FINAL"))
        self._suffix_edit.setMaximumWidth(160)
        self._suffix_edit.textChanged.connect(
            lambda t: self._svc.set("export.suffix", t)
        )
        row.addWidget(self._suffix_edit)
        row.addStretch(1)
        v.addLayout(row)
        return box

    def _on_theme_changed(self, mode: str) -> None:
        self._svc.set("appearance.theme", mode)
        cb = self._callbacks.get("theme_changed")
        if cb:
            cb(mode)
