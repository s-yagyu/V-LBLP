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


class TRFileExplorer(FileExplorer):
    def __init__(self, parent, editor):
        super().__init__(parent, editor, "top-right", False)
        # デフォルト表示色の設定
        self.folder.color = {"r": 255, "g": 0, "b": 0, "a": 255}

    def create_widgets(self):
        super().create_widgets()
        self.ImgLabel.setText("B Images Folder")

    def on_open_button_clicked(self):
        self.editor.open_folder(
            self.folder_key, dialog_message="Open Images Folder B")
