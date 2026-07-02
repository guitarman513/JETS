"""
main.py — Entry point for Joe's Electrical Takeoff Software.

"""

import sys

from PyQt6.QtWidgets import QApplication, QStackedWidget, QMainWindow
from PyQt6.QtCore import Qt
from PyQt6.QtGui import QIcon

from ui.aa_project_browser import ProjectBrowser
from ui.ba_proj_tabular import ProjWindowTabular
from models.project import ProjectInfo, ProjectManager

from models.jets import JetsConfig, initialize_jets_ecosystem_if_dne
from a_constants import *


class AppShell(QMainWindow):
    """
    Thin shell that manages navigation between HomeScreen and ProjectWindow.
    Uses a QStackedWidget so both live in memory once created.
    """

    def __init__(self):
        super().__init__()
        initialize_jets_ecosystem_if_dne()
        jets_config = JetsConfig.load(DEFAULT_JETS_CONFIG_FILE)

        self.setWindowTitle("JETS — Joe's Electrical Takeoff Software")
        self.setMinimumSize(jets_config.window_width, jets_config.window_height)

        # Stack: index 0 = projects browser, index 1 = project viewer
        self.stack = QStackedWidget()
        self.setCentralWidget(self.stack)

        # Projects Browser Screen
        self.home = ProjectBrowser(jets_config)
        self.home.project_opened.connect(self._open_project)
        self.stack.addWidget(self.home)

        # Project Viewer placeholder (created on demand)
        self._project_viewer_tabular = None

        # Start on home
        self.stack.setCurrentIndex(0)

    def _open_project(self, project_info: ProjectInfo):
        # Remove previous project viewer if it exists
        if self._project_viewer_tabular is not None:
            self.stack.removeWidget(self._project_viewer_tabular)
            self._project_viewer_tabular.deleteLater()
            self._project_viewer_tabular = None

        self._project_viewer_tabular = ProjWindowTabular(project_info)
        self._project_viewer_tabular.home_requested.connect(self._go_home) # signals are dumb. connect their logic here.
        self.stack.addWidget(self._project_viewer_tabular)
        self.stack.setCurrentWidget(self._project_viewer_tabular)

        self.setWindowTitle(project_info.project_name)

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
    # app.setStyleSheet(APP_STYLESHEET)


    shell = AppShell()
    shell.show()

    sys.exit(app.exec())


if __name__ == "__main__":
    main()
