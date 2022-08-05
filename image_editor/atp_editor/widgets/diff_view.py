import numpy as np
import cv2
from PyQt5.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QVBoxLayout
)
from PyQt5.QtGui import (
    QImage,
    QPixmap
)

from common_widgets.image_view import ImageView
from util.editor import Editor


class DiffView(QFrame):
    def __init__(self, parent: QWidget, editor: Editor) -> None:
        super().__init__(parent)

        self.editor = editor
        self.im_bin_b: np.ndarray = None
        self.im_bin_r: np.ndarray = None
        self.setFrameStyle(QFrame.StyledPanel)

        folder_b_key = "base"
        if not (folder_b_key in self.editor.folders):
            raise KeyError(f"NOT Find Key: {folder_b_key}")
            return
        self.folder_b = self.editor.folders[folder_b_key]

        folder_r_key = "rotated"
        if not (folder_r_key in self.editor.folders):
            raise KeyError(f"NOT Find Key: {folder_r_key}")
            return
        self.folder_r = self.editor.folders[folder_r_key]

        self.create_widgets()
        self.create_actions()
        self.layout_widgets()
        self.create_connections()

    def create_widgets(self) -> None:
        self.label = QLabel("Diff", self)
        self.view = ImageView(self, self.editor)

    def create_actions(self) -> None:
        ...

    def layout_widgets(self) -> None:
        vbox = QVBoxLayout()
        vbox.addWidget(self.label)
        vbox.addWidget(self.view)
        self.setLayout(vbox)

    def create_connections(self) -> None:
        self.folder_b.generated_bin_image.connect(
            self.on_folder_b_generaged_bin_img)
        self.folder_r.generated_bin_image_transformed.connect(
            self.on_folder_r_generated_bin_img)

    def update_diff_image(self) -> None:
        diff = cv2.absdiff(self.im_bin_b, self.im_bin_r)
        image = QImage(
            diff,
            diff.shape[1],
            diff.shape[0],
            diff.shape[1],
            QImage.Format_Grayscale8
        )
        pixmap = QPixmap.fromImage(image)
        self.view.update_pixmapitem("diff", pixmap)

    def on_folder_b_generaged_bin_img(self, im_bin: np.ndarray) -> None:
        self.im_bin_b = im_bin

    def on_folder_r_generated_bin_img(self, im_bin: np.ndarray) -> None:
        self.im_bin_r = im_bin
        self.update_diff_image()
