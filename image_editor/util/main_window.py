import logging
from logging.handlers import RotatingFileHandler
import argparse
import sys
import json
from os import getcwd, listdir, makedirs
from os.path import basename, relpath, isfile, splitext, join
from glob import glob
from pathlib import Path
#import msgpack
#import msgpack_numpy

from PyQt5.QtWidgets import QMainWindow, QFileDialog

from util.editor import Editor
from util.validator import Validator


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


class MainWindow(QMainWindow):
    def __init__(self, argv):
        super().__init__(None)
        self.editor: Editor

    def reset_all_windows(self):
        self.menuBar().clear()
        self.initialize()
        print("New")

    def quit_app(self):
        print("Quit")
        # TODO: 未保存のパラメータのチェック
        self.close()

    def Undo(self):
        print("Undo")

    def Redo(self):
        print("Redo")

    def _open_file_with_filter(self, file_filter: str) -> None:
        # TODO: 未保存の操作がないかチェック。
        # ダイアログを開いてファイルを指定。
        fnp = self.editor.file_name_path
        dir_path = fnp.parent if fnp is not None else Path.home()
        file_name, fil = QFileDialog.getOpenFileName(
            None,
            "Open File",
            str(dir_path),
            file_filter
        )
        #if file_name == "":
        #    return
        return
        fnp = Path(file_name)
        # 指定したファイルを辞書に展開してローカル変数に格納する。
        dict_data = self.editor.unpack_dict_from_file(fnp)
        if len(dict_data) == 0:
            # TODO: ファイルの中身が空というエラーダイアログ
            print(f"ERROR: {fnp} is empty.")
            return
        print(dict_data)
        # 展開した辞書のバリデーション。
        is_valid, message = Validator.validate_atp(dict_data)
        print(message)
        if not is_valid:
            # TODO: 辞書がバリッドでなければその旨を記したエラーダイアログ
            print(f"ERROR: {message}")
            return
        # Editor とウィンドウ内を初期化。
        self.reset_all_windows()
        # 辞書の内容をロード。
        self.editor.file_name_path = fnp
        self.editor.load_data_from_dict(dict_data)
        print("Open Params File")

    def save_params_file(self):
        self.editor.save_file()
        print("Save")

    def save_params_file_as(self):
        self.editor.save_file_as()
        print("Save As...")

    def initialize(self) -> None:
        pass

    def create_widgets(self):
        pass

    def create_actions(self):
        pass

    def layout_widgets(self):
        pass

    def create_connections(self):
        pass
