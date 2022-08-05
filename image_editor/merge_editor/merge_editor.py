import logging
from logging.handlers import RotatingFileHandler
from os import makedirs

from PyQt5.QtCore import QObject

from util.folder import Folder
from util.editor import Editor


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


class MergeEditor(Editor):
    def __init__(self, parent: QObject) -> None:
        super().__init__(parent)
        self.folders = {
            "top-left": Folder("top-left"),
            "top-right": Folder("top-right"),
            "bottom-left": Folder("bottom-left"),
            "bottom-right": Folder("bottom-right")
            }
