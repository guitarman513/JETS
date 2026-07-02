"""
project browser.py — Landing screen for JETS.
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

from models.jets import JetsConfig, RecentPath
from models.project import ProjectInfo, ProjectManager, get_projects_infos

from a_constants import *

# from db.database import get_all_projects, create_project


class ProjectBrowser(QWidget):
    """
    Landing screen. Emits project_opened(project_info:ProjectInfo) when the user
    selects or creates a project.
    """
    project_opened = pyqtSignal(object)

    def __init__(self, jets_config:JetsConfig, parent=None):
        super().__init__(parent)
        # Declare HomeScreen attributes in __init__
        self.jets_config:JetsConfig = jets_config
        self.projects_infos:list[ProjectInfo] = get_projects_infos(jets_config.project_browser_dir)
        self.project_list = QListWidget() # Will fill with projects infos
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

        lbl_title = QLabel("lbl_title in project browser _build_ui")
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
        #AI TODO: also have some visual indication of the current JetsConfig.project_browser_dir. How to make another boxlayout so it is easy and intuitive to add more ui elements?

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
        self.projects_infos = get_projects_infos(self.jets_config.project_browser_dir)
        if not self.projects_infos:
            self.empty_label.show()
            self.project_list.hide()
            return
        self.empty_label.hide()
        self.project_list.show()
        for proj_info in self.projects_infos:
            item = QListWidgetItem()
            item.setText(f"{proj_info.project_name}\n{proj_info.full_project_path}")
            item.setData(Qt.ItemDataRole.UserRole, proj_info)
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

        # try:
        #     pid = create_project(name.strip(), folder)
        #     self._load_projects()
        #     self.project_opened.emit(pid)
        # except Exception as e:
        #     QMessageBox.critical(self, "Error", str(e))

    def _change_project_folder(self):
        """Register a folder as a project by browsing to it."""

        folder = QFileDialog.getExistingDirectory(
            self, "Select existing project folder", str(Path.home())
        )
        if not folder:
            return
        name = Path(folder).name
        self._load_projects()
        
    def _open_project(self, item: QListWidgetItem):
        project_info:ProjectInfo = item.data(Qt.ItemDataRole.UserRole)
        self.project_opened.emit(project_info)

    def _open_selected(self):
        items = self.project_list.selectedItems()
        if items:
            self._open_project(items[0])
