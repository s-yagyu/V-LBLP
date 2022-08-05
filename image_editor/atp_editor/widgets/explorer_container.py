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

from atp_editor.widgets.basefile_explorer import BaseFileExplorer
from atp_editor.widgets.rotatedfile_explorer import RotatedFileExplorer

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
        self.baseExplorer = BaseFileExplorer(self, self.editor)
        self.rotatedExplorer = RotatedFileExplorer(self, self.editor)

    def create_actions(self):
        pass

    def layout_widgets(self):
        vbox = QVBoxLayout(self)
        vbox.addWidget(self.baseExplorer)
        vbox.addWidget(self.rotatedExplorer)
        self.setLayout(vbox)

    def create_connections(self):
        pass
