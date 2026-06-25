"""
theme.py — Application-wide dark industrial stylesheet.
Palette: near-black background, steel grey panels, electric blue accent,
orange secondary accent. Monospaced readouts for measurements.
"""

APP_STYLESHEET = """
/* ── Global ──────────────────────────────────────────────────── */
QWidget {
    background-color: #1A1C20;
    color: #D4D8DE;
    font-family: "Segoe UI", "Inter", sans-serif;
    font-size: 13px;
}

QMainWindow, QDialog {
    background-color: #1A1C20;
}

/* ── Panels / Frames ──────────────────────────────────────────── */
QFrame#panel {
    background-color: #22252B;
    border: 1px solid #2E3239;
    border-radius: 4px;
}

QGroupBox {
    border: 1px solid #2E3239;
    border-radius: 4px;
    margin-top: 10px;
    padding-top: 8px;
    color: #7A8290;
    font-size: 11px;
    letter-spacing: 1px;
    text-transform: uppercase;
}
QGroupBox::title {
    subcontrol-origin: margin;
    left: 8px;
    padding: 0 4px;
}

/* ── Buttons ──────────────────────────────────────────────────── */
QPushButton {
    background-color: #2A2D34;
    color: #D4D8DE;
    border: 1px solid #3A3E47;
    border-radius: 3px;
    padding: 6px 16px;
    font-size: 13px;
}
QPushButton:hover {
    background-color: #32363F;
    border-color: #00AAFF;
    color: #FFFFFF;
}
QPushButton:pressed {
    background-color: #1E2128;
}
QPushButton#primary {
    background-color: #005FAF;
    border: 1px solid #0077CC;
    color: #FFFFFF;
    font-weight: 600;
}
QPushButton#primary:hover {
    background-color: #0077CC;
}
QPushButton#primary:pressed {
    background-color: #004A88;
}
QPushButton#accent {
    background-color: #B84C00;
    border: 1px solid #E05A00;
    color: #FFFFFF;
    font-weight: 600;
}
QPushButton#accent:hover {
    background-color: #E05A00;
}
QPushButton#danger {
    background-color: #5A1A1A;
    border: 1px solid #8B2A2A;
    color: #FF8080;
}
QPushButton#danger:hover {
    background-color: #8B2A2A;
}

/* ── Inputs ───────────────────────────────────────────────────── */
QLineEdit, QTextEdit, QPlainTextEdit, QSpinBox, QDoubleSpinBox {
    background-color: #141618;
    border: 1px solid #2E3239;
    border-radius: 3px;
    padding: 5px 8px;
    color: #D4D8DE;
    selection-background-color: #005FAF;
}
QLineEdit:focus, QTextEdit:focus, QSpinBox:focus, QDoubleSpinBox:focus {
    border-color: #00AAFF;
}
QComboBox {
    background-color: #141618;
    border: 1px solid #2E3239;
    border-radius: 3px;
    padding: 5px 8px;
    color: #D4D8DE;
}
QComboBox::drop-down { border: none; }
QComboBox QAbstractItemView {
    background-color: #22252B;
    border: 1px solid #2E3239;
    selection-background-color: #005FAF;
}

/* ── Lists & Tables ───────────────────────────────────────────── */
QListWidget, QTreeWidget, QTableWidget {
    background-color: #141618;
    border: 1px solid #2E3239;
    border-radius: 3px;
    alternate-background-color: #1A1C20;
    gridline-color: #2E3239;
}
QListWidget::item, QTreeWidget::item, QTableWidget::item {
    padding: 5px 8px;
    border-bottom: 1px solid #22252B;
}
QListWidget::item:selected, QTreeWidget::item:selected, QTableWidget::item:selected {
    background-color: #005FAF;
    color: #FFFFFF;
}
QListWidget::item:hover, QTreeWidget::item:hover, QTableWidget::item:hover {
    background-color: #2A2D34;
}
QHeaderView::section {
    background-color: #22252B;
    border: none;
    border-right: 1px solid #2E3239;
    border-bottom: 1px solid #2E3239;
    padding: 5px 8px;
    color: #7A8290;
    font-size: 11px;
    letter-spacing: 1px;
    text-transform: uppercase;
}

/* ── Tabs ─────────────────────────────────────────────────────── */
QTabWidget::pane {
    border: 1px solid #2E3239;
    background-color: #1A1C20;
}
QTabBar::tab {
    background-color: #141618;
    border: 1px solid #2E3239;
    border-bottom: none;
    padding: 6px 16px;
    color: #7A8290;
}
QTabBar::tab:selected {
    background-color: #1A1C20;
    color: #D4D8DE;
    border-top: 2px solid #00AAFF;
}
QTabBar::tab:hover:!selected {
    background-color: #22252B;
    color: #AAAAAA;
}

/* ── Scroll Bars ──────────────────────────────────────────────── */
QScrollBar:vertical {
    background: #141618;
    width: 10px;
    border: none;
}
QScrollBar::handle:vertical {
    background: #3A3E47;
    border-radius: 5px;
    min-height: 20px;
}
QScrollBar::handle:vertical:hover { background: #00AAFF; }
QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical { height: 0px; }
QScrollBar:horizontal {
    background: #141618;
    height: 10px;
    border: none;
}
QScrollBar::handle:horizontal {
    background: #3A3E47;
    border-radius: 5px;
    min-width: 20px;
}
QScrollBar::handle:horizontal:hover { background: #00AAFF; }
QScrollBar::add-line:horizontal, QScrollBar::sub-line:horizontal { width: 0px; }

/* ── Splitter ─────────────────────────────────────────────────── */
QSplitter::handle {
    background-color: #2E3239;
}
QSplitter::handle:hover {
    background-color: #00AAFF;
}

/* ── Status Bar ───────────────────────────────────────────────── */
QStatusBar {
    background-color: #111316;
    border-top: 1px solid #2E3239;
    color: #7A8290;
    font-size: 12px;
}
QStatusBar::item { border: none; }

/* ── Toolbar ──────────────────────────────────────────────────── */
QToolBar {
    background-color: #22252B;
    border-bottom: 1px solid #2E3239;
    spacing: 4px;
    padding: 4px;
}
QToolButton {
    background: transparent;
    border: 1px solid transparent;
    border-radius: 3px;
    padding: 4px 8px;
    color: #D4D8DE;
}
QToolButton:hover {
    background-color: #32363F;
    border-color: #3A3E47;
}
QToolButton:checked {
    background-color: #005FAF;
    border-color: #0077CC;
}

/* ── Measurement Label ────────────────────────────────────────── */
QLabel#measurement {
    font-family: "Consolas", "Courier New", monospace;
    font-size: 14px;
    color: #00AAFF;
    padding: 2px 6px;
    background-color: #0D1117;
    border: 1px solid #1E3A5A;
    border-radius: 3px;
}
QLabel#title {
    font-size: 22px;
    font-weight: 700;
    color: #FFFFFF;
    letter-spacing: -0.5px;
}
QLabel#subtitle {
    font-size: 12px;
    color: #5A6070;
    letter-spacing: 2px;
    text-transform: uppercase;
}

/* ── Tooltip ──────────────────────────────────────────────────── */
QToolTip {
    background-color: #22252B;
    border: 1px solid #3A3E47;
    color: #D4D8DE;
    padding: 4px 8px;
}
"""
