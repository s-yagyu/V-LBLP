import logging
from logging.handlers import RotatingFileHandler
from os import makedirs
from os.path import isdir

from PyQt5.QtCore import Qt
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
    QHBoxLayout,
    QPushButton,
    QSlider,
    QColorDialog,
    QCheckBox
)
from PyQt5.QtGui import QPixmap
# from widgets.image_preview import ImagePreview
from util.editor import Editor
from util.folder import Folder
from common_widgets.folder_image_view import FolderImageView

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


# TODO: ImgFolderLineEdit の内容を書き換えてエンターを押したときにフォルダーを開く動作を追加する。
class FileExplorer(QWidget):
    def __init__(
            self,
            parent: QWidget,
            editor: Editor,
            folder_key: str = "",
            show_img=True
            ) -> None:
        super().__init__(parent)

        self.show_img = show_img
        self.editor = editor
        self.folder_key = folder_key
        if not (self.folder_key in self.editor.folders):
            raise KeyError(f"NOT Find Key: {self.folder_key}")
            return
        self.folder: Folder = self.editor.folders[folder_key]

        self.create_widgets()
        self.create_actions()
        self.layout_widgets()
        self.create_connections()

    def create_widgets(self):
        self.ImgLabel = QLabel(self)
        self.ImgFolderLineEdit = QLineEdit(self)
        self.open_button = QPushButton("Open...", self)
        self.synth_img_button = QPushButton("Synthesize Image...", self)
        if self.show_img:
            self.preview = FolderImageView(self, self.editor)
        self.color_button = QPushButton("Color...", self)
        # TODO: チェックボックスを視覚的に分かりやすいアイコンに置き換える。
        self.is_visible_cb = QCheckBox(self)
        self.is_visible_cb.setChecked(True)
        self.opacity_slider = QSlider(Qt.Horizontal, self)
        self.opacity_slider.setRange(0, 255)
        self.opacity_slider.setValue(255)
        self.set_disp_settings_enabled(False)

    def set_disp_settings_enabled(self, enabled: bool) -> None:
        self.color_button.setEnabled(enabled)
        self.is_visible_cb.setEnabled(enabled)
        self.opacity_slider.setEnabled(enabled)

    def create_actions(self):
        pass

    def layout_widgets(self):
        vbox = QVBoxLayout()
        vbox.addWidget(self.ImgLabel)
        vbox.addWidget(self.ImgFolderLineEdit)
        hbox = QHBoxLayout()
        hbox.addWidget(self.open_button)
        hbox.addWidget(self.synth_img_button)
        vbox.addLayout(hbox)
        if self.show_img:
            vbox.addWidget(self.preview)
        hbox_view = QHBoxLayout()
        hbox_view.addWidget(self.color_button)
        hbox_view.addWidget(self.is_visible_cb)
        hbox_view.addWidget(self.opacity_slider)
        vbox.addLayout(hbox_view)
        self.setLayout(vbox)

    def create_connections(self):
        self.folder.generated_disp_image.connect(
            self.on_folder_generated_disp_image)
        self.folder.updated_path.connect(self.on_folder_updated_path)
        self.folder.loaded_path.connect(self.on_folder_updated_path)
        self.folder.updated_opacity.connect(self.on_folder_updated_opacity)
        self.folder.loaded_opacity.connect(self.on_folder_loaded_opacity)
        self.folder.loaded_is_visible.connect(self.on_folder_loaded_is_visible)
        self.folder.updated_step.connect(self.on_folder_updated_step)
        if self.show_img:
            self.folder.updated_step.connect(self.preview.on_folder_updated_step)
        self.folder.ended_load.connect(self.on_folder_ended_load)
        self.open_button.clicked.connect(self.on_open_button_clicked)
        self.synth_img_button.clicked.connect(self.on_synth_img_button_clicked)
        self.color_button.clicked.connect(self.on_color_button_clicked)
        self.is_visible_cb.toggled.connect(self.on_is_visible_cb_toggled)
        self.opacity_slider.valueChanged.connect(self.on_opacity_value_changed)

    def on_folder_updated_path(self, path: str) -> None:
        self.ImgFolderLineEdit.setText(path)

    def on_folder_generated_disp_image(self, pm: QPixmap) -> None:
        if self.show_img:
            self.preview.update_pixmapitem(self.folder_key, pm)
        self.set_disp_settings_enabled(True)

    def on_folder_updated_opacity(self, opacity: float) -> None:
        # NOTE: このウィジェット上の表示では opacity は1.0 で固定する。
        # self.preview.set_opacity_mapitem(self.folder_key, opacity)
        # NOTE: ここで opacity_slider の値を変更すると無限ループになるので注意！
        pass

    def on_folder_loaded_opacity(self, opacity: float) -> None:
        self.opacity_slider.setValue(opacity*255)

    def on_folder_loaded_is_visible(self, is_visible: bool) -> None:
        self.is_visible_cb.setChecked(is_visible)

    def on_folder_updated_step(self, step: int) -> None:
        pass

    def on_folder_ended_load(self) -> None:
        if self.show_img:
            self.preview.reset_transform_to_fit()

    def on_open_button_clicked(self):
        pass

    def on_synth_img_button_clicked(self):
        self.editor.synthesize_folder_images(self.folder_key)

    def on_color_button_clicked(self) -> None:
        pre_c = self.folder.get_QColor()
        c = QColorDialog.getColor(pre_c, self)
        if c.isValid() and c != pre_c:
            self.folder.update_color(c.red(), c.green(), c.blue())

    def on_is_visible_cb_toggled(self) -> None:
        self.folder.set_visible(self.is_visible_cb.isChecked())

    def on_opacity_value_changed(self) -> None:
        self.folder.set_opacity(self.opacity_slider.value() / 255)
