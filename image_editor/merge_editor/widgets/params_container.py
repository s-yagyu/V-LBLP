from PyQt5.QtWidgets import QWidget, QVBoxLayout, QScrollArea, QGridLayout
from PyQt5.QtCore import Qt
from util.editor import Editor
from common_widgets.params_editor import ParamsEditor


class ParamsContainer(QWidget):
    def __init__(self, parent: QWidget, editor: Editor) -> None:
        super().__init__(parent)
        self.editor = editor
        self.create_widgets()
        self.layout_widgets()

    def create_widgets(self) -> None:
        self.param_tl = ParamsEditor(
            self, self.editor, "top-left", "A")
        self.param_tr = ParamsEditor(
            self, self.editor, "top-right", "B")
        self.param_bl = ParamsEditor(
            self, self.editor, "bottom-left", "C")
        self.param_br = ParamsEditor(
            self, self.editor, "bottom-right", "D")

    def layout_widgets(self) -> None:
        self.scroll_area = QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.scroll_contents = QWidget()
        self.scroll_area.setWidget(self.scroll_contents)
        self.scroll_area.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        grid = QGridLayout()
        grid.addWidget(self.scroll_area, 0, 0)
        self.setLayout(grid)

        vbox = QVBoxLayout()
        vbox.addWidget(self.param_tl)
        vbox.addWidget(self.param_tr)
        vbox.addWidget(self.param_bl)
        vbox.addWidget(self.param_br)
        self.scroll_contents.setLayout(vbox)
