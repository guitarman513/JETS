"""
main.py — Entry point for Joe's Electrical Takeoff Software.

"""

import sys

from PyQt6.QtWidgets import QApplication, QStackedWidget, QMainWindow
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from ui.home_screen import HomeScreen
from ui.viewer_window import ViewerWindow


class AppShell(QMainWindow):
    """
    Thin shell that manages navigation between HomeScreen and ProjectWindow.
    Uses a QStackedWidget so both live in memory once created.
    """

    def __init__(self):
        super().__init__()
        self.setWindowTitle("JETS — Joe's Electrical Takeoff Software")
        # self.resize(1200, 800)
        self.setMinimumSize(900, 600)

        # Stack: index 0 = home, index 1 = project viewer
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Home screen
        self.home = HomeScreen()
        self.home.project_opened.connect(self._open_project)
        self.stack.addWidget(self.home)

        # Viewer placeholder (created on demand)
        self._viewer = None

        # Start on home
        self.stack.setCurrentIndex(0)

    def _open_project(self, project_id: int):
        # Remove previous viewer if it exists
        if self._viewer is not None:
            self.stack.removeWidget(self._viewer)
            self._viewer.deleteLater()
            self._viewer = None

        self._viewer = ViewerWindow(project_id)
        self._viewer.home_requested.connect(self._go_home)
        self.stack.addWidget(self._viewer)
        self.stack.setCurrentWidget(self._viewer)

        # Update window title
        from db.database import get_project #TODO: figure out this. prob read the list of get_all_projects in the database file.
        p = get_project(project_id)
        if p:
            self.setWindowTitle(f"JETS — {p['name']}")

    def _go_home(self):
        self.stack.setCurrentWidget(self.home)
        self.home._load_projects()   # refresh the list
        self.setWindowTitle("JETS — Joe's Electrical Takeoff Software")


def main():
    # High-DPI support
    QApplication.setHighDpiScaleFactorRoundingPolicy(
        Qt.HighDpiScaleFactorRoundingPolicy.PassThrough
    )

    app = QApplication(sys.argv)
    app.setApplicationName("JETS")
    app.setOrganizationName("JETS")
    app.setStyleSheet(APP_STYLESHEET)


    shell = AppShell()
    shell.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
