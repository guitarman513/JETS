"""
viewer_window.py — Main project/PDF viewer window.

Layout:
  Left:   DrawingListPanel (260px) — file browser for the project
  Center: PDFCanvas — the interactive markup surface
  Right:  (placeholder) Database / takeoff item panel — built next phase

Toolbar controls the active markup mode and shows measurement readouts.
"""

from pathlib import Path
from PyQt6.QtWidgets import (
    QMainWindow, QWidget, QHBoxLayout, QVBoxLayout,
    QToolBar, QLabel, QStatusBar, QFrame, QSplitter,
    QMessageBox, QPushButton, QSizePolicy
)
from PyQt6.QtCore import Qt, pyqtSignal
from PyQt6.QtGui import QAction, QKeySequence, QIcon, QFont

from ui.drawing_list import DrawingListPanel
from ui.pdf_canvas import PDFCanvas
from ui.scale_dialog import ScaleDialog

from models.project import ProjectInfo, ProjectManager
from models.annotation import AnnotationStyles
from models.audit_trail import AuditTrail

def get_project():
    pass

def get_drawings_for_project():
    pass

class ProjWindowTabular(QMainWindow):
    """Main window shown after a project is selected. Where you click thru db and have audit trail."""

    home_requested = pyqtSignal()   # back-button → go home

    def __init__(self, project_info: ProjectInfo, parent=None):
        super().__init__(parent)
        self.project_manager:ProjectManager = ProjectManager(
            project_info=project_info,
            drawing_thumbnails_annotated=[],
            drawing_thumbnails_plain=[],
            active_drawing=None,
            annotation_styles=AnnotationStyles(),
            audit_trail=AuditTrail(),
        )

        self.setWindowTitle(f"JETS — {self.project_manager.project_info.project_name}")
        self.resize(1400, 900) #TODO: load from jets global config since not project specific

        self._build_ui()
        self._build_toolbar()
        self._build_statusbar()

    # ── UI ────────────────────────────────────────────────────────────────────

    def _build_ui(self):
        central = QWidget()
        self.setCentralWidget(central)
        root = QHBoxLayout(central)
        root.setContentsMargins(0, 0, 0, 0)
        root.setSpacing(0)

        # ── Drawing list (left panel) ─────────────────────────────────────────
        self.drawing_list = DrawingListPanel(self.project_id)
        self.drawing_list.drawing_selected.connect(self._open_drawing)
        self.drawing_list.scale_requested.connect(self._bulk_set_scale)

        # ── PDF canvas (center) ───────────────────────────────────────────────
        self.canvas = PDFCanvas()
        self.canvas.measurement_updated.connect(self._update_measurement)
        self.canvas.status_message.connect(self.statusBar().showMessage)
        self.canvas.scale_set.connect(self._on_scale_set)

        # ── Right placeholder panel ───────────────────────────────────────────
        self.right_panel = self._build_right_panel()

        # ── Splitter ─────────────────────────────────────────────────────────
        splitter = QSplitter(Qt.Orientation.Horizontal)
        splitter.addWidget(self.drawing_list)
        splitter.addWidget(self.canvas)
        splitter.addWidget(self.right_panel)
        splitter.setStretchFactor(0, 0)
        splitter.setStretchFactor(1, 1)
        splitter.setStretchFactor(2, 0)
        splitter.setSizes([260, 900, 240])

        root.addWidget(splitter)

        # ── Empty / no-drawing state ──────────────────────────────────────────
        self.no_drawing_overlay = QLabel(
            "← Select a drawing from the list to begin\n\n"
            "Tip: Drop PDF files into the project folder and click ↺ Refresh"
        )
        self.no_drawing_overlay.setAlignment(Qt.AlignmentFlag.AlignCenter)
        self.no_drawing_overlay.setStyleSheet(
            "color: #5A6070; font-size: 14px;"
        )
        # We overlay this on the canvas by using a stacked approach in canvas bg
        self.canvas.setVisible(True)

    def _build_right_panel(self) -> QFrame:
        """Placeholder for the database / item-picker panel."""
        panel = QFrame()
        panel.setFixedWidth(240)
        panel.setStyleSheet(
            "background-color: #111316; border-left: 1px solid #2E3239;"
        )
        layout = QVBoxLayout(panel)
        layout.setContentsMargins(0, 0, 0, 0)

        # Header
        header = QLabel("TAKEOFF ITEMS")
        header.setStyleSheet(
            "font-size: 10px; color: #5A6070; letter-spacing: 2px; "
            "padding: 12px; border-bottom: 1px solid #2E3239;"
        )
        layout.addWidget(header)

        placeholder = QLabel(
            "Database panel\ncoming next.\n\n"
            "Select an item here to\nenable markup tools."
        )
        placeholder.setAlignment(Qt.AlignmentFlag.AlignCenter)
        placeholder.setStyleSheet("color: #3A3E47; font-size: 12px; padding: 24px;")
        placeholder.setWordWrap(True)
        layout.addWidget(placeholder, 1)
        return panel

    # ── Toolbar ───────────────────────────────────────────────────────────────

    def _build_toolbar(self):
        tb = QToolBar("Tools")
        tb.setMovable(False)
        tb.setStyleSheet("QToolBar { padding: 6px 8px; }")
        self.addToolBar(tb)

        # Back to home
        act_home = QAction("⌂  Home", self)
        act_home.setToolTip("Return to project list")
        act_home.triggered.connect(self.home_requested.emit)
        tb.addAction(act_home)
        tb.addSeparator()

        # Mode buttons
        self.act_pan = QAction("✋  Pan", self)
        self.act_pan.setToolTip("Pan / zoom (Space to toggle)")
        self.act_pan.setCheckable(True)
        self.act_pan.setChecked(True)
        self.act_pan.triggered.connect(lambda: self._set_mode("pan"))

        self.act_cal = QAction("📐  Calibrate", self)
        self.act_cal.setToolTip("Set scale by clicking two reference points")
        self.act_cal.setCheckable(True)
        self.act_cal.triggered.connect(lambda: self._set_mode("calibrate"))

        self.act_poly = QAction("〰  Conduit Run", self)
        self.act_poly.setToolTip("Draw polyline to measure conduit (Esc to cancel, double-click to finish)")
        self.act_poly.setCheckable(True)
        self.act_poly.triggered.connect(lambda: self._set_mode("polyline"))

        self.act_point = QAction("⊕  Place Item", self)
        self.act_point.setToolTip("Click to place and count a device/item")
        self.act_point.setCheckable(True)
        self.act_point.triggered.connect(lambda: self._set_mode("point"))

        self._mode_actions = [self.act_pan, self.act_cal, self.act_poly, self.act_point]
        for act in self._mode_actions:
            tb.addAction(act)

        tb.addSeparator()

        # Scale display
        self.lbl_scale = QLabel("  No scale set")
        self.lbl_scale.setStyleSheet("color: #5A6070; font-size: 12px;")
        tb.addWidget(self.lbl_scale)

        tb.addSeparator()

        # Measurement readout
        self.lbl_measurement = QLabel()
        self.lbl_measurement.setObjectName("measurement")
        self.lbl_measurement.setMinimumWidth(180)
        tb.addWidget(self.lbl_measurement)

    # ── Status bar ────────────────────────────────────────────────────────────

    def _build_statusbar(self):
        sb = QStatusBar()
        self.setStatusBar(sb)
        sb.showMessage("Ready  —  select a drawing to begin")

    # ── Actions ───────────────────────────────────────────────────────────────

    def _set_mode(self, mode: str):
        for act in self._mode_actions:
            act.setChecked(False)
        mapping = {
            "pan":       self.act_pan,
            "calibrate": self.act_cal,
            "polyline":  self.act_poly,
            "point":     self.act_point,
        }
        if mode in mapping:
            mapping[mode].setChecked(True)
        self.canvas.set_mode(mode)

    def _open_drawing(self, drawing_id: int):
        self._current_drawing_id = drawing_id
        row = get_drawings_for_project(self._current_project_id)
        if not row:
            return

        pdf_path = Path(row["folder_path"]) / row["filename"]
        if not pdf_path.exists():
            QMessageBox.warning(
                self, "File Not Found",
                f"PDF not found at:\n{pdf_path}\n\n"
                "Please ensure the file is in the project folder."
            )
            return

        self.canvas.load_drawing(drawing_id, str(pdf_path))
        self._set_mode("pan")

        # Update scale display
        d = get_drawings_for_project(self._current_project_id)
        if d and d["scale_label"]:
            self.lbl_scale.setText(f"  Scale: {d['scale_label']}")
            self.lbl_scale.setStyleSheet("color: #00AAFF; font-size: 12px;")
        else:
            self.lbl_scale.setText("  No scale set")
            self.lbl_scale.setStyleSheet("color: #FF6B35; font-size: 12px;")

        self.drawing_list.select_drawing(drawing_id)
        self.statusBar().showMessage(f"Loaded: {row['filename']}")

    def _bulk_set_scale(self, drawing_ids: list):
        """Set the same scale string on multiple drawings at once."""
        dlg = ScaleDialog(self)
        if dlg.exec():
            _, label = dlg.get_result()
            if label:
                # For bulk/manual scale we store the label only
                # and flag that canvas calibration is still needed
                from db.database import set_drawing_scale
                for did in drawing_ids:
                    set_drawing_scale(did, None, label)
                self.drawing_list._refresh()
                QMessageBox.information(
                    self, "Scale Noted",
                    f"Scale label \"{label}\" saved for {len(drawing_ids)} drawing(s).\n\n"
                    "Open each drawing and use 📐 Calibrate to set the pixel ratio."
                )

    def _update_measurement(self, text: str):
        self.lbl_measurement.setText(text)

    def _on_scale_set(self, px_per_foot: float, label: str):
        self.lbl_scale.setText(f"  Scale: {label}")
        self.lbl_scale.setStyleSheet("color: #00AAFF; font-size: 12px;")
        self.drawing_list._refresh()
