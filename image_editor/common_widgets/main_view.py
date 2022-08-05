from PyQt5.QtWidgets import QWidget
from PyQt5.QtGui import QPixmap

from common_widgets.image_view import ImageView
from util.affine_transform import AffineTransform
from util.editor import Editor


class MainView(ImageView):
    def __init__(self, parent: QWidget, editor: Editor) -> None:
        super().__init__(parent, editor)

    def create_connections(self) -> None:
        super().create_connections()
        for folder in self.editor.folders.values():
            folder.generated_disp_image.connect(
                self.on_folder_generated_disp_image)
            folder.updated_transform.connect(self.on_folder_updated_transform)
            folder.loaded_transform.connect(self.on_folder_updated_transform)
            folder.updated_opacity.connect(self.on_folder_updated_opacity)
            folder.loaded_opacity.connect(self.on_folder_updated_opacity)
            folder.updated_is_visible.connect(
                self.on_folder_updated_is_visible)
            folder.loaded_is_visible.connect(self.on_folder_updated_is_visible)
            folder.ended_load.connect(self.on_folder_ended_load)

    def on_folder_generated_disp_image(self, pm: QPixmap) -> None:
        self.update_pixmapitem(self.sender().name, pm)

    def on_folder_updated_transform(self, transform: AffineTransform) -> None:
        self.set_transform_mapitem(self.sender().name, transform.QTransform())

    def on_folder_updated_opacity(self, opacity: float) -> None:
        self.set_opacity_mapitem(self.sender().name, opacity)

    def on_folder_updated_is_visible(self, is_visible: bool) -> None:
        self.set_visible_mapitem(self.sender().name, is_visible)

    def on_folder_ended_load(self) -> None:
        self.resetTransform()
        self.update_exp_rate_btn()
