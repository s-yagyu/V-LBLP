from PyQt5.QtWidgets import QWidget, QLabel

from common_widgets.image_view import ImageView
from util.editor import Editor


class FolderImageView(ImageView):
    def __init__(self, parent: QWidget, editor: Editor) -> None:
        super().__init__(parent, editor)

    def create_widgets(self) -> None:
        super().create_widgets()
        # self.step_label = QLabel("step: Undifined", self)
        # TODO: 相対的に位置を決める。
        # self._print_label_size()
        # self.step_label.move(self.width() - self.step_label.width() - 48, 0)

    def on_folder_updated_step(self, step: int) -> None:
        ...
        # self.step_label.setText(f"step: {step}")
        # self._print_label_size()
        # self.step_label.move(self.width() - self.step_label.width() - 48, 0)

    # NOTE: 検証用のプリントメソッド
    def _print_label_size(self) -> None:
        size = self.step_label.size()
        print(self.geometry().width())
        print(f"width: {size.width()}, height: {size.height()}")
