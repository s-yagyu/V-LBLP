import logging
from logging.handlers import RotatingFileHandler
from os import makedirs

from PyQt5.QtWidgets import QWidget, QGridLayout, QSplitter, QStatusBar
from PyQt5.QtCore import Qt

from common_widgets.main_view import MainView
from merge_editor.widgets.explorer_container import ExplorerContainer
from merge_editor.widgets.params_container import ParamsContainer

LOGFORM = logging.Formatter(
    "%(asctime)s %(levelname)s %(funcName)s(%(lineno)d) %(message)s"
)
makedirs("log", exist_ok=True)
LOGFILE = "log/main.log"
LOGSIZE = 1048576
LOGBACK = 2
LOGHAND = RotatingFileHandler(
    LOGFILE, mode="a",
    maxBytes=LOGSIZE,
    backupCount=LOGBACK,
    encoding=None,
    delay=0
)
LOGHAND.setFormatter(LOGFORM)
LOGHAND.setLevel(logging.DEBUG)
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)
logger.addHandler(LOGHAND)


version_str = "version 0.1.0"


class MainContainer(QWidget):
    def __init__(self, parent, editor):
        super().__init__(parent)

        self.editor = editor

        self.create_widgets()
        self.create_actions()
        self.layout_widgets()
        self.create_connections()

    def create_widgets(self):
        self.explorer_container = ExplorerContainer(self, self.editor)
        self.compImgViewer = MainView(self, self.editor)
        # self.compImgViewer = ImagePreview(self, self.editor)
        self.paramsEditor = ParamsContainer(self, self.editor)

    def create_actions(self):
        pass

    def layout_widgets(self):
        grid = QGridLayout(self)
        self.splitter = QSplitter(self)
        grid.addWidget(self.splitter, 0, 0)
        self.setLayout(grid)
        self.splitter.addWidget(self.explorer_container)
        self.splitter.addWidget(self.compImgViewer)
        self.splitter.addWidget(self.paramsEditor)
        self.splitter.setSizes([300, 1000, 300])
        self.splitter.setCollapsible(0, False)
        self.splitter.setCollapsible(1, False)
        self.splitter.setCollapsible(2, False)
        self.compImgViewer.setFocus(Qt.OtherFocusReason)

    def create_connections(self):
        pass
