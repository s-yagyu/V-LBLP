import logging
from logging.handlers import RotatingFileHandler
from os import makedirs

from PyQt5.QtWidgets import (
    QWidget,
    QFrame,
    QLabel,
    QDoubleSpinBox,
    QVBoxLayout,
    QHBoxLayout,
    QGridLayout,
    QGroupBox
)
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap

from util.editor import Editor
from util.folder import Folder
from util.affine_transform import AffineTransform


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


class ParamsEditor(QFrame):
    def __init__(
            self,
            parent: QWidget,
            editor: Editor,
            folder_key: str,
            folder_label: str
            ) -> None:
        super().__init__(parent)

        self.editor = editor
        self.folder_key = folder_key
        self.folder_label = folder_label
        if not (self.folder_key in self.editor.folders):
            raise KeyError(f"NOT Find Key: {self.folder_key}")
            return
        self.folder: Folder = self.editor.folders[self.folder_key]
        self.transform = self.folder.get_transform()
        self.setFrameStyle(QFrame.StyledPanel)
        self.setEnabled(False)

        self.create_widgets()
        self.create_actions()
        self.layout_widgets()
        self.create_connections()

    def create_widgets(self):
        self.label = QLabel(self)
        self.label.setText(self.folder_label)

        self.pos_group = QGroupBox("Offset", self)
        self.pos_label_x = QLabel("X : ", self)
        self.pos_label_x.setAlignment(Qt.AlignCenter)
        self.pos_sb_x = QDoubleSpinBox(self)
        self.pos_sb_x.setValue(0.00)
        self.pos_sb_x.setMaximum(9999.99)
        self.pos_sb_x.setMinimum(-9999.99)
        self.pos_sb_x.setAlignment(Qt.AlignRight)
        self.pos_label_y = QLabel("Y : ", self)
        self.pos_label_y.setAlignment(Qt.AlignCenter)
        self.pos_sb_y = QDoubleSpinBox(self)
        self.pos_sb_y.setValue(0.00)
        self.pos_sb_y.setMaximum(9999.99)
        self.pos_sb_y.setMinimum(-9999.99)
        self.pos_sb_y.setAlignment(Qt.AlignRight)

        self.rot_group = QGroupBox("Rotate", self)
        self.rot_label = QLabel("θ : ", self)
        self.rot_label.setAlignment(Qt.AlignCenter)
        self.rot_sb = QDoubleSpinBox(self)
        self.rot_sb.setValue(0.00)
        self.rot_sb.setMaximum(360.00)
        self.rot_sb.setMinimum(-360.00)
        self.rot_sb.setAlignment(Qt.AlignRight)

        self.scl_group = QGroupBox("Scale", self)
        self.scl_label_x = QLabel("Original X : ", self)
        self.scl_label_x.setAlignment(Qt.AlignCenter)
        self.scl_sb_x = QDoubleSpinBox(self)
        self.scl_sb_x.setDecimals(4)
        self.scl_sb_x.setValue(1.0000)
        self.scl_sb_x.setMaximum(9999.9999)
        self.scl_sb_x.setMinimum(-9999.9999)
        # self.scl_sb_x.setMinimum(0.0001)
        self.scl_sb_x.setSingleStep(0.0010)
        self.scl_sb_x.setAlignment(Qt.AlignRight)
        self.scl_label_y = QLabel("Original Y : ", self)
        self.scl_label_y.setAlignment(Qt.AlignCenter)
        self.scl_sb_y = QDoubleSpinBox(self)
        self.scl_sb_y.setDecimals(4)
        self.scl_sb_y.setValue(1.0000)
        self.scl_sb_y.setMaximum(9999.9999)
        # self.scl_sb_y.setMinimum(0.0001)
        self.scl_sb_y.setMinimum(-9999.9999)
        self.scl_sb_y.setSingleStep(0.0010)
        self.scl_sb_y.setAlignment(Qt.AlignRight)

    def create_actions(self):
        pass

    def layout_widgets(self):
        pos_grid = QGridLayout(self)
        pos_grid.addWidget(self.pos_label_x, 0, 0)
        pos_grid.addWidget(self.pos_sb_x, 0, 1, 1, 2)
        pos_grid.addWidget(self.pos_label_y, 0, 3)
        pos_grid.addWidget(self.pos_sb_y, 0, 4, 1, 2)
        self.pos_group.setLayout(pos_grid)

        rot_grid = QGridLayout(self)
        rot_grid.addWidget(self.rot_label, 0, 0)
        rot_grid.addWidget(self.rot_sb, 0, 1, 1, 2)
        rot_grid.addWidget(QWidget(self), 0, 3)
        rot_grid.addWidget(QWidget(self), 0, 4, 1, 2)
        self.rot_group.setLayout(rot_grid)

        scl_grid = QGridLayout(self)
        scl_grid.addWidget(self.scl_label_x, 0, 0)
        scl_grid.addWidget(self.scl_sb_x, 0, 1, 1, 2)
        scl_grid.addWidget(self.scl_label_y, 0, 3)
        scl_grid.addWidget(self.scl_sb_y, 0, 4, 1, 2)
        self.scl_group.setLayout(scl_grid)

        vbox = QVBoxLayout(self)
        vbox.addWidget(self.label)
        vbox.addWidget(self.pos_group)
        vbox.addWidget(self.rot_group)
        vbox.addWidget(self.scl_group)
        vbox.addWidget(QWidget(self), 3)
        self.setLayout(vbox)

    def create_connections(self):
        self.folder.generated_disp_image.connect(
            self.on_folder_generated_disp_image)
        self.folder.loaded_transform.connect(self.on_folder_loaded_transform)
        self.pos_sb_x.valueChanged.connect(self.on_update_position)
        self.pos_sb_y.valueChanged.connect(self.on_update_position)
        self.rot_sb.valueChanged.connect(self.on_update_rotation)
        self.scl_sb_x.valueChanged.connect(self.on_update_scale)
        self.scl_sb_y.valueChanged.connect(self.on_update_scale)

    def on_folder_generated_disp_image(self, pm: QPixmap) -> None:
        self.setEnabled(True)

    def on_folder_loaded_transform(self, trans: AffineTransform) -> None:
        px, py = trans.get_position()
        rz = trans.get_rotation_degree()
        sx, sy = trans.get_scale()
        self.pos_sb_x.setValue(px)
        self.pos_sb_y.setValue(py)
        self.rot_sb.setValue(rz)
        self.scl_sb_x.setValue(sx)
        self.scl_sb_y.setValue(sy)

    def on_update_position(self, val: float) -> None:
        self.transform.set_position(
            self.pos_sb_x.value(), self.pos_sb_y.value())
        self.folder.set_position(*(self.transform.get_position()))

    def on_update_rotation(self, val: float) -> None:
        self.transform.set_rotation_degree(val)
        self.folder.set_rotation_radian(
            self.transform.get_rotation_radian())

    def on_update_scale(self, val: float) -> None:
        self.transform.set_scale(
            self.scl_sb_x.value(), self.scl_sb_y.value())
        self.folder.set_scale(*(self.transform.get_scale()))
