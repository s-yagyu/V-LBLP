import numpy as np
from PyQt5.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QVBoxLayout,
    QGridLayout,
    QLineEdit
)
from PyQt5.QtCore import Qt

from util.editor import Editor


class SimilarityIndicator(QFrame):
    def __init__(self, parent: QWidget, editor: Editor) -> None:
        super().__init__(parent)

        self.editor = editor
        self.im_bin_b: np.ndarray = None
        self.im_bin_r: np.ndarray = None
        self.ncc_val = 0.0
        self.zncc_val = 0.0
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

    def create_widgets(self):
        self.title_label = QLabel("Similarity", self)
        self.ncc_label = QLabel("NCC: ", self)
        self.ncc_val_le = QLineEdit(f"{self.ncc_val:.4f}", self)
        self.ncc_val_le.setAlignment(Qt.AlignRight)
        self.zncc_label = QLabel("ZNCC: ", self)
        self.zncc_val_le = QLineEdit(f"{self.zncc_val:.4f}", self)
        self.zncc_val_le.setAlignment(Qt.AlignRight)

    def create_actions(self):
        ...

    def layout_widgets(self):
        ncc_grid = QGridLayout()
        ncc_grid.addWidget(self.ncc_label, 0, 0)
        ncc_grid.addWidget(self.ncc_val_le, 0, 1, 1, 2)

        zncc_grid = QGridLayout()
        zncc_grid.addWidget(self.zncc_label, 0, 0)
        zncc_grid.addWidget(self.zncc_val_le, 0, 1, 1, 2)

        layout = QVBoxLayout()
        layout.addWidget(self.title_label)
        layout.addLayout(ncc_grid)
        layout.addLayout(zncc_grid)
        self.setLayout(layout)

    def create_connections(self):
        self.folder_b.generated_bin_image_transformed.connect(
            self.on_folder_b_generaged_bin_img)
        self.folder_r.generated_bin_image_transformed.connect(
            self.on_folder_r_generated_bin_img)

    def update_display(self) -> None:
        self.ncc_val_le.setText(f"{self.ncc_val:.4f}")
        self.zncc_val_le.setText(f"{self.zncc_val:.4f}")

    def calc_similarity(self) -> None:
        if self.im_bin_b is None or self.im_bin_r is None:
            return
        self.ncc_val = self.ncc(self.im_bin_b, self.im_bin_r)
        self.zncc_val = self.zncc(self.im_bin_b, self.im_bin_r)
        self.update_display()

    def ncc(self, mat1: np.ndarray, mat2: np.ndarray) -> float:
        sum = np.sum(mat1 * mat2)
        n1 = np.linalg.norm(mat1)
        n2 = np.linalg.norm(mat2)
        if n1 ==0 or n2 == 0:
            return 0
        else:
            return sum / (n1*n2)

    def zncc(self, mat1: np.ndarray, mat2: np.ndarray) -> float:
        m1 = mat1 - mat1.mean()
        m2 = mat2 - mat2.mean()
        return self.ncc(m1, m2)

    def on_folder_b_generaged_bin_img(self, im_bin: np.ndarray) -> None:
        self.im_bin_b = im_bin.astype(np.float32)
        self.calc_similarity()
        
    def on_folder_r_generated_bin_img(self, im_bin: np.ndarray) -> None:
        self.im_bin_r = im_bin.astype(np.float32)
        self.calc_similarity()
