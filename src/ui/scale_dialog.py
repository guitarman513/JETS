"""
scale_dialog.py — Dialog to enter a scale ratio.
Used both for single-drawing calibration (interactive click mode)
and for bulk scale setting from the drawing list.
"""

from PyQt6.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel,
    QPushButton, QDoubleSpinBox, QComboBox, QFrame
)
from PyQt6.QtCore import Qt


class ScaleDialog(QDialog):
    """
    Simple manual scale-entry dialog.
    Returns (px_per_foot, label_string) via .get_result().

    For interactive calibration (user draws a reference line on the PDF),
    pass in known_px so the dialog just asks for the real-world distance.
    """

    def __init__(self, parent=None, known_px: float = None):
        super().__init__(parent)
        self.known_px = known_px
        self.result_scale = None   # px / foot
        self.result_label = None
        self.setWindowTitle("Set Drawing Scale")
        self.setFixedSize(400, known_px is not None and 220 or 280)
        self._build_ui()

    def _build_ui(self):
        layout = QVBoxLayout(self)
        layout.setSpacing(16)
        layout.setContentsMargins(24, 24, 24, 24)

        if self.known_px is not None:
            # Calibration mode: user drew a reference line
            lbl = QLabel(
                f"You drew a reference line of <b>{self.known_px:.1f} pixels</b>.<br>"
                "Enter the real-world length of that line:"
            )
        else:
            # Manual mode: type the scale directly
            lbl = QLabel(
                "Enter the drawing scale.<br>"
                "<small style='color:#5A6070'>Example: if the legend says 1\" = 20', "
                "enter 1 inch = 20 feet.</small>"
            )
        lbl.setWordWrap(True)
        lbl.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(lbl)

        # ── Input row ────────────────────────────────────────────────────────
        input_frame = QFrame()
        input_frame.setStyleSheet(
            "background-color: #141618; border: 1px solid #2E3239; border-radius: 4px;"
        )
        input_layout = QHBoxLayout(input_frame)
        input_layout.setContentsMargins(12, 8, 12, 8)

        if self.known_px is not None:
            lbl_eq = QLabel("Reference line =")
            lbl_eq.setStyleSheet("color: #7A8290;")
            input_layout.addWidget(lbl_eq)

            self.spin_real = QDoubleSpinBox()
            self.spin_real.setRange(0.01, 100000)
            self.spin_real.setDecimals(2)
            self.spin_real.setValue(10.0)
            self.spin_real.setFixedWidth(100)
            input_layout.addWidget(self.spin_real)

            self.unit_combo = QComboBox()
            self.unit_combo.addItems(["feet", "inches", "meters"])
            input_layout.addWidget(self.unit_combo)
        else:
            lbl1 = QLabel("1")
            lbl1.setStyleSheet("font-size: 18px; font-weight: 700; color: #FFFFFF;")
            input_layout.addWidget(lbl1)

            self.unit_from = QComboBox()
            self.unit_from.addItems(["inch", "foot", "cm"])
            input_layout.addWidget(self.unit_from)

            lbl_eq = QLabel("=")
            lbl_eq.setStyleSheet("color: #7A8290; font-size: 16px; padding: 0 8px;")
            input_layout.addWidget(lbl_eq)

            self.spin_real = QDoubleSpinBox()
            self.spin_real.setRange(0.01, 100000)
            self.spin_real.setDecimals(2)
            self.spin_real.setValue(20.0)
            self.spin_real.setFixedWidth(100)
            input_layout.addWidget(self.spin_real)

            self.unit_combo = QComboBox()
            self.unit_combo.addItems(["feet", "inches", "meters"])
            input_layout.addWidget(self.unit_combo)

        layout.addWidget(input_frame)

        # ── Buttons ───────────────────────────────────────────────────────────
        btn_row = QHBoxLayout()
        btn_cancel = QPushButton("Cancel")
        btn_cancel.clicked.connect(self.reject)
        btn_ok = QPushButton("Set Scale")
        btn_ok.setObjectName("primary")
        btn_ok.clicked.connect(self._accept)
        btn_row.addStretch()
        btn_row.addWidget(btn_cancel)
        btn_row.addWidget(btn_ok)
        layout.addLayout(btn_row)

    def _accept(self):
        real_value = self.spin_real.value()
        unit = self.unit_combo.currentText()

        # Convert everything to feet
        to_feet = {"feet": 1.0, "foot": 1.0, "inches": 1 / 12, "inch": 1 / 12, "meters": 3.28084, "cm": 0.0328084}
        real_feet = real_value * to_feet.get(unit, 1.0)

        if self.known_px is not None:
            # px_per_foot = known_px / real_feet
            self.result_scale = self.known_px / real_feet
            self.result_label = f"ref line = {real_value} {unit}"
        else:
            # Manual: 1 drawing_unit = real_feet
            # We need to know how many px = 1 drawing inch/foot/cm
            # Without a pixel reference, store a "nominal" scale and
            # require the user to calibrate on-canvas later.
            from_unit = self.unit_from.currentText()
            from_feet = to_feet.get(from_unit, 1.0)
            # Ratio: real_feet per drawing_foot
            # We'll store as a ratio string and resolve at calibration time
            self.result_scale = None  # Must calibrate on canvas
            self.result_label = f"1 {from_unit} = {real_value} {unit}"

        self.accept()

    def get_result(self):
        """Returns (px_per_foot, label) or (None, label) if canvas cal needed."""
        return self.result_scale, self.result_label
