from __future__ import annotations
from PySide6.QtGui import QPalette
from PySide6.QtWidgets import QApplication

ACCENT         = "#6C5CE7"
ACCENT_HOVER   = "#7C6CF5"
ACCENT_PRESSED = "#5A4BD1"
SUCCESS        = "#00B894"
DANGER         = "#E17055"
WARN           = "#FDCB6E"

_BASE = """
* {{
    font-family: 'Segoe UI', 'Segoe UI Variable', Arial, sans-serif;
    font-size: 13px;
}}
QMainWindow, QWidget#centralWidget {{
    background: {bg};
}}
QWidget {{
    color: {text};
}}
#Sidebar {{
    background: {sidebar_bg};
    border-right: 1px solid {border};
    min-width: 220px;
    max-width: 220px;
}}
#SidebarButton {{
    text-align: left;
    padding: 10px 16px;
    border: none;
    border-radius: 8px;
    background: transparent;
    color: {sidebar_text};
    font-size: 13px;
}}
#SidebarButton:hover  {{ background: {sidebar_hover}; }}
#SidebarButton:checked {{
    background: {accent};
    color: white;
    font-weight: 600;
}}
#AppTitle {{
    font-size: 16px;
    font-weight: 700;
    padding: 18px 16px 4px 16px;
    color: {text};
}}
#AppSubtitle {{
    font-size: 11px;
    color: {muted};
    padding: 0 16px 14px 16px;
}}
#WorkbookLabel {{
    font-size: 11px;
    color: {accent};
    padding: 0 16px 6px 16px;
    font-weight: 600;
}}
QLabel#PageTitle {{
    font-size: 22px;
    font-weight: 700;
}}
QLabel#PageSubtitle {{
    color: {muted};
    font-size: 12px;
    margin-bottom: 4px;
}}
QFrame#Card {{
    background: {card_bg};
    border: 1px solid {border};
    border-radius: 12px;
}}
QLabel#CardValue {{
    font-size: 28px;
    font-weight: 700;
}}
QLabel#CardLabel {{
    color: {muted};
    font-size: 11px;
    letter-spacing: 0.5px;
}}
QLabel#StatusDot {{
    font-size: 16px;
}}
QPushButton {{
    background: {button_bg};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 8px 16px;
    color: {text};
}}
QPushButton:hover   {{ background: {button_hover}; }}
QPushButton:pressed {{ background: {button_pressed}; }}
QPushButton#Primary {{
    background: {accent};
    color: white;
    border: none;
    font-weight: 600;
    padding: 9px 20px;
}}
QPushButton#Primary:hover   {{ background: {accent_hover}; }}
QPushButton#Primary:pressed {{ background: {accent_pressed}; }}
QPushButton#Success {{
    background: {success};
    color: white;
    border: none;
    font-weight: 600;
    padding: 9px 20px;
}}
QPushButton#Danger {{
    background: transparent;
    border: 1px solid {danger};
    color: {danger};
}}
QPushButton#Danger:hover {{
    background: {danger};
    color: white;
}}
QPushButton#Toolbar {{
    background: {button_bg};
    border: 1px solid {border};
    border-radius: 6px;
    padding: 6px 14px;
    font-size: 12px;
}}
QPushButton#Toolbar:hover {{ background: {button_hover}; }}
QLineEdit, QTextEdit, QPlainTextEdit, QComboBox, QSpinBox {{
    background: {input_bg};
    border: 1px solid {border};
    border-radius: 8px;
    padding: 6px 10px;
    selection-background-color: {accent};
}}
QLineEdit:focus, QTextEdit:focus, QPlainTextEdit:focus, QComboBox:focus {{
    border: 1px solid {accent};
}}
QTableWidget {{
    background: {card_bg};
    border: 1px solid {border};
    border-radius: 10px;
    gridline-color: {border};
    outline: none;
}}
QTableWidget::item {{
    padding: 6px 8px;
    border-bottom: 1px solid {border};
}}
QTableWidget::item:selected {{
    background: {accent};
    color: white;
}}
QHeaderView::section {{
    background: {sidebar_bg};
    border: none;
    border-bottom: 2px solid {border};
    border-right: 1px solid {border};
    padding: 8px 10px;
    font-weight: 600;
    font-size: 12px;
    color: {muted};
}}
QListWidget {{
    background: {card_bg};
    border: 1px solid {border};
    border-radius: 10px;
    outline: none;
}}
QListWidget::item {{
    padding: 8px 12px;
    border-bottom: 1px solid {border};
    border-radius: 0px;
}}
QListWidget::item:selected {{
    background: {accent};
    color: white;
}}
QScrollBar:vertical {{
    background: transparent;
    width: 8px;
    margin: 0;
}}
QScrollBar::handle:vertical {{
    background: {border};
    border-radius: 4px;
    min-height: 20px;
}}
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{ height: 0; }}
QScrollBar:horizontal {{
    background: transparent;
    height: 8px;
}}
QScrollBar::handle:horizontal {{
    background: {border};
    border-radius: 4px;
}}
QTabWidget::pane {{
    border: 1px solid {border};
    border-radius: 10px;
    top: -1px;
}}
QTabBar::tab {{
    padding: 8px 18px;
    margin-right: 4px;
    border-top-left-radius: 8px;
    border-top-right-radius: 8px;
    background: {button_bg};
    border: 1px solid {border};
    border-bottom: none;
}}
QTabBar::tab:selected {{
    background: {accent};
    color: white;
    border-color: {accent};
}}
QToolTip {{
    background: {card_bg};
    color: {text};
    border: 1px solid {border};
    padding: 4px 8px;
    border-radius: 6px;
}}
QGroupBox {{
    border: 1px solid {border};
    border-radius: 10px;
    margin-top: 12px;
    padding-top: 8px;
    font-weight: 600;
}}
QGroupBox::title {{
    subcontrol-origin: margin;
    left: 12px;
    top: -6px;
    color: {muted};
    font-size: 11px;
    padding: 0 6px;
    background: {bg};
}}
QCheckBox::indicator {{
    width: 16px;
    height: 16px;
    border-radius: 4px;
    border: 1px solid {border};
    background: {input_bg};
}}
QCheckBox::indicator:checked {{
    background: {accent};
    border: 1px solid {accent};
}}
QMessageBox {{ background: {bg}; }}
QComboBox::drop-down {{ border: none; }}
QComboBox QAbstractItemView {{
    background: {card_bg};
    border: 1px solid {border};
    selection-background-color: {accent};
}}
"""

