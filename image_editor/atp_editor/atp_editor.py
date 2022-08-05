import logging
from logging.handlers import RotatingFileHandler
from os import makedirs
from pathlib import Path
#import msgpack
#import msgpack_numpy

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


class ATPEditor(Editor):
    def __init__(self, parent: QObject) -> None:
        super().__init__(parent)
        self.editor_type = "atp_editor"
        self.folders = {
            "base": Folder("base"),
            "rotated": Folder("rotated")
            }

    def save_file_as(self) -> bool:
        # ダイアログを開いてファイルを指定させる。
        fnp = self._get_save_file_name_path(".atp", "ATP files (*.atp)")
        if fnp is None:
            return False
        # 既存のファイルの場合、上書きするか尋ねる。
        # NOTE: この処理は QFileDialog に含まれていたのでオミット。
        # if not self._confirm_overwrite_file(fnp):
        #     return False
        # 保存するデータを辞書に格納。
        dic_save = self.pack_data_into_dict()
        # TODO: 出力するファイルに不備がないか辞書をバリデーションする？
        # 辞書をバイナリに変換してファイルに書き出す。
        self.write_dict_to_file(fnp, dic_save)
        return True

    def save_file(self) -> bool:
        # file_name_path が空であれば save_file_as() を呼ぶ。
        if self.file_name_path is None:
            return self.save_file_as()
        # そうでなければ file_name_path に上書き保存する。
        dict_data = self.pack_data_into_dict()
        self.write_dict_to_file(self.file_name_path, dict_data)
        return True

    def load_data_from_dict(self, dict_data: dict) -> None:
        dict_f = dict_data["folders"]
        for key, folder in self.folders.items():
            folder.load_data_from_dict(dict_f[key])

    def pack_data_into_dict(self) -> dict:
        f = {
            "base": self.folders["base"].pack_data_into_dict(),
            "rotated": self.folders["rotated"].pack_data_into_dict()
        }
        d = {
            "version": self._version,
            "editor_type": self.editor_type,
            "folders": f
        }
        return d
