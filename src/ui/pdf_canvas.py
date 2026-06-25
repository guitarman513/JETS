"""
pdf_canvas.py — The main drawing/markup surface.

Renders a PDF page using PyMuPDF onto a QGraphicsScene.
Supports:
  - Pan (middle-mouse or space+drag) and zoom (scroll wheel)
  - Scale calibration (two-point click)
  - Polyline drawing for conduit runs
  - Point placement for device counts
  - Viewing previously saved annotations

Modes (set via .set_mode()):
  'pan'        — navigate only
  'calibrate'  — click two points to define a reference length
  'polyline'   — draw conduit runs (click to add vertex, dbl-click to finish)
  'point'      — click to place a device/item
"""

import math
import json
from pathlib import Path

import fitz   # PyMuPDF

from PyQt6.QtWidgets import (
    QGraphicsView, QGraphicsScene, QGraphicsPixmapItem,
    QGraphicsLineItem, QGraphicsEllipseItem, QGraphicsPathItem,
    QGraphicsItem, QRubberBand
)
from PyQt6.QtCore import Qt, QPointF, QRectF, pyqtSignal, QSizeF, QLineF
from PyQt6.QtGui import (
    QPixmap, QImage, QPen, QColor, QBrush, QPainterPath,
    QTransform, QCursor, QPainter
)

# from db.database import get_connection, set_drawing_scale


# ── Constants ────────────────────────────────────────────────────────────────

CONDUIT_COLOR   = QColor("#00BFFF")   # electric blue
POINT_COLOR     = QColor("#FF6B35")   # orange
CAL_COLOR       = QColor("#FFDD00")   # yellow
VERTEX_RADIUS   = 4
POINT_RADIUS    = 8
CAL_DASH        = [8, 4]
RENDER_DPI      = 150   # PDF render resolution