_DARK = dict(
    bg             = "#15161C",
    text           = "#EDEDF2",
    muted          = "#93939F",
    sidebar_bg     = "#1B1C24",
    sidebar_text   = "#C9CAD4",
    sidebar_hover  = "#26272F",
    border         = "#2A2B34",
    card_bg        = "#1E1F28",
    button_bg      = "#22232C",
    button_hover   = "#2B2C36",
    button_pressed = "#33343F",
    input_bg       = "#22232C",
    accent         = ACCENT,
    accent_hover   = ACCENT_HOVER,
    accent_pressed = ACCENT_PRESSED,
    success        = SUCCESS,
    danger         = DANGER,
)

_LIGHT = dict(
    bg             = "#F5F6FA",
    text           = "#1D1E24",
    muted          = "#7A7F8D",
    sidebar_bg     = "#FFFFFF",
    sidebar_text   = "#3A3D46",
    sidebar_hover  = "#F0EEFE",
    border         = "#E3E5EC",
    card_bg        = "#FFFFFF",
    button_bg      = "#FFFFFF",
    button_hover   = "#F1F2F6",
    button_pressed = "#E5E7ED",
    input_bg       = "#FFFFFF",
    accent         = ACCENT,
    accent_hover   = ACCENT_HOVER,
    accent_pressed = ACCENT_PRESSED,
    success        = "#00A67E",
    danger         = DANGER,
)


def stylesheet(dark: bool) -> str:
    return _BASE.format(**(  _DARK if dark else _LIGHT))


def system_prefers_dark() -> bool:
    app = QApplication.instance()
    if app is None:
        return True
    palette = app.palette()
    w = palette.color(QPalette.ColorRole.Window)
    return (0.299 * w.red() + 0.587 * w.green() + 0.114 * w.blue()) < 128


def apply_theme(app: QApplication, mode: str) -> None:
    m = (mode or "Dark").lower()
    if m == "light":
        dark = False
    elif m == "dark":
        dark = True
    else:
        dark = system_prefers_dark()
    app.setStyleSheet(stylesheet(dark))
