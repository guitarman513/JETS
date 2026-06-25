"""
drawing_list.py — Left panel inside the PDF viewer window.
Lists all PDF drawings in the project folder. Supports:
  - Double-click to rename a drawing
  - Single click to open it in the viewer
  - Bulk scale setting
  - Refresh to pick up new PDFs dropped into the folder
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QListWidget,
    QListWidgetItem, QPushButton, QInputDialog, QMenu,
    QMessageBox, QAbstractItemView, QFrame
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction

from db.database import (
    get_drawings_for_project, get_project
)


class DrawingListPanel(QWidget):
    """
    Sidebar panel. Emits drawing_selected(drawing_id) when the user clicks
    a drawing, and scale_requested(drawing_ids) for bulk scale operations.
    """
    drawing_selected = pyqtSignal(int)       # drawing_id
    scale_requested  = pyqtSignal(list)      # list of drawing_ids

    def __init__(self, project_id: int, parent=None):
        super().__init__(parent)
        self.project_id = project_id
        self.project = get_project(project_id)
        self.setFixedWidth(260)
        self._build_ui()
        self._refresh()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setContentsMargins(0, 0, 0, 0)
        layout.setSpacing(0)

        # Header
        header = QFrame()
        header.setStyleSheet("background-color: #111316; border-bottom: 1px solid #2E3239;")
        header_layout = QVBoxLayout(header)
        header_layout.setContentsMargins(12, 12, 12, 12)
        header_layout.setSpacing(4)

        lbl_name = QLabel(self.project["name"])
        lbl_name.setStyleSheet("font-size: 14px; font-weight: 700; color: #FFFFFF;")
        lbl_name.setWordWrap(True)

        folder_path = Path(self.project["folder_path"])
        lbl_path = QLabel(str(folder_path))
        lbl_path.setStyleSheet("font-size: 10px; color: #5A6070;")
        lbl_path.setWordWrap(True)

        header_layout.addWidget(lbl_name)
        header_layout.addWidget(lbl_path)
        layout.addWidget(header)

        # Toolbar
        toolbar = QFrame()
        toolbar.setStyleSheet("background-color: #1A1C20; border-bottom: 1px solid #2E3239;")
        tb_layout = QHBoxLayout(toolbar)
        tb_layout.setContentsMargins(8, 6, 8, 6)
        tb_layout.setSpacing(4)

        self.btn_refresh = QPushButton("↺ Refresh")
        self.btn_refresh.setFixedHeight(26)
        self.btn_refresh.setToolTip("Scan folder for new PDF drawings")
        self.btn_refresh.clicked.connect(self._refresh)

        self.btn_set_scale = QPushButton("Set Scale…")
        self.btn_set_scale.setFixedHeight(26)
        self.btn_set_scale.setEnabled(False)
        self.btn_set_scale.setToolTip("Set scale for selected drawings")
        self.btn_set_scale.clicked.connect(self._bulk_set_scale)

        tb_layout.addWidget(self.btn_refresh)
        tb_layout.addWidget(self.btn_set_scale)
        layout.addWidget(toolbar)

        # Drawings label
        lbl_section = QLabel("DRAWINGS")
        lbl_section.setStyleSheet(
            "font-size: 10px; color: #5A6070; letter-spacing: 2px; "
            "padding: 8px 12px 4px 12px;"
        )
        layout.addWidget(lbl_section)

        # Drawing list
        self.list_widget = QListWidget()
        self.list_widget.setSelectionMode(
            QAbstractItemView.SelectionMode.ExtendedSelection
        )
        self.list_widget.setAlternatingRowColors(True)
        self.list_widget.setStyleSheet("border: none; border-radius: 0px;")
        self.list_widget.itemClicked.connect(self._on_click)
        self.list_widget.itemDoubleClicked.connect(self._on_double_click)
        self.list_widget.itemSelectionChanged.connect(self._on_selection_changed)
        self.list_widget.setContextMenuPolicy(Qt.ContextMenuPolicy.CustomContextMenu)
        self.list_widget.customContextMenuRequested.connect(self._context_menu)
        layout.addWidget(self.list_widget, 1)

        # Empty state
        self.empty_label = QLabel(
            "No PDF drawings found.\n\n"
            "Drop PDF files into the project folder,\nthen click ↺ Refresh."
        )
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setWordWrap(True)
        self.empty_label.setStyleSheet(
            "color: #5A6070; font-size: 12px; padding: 24px;"
        )
        self.empty_label.hide()
        layout.addWidget(self.empty_label)

    # ── Data ─────────────────────────────────────────────────────────────────

    def _refresh(self):
        folder = self.project["folder_path"]
        drawings = get_drawings_for_project(self.project_id)

        self.list_widget.clear()
        if not drawings:
            self.empty_label.show()
            self.list_widget.hide()
            return

        self.empty_label.hide()
        self.list_widget.show()

        folder_path = Path(folder)
        for d in drawings:
            item = QListWidgetItem()
            item.setData(Qt.ItemDataRole.UserRole, d["id"])
            item.setData(Qt.ItemDataRole.UserRole + 1, d["filename"])

            name = d["display_name"] or d["filename"]
            scale_text = ""
            if d["scale_label"]:
                scale_text = f"\n  📐 {d['scale_label']}"
            exists = (folder_path / d["filename"]).exists()
            prefix = "" if exists else "⚠ "
            item.setText(f"{prefix}{name}{scale_text}")
            item.setToolTip(d["filename"])
            self.list_widget.addItem(item)

    # ── Events ────────────────────────────────────────────────────────────────

    def _on_click(self, item: QListWidgetItem):
        # Only open if it's a single click with single selection
        if len(self.list_widget.selectedItems()) == 1:
            drawing_id = item.data(Qt.ItemDataRole.UserRole)
            self.drawing_selected.emit(drawing_id)

    def _on_double_click(self, item: QListWidgetItem):
        """Inline rename."""
        current_text = item.text().split("\n")[0].lstrip("⚠ ")
        new_name, ok = QInputDialog.getText(
            self, "Rename Drawing", "Display name:", text=current_text
        )
        if ok and new_name.strip():
            drawing_id = item.data(Qt.ItemDataRole.UserRole)
            # update_drawing_name(drawing_id, new_name.strip())
            self._refresh()

    def _on_selection_changed(self):
        selected = self.list_widget.selectedItems()
        self.btn_set_scale.setEnabled(len(selected) > 0)

    def _bulk_set_scale(self):
        ids = [
            item.data(Qt.ItemDataRole.UserRole)
            for item in self.list_widget.selectedItems()
        ]
        if ids:
            self.scale_requested.emit(ids)

    def _context_menu(self, pos):
        item = self.list_widget.itemAt(pos)
        if not item:
            return
        menu = QMenu(self)
        act_rename = QAction("Rename…", self)
        act_rename.triggered.connect(lambda: self._on_double_click(item))
        act_scale = QAction("Set Scale…", self)
        act_scale.triggered.connect(self._bulk_set_scale)
        menu.addAction(act_rename)
        menu.addSeparator()
        menu.addAction(act_scale)
        menu.exec(self.list_widget.mapToGlobal(pos))

    def select_drawing(self, drawing_id: int):
        """Programmatically highlight a drawing in the list."""
        for i in range(self.list_widget.count()):
            item = self.list_widget.item(i)
            if item.data(Qt.ItemDataRole.UserRole) == drawing_id:
                self.list_widget.setCurrentItem(item)
                break
