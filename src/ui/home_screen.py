"""
home_screen.py — Landing screen for JETS.
Shows existing projects from the DB and lets you create or open one.
"""

import os
from pathlib import Path
from PyQt6.QtWidgets import (
    QWidget, QVBoxLayout, QHBoxLayout, QLabel, QPushButton,
    QListWidget, QListWidgetItem, QFileDialog, QInputDialog,
    QMessageBox, QFrame, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QFont, QIcon

from db.database import get_all_projects, create_project


class HomeScreen(QWidget):
    """
    Landing screen. Emits project_opened(project_id) when the user
    selects or creates a project.
    """
    project_opened = pyqtSignal(int)   # project_id

    def __init__(self, parent=None):
        super().__init__(parent)
        # Declare HomeScreen attributes in __init__
        self.project_list = QListWidget() # Loads from default project folder, or from a user-specified folder. Need to override the user's default project folder if they change it.

        self._build_ui()
        self._load_projects()

    # ── UI Construction ──────────────────────────────────────────────────────

    def _build_ui(self):
        root = QHBoxLayout(self)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Left brand panel ─────────────────────────────────────────────────
        brand = QFrame()
        brand.setFixedWidth(300)
        brand.setObjectName("panel")
        brand.setStyleSheet("""
            QFrame#panel {
                background-color: #111316;
                border-right: 1px solid #2E3239;
                border-radius: 0px;
            }
        """)
        brand_layout = QVBoxLayout(brand)
        brand_layout.setContentsMargins(32, 48, 32, 32)
        brand_layout.setSpacing(8)

        lbl_title = QLabel("JETS")
        lbl_title.setObjectName("title")
        lbl_title.setStyleSheet("font-size: 28px; font-weight: 800; color: #FFFFFF; letter-spacing: -1px;")

        lbl_sub = QLabel("Joe's Electrical Takeoff Software")
        lbl_sub.setObjectName("subtitle")

        brand_layout.addWidget(lbl_title)
        brand_layout.addWidget(lbl_sub)
        brand_layout.addSpacing(32)

        # ── Divider ───────────────────────────────────────────────────────────
        div = QFrame()
        div.setFrameShape(QFrame.Shape.HLine)
        div.setStyleSheet("background-color: #2E3239; max-height: 1px;")
        brand_layout.addWidget(div)
        brand_layout.addSpacing(24)

        # ── Quick tips ────────────────────────────────────────────────────────
        tips = [
            ("📁", "Projects map to folders on disk"),
            ("📐", "Set scale once per drawing"),
            ("📏", "Draw polylines to measure conduit runs"),
            ("🔌", "Click to count devices"),
        ]
        for icon, text in tips:
            row = QHBoxLayout()
            icon_lbl = QLabel(icon)
            icon_lbl.setFixedWidth(24)
            icon_lbl.setStyleSheet("font-size: 16px;")
            text_lbl = QLabel(text)
            text_lbl.setStyleSheet("color: #5A6070; font-size: 12px;")
            text_lbl.setWordWrap(True)
            row.addWidget(icon_lbl)
            row.addWidget(text_lbl)
            brand_layout.addLayout(row)
            brand_layout.addSpacing(4)

        brand_layout.addStretch()

        ver = QLabel("v0.1.0  —  alpha")
        ver.setStyleSheet("color: #3A3E47; font-size: 11px;")
        brand_layout.addWidget(ver)

        # ── Right main panel ─────────────────────────────────────────────────
        main_panel = QWidget()
        main_layout = QVBoxLayout(main_panel)
        main_layout.setContentsMargins(48, 48, 48, 48)
        main_layout.setSpacing(0)

        # Header row
        header = QHBoxLayout()
        lbl_projects = QLabel("Projects")
        lbl_projects.setStyleSheet("font-size: 18px; font-weight: 600; color: #FFFFFF;")
        header.addWidget(lbl_projects)
        header.addStretch()

        btn_new = QPushButton("+ New Project")
        btn_new.setObjectName("primary")
        btn_new.setFixedHeight(34)
        btn_new.clicked.connect(self._create_project)

        btn_change_folder = QPushButton("Change Project Folder...")
        btn_change_folder.setFixedHeight(34)
        btn_change_folder.clicked.connect(self._change_project_folder)

        header.addWidget(btn_change_folder)
        header.addSpacing(8)
        header.addWidget(btn_new)
        main_layout.addLayout(header)
        main_layout.addSpacing(16)

        # Project list
        self.project_list.setAlternatingRowColors(True)
        self.project_list.itemDoubleClicked.connect(self._open_project)
        self.project_list.setStyleSheet("""
            QListWidget::item { padding: 12px 16px; }
        """)
        main_layout.addWidget(self.project_list)
        main_layout.addSpacing(16)

        # Open button row
        btn_row = QHBoxLayout()
        btn_row.addStretch()
        self.btn_open = QPushButton("Open Selected Project →")
        self.btn_open.setObjectName("primary")
        self.btn_open.setFixedHeight(38)
        self.btn_open.setEnabled(False)
        self.btn_open.clicked.connect(self._open_selected)
        btn_row.addWidget(self.btn_open)
        main_layout.addLayout(btn_row)

        # Empty state
        self.empty_label = QLabel(
            "No projects yet.\nClick \"+ New Project\" to create your first project."
        )
        self.empty_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.empty_label.setStyleSheet("color: #5A6070; font-size: 14px; padding: 48px;")
        self.empty_label.hide()
        main_layout.addWidget(self.empty_label)

        # Wire selection state
        self.project_list.itemSelectionChanged.connect(
            lambda: self.btn_open.setEnabled(bool(self.project_list.selectedItems()))
        )

        root.addWidget(brand)
        root.addWidget(main_panel, 1)

    # ── Data ─────────────────────────────────────────────────────────────────

    def _load_projects(self):
        self.project_list.clear()
        projects = get_all_projects()
        if not projects:
            self.empty_label.show()
            self.project_list.hide()
        else:
            self.empty_label.hide()
            self.project_list.show()
            for p in projects:
                item = QListWidgetItem()
                folder_exists = Path(p["folder_path"]).exists()
                status = "" if folder_exists else "  ⚠ folder missing"
                item.setText(f"{p['name']}{status}\n{p['folder_path']}")
                item.setData(Qt.ItemDataRole.UserRole, p["id"])
                if not folder_exists:
                    item.setForeground(
                        item.foreground()  # muted — handled by stylesheet
                    )
                self.project_list.addItem(item)

    # ── Actions ──────────────────────────────────────────────────────────────

    def _create_project(self):
        name, ok = QInputDialog.getText(
            self, "New Project", "Project name:"
        )
        if not ok or not name.strip():
            return

        folder = QFileDialog.getExistingDirectory(
            self,
            "Choose or create a folder for this project",
            str(Path.home())
        )
        if not folder:
            return

        try:
            pid = create_project(name.strip(), folder)
            self._load_projects()
            self.project_opened.emit(pid)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))

    def _change_project_folder(self):
        """Register a folder as a project by browsing to it."""
        folder = QFileDialog.getExistingDirectory(
            self, "Select existing project folder", str(Path.home())
        )
        if not folder:
            return
        name = Path(folder).name
        try:
            pid = create_project(name, folder)
            self._load_projects()
            self.project_opened.emit(pid)
        except Exception as e:
            # If it already exists in DB, just open it
            from db.database import get_connection
            with get_connection() as conn:
                row = conn.execute(
                    "SELECT id FROM projects WHERE folder_path = ?", (folder,)
                ).fetchone()
                if row:
                    self.project_opened.emit(row["id"])
                else:
                    QMessageBox.critical(self, "Error", str(e))

    def _open_project(self, item: QListWidgetItem):
        pid = item.data(Qt.ItemDataRole.UserRole)
        self.project_opened.emit(pid)

    def _open_selected(self):
        items = self.project_list.selectedItems()
        if items:
            self._open_project(items[0])
