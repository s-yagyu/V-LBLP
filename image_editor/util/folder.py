from os.path import isdir
from pathlib import Path
import copy
from PyQt5.QtCore import QObject, Qt, QThread, pyqtSignal
from PyQt5.QtGui import QImage, QPixmap, QColor
from PyQt5.QtWidgets import (
    QWidget,
    QFileDialog,
    QProgressDialog,
    QPushButton,
    QMessageBox
)
import numpy as np
import cv2

from util.tiff_synthesizer import TiffSynthesizer, TiffSynthWorker
from util.affine_transform import AffineTransform


# TODO: 別のフォルダーを開くときに既存のデータをリセットしてシグナルを発信する処理を追加。
class Folder(QObject):
    generated_disp_image = pyqtSignal(QPixmap)
    generated_bin_image = pyqtSignal(np.ndarray)
    generated_bin_image_transformed = pyqtSignal(np.ndarray)
    generated_raw_image_transformed = pyqtSignal(np.ndarray)
    updated_path = pyqtSignal(str)
    updated_transform = pyqtSignal(AffineTransform)
    updated_opacity = pyqtSignal(float)
    updated_is_visible = pyqtSignal(bool)
    updated_step = pyqtSignal(int)
    loaded_path = pyqtSignal(str)
    loaded_transform = pyqtSignal(AffineTransform)
    loaded_opacity = pyqtSignal(float)
    loaded_is_visible = pyqtSignal(bool)
    ended_load = pyqtSignal()

    def __init__(self, name: str) -> None:
        super().__init__()
        self.path = ""
        self.name = name
        self.raw_img: np.ndarray = None
        self.raw_img_transformed: np.ndarray = None
        self.bin_img: np.ndarray = None
        self.bin_img_transformed: np.ndarray = None
        self.image_img: QImage = None
        self.pm_img: QPixmap = None
        self.step: int = 16
        self.is_synth_ready = False
        self.opacity = 1.0
        self.is_visible = True
        self.transform = AffineTransform()

        self.mean = 0.0
        self.threshold = 0.0
        self.color = {"r": 255, "g": 0, "b": 0, "a": 255}

    # FIXME: 思いがけず意図しない transform を設定しかねないので少なくとも公開しないほうがよいか？
    def _set_transform(self, transform: AffineTransform) -> None:
        self.transform = copy.deepcopy(transform)
        self.updated_transform.emit(self.transform)
        self.generate_image_transformed()

    def set_position(self, x: float, y: float) -> None:
        self.transform.set_position(x, y)
        self.updated_transform.emit(self.transform)
        self.generate_image_transformed()

    def set_rotation_radian(self, radian: float) -> None:
        self.transform.set_rotation_radian(radian)
        self.updated_transform.emit(self.transform)
        self.generate_image_transformed()

    def set_scale(self, x: float, y: float) -> None:
        self.transform.set_scale(x, y)
        self.updated_transform.emit(self.transform)
        self.generate_image_transformed()

    def get_transform(self) -> AffineTransform:
        return copy.deepcopy(self.transform)

    def set_opacity(self, opacity: float) -> float:
        opacity = min(1.0, max(opacity, 0.0))
        self.opacity = opacity
        self.updated_opacity.emit(self.opacity)
        return self.opacity

    def set_visible(self, is_visible: bool) -> bool:
        self.is_visible = is_visible
        self.updated_is_visible.emit(self.is_visible)
        return self.is_visible

    def set_step(self, step: int) -> int:
        step = min(32, max(step, 1))
        self.step = step
        self.updated_step.emit(self.step)
        return self.step

    def update_color(self, r: int, g: int, b: int, a: int = 255) -> None:
        self.color["r"] = self._clamp_8bit(r)
        self.color["g"] = self._clamp_8bit(g)
        self.color["b"] = self._clamp_8bit(b)
        self.color["a"] = self._clamp_8bit(a)
        if self.raw_img is None:
            print(f"Folder (\"{self.name}\") DOSEN'T Have Any Image Data.")
            return
        self.update_display_image_color()

    def _clamp_8bit(self, val: int) -> int:
        return min(255, max(val, 0))

    def get_QColor(self) -> QColor:
        return QColor(self.color["r"], self.color["g"], self.color["b"])

    def pack_data_into_dict(self) -> dict:
        px, py = self.transform.get_position()
        rz = self.transform.get_rotation_radian()
        sx, sy = self.transform.get_scale()
        ox, oy = self.transform.get_origin()
        return {
            "name": self.name,
            "path": self.path,
            "step": self.step,
            "raw_img": self.raw_img,
            "params": {
                "px": px,
                "py": py,
                "rz": rz,
                "sx": sx,
                "sy": sy,
                "ox": ox,
                "oy": oy
            },
            "is_synth_ready": self.is_synth_ready,
            "opacity": self.opacity,
            "is_visible": self.is_visible,
            "mean": self.mean,
            "threshold": self.threshold,
            "color": self.color
        }

    def load_data_from_dict(self, dict_data: dict) -> None:
        d = dict_data
        p = d["params"]
        self.path = d["path"]
        self.loaded_path.emit(self.path)
        self.step = d["step"]
        self.is_synth_ready = d["is_synth_ready"]
        self.mean = d["mean"]
        self.threshold = d["threshold"]
        self.color = d["color"]
        raw_img = d["raw_img"]
        if raw_img is not None:
            self.raw_img = raw_img
            self.generate_display_image()
        self.opacity = (min(1.0, max(d["opacity"], 0.0)))
        self.loaded_opacity.emit(self.opacity)
        self.is_visible = (d["is_visible"])
        self.loaded_is_visible.emit(self.is_visible)
        self.transform.set_position(p["px"], p["py"])
        self.transform.set_rotation_radian(p["rz"])
        self.transform.set_scale(p["sx"], p["sy"])
        self.transform.set_origin(p["ox"], p["oy"])
        self.loaded_transform.emit(self.transform)
        if self.raw_img is not None:
            self.generate_image_transformed()
        # NOTE: 最後にビューの拡大率を合わせるために送るシグナル
        self.ended_load.emit()

    def open(
            self,
            parent: QWidget,
            path: str = "",
            dialog_message: str = "Open Folder"
            ) -> str:
        """
        path が空文字列ならダイアログを表示してユーザーにフォルダーを選択させる。
        フォルダーの取得に失敗もしくは現在と同じフォルダーを取得した時は空文字列を返す。
        """
        p = path
        if p != "":
            if not isdir(p):
                self.mbox = QMessageBox()
                self.mbox.setWindowTitle("ERROR")
                self.mbox.setText(f"ERROR: CANNOT Open The Folder: {p}")
                # TODO: エラーと分かりやすいようにアイコンを設定する。
                self.mbox.exec()
                print(f"ERROR: CANNOT Open The Folder: {p}")
                return ""
        else:
            p = QFileDialog.getExistingDirectory(
                   parent,
                   dialog_message,
                   str(Path.home()) if self.path == "" else self.path,
                   QFileDialog.ShowDirsOnly)
        if p == self.path or p == "":
            return ""
        self.path = p
        self.updated_path.emit(self.path)

        self.is_synth_ready = True
        return p

    def synthesize_images(self, parent: QWidget, step: int) -> None:
        if not self.is_synth_ready:
            print(f"Folder (\"{self.name}\") Is NOT Ready For Synthesizing.")
            return
        step = min(32, max(step, 1))
        self.tmp_step = step
        # プログレスダイアログの初期化
        self.synth_progress = QProgressDialog(
            "Progress",
            "Cancel",
            0,
            100,
            parent
            )
        self.synth_progress.setWindowModality(Qt.WindowModal)
        self.synth_progress.setAutoReset(False)
        self.synth_progress.setAutoClose(False)
        self.synth_progress.setWindowTitle("Synthesizing Image")
        self.progress_cancel_btn = self.synth_progress.findChild(QPushButton)
        self.synth_progress.setValue(0)
        self.synth_progress.show()

        # スレッドの初期化
        self.thread = QThread()
        self.worker = TiffSynthWorker(self.path, step=step)
        self.worker.moveToThread(self.thread)
        self.thread.started.connect(self.worker.run)
        self.worker.updated.connect(self.on_worker_updated)
        self.worker.finished.connect(self.on_worker_finished)
        # self.worker.finished.connect(self.thread.quit)
        self.worker.finished.connect(self.thread.deleteLater)
        self.worker.finished.connect(self.worker.deleteLater)
        self.worker.synthesized.connect(self.on_worker_synthesized)
        self.worker.aborted.connect(self.on_worker_aborted)
        self.worker.aborted.connect(self.thread.deleteLater)
        self.worker.aborted.connect(self.worker.deleteLater)
        self.worker.error_occured.connect(self.on_worker_error_occured)

        # キャンセルボタンをクリックしたときの挙動
        self.synth_progress.canceled.connect(self.on_progress_canceled)

        # スレッドの開始
        self.thread.start()

    def on_worker_updated(self, value: int):
        print(f"UPDATE: {value}")
        self.synth_progress.setValue(value)

    def on_worker_finished(self):
        self.close_progress()
        self.thread.quit()
        self.thread.wait()
        print("QThread FINISHED.")

    def on_worker_synthesized(self, image: np.ndarray):
        self.progress_cancel_btn.setEnabled(False)
        self.raw_img = image
        self.mean = self.threshold = np.median(self.raw_img)
        self.set_step(self.tmp_step)
        self.generate_display_image()
        self.generate_image_transformed()

    def on_worker_aborted(self):
        self.close_progress()
        self.thread.quit()
        self.thread.wait()
        print("QThread ABORTED.")

    def on_progress_canceled(self):
        print("CALLED on_progress_canceled")
        self.worker.stop()

    def on_worker_error_occured(self, err_msg):
        self.close_progress()
        self.thread.quit()
        self.thread.wait()
        self.mbox = QMessageBox()
        self.mbox.setWindowTitle("ERROR")
        self.mbox.setText(err_msg)
        # TODO: エラーと分かりやすいようにアイコンを設定する。
        self.mbox.exec()
        print(f"ERROR: {err_msg}")

    def close_progress(self):
        print("CALLED close_progress")
        self.synth_progress.reset()
        self.synth_progress.close()

    def generate_display_image(self):
        if self.raw_img is None:
            print(f"Folder (\"{self.name}\") DOSEN'T Have Any Image Data.")
            return
        h, w = self.raw_img.shape
        self.transform.set_origin(w/2, h/2)
        self.bin_img = TiffSynthesizer.binarize(self.raw_img)
        self.bin_img[h//2,:] = True
        self.bin_img[:,w//2] = True        
        self.generated_bin_image.emit(self.bin_img)
        self.bin_img_transformed = self.bin_img
        self.update_display_image_color()
        
    def update_display_image_color(self):
        h, w = self.raw_img.shape
        im_bool = self.bin_img > 0
        im_rgba = np.empty((h, w, 4), np.uint8)
        for i, c in enumerate(self.color.values()):
            im_rgba[:, :, i] = im_bool * c
        self.image_img = QImage(
            im_rgba,
            im_rgba.shape[1],
            im_rgba.shape[0],
            QImage.Format_RGBA8888
            )
        self.pm_img = QPixmap.fromImage(self.image_img)
        self.generated_disp_image.emit(self.pm_img)

    def generate_image_transformed(self):
        if self.raw_img is None:
            print(f"Folder (\"{self.name}\") DOSEN'T Have Any Image Data.")
            return
        m = self.transform.M()
        h, w = self.bin_img.shape
        self.bin_img_transformed = cv2.warpAffine(self.bin_img, m, (w, h))
        # self.generated_raw_image_transformed.emit(self.raw_img_transformed)
        # self.bin_img_transformed = TiffSynthesizer.binarize(self.raw_img_transformed)
        self.generated_bin_image_transformed.emit(self.bin_img_transformed)