class PDFCanvas(QGraphicsView):
    """
    Interactive PDF markup canvas. Drop this into any layout.
    """
    scale_set        = pyqtSignal(float, str)   # px_per_foot, label
    measurement_updated = pyqtSignal(str)        # human-readable length string
    status_message   = pyqtSignal(str)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.scene = QGraphicsScene(self)
        self.setScene(self.scene)

        # State
        self._drawing_id   = None
        self._pdf_doc      = None
        self._page_index   = 0
        self._px_per_foot  = None
        self._mode         = "pan"

        # Active takeoff item from the database panel
        self._active_item_id     = None
        self._active_assembly_id = None
        self._active_color       = CONDUIT_COLOR

        # Calibration state
        self._cal_point1   = None
        self._cal_line_item = None

        # Polyline drawing state
        self._poly_points  = []         # list of QPointF (scene coords)
        self._poly_items   = []         # graphics items for current draft polyline
        self._poly_preview = None       # the "rubber" segment following the mouse

        # Pan state
        self._pan_active   = False
        self._pan_start    = None

        self._setup_view()

    # ── View setup ────────────────────────────────────────────────────────────

    def _setup_view(self):
        self.setRenderHint(QPainter.RenderHint.Antialiasing)
        self.setRenderHint(QPainter.RenderHint.SmoothPixmapTransform)
        self.setDragMode(QGraphicsView.DragMode.NoDrag)
        self.setTransformationAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setResizeAnchor(QGraphicsView.ViewportAnchor.AnchorUnderMouse)
        self.setBackgroundBrush(QBrush(QColor("#0D1117")))
        self.setInteractive(True)
        self.setMouseTracking(True)

    # ── Public API ────────────────────────────────────────────────────────────

    def load_drawing(self, drawing_id: int, pdf_path: str):
        """Load a PDF drawing by its DB id and file path."""
        self._drawing_id = drawing_id
        self._pdf_doc = fitz.open(pdf_path)
        self._page_index = 0

       
            # if row and row["scale_px"]:
            #     self._px_per_foot = row["scale_px"]

        self._render_page()
        self._load_annotations()
        self.fitInView(self.scene.sceneRect(), Qt.AspectRatioMode.KeepAspectRatio)

    def set_mode(self, mode: str):
        """Set interaction mode: 'pan', 'calibrate', 'polyline', 'point'."""
        # Cancel any in-progress polyline
        if self._mode == "polyline" and mode != "polyline":
            self._cancel_polyline()

        self._mode = mode
        self._cal_point1 = None
        if self._cal_line_item:
            self.scene.removeItem(self._cal_line_item)
            self._cal_line_item = None

        cursors = {
            "pan":       Qt.CursorShape.OpenHandCursor,
            "calibrate": Qt.CursorShape.CrossCursor,
            "polyline":  Qt.CursorShape.CrossCursor,
            "point":     Qt.CursorShape.CrossCursor,
        }
        self.setCursor(QCursor(cursors.get(mode, Qt.CursorShape.ArrowCursor)))

        mode_hints = {
            "pan":       "Pan mode  —  scroll to zoom",
            "calibrate": "Calibrate: click two points to define a reference length",
            "polyline":  "Polyline: click to add vertices, double-click to finish",
            "point":     "Point: click to place item",
        }
        self.status_message.emit(mode_hints.get(mode, ""))

    def set_active_takeoff_item(self, item_id=None, assembly_id=None, color=None):
        """Set which DB item/assembly will be tagged to new markup."""
        self._active_item_id     = item_id
        self._active_assembly_id = assembly_id
        if color:
            self._active_color = QColor(color)

    def apply_scale(self, px_per_foot: float, label: str):
        """Called after calibration to commit the scale."""
        self._px_per_foot = px_per_foot
        # if self._drawing_id:
        #     set_drawing_scale(self._drawing_id, px_per_foot, label)
        self.scale_set.emit(px_per_foot, label)
        self._refresh_length_labels()

    # ── Rendering ────────────────────────────────────────────────────────────

    def _render_page(self):
        """Render the current PDF page to a pixmap and display it."""
        if not self._pdf_doc:
            return
        page = self._pdf_doc[self._page_index]
        mat = fitz.Matrix(RENDER_DPI / 72, RENDER_DPI / 72)
        pix = page.get_pixmap(matrix=mat, alpha=False)
        img = QImage(
            pix.samples, pix.width, pix.height,
            pix.stride, QImage.Format.Format_RGB888
        )
        qpix = QPixmap.fromImage(img)

        self.scene.clear()
        self._pdf_item = QGraphicsPixmapItem(qpix)
        self._pdf_item.setZValue(0)
        self.scene.addItem(self._pdf_item)
        self.scene.setSceneRect(QRectF(qpix.rect()))

    def _load_annotations(self):
        """Re-draw all saved annotations for this drawing from the DB."""
        if not self._drawing_id:
            return
        # with get_connection() as conn:
        #     lines = conn.execute(
        #         "SELECT * FROM takeoff_lines WHERE drawing_id = ?",
        #         (self._drawing_id,)
        #     ).fetchall()
        #     points = conn.execute(
        #         "SELECT * FROM takeoff_points WHERE drawing_id = ?",
        #         (self._drawing_id,)
        #     ).fetchall()

        # for ln in lines:
        #     pts = [QPointF(p["x"], p["y"]) for p in json.loads(ln["points_json"])]
        #     color = QColor(ln["color"] or "#00BFFF")
        #     self._draw_saved_polyline(pts, color, ln["id"])

        # for pt in points:
        #     color = QColor(pt["color"] or "#FF6B35")
        #     self._draw_saved_point(QPointF(pt["x"], pt["y"]), color, pt["id"])

    # ── Mouse events ─────────────────────────────────────────────────────────

    def mousePressEvent(self, event):
        if event.button() == Qt.MouseButton.MiddleButton:
            self._pan_active = True
            self._pan_start = event.position().toPoint()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))
            event.accept()
            return

        scene_pos = self.mapToScene(event.position().toPoint())

        if self._mode == "pan":
            self._pan_active = True
            self._pan_start = event.position().toPoint()
            self.setCursor(QCursor(Qt.CursorShape.ClosedHandCursor))

        elif self._mode == "calibrate":
            self._handle_calibrate_click(scene_pos)

        elif self._mode == "polyline":
            if event.button() == Qt.MouseButton.LeftButton:
                self._handle_polyline_click(scene_pos)
            elif event.button() == Qt.MouseButton.RightButton:
                self._cancel_polyline()

        elif self._mode == "point":
            if event.button() == Qt.MouseButton.LeftButton:
                self._handle_point_click(scene_pos)

        super().mousePressEvent(event)

    def mouseDoubleClickEvent(self, event):
        if self._mode == "polyline":
            scene_pos = self.mapToScene(event.position().toPoint())
            # Finish the polyline at the double-click position
            if self._poly_points:
                self._finish_polyline()
            event.accept()
            return
        super().mouseDoubleClickEvent(event)

    def mouseMoveEvent(self, event):
        if self._pan_active:
            delta = event.position().toPoint() - self._pan_start
            self._pan_start = event.position().toPoint()
            self.horizontalScrollBar().setValue(
                self.horizontalScrollBar().value() - delta.x()
            )
            self.verticalScrollBar().setValue(
                self.verticalScrollBar().value() - delta.y()
            )
            event.accept()
            return

        scene_pos = self.mapToScene(event.position().toPoint())

        if self._mode == "polyline" and self._poly_points:
            self._update_polyline_preview(scene_pos)
        elif self._mode == "calibrate" and self._cal_point1 and self._cal_line_item:
            self._cal_line_item.setLine(
                QLineF(self._cal_point1, scene_pos)
            )

        # Update coordinate readout
        ft_str = ""
        if self._px_per_foot:
            pass  # could show cursor coords in feet
        self.measurement_updated.emit(f"  x:{scene_pos.x():.0f}  y:{scene_pos.y():.0f}")

        super().mouseMoveEvent(event)

    def mouseReleaseEvent(self, event):
        if event.button() in (Qt.MouseButton.MiddleButton, Qt.MouseButton.LeftButton):
            if self._pan_active and self._mode == "pan":
                self._pan_active = False
                self.setCursor(QCursor(Qt.CursorShape.OpenHandCursor))
            elif self._pan_active:
                self._pan_active = False
                self.setCursor(QCursor(Qt.CursorShape.CrossCursor))
        super().mouseReleaseEvent(event)

    def wheelEvent(self, event):
        factor = 1.15 if event.angleDelta().y() > 0 else 1 / 1.15
        self.scale(factor, factor)

    def keyPressEvent(self, event):
        if event.key() == Qt.Key.Key_Escape:
            if self._mode == "polyline":
                self._cancel_polyline()
            elif self._mode in ("calibrate", "point"):
                self.set_mode("pan")
        elif event.key() == Qt.Key.Key_Space:
            self._pre_mode = self._mode
            self.set_mode("pan")
        super().keyPressEvent(event)

    def keyReleaseEvent(self, event):
        if event.key() == Qt.Key.Key_Space and hasattr(self, "_pre_mode"):
            self.set_mode(self._pre_mode)
        super().keyReleaseEvent(event)

    # ── Calibration ───────────────────────────────────────────────────────────

    def _handle_calibrate_click(self, pos: QPointF):
        if self._cal_point1 is None:
            self._cal_point1 = pos
            # Draw first point marker
            self._draw_cal_marker(pos)
            # Start the preview line
            pen = QPen(QColor(CAL_COLOR), 1.5, Qt.PenStyle.DashLine)
            pen.setDashPattern(CAL_DASH)
            pen.setCosmetic(True)
            self._cal_line_item = self.scene.addLine(
                QLineF(pos, pos), pen
            )
            self._cal_line_item.setZValue(10)
            self.status_message.emit("Calibrate: click the second point")
        else:
            # Second click — compute distance and open dialog
            p1, p2 = self._cal_point1, pos
            dist_px = math.hypot(p2.x() - p1.x(), p2.y() - p1.y())
            self._draw_cal_marker(pos)
            if self._cal_line_item:
                pen = QPen(QColor(CAL_COLOR), 1.5)
                pen.setCosmetic(True)
                self._cal_line_item.setPen(pen)

            from src.ui.scale_dialog import ScaleDialog
            dlg = ScaleDialog(self, known_px=dist_px)
            if dlg.exec():
                px_per_foot, label = dlg.get_result()
                if px_per_foot:
                    self.apply_scale(px_per_foot, label)
                    self.status_message.emit(f"Scale set: {label}")
            # Clean up cal graphics
            self._clear_cal_markers()
            self._cal_point1 = None
            self._cal_line_item = None
            self.set_mode("pan")

    def _draw_cal_marker(self, pos: QPointF):
        r = 6
        ell = self.scene.addEllipse(
            pos.x() - r, pos.y() - r, r * 2, r * 2,
            QPen(QColor(CAL_COLOR), 1.5),
            QBrush(QColor(CAL_COLOR))
        )
        ell.setZValue(11)
        ell.setData(0, "cal_marker")

    def _clear_cal_markers(self):
        for item in self.scene.items():
            if item.data(0) == "cal_marker":
                self.scene.removeItem(item)

    # ── Polyline drawing ─────────────────────────────────────────────────────

    def _handle_polyline_click(self, pos: QPointF):
        self._poly_points.append(pos)
        # Draw vertex dot
        r = VERTEX_RADIUS
        dot = self.scene.addEllipse(
            pos.x() - r, pos.y() - r, r * 2, r * 2,
            QPen(self._active_color),
            QBrush(self._active_color)
        )
        dot.setZValue(11)
        dot.setData(0, "draft")
        self._poly_items.append(dot)

        if len(self._poly_points) >= 2:
            p1 = self._poly_points[-2]
            p2 = self._poly_points[-1]
            pen = QPen(self._active_color, 2)
            pen.setCosmetic(True)
            seg = self.scene.addLine(QLineF(p1, p2), pen)
            seg.setZValue(10)
            seg.setData(0, "draft")
            self._poly_items.append(seg)

        self._update_running_length()

    def _update_polyline_preview(self, pos: QPointF):
        if self._poly_preview:
            self.scene.removeItem(self._poly_preview)
        if self._poly_points:
            pen = QPen(self._active_color, 1.5, Qt.PenStyle.DashLine)
            pen.setCosmetic(True)
            self._poly_preview = self.scene.addLine(
                QLineF(self._poly_points[-1], pos), pen
            )
            self._poly_preview.setZValue(9)

    def _finish_polyline(self):
        if len(self._poly_points) < 2:
            self._cancel_polyline()
            return

        length_px = self._polyline_length(self._poly_points)
        length_ft = (length_px / self._px_per_foot) if self._px_per_foot else None

        pts_json = json.dumps([{"x": p.x(), "y": p.y()} for p in self._poly_points])
        color_hex = self._active_color.name()

        # Persist to DB
        with get_connection() as conn:
            conn.execute(
                """INSERT INTO takeoff_lines
                   (drawing_id, item_id, assembly_id, points_json, length_px, length_ft, color)
                   VALUES (?, ?, ?, ?, ?, ?, ?)""",
                (
                    self._drawing_id,
                    self._active_item_id,
                    self._active_assembly_id,
                    pts_json,
                    length_px,
                    length_ft,
                    color_hex,
                )
            )

        ft_str = f"{length_ft:.2f} ft" if length_ft else f"{length_px:.0f} px (no scale)"
        self.status_message.emit(f"Conduit run saved — {ft_str}")

        # Replace draft items with permanent ones
        self._clear_draft()
        self._draw_saved_polyline(self._poly_points, self._active_color, None)

        self._poly_points = []
        self._poly_items  = []
        if self._poly_preview:
            self.scene.removeItem(self._poly_preview)
            self._poly_preview = None
        self.measurement_updated.emit(ft_str)

    def _cancel_polyline(self):
        self._clear_draft()
        if self._poly_preview:
            self.scene.removeItem(self._poly_preview)
            self._poly_preview = None
        self._poly_points = []
        self._poly_items  = []
        self.measurement_updated.emit("")

    def _clear_draft(self):
        for item in self.scene.items():
            if item.data(0) == "draft":
                self.scene.removeItem(item)

    def _draw_saved_polyline(self, points, color: QColor, db_id):
        """Draw a finished polyline (from DB or just committed)."""
        if len(points) < 2:
            return
        path = QPainterPath(points[0])
        for p in points[1:]:
            path.lineTo(p)

        pen = QPen(color, 2)
        pen.setCosmetic(True)
        item = self.scene.addPath(path, pen)
        item.setZValue(10)
        item.setData(0, "saved_line")
        item.setData(1, db_id)

        # Endpoint dots
        for p in [points[0], points[-1]]:
            r = VERTEX_RADIUS
            dot = self.scene.addEllipse(
                p.x() - r, p.y() - r, r * 2, r * 2,
                QPen(color), QBrush(color)
            )
            dot.setZValue(11)

    def _draw_saved_point(self, pos: QPointF, color: QColor, db_id):
        r = POINT_RADIUS
        ell = self.scene.addEllipse(
            pos.x() - r, pos.y() - r, r * 2, r * 2,
            QPen(color.darker(120), 1.5),
            QBrush(color)
        )
        ell.setZValue(12)
        ell.setData(0, "saved_point")
        ell.setData(1, db_id)

    # ── Point placement ───────────────────────────────────────────────────────

    def _handle_point_click(self, pos: QPointF):
        with get_connection() as conn:
            conn.execute(
                """INSERT INTO takeoff_points
                   (drawing_id, item_id, assembly_id, x, y, color)
                   VALUES (?, ?, ?, ?, ?, ?)""",
                (
                    self._drawing_id,
                    self._active_item_id,
                    self._active_assembly_id,
                    pos.x(), pos.y(),
                    self._active_color.name(),
                )
            )
        self._draw_saved_point(pos, self._active_color, None)
        self.status_message.emit("Item placed")

    # ── Helpers ───────────────────────────────────────────────────────────────

    @staticmethod
    def _polyline_length(points):
        total = 0.0
        for i in range(1, len(points)):
            dx = points[i].x() - points[i-1].x()
            dy = points[i].y() - points[i-1].y()
            total += math.hypot(dx, dy)
        return total

    def _update_running_length(self):
        if not self._poly_points:
            return
        length_px = self._polyline_length(self._poly_points)
        if self._px_per_foot:
            ft = length_px / self._px_per_foot
            self.measurement_updated.emit(f"{ft:.2f} ft")
        else:
            self.measurement_updated.emit(f"{length_px:.0f} px  (set scale to convert)")

    def _refresh_length_labels(self):
        """After scale is set, recompute all saved lines in DB."""
        if not self._drawing_id or not self._px_per_foot:
            return
        with get_connection() as conn:
            lines = conn.execute(
                "SELECT id, length_px FROM takeoff_lines WHERE drawing_id = ?",
                (self._drawing_id,)
            ).fetchall()
            for ln in lines:
                ft = ln["length_px"] / self._px_per_foot
                conn.execute(
                    "UPDATE takeoff_lines SET length_ft = ? WHERE id = ?",
                    (ft, ln["id"])
                )
