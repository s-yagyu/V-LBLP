import logging
from logging.handlers import RotatingFileHandler
from os import makedirs
from os.path import isdir

from PyQt5.QtWidgets import (
    QWidget,
    QLabel,
    QFrame,
    QGridLayout,
    QGroupBox,
    QFileSystemModel,
    QListView,
    QLineEdit,
    QVBoxLayout,
    QPushButton
)
from PyQt5.QtCore import QDir

from common_widgets.file_explorer import FileExplorer


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


class RotatedFileExplorer(FileExplorer):
    def __init__(self, parent, editor):
        super().__init__(parent, editor, "rotated")

    def create_widgets(self):
        super().create_widgets()
        self.ImgLabel.setText("Rotated Images Folder")

    def on_open_button_clicked(self):
        # TODO: パスを指定する場合も記述する。
        self.editor.open_folder(
            self.folder_key, dialog_message="Open Rotated Images Folder")
