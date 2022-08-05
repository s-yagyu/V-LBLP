import logging
from logging.handlers import RotatingFileHandler
from os import makedirs

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QGridLayout,
    QGroupBox,
    QListView,
    QLineEdit,
    QVBoxLayout,
    QPushButton
)

from merge_editor.widgets.tl_file_explorer import TLFileExplorer
from merge_editor.widgets.tr_file_explorer import TRFileExplorer
from merge_editor.widgets.bl_file_explorer import BLFileExplorer
from merge_editor.widgets.br_file_explorer import BRFileExplorer

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


class ExplorerContainer(QFrame):
    def __init__(self, parent, editor):
        super().__init__(parent)

        self.editor = editor

        self.create_widgets()
        self.create_actions()
        self.layout_widgets()
        self.create_connections()

    def create_widgets(self):
        self.tlExplorer = TLFileExplorer(self, self.editor)
        self.trExplorer = TRFileExplorer(self, self.editor)
        self.blExplorer = BLFileExplorer(self, self.editor)
        self.brExplorer = BRFileExplorer(self, self.editor)

    def create_actions(self):
        pass

    def layout_widgets(self):
        grid = QGridLayout()
        grid.addWidget(self.tlExplorer, 0, 0)
        grid.addWidget(self.trExplorer, 1, 0)
        grid.addWidget(self.blExplorer, 2, 0)
        grid.addWidget(self.brExplorer, 3, 0)
        self.setLayout(grid)

    def create_connections(self):
        pass
