from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtWidgets import QInputDialog, QFileDialog, QMessageBox
from PyQt5.QtGui import QPixmap

from pathlib import Path
#import msgpack
#import msgpack_numpy


class Editor(QObject):
    changed_folder_path = pyqtSignal(str, str)
    generated_folder_image = pyqtSignal(str, QPixmap)
    reseted = pyqtSignal()

    def __init__(self, parent: QObject):
        super().__init__(parent)
        self.file_name_path: Path = None
        # TODO: ファイルのバージョンは Editor に持たせるので本当に良いのか要検討
        self._version = 1.00

    def open_folder(
            self,
            key: str,
            path: str = "",
            dialog_message: str = "Open Folder"
            ):
        if not (key in self.folders):
            print(f"Invalid Folder Key: {key}")
            return
        import os
        print(self.folders, path, os.path.abspath(path))
        p = self.folders[key].open(self.parent(), path, dialog_message)
        if p == "":
            return p
        self.changed_folder_path.emit(key, p)
        self.synthesize_folder_images(key)

    def synthesize_folder_images(self, key: str):
        print(f"SYNTH0 {key}")
        if not (key in self.folders):
            print(f"Invalid Folder Key: {key}")
            return
        print(f"SYNTH1 {key}")        
        if not self.folders[key].is_synth_ready:
            print("NOT Ready To Synthesize Image.")
            # TODO: エラーダイアログの表示
            return
        print(f"SYNTH2 {key}")        
        step, is_ok = QInputDialog.getInt(
            self.parent(),
            "Synthesize Image Setting",
            """Step: (The smaller this value is, the more precision
the result is, and the longer it takes.)""",
            self.folders[key].step,
            1,
            1024,
            1
            )
        print(f"SYNTH3 {key}")        
        if not is_ok:
            return
        print(f"SYNTH4 {key}")        
        self.folders[key].synthesize_images(self.parent(), step)
        print(f"SYNTH5 {key}")
        
    def reset(self) -> None:
        self.reseted.emit()

    def save_file(self) -> bool:
        return False

    def save_file_as(self) -> bool:
        return False

    def write_dict_to_file(self, file_name: Path, dict_data: dict) -> None:
        return
        #b = msgpack.packb(dict_data, default=msgpack_numpy.encode)
        #    with open(file_name, mode="wb") as f:
        #        f.write(b)

    def pack_data_into_dict(self) -> dict:
        return {}

    def unpack_dict_from_file(self, file_name: Path) -> dict:
        return
        #if not file_name.exists():
        #    return {}
        #with open(file_name, mode="rb") as f:
        #    byte = f.read()
        #return msgpack.unpackb(byte, object_hook=msgpack_numpy.decode)

    def load_data_from_dict(self, dict_data: dict) -> None:
        # NOTE: dict_data はバリデーション済みとして扱う
        ...
        print("CALLED: load_data_from_dict()")

    def _get_save_file_name_path(self, suffix: str, file_filter: str) -> Path:
        fnp = self.file_name_path
        default_path = fnp if fnp is not None else Path.home() / "untitled.atp"
        file_name, fil = QFileDialog.getSaveFileName(
            None,
            "Save File",
            str(default_path),
            file_filter
        )
        if file_name == "" or file_name is None:
            return None
        fnp = Path(file_name)
        name = fnp.name
        if suffix != fnp.suffix:
            name += suffix
        fnp = fnp.parent / name
        return fnp

    def _confirm_overwrite_file(self, file_name: Path) -> bool:
        """
        file_name で指定したファイルが既存の場合に
        上書きするか確認するダイアログを表示する。
        上書きする場合は True をそうでない場合は False を返す。
        既存のファイルが無い場合は True を返す。
        """
        if not file_name.exists():
            return True
        msgbox = QMessageBox()
        msgbox.setIcon(QMessageBox.Icon.Question)
        msgbox.setWindowTitle(" ")
        msgbox.setText("Overwrite Existing File?")
        msgbox.setInformativeText(f"""{file_name} has already exited.
Do you want to overwrite it?""")
        msgbox.setStandardButtons(
            QMessageBox.StandardButton.Ok | QMessageBox.StandardButton.Cancel)
        msgbox.setDefaultButton(QMessageBox.StandardButton.Ok)
        ret = msgbox.exec()
        if ret == QMessageBox.StandardButton.Ok:
            return True
        else:
            return False
